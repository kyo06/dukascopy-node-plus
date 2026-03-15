import { describe, it, expect } from 'vitest';
import { Readable } from 'stream';
import { getHistoricalRatesToStream } from './getHistoricalRatesToStream';

describe('getHistoricalRatesToStream - Basic Structure Tests', () => {
  it('should return a Readable stream', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'eurusd',
      dates: {
        from: new Date('2023-01-01'),
        to: new Date('2023-01-02')
      },
      timeframe: 'h1',
      format: 'json'
    });

    expect(stream).toBeInstanceOf(Readable);
    expect(stream.readable).toBe(true);
  });

  it('should emit error event for invalid instrument', () => {
    return new Promise<void>((resolve, reject) => {
      try {
        const stream = getHistoricalRatesToStream({
          // @ts-expect-error - Testing invalid config
          instrument: 'invalid_instrument_xyz',
          dates: {
            from: new Date('2023-01-01'),
            to: new Date('2023-01-02')
          },
          timeframe: 'h1',
          format: 'json'
        });

        stream.on('error', err => {
          try {
            expect(err).toBeDefined();
            expect(err.message).toContain('validation');
            resolve();
          } catch (e) {
            reject(e);
          }
        });

        stream.on('data', () => {
          reject(new Error('Should not emit data for invalid config'));
        });
      } catch (err) {
        // If error is thrown synchronously in try block, that's also valid
        try {
          expect(err).toBeDefined();
          resolve();
        } catch (e) {
          reject(e);
        }
      }
    });
  });

  it('should accept valid configuration with all parameters', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'eurusd',
      dates: {
        from: new Date('2023-01-01'),
        to: new Date('2023-01-02')
      },
      timeframe: 'h1',
      format: 'json',
      priceType: 'ask',
      volumes: true,
      volumeUnits: 'millions',
      ignoreFlats: false,
      utcOffset: 0,
      batchSize: 10,
      pauseBetweenBatchesMs: 1000,
      useCache: false,
      retryCount: 3,
      pauseBetweenRetriesMs: 500,
      retryOnEmpty: false
    });

    expect(stream).toBeInstanceOf(Readable);
  });

  it('should accept tick timeframe configuration', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'btcusd',
      dates: {
        from: new Date('2023-01-01T00:00:00Z'),
        to: new Date('2023-01-01T01:00:00Z')
      },
      timeframe: 'tick',
      format: 'json'
    });

    expect(stream).toBeInstanceOf(Readable);
  });

  it('should accept array format configuration', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'eurusd',
      dates: {
        from: new Date('2023-01-01'),
        to: new Date('2023-01-02')
      },
      timeframe: 'h1',
      format: 'array'
    });

    expect(stream).toBeInstanceOf(Readable);
  });

  it('should accept CSV format configuration', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'eurusd',
      dates: {
        from: new Date('2023-01-01'),
        to: new Date('2023-01-02')
      },
      timeframe: 'd1',
      format: 'csv'
    });

    expect(stream).toBeInstanceOf(Readable);
  });

  it('should accept cache configuration', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'eurusd',
      dates: {
        from: new Date('2023-01-01'),
        to: new Date('2023-01-02')
      },
      timeframe: 'h1',
      format: 'json',
      useCache: true,
      cacheFolderPath: './.test-cache'
    });

    expect(stream).toBeInstanceOf(Readable);
  });

  it('should have standard stream methods', () => {
    const stream = getHistoricalRatesToStream({
      instrument: 'eurusd',
      dates: {
        from: new Date('2023-01-01'),
        to: new Date('2023-01-02')
      },
      timeframe: 'h1',
      format: 'json'
    });

    expect(typeof stream.on).toBe('function');
    expect(typeof stream.pipe).toBe('function');
    expect(typeof stream.pause).toBe('function');
    expect(typeof stream.resume).toBe('function');
    expect(typeof stream.destroy).toBe('function');
  });

  it('should validate dates are required', () => {
    return new Promise<void>((resolve, reject) => {
      try {
        const stream = getHistoricalRatesToStream({
          instrument: 'eurusd',
          // @ts-expect-error - Testing missing dates
          dates: {},
          timeframe: 'h1',
          format: 'json'
        });

        stream.on('error', err => {
          try {
            expect(err).toBeDefined();
            resolve();
          } catch (e) {
            reject(e);
          }
        });

        stream.on('data', () => {
          reject(new Error('Should not emit data for invalid config'));
        });
      } catch (err) {
        // If error is thrown synchronously in try block, that's also valid
        try {
          expect(err).toBeDefined();
          resolve();
        } catch (e) {
          reject(e);
        }
      }
    });
  });

  it('should validate instrument is required', () => {
    return new Promise<void>((resolve, reject) => {
      try {
        const stream = getHistoricalRatesToStream({
          // @ts-expect-error - Testing missing instrument
          instrument: undefined,
          dates: {
            from: new Date('2023-01-01'),
            to: new Date('2023-01-02')
          },
          timeframe: 'h1',
          format: 'json'
        });

        stream.on('error', err => {
          try {
            expect(err).toBeDefined();
            resolve();
          } catch (e) {
            reject(e);
          }
        });

        stream.on('data', () => {
          reject(new Error('Should not emit data for invalid config'));
        });
      } catch (err) {
        // If error is thrown synchronously in try block, that's also valid
        try {
          expect(err).toBeDefined();
          resolve();
        } catch (e) {
          reject(e);
        }
      }
    });
  });
});
