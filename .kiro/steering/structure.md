---
inclusion: auto
---

# Project Structure

## Root Organization

```
dukascopy-node-plus/
├── src/              # Source code
├── dist/             # Build output (ESM + CJS)
├── examples/         # Usage examples
├── download/         # Sample downloaded data
└── node_modules/     # Dependencies
```

## Source Code Structure

The `src/` directory follows a modular architecture with clear separation of concerns:

### Core Modules

- **aggregator/** - OHLC candle aggregation from tick data
- **buffer-fetcher/** - HTTP data fetching and buffering
- **cache-manager/** - Caching layer for downloaded data
- **cli/** - Command-line interface implementation
- **config/** - Configuration schemas and metadata
- **config-validator/** - Input validation using fastest-validator
- **data-normaliser/** - Data normalization and transformation
- **dates-normaliser/** - Date/time handling and timezone conversion
- **decompressor/** - LZMA decompression for Dukascopy data
- **output-formatter/** - Format conversion (JSON, CSV, Array)
- **processor/** - Main data processing pipeline
- **stream-writer/** - Stream-based output writing
- **url-generator/** - Dukascopy URL construction
- **utils/** - Shared utilities and helpers

### Entry Points

- **index.ts** - Main library exports
- **getHistoricalRates.ts** - Historical data API
- **getRealTimeRates.ts** - Real-time data API
- **cli/index.ts** - CLI entry point

## Module Pattern

Each module typically contains:
- `index.ts` - Main implementation
- `types.ts` - TypeScript type definitions (if needed)
- `*.test.ts` - Unit tests
- `tests/` - Test fixtures and cases (for complex modules)

## Configuration Files

- **instruments.ts** - Supported instruments catalog
- **instruments-metadata.ts** - Instrument metadata (earliest data dates, etc.)
- **timeframes.ts** - Supported timeframe definitions
- **format.ts** - Output format types
- **price-types.ts** - Bid/Ask price type definitions

## Examples Directory

Organized by feature:
- `basic/` - Simple usage examples
- `with-cache/` - Caching examples
- `with-custom-batching/` - Batch processing
- `with-debugging/` - Debug mode examples
- `with-tick-data/` - Tick data specific examples
- `with-typescript/` - TypeScript usage examples

## Naming Conventions

- **Files**: kebab-case (e.g., `buffer-fetcher.ts`)
- **Directories**: kebab-case (e.g., `config-validator/`)
- **Test files**: `*.test.ts` suffix
- **Type files**: `types.ts` or inline in main file
- **Example files**: descriptive names with `.js` extension
