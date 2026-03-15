import {
  Config,
  ConfigArrayItem,
  ConfigArrayTickItem,
  ConfigJsonItem,
  ConfigJsonTickItem,
  ConfigCsvItem
} from './config';

import { validateConfigNode } from './config-validator';
import { normaliseDates } from './dates-normaliser';

import { generateUrls } from './url-generator';
import { BufferFetcher } from './buffer-fetcher';
import { processData } from './processor';
import { candleHeaders, tickHeaders } from './output-formatter';
import { CacheManager } from './cache-manager';
import { formatBytes } from './utils/formatBytes';
import { BufferFetcherInput } from './buffer-fetcher/types';

import { version } from '../package.json';

import debug from 'debug';
import os from 'os';

const DEBUG_NAMESPACE = 'dukascopy-node';

import { Readable } from 'stream';
import { Format } from './config/format';
import { Timeframe } from './config/timeframes';

/**
 * Downloads historical market data from Dukascopy and returns it as a Node.js Readable stream.
 *
 * This function is ideal for processing large datasets progressively without loading
 * everything into memory at once. Data is fetched in batches and streamed as it becomes available.
 *
 * @param config - Configuration object specifying instrument, dates, timeframe, and format
 * @returns A Node.js Readable stream that emits data items progressively
 *
 * @remarks
 * **When to use `getHistoricalRatesToStream` vs `getHistoricalRates`:**
 *
 * Use `getHistoricalRatesToStream` when:
 * - Working with large datasets (> 10,000 items)
 * - Memory efficiency is important
 * - You want to process data progressively (e.g., pipe to file, transform stream)
 * - Building data pipelines with Node.js streams
 *
 * Use `getHistoricalRates` when:
 * - Working with small to medium datasets (< 10,000 items)
 * - You need the complete dataset in memory for analysis
 * - Simpler async/await API is preferred
 * - You want to work with the data as a complete array/object
 *
 * @example
 * **Array format (streaming OHLC candles):**
 * ```typescript
 * const stream = getHistoricalRatesToStream({
 *   instrument: 'eurusd',
 *   dates: { from: new Date('2023-01-01'), to: new Date('2023-01-02') },
 *   timeframe: 'h1',
 *   format: 'array'
 * });
 *
 * stream.on('data', (candle: number[]) => {
 *   const [timestamp, open, high, low, close, volume] = candle;
 *   console.log('Candle:', { timestamp, open, high, low, close, volume });
 * });
 *
 * stream.on('end', () => console.log('Stream complete'));
 * stream.on('error', (err) => console.error('Error:', err));
 * ```
 *
 * @example
 * **JSON format (streaming tick data):**
 * ```typescript
 * const stream = getHistoricalRatesToStream({
 *   instrument: 'btcusd',
 *   dates: { from: new Date('2023-01-01'), to: new Date('2023-01-02') },
 *   timeframe: 'tick',
 *   format: 'json'
 * });
 *
 * stream.on('data', (tick: { timestamp: number; price: number; volume: number }) => {
 *   console.log('Tick:', tick);
 * });
 * ```
 *
 * @example
 * **CSV format (pipe to file):**
 * ```typescript
 * import { createWriteStream } from 'fs';
 *
 * const stream = getHistoricalRatesToStream({
 *   instrument: 'eurusd',
 *   dates: { from: new Date('2023-01-01'), to: new Date('2023-12-31') },
 *   timeframe: 'd1',
 *   format: 'csv'
 * });
 *
 * stream.pipe(createWriteStream('eurusd-2023.csv'));
 * ```
 *
 * @throws Emits 'error' event if configuration validation fails or data fetching encounters errors
 *
 * @see {@link getHistoricalRates} for the non-streaming version that returns a Promise
 */
export function getHistoricalRatesToStream(config: ConfigArrayItem): Readable;
export function getHistoricalRatesToStream(config: ConfigArrayTickItem): Readable;
export function getHistoricalRatesToStream(config: ConfigJsonItem): Readable;
export function getHistoricalRatesToStream(config: ConfigJsonTickItem): Readable;
export function getHistoricalRatesToStream(config: ConfigCsvItem): Readable;
export function getHistoricalRatesToStream(config: Config): Readable;

export function getHistoricalRatesToStream(config: Config): Readable {
  const stream = new Readable({
    objectMode: true,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    async read(_size) {}
  });

  try {
    debug(`${DEBUG_NAMESPACE}:version`)(version);
    debug(`${DEBUG_NAMESPACE}:nodejs`)(process.version);
    debug(`${DEBUG_NAMESPACE}:os`)(`${os.type()}, ${os.release()} (${os.platform()})`);

    const { input, isValid, validationErrors } = validateConfigNode(config);

    debug(`${DEBUG_NAMESPACE}:config`)('%O', {
      input,
      isValid,
      validationErrors
    });

    if (!isValid) {
      const error = new Error('Configuration validation failed');
      Object.assign(error, { validationErrors });
      stream.emit('error', error);
      stream.push(null);
      return stream;
    }

    const {
      instrument,
      dates: { from, to },
      timeframe,
      priceType,
      volumes,
      volumeUnits,
      utcOffset,
      ignoreFlats,
      format,
      batchSize,
      pauseBetweenBatchesMs,
      useCache,
      cacheFolderPath,
      retryCount,
      pauseBetweenRetriesMs,
      retryOnEmpty
    } = input;

    const [startDate, endDate] = normaliseDates({
      instrument,
      startDate: from,
      endDate: to,
      timeframe,
      utcOffset
    });
    const [startDateMs, endDateMs] = [+startDate, +endDate];

    const urls = generateUrls({
      instrument,
      timeframe,
      priceType,
      startDate,
      endDate
    });

    debug(`${DEBUG_NAMESPACE}:urls`)(`Generated ${urls.length} urls`);
    debug(`${DEBUG_NAMESPACE}:urls`)('%O', urls);

    const onItemFetch: BufferFetcherInput['onItemFetch'] = process.env.DEBUG
      ? (url, buffer, isCacheHit) => {
          debug(`${DEBUG_NAMESPACE}:fetcher`)(
            url,
            `| ${formatBytes(buffer.length)} |`,
            `${isCacheHit ? 'cache' : 'network'}`
          );
        }
      : undefined;

    const bufferFetcher = new BufferFetcher({
      batchSize,
      pauseBetweenBatchesMs,
      cacheManager: useCache ? new CacheManager({ cacheFolderPath }) : undefined,
      retryCount,
      pauseBetweenRetriesMs,
      onItemFetch,
      retryOnEmpty
    });

    const bodyHeaders = timeframe === Timeframe.tick ? tickHeaders : candleHeaders;

    let firstLine = true;

    // Fetch all URLs using the configured batching
    bufferFetcher
      .fetch(urls)
      .then(bufferredData => {
        debug(`${DEBUG_NAMESPACE}:fetcher`)(`Fetched ${bufferredData.length} buffer objects`);

        // Process all data at once
        const processedData = processData({
          instrument,
          requestedTimeframe: timeframe,
          bufferObjects: bufferredData,
          priceType,
          volumes,
          volumeUnits,
          ignoreFlats
        });

        debug(`${DEBUG_NAMESPACE}:data`)(
          `Generated ${processedData.length} ${timeframe === Timeframe.tick ? 'ticks' : 'OHLC candles'}`
        );

        // Filter and stream the data
        const filteredData = processedData.filter(
          ([timestamp]) => timestamp && timestamp >= startDateMs && timestamp < endDateMs
        );

        debug(`${DEBUG_NAMESPACE}:data`)(`Filtered to ${filteredData.length} items`);

        // Stream the filtered data
        filteredData.forEach((item: number[]) => {
          if (format === Format.array) {
            stream.push(item);
          } else if (format === Format.json) {
            const data = item.reduce(
              (all, value, i) => {
                const name = bodyHeaders[i];
                all[name] = value;
                return all;
              },
              {} as Record<string, number>
            );
            stream.push(data);
          } else if (format === Format.csv) {
            if (firstLine) {
              const csvHeaders = bodyHeaders.join(',');
              stream.push(csvHeaders);
              firstLine = false;
            }
            stream.push(`\n${item.join(',')}`);
          }
        });

        stream.push(null);
      })
      .catch(err => {
        debug(`${DEBUG_NAMESPACE}:error`)('Error fetching data: %O', err);
        stream.emit('error', err);
        stream.push(null);
      });
  } catch (err) {
    debug(`${DEBUG_NAMESPACE}:error`)('Unexpected error: %O', err);
    stream.emit('error', err);
    stream.push(null);
  }

  return stream;
}
