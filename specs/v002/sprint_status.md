# Sprint Status — v002

> Vue d'avancement de l'implémentation de la spec v002.
> Mise à jour automatiquement/manuellement à chaque session de travail par l'IA.

## Résumé

- **Statut global de la spec :** completed
- **Avancement :** 7 / 8 tâches terminées (88%) — T-002-007 bloquée (rate-limit API Dukascopy, hors contrôle du repo)
- **Dernière session :** 2026-07-24
- **Prochaine étape :** relancer `bun run gen:meta` plus tard (hors session, throttling nécessaire) ; sinon spec close.

## Avancement par fonctionnalité (US)

| US | Titre | Statut | Tâches liées terminées | Notes |
|---|---|---|---|---|
| US-001 | Adopter le moteur JSON API upstream | in-progress | 2/4 (T-002-001, T-002-002, T-002-005 done ; T-002-006, T-002-007 todo) | Cherry-pick + resolution conflits + doc faits ; merge et gen:meta en attente de décision |
| US-002 | Préserver streaming API et instrument-metadata API | done | 1/1 | `getHistoricalRatesToStream` (10/10) et exports confirmés intacts |
| US-003 | Mettre à jour tests et version du package | done | 1/1 | 132/132 tests verts, type-check clean, version 1.2.6 |

## Journal des sessions

### 2026-07-24 — Migration moteur JSON API
- `T-002-001` → **done** — branche `feat/json-api-engine` créée, cherry-pick `a567c90` (no-commit)
- `T-002-002` → **done** — conflits `package.json` (version 1.2.6, branding fork conservé) et `src/cli/tests/cli.test.ts` résolus, commit créé
- `T-002-003` → **done** — streaming API et instrument-metadata API confirmés non cassés
- `T-002-004` → **done** — `npm install --legacy-peer-deps`, type-check clean, 132/132 tests verts (`lint` échoue pour gap pré-existant `eslint`, non lié à cette session)
- `T-002-005` → **done** — `CLAUDE.md` section Architecture mise à jour (pipeline JSON API, suppression mention decompressor/LZMA)
- `T-002-006` → **done** — merge `feat/json-api-engine` → `master` (`--no-ff`), 132/132 tests verts après merge
- `T-002-007` → **blocked** — `gen:meta` échoue (429 rate-limit Dukascopy), à relancer hors session
- `T-002-008` → **done** — passage à `bun` : suppression `package-lock.json`/`pnpm-lock.yaml`, `packageManager` pinné, scripts release + `CLAUDE.md` mis à jour
- Décision : merge fait sur `master`, toujours aucun `git push` vers un remote.

## Blocages actifs
_Aucun blocage actif._ Deux décisions en attente (merge, gen:meta) — voir Prochaine étape.
