<!-- SPEC-DRIVEN:START -->
## Spécifications (spec-driven development)

Ce projet suit une approche *spec-driven* : toute fonctionnalité significative est d'abord spécifiée dans `specs/vXXX/` avant implémentation.

- **Spec active :** {{ACTIVE_VERSION}}
- **Emplacement :** `specs/{{ACTIVE_VERSION}}/`
  - `user-stories.md` — fonctionnalités métier + spécifications techniques
  - `tasks.md` — découpage en tâches actionnables
  - `sprint_status.md` — avancement de l'implémentation (à tenir à jour à chaque session)

**Règles à suivre par tout agent IA travaillant sur ce repo :**
1. Avant d'implémenter une fonctionnalité, vérifier si elle est déjà décrite dans la spec active. Si non, proposer de créer/mettre à jour la spec avant de coder.
2. Après avoir livré une tâche, mettre à jour `tasks.md` (statut) et `sprint_status.md` (journal de session + avancement).
3. Ne jamais modifier `user-stories.md` d'une version déjà `validated`/`in-progress` sans le signaler explicitement à l'utilisateur (créer une nouvelle version si le besoin change significativement).
4. L'historique des specs (`specs/v001`, `specs/v002`, ...) fait foi sur les décisions passées : le consulter en cas de doute sur le comportement attendu.

**Historique des versions de spec :** voir `specs/CHANGELOG.md`.

### Memory bank

Ce projet utilise un memory-bank (`memory-bank/`) pour persister le contexte entre les sessions, car le contexte de conversation d'un agent IA ne survit pas d'une session à l'autre.

**Tout agent IA doit lire `memory-bank/activeContext.md` en tout premier, avant toute autre action, en début de session.** Lire aussi `memory-bank/progress.md` pour l'état d'avancement, et `projectbrief.md` / `productContext.md` / `systemPatterns.md` / `techContext.md` en cas de besoin de contexte plus large.

En fin de session (ou après toute mise à jour de tâche/spec), synchroniser le memory-bank :
```
python3 <chemin-skill-spec-driven>/scripts/sync_memory_bank.py --root <racine-projet> --spec-dir specs/{{ACTIVE_VERSION}}
```
<!-- SPEC-DRIVEN:END -->
