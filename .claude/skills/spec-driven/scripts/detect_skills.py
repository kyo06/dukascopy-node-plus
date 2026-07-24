#!/usr/bin/env python3
"""
detect_skills.py — Détecte les skills (fichiers SKILL.md) déjà présentes dans
le projet, pour permettre de les référencer dans tasks.md (colonne "Skill(s)
recommandée(s)").

Recherche récursive de fichiers `SKILL.md` dans le projet, sous les
emplacements usuels en priorité (ce sont les dossiers "skills projet" reconnus
par les principaux outils IA — Claude Code, GitHub Copilot, et le standard
Agent Skills ouvert repris par plusieurs autres) :
    .claude/skills/**/SKILL.md
    .github/skills/**/SKILL.md
    .agents/skills/**/SKILL.md
    skills/**/SKILL.md
puis en fallback une recherche récursive complète du projet (en excluant les
dossiers volumineux/non pertinents : node_modules, .git, dist, build, vendor,
venv, .venv, __pycache__).

Note : les skills "personnelles" installées hors du projet (ex. ~/.claude/skills/,
~/.copilot/skills/, ~/.agents/skills/) ne sont volontairement pas scannées ici
— seules les skills versionnées avec le projet sont pertinentes pour tasks.md.

Usage:
    python3 detect_skills.py --root PROJECT_ROOT [--json]

Sortie par défaut : liste Markdown "nom — description" prête à coller dans
la section "Skills du projet détectées" de tasks.md.
Avec --json : liste structurée [{"name":..., "description":..., "path":...}]
"""
import argparse
import json
import sys
from pathlib import Path

PRIORITY_DIRS = [".claude/skills", ".github/skills", ".agents/skills", "skills"]
EXCLUDE_DIR_NAMES = {
    "node_modules", ".git", "dist", "build", "vendor",
    "venv", ".venv", "__pycache__", ".next", ".turbo", "target",
}


def parse_frontmatter(text: str) -> dict:
    """Parse minimal YAML frontmatter (name/description only, single-line values)."""
    result = {"name": "", "description": ""}
    if not text.startswith("---"):
        return result
    lines = text.split("\n")
    in_block = False
    current_key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            result["name"] = line.split(":", 1)[1].strip()
            current_key = "name"
        elif line.startswith("description:"):
            result["description"] = line.split(":", 1)[1].strip()
            current_key = "description"
        elif current_key and (line.startswith(" ") or line.startswith("\t")):
            # continuation line (multi-line YAML value)
            result[current_key] += " " + line.strip()
    return result


def find_skill_files(root: Path) -> list[Path]:
    found = []
    seen = set()

    for rel in PRIORITY_DIRS:
        d = root / rel
        if d.exists():
            for p in d.rglob("SKILL.md"):
                if p not in seen:
                    found.append(p)
                    seen.add(p)

    for p in root.rglob("SKILL.md"):
        if p in seen:
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in p.relative_to(root).parts):
            continue
        found.append(p)
        seen.add(p)

    return found


def main():
    parser = argparse.ArgumentParser(description="Détecte les skills présentes dans le projet.")
    parser.add_argument("--root", default=".", help="Racine du projet (défaut: dossier courant)")
    parser.add_argument("--json", action="store_true", help="Sortie JSON structurée")
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    skill_files = find_skill_files(project_root)

    skills = []
    for path in skill_files:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = parse_frontmatter(text)
        name = meta["name"] or path.parent.name
        skills.append({
            "name": name,
            "description": meta["description"],
            "path": str(path.relative_to(project_root)),
        })

    if args.json:
        print(json.dumps(skills, ensure_ascii=False, indent=2))
        return

    if not skills:
        print("Aucune skill projet détectée.")
        return

    print(f"# {len(skills)} skill(s) détectée(s) dans le projet\n")
    for s in skills:
        desc = s["description"] or "(pas de description)"
        print(f"- **{s['name']}** ({s['path']}) — {desc}")


if __name__ == "__main__":
    main()
