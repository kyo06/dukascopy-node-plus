#!/usr/bin/env python3
"""
sync_agent_docs.py — Met à jour le(s) fichier(s) d'instructions IA du projet
pour référencer la spec active, sans écraser le reste du contenu. Connaît
aussi l'emplacement des skills et des hooks (JSON) de chaque outil, pour
pouvoir en informer l'utilisateur/l'agent (ce script ne crée jamais de hook
lui-même : les hooks sont hors du périmètre de cette skill, mais leur
emplacement est utile à connaître pour brancher une vérification déterministe
du workflow spec-driven si l'utilisateur le souhaite).

Usage:
    python3 sync_agent_docs.py --list-tools
    python3 sync_agent_docs.py --root PROJECT_ROOT --detect
    python3 sync_agent_docs.py --root PROJECT_ROOT --version v003 --tools claude,copilot
    python3 sync_agent_docs.py --root PROJECT_ROOT --version v003 --tools claude --create-missing
    python3 sync_agent_docs.py --root PROJECT_ROOT --version v003              # fallback autodetect

Comportement recommandé (ne pas deviner l'outil à l'aveugle) :
1. Lancer avec --list-tools pour obtenir la liste des outils supportés (fichier
   d'instructions + emplacement des hooks JSON pour chacun).
2. Optionnel : lancer avec --detect (lecture seule) pour voir quels fichiers
   d'instructions et quels hooks existent déjà dans le projet — c'est un
   signal utile à présenter à l'utilisateur, mais ça ne remplace jamais sa
   confirmation explicite lors de la toute première synchronisation.
3. Demander explicitement à l'utilisateur quel(s) outil(s) IA sont utilisés sur
   ce projet (Claude Code, Copilot, Cursor, Windsurf, Cline, Gemini, AGENTS.md...).
4. Relancer avec --tools <clé1>,<clé2> correspondant à sa réponse.

Sans --tools : comportement de repli "autodetect" — met à jour uniquement les
fichiers d'instructions déjà présents dans le projet (n'en crée aucun sauf
--create-missing). Utile pour une resynchro rapide sur un projet déjà configuré,
mais ne doit PAS servir à choisir l'outil à la place de l'utilisateur lors de la
toute première synchronisation.
"""
import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
BLOCK_TEMPLATE_PATH = SKILL_DIR / "templates" / "agent-instructions-block.md"

START_MARKER = "<!-- SPEC-DRIVEN:START -->"
END_MARKER = "<!-- SPEC-DRIVEN:END -->"

# Outils IA reconnus -> (chemins relatifs du fichier d'instructions, du plus
# "moderne/recommandé pour une création" au plus "legacy", libellé humain).
# Le premier chemin de la liste est celui utilisé pour une CRÉATION
# (--create-missing) ; tous les chemins de la liste sont vérifiés pour la
# DÉTECTION d'un fichier déjà existant.
TOOL_MAP = {
    "claude":  (["CLAUDE.md"],
                "Claude Code"),
    "agents":  (["AGENTS.md"],
                "Standard ouvert AGENTS.md (Codex, Jules, et autres outils qui l'adoptent)"),
    "copilot": ([".github/copilot-instructions.md"],
                "GitHub Copilot (instructions dépôt entier)"),
    "cursor":  ([".cursor/rules/spec-driven.mdc", ".cursorrules"],
                "Cursor (règle moderne .cursor/rules/*.mdc ; .cursorrules = ancien format à plat, encore lu)"),
    "windsurf":([".windsurf/rules/spec-driven.md", ".windsurfrules"],
                "Windsurf / Cascade (règle moderne .windsurf/rules/*.md ; .windsurfrules = ancien format à plat)"),
    "cline":   ([".clinerules/spec-driven.md", ".clinerules"],
                "Cline (règle moderne dossier .clinerules/*.md ; .clinerules = ancien fichier à plat)"),
    "gemini":  (["GEMINI.md"],
                "Gemini CLI / Gemini Code Assist"),
}

# Emplacement des hooks (automatisations JSON déterministes) de chaque outil,
# quand l'outil en propose. None = pas de système de hooks documenté à ce
# jour pour cet outil (il ne faut jamais en inventer un). Ces hooks ne sont
# JAMAIS créés par cette skill : l'information sert uniquement à orienter
# l'utilisateur s'il veut, par exemple, faire échouer un commit ou bloquer un
# outil tant que sprint_status.md n'a pas été mis à jour.
HOOKS_MAP = {
    "claude":  (".claude/settings.json",
                "clé JSON \"hooks\" (événements PreToolUse/PostToolUse/Stop/...)"),
    "agents":  (None,
                "dépend de l'outil qui lit AGENTS.md — pas d'emplacement de hooks standard"),
    "copilot": (".github/hooks/*.json",
                "un fichier JSON par hook (événements sessionStart/preToolUse/postToolUse/... — fonctionnalité en Preview)"),
    "cursor":  (".cursor/hooks.json",
                "clé JSON \"hooks\" (beforeShellExecution, afterFileEdit, stop, ...)"),
    "windsurf":(".windsurf/hooks.json",
                "clé JSON \"hooks\" (post_setup_worktree, ...) — existe aussi en version utilisateur/système"),
    "cline":   (None,
                "pas de système de hooks documenté à ce jour — uniquement des règles (.clinerules/)"),
    "gemini":  (".gemini/settings.json",
                "clé JSON \"hooks\" (BeforeTool/AfterTool/SessionStart/...)"),
}

# À plat, pour le mode autodetect (fallback sans --tools) : tous les chemins
# de fichiers d'instructions connus, quel que soit l'outil.
KNOWN_AGENT_FILES = [path for paths, _ in TOOL_MAP.values() for path in paths]

# Fichiers créés par défaut si --create-missing est utilisé sans --tools et
# qu'aucun fichier d'instructions n'existe encore dans le projet.
DEFAULT_FILES_TO_CREATE = ["CLAUDE.md", "AGENTS.md"]


def build_block(version: str) -> str:
    raw = BLOCK_TEMPLATE_PATH.read_text(encoding="utf-8")
    return raw.replace("{{ACTIVE_VERSION}}", version)


def upsert_block(file_path: Path, block: str) -> str:
    """Retourne 'updated', 'inserted' ou 'created'."""
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(block.strip() + "\n", encoding="utf-8")
        return "created"

    content = file_path.read_text(encoding="utf-8")
    if START_MARKER in content and END_MARKER in content:
        start = content.index(START_MARKER)
        end = content.index(END_MARKER) + len(END_MARKER)
        new_content = content[:start] + block.strip() + content[end:]
        file_path.write_text(new_content, encoding="utf-8")
        return "updated"
    else:
        separator = "\n\n" if not content.endswith("\n\n") else ""
        new_content = content.rstrip("\n") + "\n" + separator + block.strip() + "\n"
        file_path.write_text(new_content, encoding="utf-8")
        return "inserted"


def print_tool_list():
    print("Outils IA supportés (clé → fichier(s) d'instructions → hooks JSON) :\n")
    for key, (paths, label) in TOOL_MAP.items():
        hooks_path, hooks_note = HOOKS_MAP[key]
        print(f"  {key:9s} → {label}")
        print(f"              instructions : {', '.join(paths)}")
        if hooks_path:
            print(f"              hooks        : {hooks_path}  ({hooks_note})")
        else:
            print(f"              hooks        : — ({hooks_note})")
        print()


def detect_existing(project_root: Path):
    """Lecture seule : renvoie, pour chaque outil, les fichiers d'instructions
    et hooks déjà présents dans le projet. Ne modifie rien. Sert de contexte
    informatif avant de poser la question à l'utilisateur (étape 2.2 de la
    skill) — ne remplace jamais la confirmation explicite."""
    report = {}
    for key, (paths, label) in TOOL_MAP.items():
        found_instructions = [p for p in paths if (project_root / p).exists()]
        hooks_path, _ = HOOKS_MAP[key]
        found_hooks = []
        if hooks_path:
            if hooks_path.endswith("/*.json"):
                hook_dir = project_root / hooks_path[: -len("/*.json")]
                if hook_dir.is_dir():
                    found_hooks = sorted(str(p.relative_to(project_root)) for p in hook_dir.glob("*.json"))
            else:
                if (project_root / hooks_path).exists():
                    found_hooks = [hooks_path]
        if found_instructions or found_hooks:
            report[key] = {"label": label, "instructions": found_instructions, "hooks": found_hooks}
    return report


def print_detect_report(report: dict):
    if not report:
        print("ℹ️  Aucun fichier d'instructions IA ni hook connu détecté dans ce projet.")
        print("   Cela ne veut pas dire qu'aucun outil n'est utilisé — demander à l'utilisateur.")
        return
    print("Fichiers déjà présents dans ce projet (lecture seule, à confirmer avec l'utilisateur) :\n")
    for key, info in report.items():
        print(f"  {key:9s} ({info['label']})")
        for p in info["instructions"]:
            print(f"              instructions trouvées : {p}")
        for p in info["hooks"]:
            print(f"              hooks trouvés          : {p}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Synchronise les fichiers d'instructions IA avec la spec active.")
    parser.add_argument("--root", default=".", help="Racine du projet (défaut: dossier courant)")
    parser.add_argument("--version", help="Version active de la spec, ex: v003")
    parser.add_argument(
        "--tools",
        default="",
        help="Liste de clés d'outils séparées par des virgules (ex: claude,copilot). "
             "Si fourni, SEULS ces outils sont créés/mis à jour (pas d'autodétection).",
    )
    parser.add_argument(
        "--create-missing",
        action="store_true",
        help="Crée les fichiers manquants pour les outils ciblés (ou CLAUDE.md/AGENTS.md en mode autodetect).",
    )
    parser.add_argument("--list-tools", action="store_true", help="Liste les outils supportés (instructions + hooks) et quitte.")
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Lecture seule : liste les fichiers d'instructions et hooks déjà présents dans le projet, puis quitte. "
             "Ne modifie rien et ne choisit pas d'outil à la place de l'utilisateur.",
    )
    args = parser.parse_args()

    if args.list_tools:
        print_tool_list()
        return

    if args.detect:
        project_root = Path(args.root).resolve()
        print_detect_report(detect_existing(project_root))
        return

    if not args.version:
        print("❌ --version est requis (sauf avec --list-tools / --detect).", file=sys.stderr)
        sys.exit(1)

    project_root = Path(args.root).resolve()
    block = build_block(args.version)
    results = []

    if args.tools.strip():
        # Mode explicite : l'utilisateur a choisi ses outils.
        keys = [t.strip() for t in args.tools.split(",") if t.strip()]
        unknown = [k for k in keys if k not in TOOL_MAP]
        if unknown:
            print(f"❌ Outil(s) inconnu(s) : {', '.join(unknown)}. Utiliser --list-tools pour voir les clés valides.", file=sys.stderr)
            sys.exit(1)
        for key in keys:
            paths, _label = TOOL_MAP[key]
            # Pour un outil ayant plusieurs chemins possibles (ex: cursor,
            # windsurf, cline : format moderne "dossier" + ancien format "à
            # plat"), on met à jour ceux qui existent déjà ; si aucun n'existe,
            # on crée le premier chemin de la liste (le format moderne
            # recommandé) si --create-missing.
            existing = [p for p in paths if (project_root / p).exists()]
            targets = existing if existing else ([paths[0]] if args.create_missing else [])
            if not targets and not existing:
                print(f"⚠️  {key} : aucun fichier trouvé ({', '.join(paths)}) et --create-missing non spécifié.", file=sys.stderr)
                continue
            for rel_path in targets:
                file_path = project_root / rel_path
                status = upsert_block(file_path, block)
                results.append((key, str(file_path), status))
    else:
        # Mode autodetect (fallback) : ne touche que ce qui existe déjà.
        found_any = False
        for key, (paths, _label) in TOOL_MAP.items():
            for rel_path in paths:
                file_path = project_root / rel_path
                if file_path.exists():
                    found_any = True
                    status = upsert_block(file_path, block)
                    results.append((key, str(file_path), status))

        if not found_any and args.create_missing:
            for rel_path in DEFAULT_FILES_TO_CREATE:
                file_path = project_root / rel_path
                status = upsert_block(file_path, block)
                results.append(("", str(file_path), status))

    if not results:
        print(
            "⚠️  Aucun fichier mis à jour. Utiliser --tools <clé1>,<clé2> après avoir "
            "demandé à l'utilisateur quel(s) outil(s) IA il utilise (--list-tools pour "
            "la liste, --detect pour voir ce qui existe déjà), éventuellement avec --create-missing.",
            file=sys.stderr,
        )
        sys.exit(2)

    icon = {"created": "🆕", "inserted": "➕", "updated": "🔄"}
    seen_hook_hints = set()
    for key, path, status in results:
        print(f"{icon[status]} {status:9s} {path}")
        if key and key not in seen_hook_hints:
            hooks_path, hooks_note = HOOKS_MAP[key]
            if hooks_path:
                print(f"   ℹ️  hooks {key} (si besoin d'automatisation déterministe) : {hooks_path} — {hooks_note}")
            seen_hook_hints.add(key)


if __name__ == "__main__":
    main()
