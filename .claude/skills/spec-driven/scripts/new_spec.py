#!/usr/bin/env python3
"""
new_spec.py — Scaffold une nouvelle version de spec dans specs/vXXX/

Usage:
    python3 new_spec.py [--root PROJECT_ROOT] [--name "Nom court de la spec"]

Comportement :
- Cherche/crée le dossier specs/ à la racine du projet (PROJECT_ROOT, défaut: cwd)
- Détecte la dernière version vXXX existante et incrémente (v001 si aucune)
- Copie les templates (user-stories.md, tasks.md, sprint_status.md) en remplaçant
  les placeholders {{VERSION}}, {{VERSION_NUM}}, {{DATE}}, {{TOTAL_TASKS}}
- Ajoute une entrée dans specs/CHANGELOG.md
- N'écrase JAMAIS une version existante : crée toujours la version suivante.

Ce script ne pose aucune question : l'interview métier/technique doit être
menée par l'IA en conversation AVANT d'appeler ce script. Le script scaffold
seulement la structure de fichiers/templates.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"

VERSION_RE = re.compile(r"^v(\d{3})$")


def find_next_version(specs_dir: Path) -> tuple[str, str]:
    """Retourne (version_str 'v004', version_num '004')."""
    max_num = 0
    if specs_dir.exists():
        for child in specs_dir.iterdir():
            if child.is_dir():
                m = VERSION_RE.match(child.name)
                if m:
                    max_num = max(max_num, int(m.group(1)))
    next_num = max_num + 1
    return f"v{next_num:03d}", f"{next_num:03d}"


def render(template_text: str, mapping: dict) -> str:
    out = template_text
    for key, value in mapping.items():
        out = out.replace("{{" + key + "}}", value)
    return out


def main():
    parser = argparse.ArgumentParser(description="Scaffold une nouvelle version de spec.")
    parser.add_argument("--root", default=".", help="Racine du projet (défaut: dossier courant)")
    parser.add_argument("--name", default="", help="Nom court/titre de la spec (optionnel, pour le changelog)")
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    specs_dir = project_root / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    version, version_num = find_next_version(specs_dir)
    version_dir = specs_dir / version
    if version_dir.exists():
        print(f"❌ Le dossier {version_dir} existe déjà. Abandon.", file=sys.stderr)
        sys.exit(1)

    version_dir.mkdir(parents=True)

    today = datetime.date.today().isoformat()
    mapping = {
        "VERSION": version,
        "VERSION_NUM": version_num,
        "DATE": today,
        "TOTAL_TASKS": "0",
    }

    files = {
        "user-stories.template.md": "user-stories.md",
        "tasks.template.md": "tasks.md",
        "sprint_status.template.md": "sprint_status.md",
    }

    for template_name, output_name in files.items():
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            print(f"❌ Template introuvable : {template_path}", file=sys.stderr)
            sys.exit(1)
        content = render(template_path.read_text(encoding="utf-8"), mapping)
        (version_dir / output_name).write_text(content, encoding="utf-8")

    # Changelog
    changelog_path = specs_dir / "CHANGELOG.md"
    title = f" — {args.name}" if args.name else ""
    entry = f"- **{version}**{title} — créée le {today} (statut: draft)\n"
    if changelog_path.exists():
        existing = changelog_path.read_text(encoding="utf-8")
        changelog_path.write_text(existing.rstrip("\n") + "\n" + entry, encoding="utf-8")
    else:
        changelog_path.write_text(
            "# Changelog des spécifications\n\n" + entry, encoding="utf-8"
        )

    print(f"✅ Spec {version} créée dans {version_dir}")
    print(f"   - {version_dir / 'user-stories.md'}")
    print(f"   - {version_dir / 'tasks.md'}")
    print(f"   - {version_dir / 'sprint_status.md'}")
    print(f"   - {changelog_path} (mis à jour)")
    print(version)  # dernière ligne : version seule, pratique pour être capturée par un autre script


if __name__ == "__main__":
    main()
