# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`dukascopy-node-plus` — Node.js library + CLI for downloading historical/real-time market tick data from Dukascopy (Forex, Crypto, Stocks, ETFs, CFDs, Commodities, Bonds). Fork of `dukascopy-node`. Node >=18 required, TypeScript strict mode.

Three public entry points:
- `getHistoricalRates(config)` — Promise-based, returns full dataset. Best under ~10k items.
- `getHistoricalRatesToStream(config)` — returns a Node `Readable`, streams progressively. Best for large/tick datasets and file piping.
- `getRealTimeRates(config)` — Promise-based, fetches most recent data.

## Commands

Package manager: **bun** (`bun.lock` is the source of truth; `npm`/`pnpm` lockfiles removed).

```bash
bun install            # install dependencies
bun run build          # rm -rf dist && tsup build (esm+cjs+dts, legacy output)
bun run test            # vitest run
bun run test -- <pattern>       # run a single test file, e.g. bun run test -- buffer-fetcher.test.ts
bun run test -- --watch         # watch mode
bun run coverage        # vitest run --coverage
bun run lint             # eslint ./src --ext ts --ext js
bun run format           # prettier --write src/**/*.ts
bun run type-check       # tsc --noEmit --skipLibCheck
bun run gen:meta         # regenerate src/config/instruments-metadata.ts (hits live Dukascopy API, can 429)
bun run gen:instruments-md  # regenerate instrument docs table
```

CLI (after build, or via `tsx`/`npx`):
```bash
npx dukascopy-node -i btcusd -from 2019-01-13 -to 2019-01-14 -t tick -f csv
```

Release (`bun run release`) runs `standard-version`, pushes tags, builds, and publishes to npm via `bun publish` — don't run unless explicitly asked.

## Architecture

`src/index.ts` is the public export barrel — any new public API/type must be re-exported there.

Data flows through a fixed module pipeline (see `src/processor/index.ts`, the orchestrator called by both `getHistoricalRates` and `getHistoricalRatesToStream`):

```
config-validator → url-generator → buffer-fetcher (+ cache-manager) → data-normaliser → aggregator → output-formatter
```

Since the v1.2.6 engine migration (adopted from upstream `dukascopy-node`, commit `a567c90`), Dukascopy is queried via a JSON API instead of raw `.bi5` binary files — there is no decompression step anymore.

1. **config-validator** — validates/sanitizes user config via `fastest-validator` (`schema.ts`), throws `ConfigValidationError`.
2. **url-generator** — builds Dukascopy JSON API URLs from instrument/dates/timeframe.
3. **buffer-fetcher** — HTTP-fetches raw JSON response buffers per URL (native `fetch`), batches requests, retries; consults **cache-manager** first when caching enabled.
4. **data-normaliser** — parses the JSON response (`JSON.parse` in `processor/index.ts`) and converts it into normalised numeric arrays (timestamp, OHLC/price, volume), timezone/UTC-offset aware (`dates-normaliser`).
5. **aggregator** — aggregates normalised data from the source timeframe (fetched at) up to the requested timeframe (e.g. tick → m1 → h1), handles `ignoreFlats`.
6. **output-formatter** — converts internal numeric-array representation (`number[][]`) into the requested output shape: `json`, `csv`, or `array`, tick vs candle item types.

`getHistoricalRatesToStream` wraps the same pipeline but streams `processData` output progressively per URL/batch instead of collecting everything before returning (see `.kiro/skills/streaming-patterns.md` for stream usage patterns/backpressure handling — that file documents illustrative examples, not verbatim source).

`config/` holds the static domain catalogs consumed everywhere: `instruments.ts`, `instruments-metadata.ts` (generated — don't hand-edit, use `gen:meta`), `timeframes.ts`, `format.ts`, `price-types.ts`, `volume-unit.ts`.

Each module under `src/` is single-responsibility, kebab-case directory, with `index.ts` as the public surface and `types.ts` for its types; simple modules have `*.test.ts` alongside, more complex ones have a `tests/` folder with fixtures/cases.

## Style

- Single quotes, no trailing commas, arrow-parens avoid, 2-space indent, printWidth 100 (enforced by Prettier config, not manual).
- Named exports only (no default exports).
- `debug` package for logging (`debug('dukascopy:<module>')`), not `console.log` (lint warns on `console`).
- Custom `Error` subclasses per failure domain (e.g. `ConfigValidationError`) rather than generic `Error` throws.

## Reference docs

`.kiro/steering/` and `.kiro/skills/` contain steering docs and pattern guides (module architecture, data processing, error handling, streaming, testing, TypeScript conventions) written for this repo — consult them for idiomatic examples before introducing new patterns. Note their code blocks are illustrative snippets, not copies of the real source.


<!-- SPEC-DRIVEN:START -->
## Spécifications (spec-driven development)

Ce projet suit une approche *spec-driven* : toute fonctionnalité significative est d'abord spécifiée dans `specs/vXXX/` avant implémentation.

- **Spec active :** v003
- **Emplacement :** `specs/v003/`
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
python3 <chemin-skill-spec-driven>/scripts/sync_memory_bank.py --root <racine-projet> --spec-dir specs/v003
```
<!-- SPEC-DRIVEN:END -->
