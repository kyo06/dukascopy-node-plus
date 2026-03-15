---
name: Streaming Patterns
description: Best practices for using Node.js streams with dukascopy-node-plus
tags: [streaming, nodejs, performance, memory]
---

# Streaming Patterns

## When to Use Streams

### Use getHistoricalRatesToStream When:

✅ **Large Datasets**
- More than 10,000 data points
- Multiple months or years of data
- Tick data (very high volume)

✅ **Memory Constraints**
- Running in memory-limited environments
- Processing multiple instruments simultaneously
- Need to keep memory usage predictable

✅ **Progressive Processing**
- Writing directly to files
- Piping to other streams (compression, transformation)
- Real-time processing as data arrives
- Building data pipelines

✅ **Integration with Node.js Ecosystem**
- Using stream-based libraries
- Building ETL pipelines
- Integrating with databases that support streams

### Use getHistoricalRates When:

✅ **Small to Medium Datasets**
- Less than 10,000 data points
- Single day or week of data
- OHLC data (lower volume than ticks)

✅ **In-Memory Analysis**
- Need complete dataset for calculations
- Statistical analysis requiring all data
- Sorting or filtering entire dataset

✅ **Simpler Code**
- Prefer async/await syntax
- Don't need streaming capabilities
- Prototyping or quick scripts

## Stream Basics

### Creating a Stream

```typescript
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';

const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-12-31') },
  timeframe: 'd1',
  format: 'json'
});
```

### Listening to Events

```typescript
// Data event - emitted for each item
stream.on('data', (item) => {
  console.log('Received:', item);
});

// End event - emitted when stream is complete
stream.on('end', () => {
  console.log('Stream complete');
});

// Error event - emitted on errors
stream.on('error', (err) => {
  console.error('Stream error:', err);
});
```

## Common Patterns

### Pattern 1: Write to File

```typescript
import { createWriteStream } from 'fs';
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';

const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-12-31') },
  timeframe: 'd1',
  format: 'csv'
});

const fileStream = createWriteStream('eurusd-2023.csv');

stream.pipe(fileStream);

fileStream.on('finish', () => {
  console.log('File written successfully');
});

fileStream.on('error', (err) => {
  console.error('File write error:', err);
});
```

### Pattern 2: Transform Stream

```typescript
import { Transform } from 'stream';
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';

// Create a transform stream to calculate moving average
const movingAverageTransform = new Transform({
  objectMode: true,
  transform(candle, encoding, callback) {
    // Add your transformation logic
    const enhanced = {
      ...candle,
      ma20: calculateMA(candle, 20)
    };
    callback(null, enhanced);
  }
});

const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-01-31') },
  timeframe: 'h1',
  format: 'json'
});

stream
  .pipe(movingAverageTransform)
  .on('data', (enhanced) => {
    console.log('Enhanced candle:', enhanced);
  });
```

### Pattern 3: Collect to Array (with Backpressure Handling)

```typescript
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';

async function collectToArray(config) {
  const stream = getHistoricalRatesToStream(config);
  const results = [];

  return new Promise((resolve, reject) => {
    stream.on('data', (item) => {
      results.push(item);
    });

    stream.on('end', () => {
      resolve(results);
    });

    stream.on('error', (err) => {
      reject(err);
    });
  });
}

// Usage
const data = await collectToArray({
  instrument: 'btcusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-01-02') },
  timeframe: 'tick',
  format: 'json'
});
```

### Pattern 4: Pipeline with Multiple Transforms

```typescript
import { pipeline } from 'stream/promises';
import { Transform, Writable } from 'stream';
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';

// Filter transform
const filterTransform = new Transform({
  objectMode: true,
  transform(candle, encoding, callback) {
    // Only pass through candles with volume > 1000
    if (candle.volume > 1000) {
      callback(null, candle);
    } else {
      callback();
    }
  }
});

// Process transform
const processTransform = new Transform({
  objectMode: true,
  transform(candle, encoding, callback) {
    const processed = {
      timestamp: new Date(candle.timestamp).toISOString(),
      price: candle.close,
      volume: candle.volume
    };
    callback(null, JSON.stringify(processed) + '\n');
  }
});

// Write stream
const writeStream = createWriteStream('filtered-data.json');

const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-01-31') },
  timeframe: 'h1',
  format: 'json'
});

// Pipeline automatically handles errors and cleanup
await pipeline(
  stream,
  filterTransform,
  processTransform,
  writeStream
);

console.log('Pipeline complete');
```

### Pattern 5: Batch Processing

```typescript
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';

async function processBatches(config, batchSize = 100) {
  const stream = getHistoricalRatesToStream(config);
  let batch = [];

  return new Promise((resolve, reject) => {
    stream.on('data', async (item) => {
      batch.push(item);

      if (batch.length >= batchSize) {
        // Pause stream while processing batch
        stream.pause();

        try {
          await processBatch(batch);
          batch = [];
          stream.resume();
        } catch (err) {
          stream.destroy();
          reject(err);
        }
      }
    });

    stream.on('end', async () => {
      // Process remaining items
      if (batch.length > 0) {
        try {
          await processBatch(batch);
          resolve();
        } catch (err) {
          reject(err);
        }
      } else {
        resolve();
      }
    });

    stream.on('error', reject);
  });
}

async function processBatch(items) {
  // Process batch (e.g., insert to database)
  console.log(`Processing batch of ${items.length} items`);
  // await db.insertMany(items);
}
```

### Pattern 6: Multiple Instruments in Parallel

```typescript
import { getHistoricalRatesToStream } from 'dukascopy-node-plus';
import { createWriteStream } from 'fs';

async function downloadMultipleInstruments(instruments, dates) {
  const promises = instruments.map(instrument => {
    return new Promise((resolve, reject) => {
      const stream = getHistoricalRatesToStream({
        instrument,
        dates,
        timeframe: 'd1',
        format: 'csv'
      });

      const fileStream = createWriteStream(`${instrument}-data.csv`);

      stream.pipe(fileStream);

      fileStream.on('finish', () => {
        console.log(`${instrument} complete`);
        resolve();
      });

      fileStream.on('error', reject);
      stream.on('error', reject);
    });
  });

  await Promise.all(promises);
  console.log('All instruments downloaded');
}

// Usage
await downloadMultipleInstruments(
  ['eurusd', 'gbpusd', 'usdjpy'],
  { from: new Date('2023-01-01'), to: new Date('2023-12-31') }
);
```

## Error Handling

### Proper Error Handling

```typescript
const stream = getHistoricalRatesToStream(config);

// ✅ Good - Handle all error scenarios
stream.on('error', (err) => {
  if (err.message.includes('validation')) {
    console.error('Configuration error:', err);
  } else if (err.message.includes('fetch')) {
    console.error('Network error:', err);
  } else {
    console.error('Unexpected error:', err);
  }
});

// ✅ Good - Clean up on error
stream.on('error', (err) => {
  console.error('Error:', err);
  stream.destroy(); // Clean up resources
});
```

### Error Recovery

```typescript
async function downloadWithRetry(config, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await new Promise((resolve, reject) => {
        const stream = getHistoricalRatesToStream(config);
        const results = [];

        stream.on('data', (item) => results.push(item));
        stream.on('end', () => resolve(results));
        stream.on('error', reject);
      });
    } catch (err) {
      console.error(`Attempt ${attempt} failed:`, err);
      
      if (attempt === maxRetries) {
        throw new Error(`Failed after ${maxRetries} attempts`);
      }

      // Wait before retry
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
}
```

## Performance Tips

### 1. Use Appropriate Batch Size

```typescript
// ✅ Good - Configure batch size based on your needs
const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-12-31') },
  timeframe: 'd1',
  format: 'json',
  batchSize: 20, // Larger batches = fewer HTTP requests
  pauseBetweenBatchesMs: 500 // Avoid rate limiting
});
```

### 2. Enable Caching for Repeated Access

```typescript
// ✅ Good - Use cache for repeated downloads
const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: new Date('2023-01-01'), to: new Date('2023-12-31') },
  timeframe: 'd1',
  format: 'json',
  useCache: true,
  cacheFolderPath: './.cache'
});
```

### 3. Handle Backpressure

```typescript
// ✅ Good - Respect backpressure
stream.on('data', async (item) => {
  stream.pause(); // Pause while processing
  
  await processItem(item);
  
  stream.resume(); // Resume after processing
});
```

## Memory Comparison

### getHistoricalRates (Non-Streaming)
```typescript
// Loads entire dataset into memory
const data = await getHistoricalRates({
  instrument: 'eurusd',
  dates: { from: '2023-01-01', to: '2023-12-31' },
  timeframe: 'd1',
  format: 'json'
});
// Memory: ~365 items × ~100 bytes = ~36 KB
// For tick data: Could be 100+ MB
```

### getHistoricalRatesToStream (Streaming)
```typescript
// Processes items one at a time
const stream = getHistoricalRatesToStream({
  instrument: 'eurusd',
  dates: { from: '2023-01-01', to: '2023-12-31' },
  timeframe: 'd1',
  format: 'json'
});

stream.on('data', (item) => {
  // Process item
});
// Memory: ~1 item × ~100 bytes = ~100 bytes
// Constant memory usage regardless of dataset size
```

## Best Practices

1. **Always handle errors** - Streams can fail at any point
2. **Clean up resources** - Call `stream.destroy()` on errors
3. **Use pipeline()** - Automatically handles errors and cleanup
4. **Respect backpressure** - Pause stream during heavy processing
5. **Enable caching** - For repeated access to same data
6. **Configure batch size** - Balance between speed and rate limiting
7. **Use appropriate format** - CSV for files, JSON for processing
8. **Monitor memory** - Ensure streaming is actually reducing memory usage

## Anti-Patterns to Avoid

```typescript
// ❌ Bad - Collecting entire stream to array defeats the purpose
const stream = getHistoricalRatesToStream(config);
const allData = [];
stream.on('data', (item) => allData.push(item));
// Use getHistoricalRates instead!

// ❌ Bad - Not handling errors
const stream = getHistoricalRatesToStream(config);
stream.on('data', (item) => { /* ... */ });
// Missing: stream.on('error', ...)

// ❌ Bad - Blocking the event loop
stream.on('data', (item) => {
  // Synchronous heavy computation
  for (let i = 0; i < 1000000; i++) { /* ... */ }
});
// Use async processing or worker threads

// ❌ Bad - Not cleaning up on error
stream.on('error', (err) => {
  console.error(err);
  // Missing: stream.destroy()
});
```
