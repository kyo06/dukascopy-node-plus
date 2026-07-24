# Tasks — v003

> Généré à partir de `user-stories.md`. Chaque tâche référence l'US qu'elle implémente.
> Convention d'ID : `T-003-XXX`

## Légende statut
`todo` · `in-progress` · `blocked` · `review` · `done`

## Skills du projet détectées

Aucune skill projet détectée pertinente pour le contenu de ces tâches.

## Backlog technique

| ID | Tâche | US liée | Type | Statut | Estimation | Skill(s) recommandée(s) | Assigné |
|---|---|---|---|---|---|---|---|
| T-003-001 | Décider avec le mainteneur : rebase interactif de `eeff88b` ou refus documenté | US-001 | tech | done | S | - | - |
| T-003-002 | Ajouter note explicative dans `specs/CHANGELOG.md` (renversement v001→v002) | US-002 | doc | done | XS | - | - |
| T-003-003 | Ajouter throttle + retry/backoff sur 429 dans `generate-data.ts` | US-003 | tech | done | M | - | - |
| T-003-004 | Ajouter test `getPriceScale` pour multiplier en notation scientifique | US-004 | test | done | XS | - | - |
| T-003-005 | Auditer/compléter tests retry/rate-limit de `src/buffer-fetcher/` | US-005 | test | done | S | - | - |
| T-003-006 | Évaluer remplacement `standard-version` (deprecated) | US-006 | tech | done (reporté) | M | - | - |
| T-003-007 | Évaluer bump `eslint`/`@typescript-eslint` vers versions plus récentes | US-006 | tech | done | S | - | - |

## Détail des tâches

### T-003-001 — Nettoyage historique commit migration
- **Description :** Présenter au mainteneur le contenu réel de `eeff88b` (mix rewrite + fichiers hors-sujet). Si accord, `git rebase -i` pour séparer en commits atomiques ; sinon consigner le refus et la raison dans cette spec.
- **Fichiers/modules concernés :** historique git (`master` local, pas encore pushé).
- **Critères de complétion :** décision actée, section 4.5 mise à jour avec le résultat.
- **Dépend de :** aucune
- **Résultat :** mainteneur a choisi le rebase interactif (`git rebase -i --rebase-merges`). `eeff88b` (227 fichiers) séparé en deux commits atomiques : `feat: adopt upstream JSON API engine` (194 fichiers moteur) et `chore: scaffold spec-driven skill and initial CLAUDE.md/specs` (33 fichiers infra). Historique local rejoué sans conflit, suite complète (`lint`/`type-check`/`test`/`build`) revalidée après coup.

### T-003-002 — Traçabilité changelog v001→v002
- **Description :** Ajouter une ligne dans `specs/CHANGELOG.md` sous l'entrée v002 précisant que le mainteneur est revenu explicitement sur la conclusion de v001, sans nouvelle analyse de bénéfice technique.
- **Fichiers/modules concernés :** `specs/CHANGELOG.md`.
- **Critères de complétion :** ligne ajoutée, relue.
- **Dépend de :** aucune

### T-003-003 — Throttle/backoff `gen:meta`
- **Description :** Dans `src/utils/instrument-meta-data/generate-data.ts`, ajouter un délai minimal entre requêtes et un retry avec backoff exponentiel sur réponse 429, au lieu d'abandonner immédiatement (`fetchJsonWithRetry`).
- **Fichiers/modules concernés :** `src/utils/instrument-meta-data/generate-data.ts`.
- **Critères de complétion :** script relancé sur un sous-ensemble d'instruments sans échec 429 bloquant.
- **Dépend de :** aucune

### T-003-004 — Test `getPriceScale` notation scientifique
- **Description :** Ajouter un cas de test (fichier `*.test.ts` du module `data-normaliser`) vérifiant `getPriceScale(1e-5)` (et variantes similaires) retourne le scale correct sans exception.
- **Fichiers/modules concernés :** `src/data-normaliser/*.test.ts` (ou équivalent existant).
- **Critères de complétion :** test ajouté, vert via `bun run test`.
- **Dépend de :** aucune

### T-003-005 — Couverture retry/rate-limit `buffer-fetcher`
- **Description :** Lister les tests existants de `src/buffer-fetcher/`, confirmer si un scénario retry/429 HTTP est couvert ; si absent, ajouter un test basé sur les mocks MSW existants.
- **Fichiers/modules concernés :** `src/buffer-fetcher/` et son dossier de tests.
- **Critères de complétion :** couverture confirmée ou test ajouté et vert.
- **Dépend de :** aucune

### T-003-006 — Évaluation `standard-version`
- **Description :** Comparer `standard-version` (deprecated) à des alternatives maintenues (ex. `release-please`, `changesets`), évaluer l'effort de migration vs bénéfice.
- **Fichiers/modules concernés :** `package.json` (script `release`), CI éventuelle.
- **Critères de complétion :** décision consignée (migrer / reporter / ne pas migrer) avec justification.
- **Dépend de :** aucune
- **Résultat :** reporté. `standard-version` reste fonctionnel malgré le statut deprecated ; migration vers `release-please`/`changesets` non urgente, effort non justifié dans ce sprint. À reconsidérer si un incident de release survient.

### T-003-007 — Évaluation bump `eslint`/`@typescript-eslint`
- **Description :** Vérifier compatibilité d'un bump vers `eslint@10.x` et/ou une version plus récente de `@typescript-eslint` ; tester en isolation (`bun run lint`) avant toute adoption.
- **Fichiers/modules concernés :** `package.json` (devDependencies), `eslint.config.mjs`.
- **Critères de complétion :** décision consignée, bump effectué uniquement si `bun run lint` reste vert sans régression majeure.
- **Dépend de :** aucune
