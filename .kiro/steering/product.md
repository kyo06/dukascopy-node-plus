---
name: Product Overview
description: Summary of the dukascopy-node-plus product and its capabilities
inclusion: auto
---

# Product Overview

dukascopy-node-plus is a Node.js library and CLI tool for downloading historical and real-time market price tick data from Dukascopy.

## What It Does

- Downloads historical market data (tick, minute, hour, day, month timeframes)
- Fetches real-time market price data
- Supports multiple asset classes: Crypto, Stocks, ETFs, CFDs, Forex, Commodities, Bonds
- Provides both programmatic API and CLI interface
- Outputs data in multiple formats: JSON, CSV, Array
- Includes caching capabilities for efficient data retrieval
- Aggregates tick data into OHLC (Open, High, Low, Close) candles
- Supports streaming for memory-efficient processing of large datasets

## Key Features

- 1000+ supported instruments across global markets
- Configurable date ranges and timeframes
- Volume data support where available
- UTC offset customization
- Stream-based and non-stream data fetching
- Built-in data validation and normalization
- Batch processing with configurable retry logic
- Debug logging for troubleshooting

## Main APIs

### getHistoricalRates
Downloads historical data and returns a Promise with the complete dataset.
Best for small to medium datasets (< 10,000 items).

```typescript
const data = await getHistoricalRates({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-01-02') },
  timeframe: 'h1',
  format: 'json'
});
```

### getHistoricalRatesToStream
Downloads historical data and returns a Node.js Readable stream.
Best for large datasets (> 10,000 items) and memory-efficient processing.

```typescript
const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-12-31') },
  timeframe: 'd1',
  format: 'csv'
});

stream.pipe(createWriteStream('eurusd-2023.csv'));
```

### getRealTimeRates
Fetches the most recent market data available.

```typescript
const data = await getRealTimeRates({
  instrument: 'btcusd',
  timeframe: 'tick',
  format: 'json'
});
```
