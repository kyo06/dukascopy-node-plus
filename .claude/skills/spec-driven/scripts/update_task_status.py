#!/usr/bin/env python3
"""
update_task_status.py — Met à jour le statut d'une tâche dans tasks.md et
ajoute une entrée dans le journal de sprint_status.md.

Usage:
    python3 update_task_status.py --spec-dir specs/v003 --task T-003-001 --status done
    python3 update_task_status.py --spec-dir specs/v003 --task T-003-002 --status in-progress \
        --note "Démarré, dépend de T-003-001"

    # Resynchroniser uniquement le compteur d'avancement (ex: juste après avoir
    # rempli tasks.md à l'étape 1.4, avant toute tâche démarrée), sans changer
    # le statut d'une tâche ni ajouter d'entrée de journal :
    python3 update_task_status.py --spec-dir specs/v003 --recount-only

Ce script fait une mise à jour ciblée et non destructive :
- Dans tasks.md : remplace uniquement le champ Statut de la ligne du tableau
  correspondant à l'ID de tâche donné (recherche par ID en début de ligne).
  La colonne Statut est repérée dynamiquement à partir de l'en-tête du
  tableau (colonnes attendues : ID | Tâche | US liée | Type | Statut |
  Estimation | Skill(s) recommandée(s) | Assigné — l'ordre exact des colonnes
  après "Statut" n'a pas d'importance pour ce script).
- Dans sprint_status.md : ajoute une ligne dans le journal des sessions du jour
  (crée l'entrée du jour si elle n'existe pas encore) et recalcule le compteur
  d'avancement (X / total tâches terminées) à partir de tasks.md.
- Si la tâche donnée n'est trouvée dans aucune ligne de tasks.md, le script
  s'arrête en erreur SANS toucher à sprint_status.md (pas de faux journal).

Statuts valides : todo, in-progress, blocked, review, done
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

VALID_STATUSES = {"todo", "in-progress", "blocked", "review", "done"}


def find_status_column_index(tasks_path: Path) -> int:
    """Repère l'index de la colonne 'Statut' à partir de la ligne d'en-tête
    du tableau (`| ID | Tâche | ... | Statut | ... |`). Retombe sur l'index 4
    (position attendue par le template par défaut) si l'en-tête est introuvable
    ou ne contient pas de colonne 'Statut' exploitable."""
    content = tasks_path.read_text(encoding="utf-8")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and "ID" in stripped and "Statut" in stripped:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            for i, cell in enumerate(cells):
                if cell.lower() == "statut":
                    return i
    return 4


def update_tasks_md(tasks_path: Path, task_id: str, new_status: str, status_idx: int) -> bool:
    lines = tasks_path.read_text(encoding="utf-8").splitlines(keepends=True)
    updated = False
    out_lines = []
    for line in lines:
        if line.strip().startswith(f"| {task_id} "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) > status_idx:
                cells[status_idx] = new_status
                line = "| " + " | ".join(cells) + " |\n"
                updated = True
        out_lines.append(line)
    if updated:
        tasks_path.write_text("".join(out_lines), encoding="utf-8")
    return updated


def count_progress(tasks_path: Path) -> tuple[int, int]:
    content = tasks_path.read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*T-\d+-\d+.*\|$", content, flags=re.MULTILINE)
    total = len(rows)
    done = sum(1 for r in rows if re.search(r"\|\s*done\s*\|", r))
    return done, total


def update_sprint_status(sprint_path: Path, task_id: str, new_status: str, note: str) -> None:
    content = sprint_path.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    header = f"### {today}"

    log_entry = f"- `{task_id}` → **{new_status}**" + (f" — {note}" if note else "") + "\n"

    if header in content:
        idx = content.index(header)
        end_of_line = content.index("\n", idx) + 1
        content = content[:end_of_line] + log_entry + content[end_of_line:]
    else:
        marker = "## Journal des sessions"
        if marker in content:
            idx = content.index(marker) + len(marker)
            insertion = f"\n\n{header} — mise à jour\n{log_entry}"
            content = content[:idx] + insertion + content[idx:]
        else:
            content = content.rstrip("\n") + f"\n\n## Journal des sessions\n\n{header}\n{log_entry}"

    sprint_path.write_text(content, encoding="utf-8")


def update_progress_summary(sprint_path: Path, done: int, total: int) -> None:
    content = sprint_path.read_text(encoding="utf-8")
    pct = int((done / total) * 100) if total else 0
    pattern = re.compile(r"- \*\*Avancement :\*\* .*")
    replacement = f"- **Avancement :** {done} / {total} tâches terminées ({pct}%)"
    if pattern.search(content):
        content = pattern.sub(replacement, content, count=1)
        sprint_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Met à jour le statut d'une tâche et journalise la session.")
    parser.add_argument("--spec-dir", required=True, help="Dossier de la spec, ex: specs/v003")
    parser.add_argument("--task", help="ID de la tâche, ex: T-003-001 (requis sauf avec --recount-only)")
    parser.add_argument("--status", choices=sorted(VALID_STATUSES), help="Nouveau statut (requis sauf avec --recount-only)")
    parser.add_argument("--note", default="", help="Note optionnelle pour le journal de session")
    parser.add_argument(
        "--recount-only",
        action="store_true",
        help="Ne change le statut d'aucune tâche et n'ajoute aucune entrée de journal : "
             "recalcule seulement la ligne 'Avancement' de sprint_status.md à partir de "
             "l'état actuel de tasks.md. Utile juste après avoir rempli tasks.md (étape 1.4) "
             "pour que le compteur reflète le nombre réel de tâches dès le départ.",
    )
    args = parser.parse_args()

    if not args.recount_only and (not args.task or not args.status):
        print("❌ --task et --status sont requis (sauf avec --recount-only).", file=sys.stderr)
        sys.exit(1)

    spec_dir = Path(args.spec_dir).resolve()
    tasks_path = spec_dir / "tasks.md"
    sprint_path = spec_dir / "sprint_status.md"

    for p in (tasks_path, sprint_path):
        if not p.exists():
            print(f"❌ Fichier introuvable : {p}", file=sys.stderr)
            sys.exit(1)

    if args.recount_only:
        done, total = count_progress(tasks_path)
        update_progress_summary(sprint_path, done, total)
        print(f"✅ Avancement resynchronisé : {done}/{total} tâches terminées")
        return

    status_idx = find_status_column_index(tasks_path)
    if not update_tasks_md(tasks_path, args.task, args.status, status_idx):
        print(f"❌ Tâche {args.task} non trouvée dans {tasks_path} — aucune ligne modifiée, "
              f"sprint_status.md n'a pas été touché.", file=sys.stderr)
        sys.exit(1)

    update_sprint_status(sprint_path, args.task, args.status, args.note)
    done, total = count_progress(tasks_path)
    update_progress_summary(sprint_path, done, total)

    print(f"✅ {args.task} → {args.status}")
    print(f"   Avancement : {done}/{total} tâches terminées")


if __name__ == "__main__":
    main()
