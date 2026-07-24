#!/usr/bin/env python3
"""
sync_memory_bank.py — Synchronise memory-bank/activeContext.md et
memory-bank/progress.md avec l'état courant de la spec active
(specs/vXXX/sprint_status.md), sans toucher au reste du contenu de ces
fichiers (sections manuelles préservées).

Usage:
    python3 sync_memory_bank.py --root PROJECT_ROOT --spec-dir specs/v003

À lancer : après chaque `new_spec.py`, après chaque `update_task_status.py`,
et en général à chaque fin de session de travail sur une spec, pour que le
memory-bank reste la source de vérité "où en est-on" pour la prochaine
session (qui n'aura plus le contexte de la conversation actuelle).
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

SYNC_START = "<!-- SYNC:START -->"
SYNC_END = "<!-- SYNC:END -->"


def extract_field(content: str, label: str) -> str:
    m = re.search(rf"\*\*{re.escape(label)} :\*\*\s*(.+)", content)
    return m.group(1).strip() if m else "inconnu"


def replace_sync_block(file_path: Path, new_block_body: str) -> None:
    content = file_path.read_text(encoding="utf-8")
    if SYNC_START not in content or SYNC_END not in content:
        print(f"⚠️  Marqueurs SYNC introuvables dans {file_path}, section ajoutée en tête.", file=sys.stderr)
        content = f"{SYNC_START}\n{new_block_body}\n{SYNC_END}\n\n" + content
    else:
        start = content.index(SYNC_START) + len(SYNC_START)
        end = content.index(SYNC_END)
        content = content[:start] + "\n" + new_block_body + "\n" + content[end:]
    file_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Synchronise memory-bank/ avec la spec active.")
    parser.add_argument("--root", default=".", help="Racine du projet (défaut: dossier courant)")
    parser.add_argument("--spec-dir", required=True, help="Dossier de la spec active, ex: specs/v003")
    args = parser.parse_args()

    project_root = Path(args.root).resolve()
    spec_dir = Path(args.spec_dir)
    if not spec_dir.is_absolute():
        spec_dir = project_root / spec_dir

    sprint_status_path = spec_dir / "sprint_status.md"
    if not sprint_status_path.exists():
        print(f"❌ {sprint_status_path} introuvable.", file=sys.stderr)
        sys.exit(1)

    mb_dir = project_root / "memory-bank"
    active_context_path = mb_dir / "activeContext.md"
    progress_path = mb_dir / "progress.md"
    if not active_context_path.exists() or not progress_path.exists():
        print(
            "❌ memory-bank/ incomplet. Lancer d'abord init_memory_bank.py.",
            file=sys.stderr,
        )
        sys.exit(1)

    sprint_content = sprint_status_path.read_text(encoding="utf-8")
    version = spec_dir.name
    statut_global = extract_field(sprint_content, "Statut global de la spec")
    avancement = extract_field(sprint_content, "Avancement")
    prochaine_etape = extract_field(sprint_content, "Prochaine étape")
    today = datetime.date.today().isoformat()

    active_block = (
        f"- **Spec active :** {version}\n"
        f"- **Statut :** {statut_global}\n"
        f"- **Avancement :** {avancement}\n"
        f"- **Prochaine étape :** {prochaine_etape}\n"
        f"- **Dernière synchro :** {today}"
    )
    replace_sync_block(active_context_path, active_block)

    def escape_pipes(value: str) -> str:
        return value.replace("|", "\\|")

    progress_block = (
        f"| Spec | Statut | Avancement | Dernière synchro |\n"
        f"|---|---|---|---|\n"
        f"| {version} | {escape_pipes(statut_global)} | {escape_pipes(avancement)} | {today} |"
    )
    replace_sync_block(progress_path, progress_block)

    print(f"✅ memory-bank/activeContext.md synchronisé (spec {version})")
    print(f"✅ memory-bank/progress.md synchronisé (spec {version})")


if __name__ == "__main__":
    main()
