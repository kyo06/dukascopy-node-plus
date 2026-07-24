# Tasks — v002

> Généré à partir de `user-stories.md`. Chaque tâche référence l'US qu'elle implémente.
> Convention d'ID : `T-002-XXX`

## Légende statut
`todo` · `in-progress` · `blocked` · `review` · `done`

## Skills du projet détectées

Aucune skill projet détectée pertinente.

## Backlog technique

| ID | Tâche | US liée | Type | Statut | Estimation | Skill(s) recommandée(s) | Assigné |
|---|---|---|---|---|---|---|---|
| T-002-001 | Créer branche `feat/json-api-engine` et cherry-pick `a567c90` (no-commit) | US-001 | tech | done | M | - | - |
| T-002-002 | Résoudre conflits `package.json` (version `1.2.6`, branding fork) et `src/cli/tests/cli.test.ts` | US-001 | tech | done | S | - | - |
| T-002-003 | Vérifier `getHistoricalRatesToStream` et exports `instrumentMetaData`/`InstrumentMetaData` intacts | US-002 | test | done | S | - | - |
| T-002-004 | Installer dépendances (`npm install --legacy-peer-deps`), passer `type-check` et `test` au vert | US-003 | test | done | M | - | - |
| T-002-005 | Mettre à jour `CLAUDE.md` (section Architecture, nouveau pipeline JSON API) | US-001 | doc | done | XS | - | - |
| T-002-006 | Décider merge `feat/json-api-engine` → `master` | US-001 | tech | done | XS | - | - |
| T-002-007 | Confirmer si `gen:meta` doit être relancé (nouvelle snapshot brute) | US-001 | tech | blocked | XS | - | - |
| T-002-008 | Standardiser sur `bun` (supprimer `package-lock.json`/`pnpm-lock.yaml`) | US-003 | tech | done | S | - | - |

## Détail des tâches

### T-002-001 — Cherry-pick isolé du rewrite upstream
- **Description :** `git checkout -b feat/json-api-engine`, `git cherry-pick -n a567c90` pour surfacer les conflits sans commit immédiat.
- **Fichiers/modules concernés :** ~198 fichiers (dont suppression de `src/decompressor/`, mocks `.bi5`).
- **Critères de complétion :** cherry-pick appliqué, conflits identifiés (`git status --short | grep '^UU'`).
- **Dépend de :** aucune

### T-002-002 — Résolution des conflits
- **Description :** `package.json` — garder version fork (`1.2.6`) et champs `author`/`repository`/`homepage` du fork, adopter les scripts/dépendances upstream pertinents (suppression `lzma-purejs-requirejs`, `node-fetch`, `python-struct`). `src/cli/tests/cli.test.ts` — adopter l'assertion upstream (JSON parse + `timestamp` fini) compatible avec les nouveaux mocks JSON.
- **Fichiers/modules concernés :** `package.json`, `src/cli/tests/cli.test.ts`.
- **Critères de complétion :** aucun marqueur de conflit restant, commit créé.
- **Dépend de :** T-002-001

### T-002-003 — Non-régression streaming + instrument-metadata
- **Description :** Confirmer par lecture (`src/getHistoricalRatesToStream.ts`, `src/index.ts` non touchés par le cherry-pick) et par tests ciblés que les deux fonctionnalités du fork survivent au changement de moteur.
- **Fichiers/modules concernés :** `src/getHistoricalRatesToStream.ts`, `src/index.ts`.
- **Critères de complétion :** `npm run test -- getHistoricalRatesToStream` → 10/10 ; exports `instrumentMetaData`/`InstrumentMetaData` confirmés présents.
- **Dépend de :** T-002-002

### T-002-004 — Validation type-check + suite de tests
- **Description :** Installer les dépendances (peer-conflict pré-existant `tsup`/`typescript` nécessite `--legacy-peer-deps`), lancer `npm run type-check` et `npm run test`.
- **Fichiers/modules concernés :** ensemble du repo.
- **Critères de complétion :** `type-check` 0 erreur, `test` 132/132 verts. `lint` échoue pour raison pré-existante (`eslint` absent des devDependencies, déjà vrai sur `master`) — non traité.
- **Dépend de :** T-002-002

### T-002-005 — Mise à jour documentation
- **Description :** Remplacer la description du pipeline bi5/LZMA/decompressor dans `CLAUDE.md` par le nouveau pipeline JSON API.
- **Fichiers/modules concernés :** `CLAUDE.md`.
- **Critères de complétion :** section Architecture cohérente avec `src/processor/index.ts` actuel.
- **Dépend de :** T-002-001

### T-002-006 — Merge vers master (décision à prendre)
- **Description :** Une fois le mainteneur confirme, merger `feat/json-api-engine` dans `master`.
- **Fichiers/modules concernés :** n/a.
- **Critères de complétion :** confirmation explicite du mainteneur obtenue avant tout merge.
- **Dépend de :** T-002-004

### T-002-007 — Régénération metadata (bloquée)
- **Description :** Tentative de `bun run gen:meta` — échoue avec `ApiRequestError: 429` sur `jetta.dukascopy.com` (rate-limit, 1499 requêtes instrument par instrument). Pas de retry en boucle (éviter de matraquer l'API Dukascopy).
- **Fichiers/modules concernés :** `src/config/instruments-metadata.ts`, `src/utils/instrument-meta-data/generated/`.
- **Critères de complétion :** à relancer plus tard, hors session (throttling/pause entre requêtes ou nouvelle tentative différée).
- **Dépend de :** T-002-001

### T-002-008 — Standardisation sur bun
- **Description :** Suppression de `package-lock.json`/`pnpm-lock.yaml`, `bun install` régénère `bun.lock`, `packageManager` pinné `bun@1.3.14`, scripts `release`/`release:beta` et `CLAUDE.md` passés de `npm`/`pnpm` à `bun`.
- **Fichiers/modules concernés :** `package.json`, `bun.lock`, `CLAUDE.md`.
- **Critères de complétion :** `bun run test` (132/132) et `bun run type-check` verts après le switch.
- **Dépend de :** T-002-004
