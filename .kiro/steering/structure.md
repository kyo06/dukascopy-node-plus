---
name: Project Structure
description: Project organization, folder structure, and module architecture
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
- **getHistoricalRates.ts** - Historical data API (Promise-based)
- **getHistoricalRatesToStream.ts** - Historical data API (Stream-based)
- **getRealTimeRates.ts** - Real-time data API
- **cli/index.ts** - CLI entry point

## API Functions

### getHistoricalRates
Promise-based API for downloading historical data. Returns the complete dataset.

**Use when:**
- Working with small to medium datasets (< 10,000 items)
- Need complete dataset in memory
- Prefer async/await syntax

**Signature:**
```typescript
async function getHistoricalRates(config: Config): Promise<Output>
```

### getHistoricalRatesToStream
Stream-based API for downloading historical data. Returns a Node.js Readable stream.

**Use when:**
- Working with large datasets (> 10,000 items)
- Memory efficiency is important
- Building data pipelines
- Writing directly to files

**Signature:**
```typescript
function getHistoricalRatesToStream(config: Config): Readable
```

**Key differences:**
- Fetches data in batches and streams progressively
- Lower memory footprint
- Can pipe to file or other streams
- Emits 'data', 'end', and 'error' events

### getRealTimeRates
Promise-based API for fetching the most recent market data.

**Signature:**
```typescript
async function getRealTimeRates(config: RealTimeRatesConfig): Promise<Output>
```

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
