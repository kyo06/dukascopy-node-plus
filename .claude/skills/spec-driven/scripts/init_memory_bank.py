#!/usr/bin/env python3
"""
init_memory_bank.py — Crée le dossier memory-bank/ du projet (convention
popularisée par Cline/Roo/Cursor : un ensemble de fichiers Markdown qui
persistent le contexte projet entre les sessions d'un agent IA, puisque le
contexte de conversation ne survit pas d'une session à l'autre).

Usage:
    python3 init_memory_bank.py --root PROJECT_ROOT [--project-name "Mon projet"]

Comportement : non destructif. Ne crée que les fichiers manquants ; ne touche
jamais à un fichier de memory-bank/ déjà existant.
"""
import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates" / "memory-bank"

FILES = [
    "projectbrief.md",
    "productContext.md",
    "systemPatterns.md",
    "techContext.md",
    "activeContext.md",
    "progress.md",
]


def main():
    parser = argparse.ArgumentParser(description="Initialise memory-bank/ dans le projet.")
    parser.add_argument("--root", default=".", help="Racine du projet (défaut: dossier courant)")
    parser.add_argument("--project-name", default="", help="Nom du projet, injecté dans projectbrief.md")
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    mb_dir = project_root / "memory-bank"
    mb_dir.mkdir(parents=True, exist_ok=True)

    created, skipped = [], []
    for filename in FILES:
        target = mb_dir / filename
        if target.exists():
            skipped.append(filename)
            continue
        template_path = TEMPLATES_DIR / (filename.replace(".md", ".template.md"))
        content = template_path.read_text(encoding="utf-8")
        if filename == "projectbrief.md":
            content = content.replace("{{PROJECT_NAME}}", args.project_name or project_root.name)
        target.write_text(content, encoding="utf-8")
        created.append(filename)

    for f in created:
        print(f"🆕 créé   memory-bank/{f}")
    for f in skipped:
        print(f"⏭️  existe déjà, ignoré   memory-bank/{f}")

    if created:
        print(f"\n✅ memory-bank/ initialisé dans {mb_dir}")
    else:
        print(f"\nℹ️  memory-bank/ déjà complet dans {mb_dir}, rien créé.")


if __name__ == "__main__":
    main()
