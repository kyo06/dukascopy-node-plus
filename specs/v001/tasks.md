# Tasks — v001

> Généré à partir de `user-stories.md`. Chaque tâche référence l'US qu'elle implémente.
> Convention d'ID : `T-001-XXX`

## Légende statut
`todo` · `in-progress` · `blocked` · `review` · `done`

## Skills du projet détectées

Aucune skill projet détectée pertinente (seule `spec-driven` est présente, non applicable au contenu des tâches).

## Backlog technique

| ID | Tâche | US liée | Type | Statut | Estimation | Skill(s) recommandée(s) | Assigné |
|---|---|---|---|---|---|---|---|
| T-001-001 | Ajouter le remote `upstream` et comparer `master` vs `upstream/master` | US-001 | tech | done | XS | - | - |
| T-001-002 | Documenter la divergence (commit `a567c90`, modules impactés) dans `user-stories.md` | US-002 | doc | done | XS | - | - |
| T-001-003 | Faire valider la spec (statut `draft` → `validated`) par le mainteneur | US-002 | doc | done | XS | - | - |

## Détail des tâches

### T-001-001 — Ajouter le remote upstream et comparer l'historique
- **Description :** `git remote add upstream https://github.com/Leo4815162342/dukascopy-node.git`, `git fetch upstream`, puis `git log master..upstream/master` et `git log upstream/master..master`. Résultat : 3 commits upstream non mergés (2 bumps de version + `a567c90` engine rewrite), fork 22 commits en avance sur son propre historique de features.
- **Fichiers/modules concernés :** aucun (opération git uniquement, remote local).
- **Skill(s) à utiliser :** -
- **Critères de complétion :** liste de commits confirmée et consignée dans `user-stories.md` §4.5.
- **Dépend de :** aucune

### T-001-002 — Documenter la divergence intentionnelle
- **Description :** Rédiger dans `user-stories.md` la raison de ne pas merger `a567c90` (suppression du pipeline bi5/LZMA dont dépendent `buffer-fetcher`, `decompressor`, `data-normaliser`, `getHistoricalRatesToStream`, `instrumentMetaData`), et lister les modules concernés pour une future réévaluation.
- **Fichiers/modules concernés :** `specs/v001/user-stories.md`.
- **Skill(s) à utiliser :** -
- **Critères de complétion :** section 4.1/4.5 remplie, relue et cohérente avec l'investigation git.
- **Dépend de :** T-001-001

### T-001-003 — Validation de la spec
- **Description :** Faire relire la spec au mainteneur (résumé US + points ouverts §4.5) et passer le statut d'en-tête de `draft` à `validated` une fois confirmé.
- **Fichiers/modules concernés :** `specs/v001/user-stories.md`.
- **Skill(s) à utiliser :** -
- **Critères de complétion :** confirmation explicite obtenue, statut mis à jour.
- **Dépend de :** T-001-002
