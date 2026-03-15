---
name: Data Processing Best Practices
description: Bonnes pratiques pour le traitement des données financières
tags: [data, processing, financial]
---

# Data Processing Best Practices

## Principes Fondamentaux

### Immutabilité des Données

```typescript
// ✅ Bon - Créer de nouvelles instances
function normaliseCandle(candle: RawCandle): NormalisedCandle {
  return {
    ...candle,
    timestamp: normaliseTimestamp(candle.timestamp),
    volume: candle.volume ?? 0
  };
}

// ❌ Éviter - Mutation directe
function normaliseCandle(candle: RawCandle): void {
  candle.timestamp = normaliseTimestamp(candle.timestamp);
  candle.volume = candle.volume ?? 0;
}
```

### Validation des Données

```typescript
// Toujours valider les données entrantes
function validateCandle(candle: unknown): candle is Candle {
  if (typeof candle !== 'object' || candle === null) return false;
  
  const c = candle as Partial<Candle>;
  
  return (
    typeof c.timestamp === 'number' &&
    typeof c.open === 'number' &&
    typeof c.high === 'number' &&
    typeof c.low === 'number' &&
    typeof c.close === 'number' &&
    c.high >= c.low &&
    c.high >= c.open &&
    c.high >= c.close &&
    c.low <= c.open &&
    c.low <= c.close
  );
}

// Utilisation
export function processCandles(data: unknown[]): Candle[] {
  return data.filter(validateCandle);
}
```

## Traitement des Timestamps

### Normalisation

```typescript
// Dukascopy utilise des timestamps en millisecondes
export function normaliseTimestamp(
  timestamp: number,
  utcOffset: number = 0
): number {
  // Appliquer l'offset UTC si nécessaire
  return timestamp + (utcOffset * 60 * 60 * 1000);
}

// Conversion vers Date
export function timestampToDate(timestamp: number): Date {
  return new Date(timestamp);
}

// Formatage personnalisé
export function formatTimestamp(
  timestamp: number,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  return dayjs(timestamp).format(format);
}
```

### Gestion des Fuseaux Horaires

```typescript
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

dayjs.extend(utc);
dayjs.extend(timezone);

export function convertTimezone(
  timestamp: number,
  targetTimezone: string = 'UTC'
): number {
  return dayjs(timestamp).tz(targetTimezone).valueOf();
}

// Exemple
const utcTime = 1234567890000;
const nyTime = convertTimezone(utcTime, 'America/New_York');
const tokyoTime = convertTimezone(utcTime, 'Asia/Tokyo');
```

## Agrégation de Données

### OHLC (Open, High, Low, Close)

```typescript
export interface TickData {
  timestamp: number;
  price: number;
  volume?: number;
}

export interface OHLCCandle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

/**
 * Agrège les ticks en bougies OHLC
 */
export function aggregateTicksToOHLC(
  ticks: TickData[],
  timeframe: number // en millisecondes
): OHLCCandle[] {
  if (ticks.length === 0) return [];

  const candles: OHLCCandle[] = [];
  let currentCandle: Partial<OHLCCandle> | null = null;
  let candleStartTime = 0;

  for (const tick of ticks) {
    const tickCandleTime = Math.floor(tick.timestamp / timeframe) * timeframe;

    // Nouvelle bougie
    if (tickCandleTime !== candleStartTime) {
      if (currentCandle) {
        candles.push(currentCandle as OHLCCandle);
      }

      currentCandle = {
        timestamp: tickCandleTime,
        open: tick.price,
        high: tick.price,
        low: tick.price,
        close: tick.price,
        volume: tick.volume ?? 0
      };
      candleStartTime = tickCandleTime;
    } else if (currentCandle) {
      // Mise à jour de la bougie courante
      currentCandle.high = Math.max(currentCandle.high!, tick.price);
      currentCandle.low = Math.min(currentCandle.low!, tick.price);
      currentCandle.close = tick.price;
      currentCandle.volume = (currentCandle.volume ?? 0) + (tick.volume ?? 0);
    }
  }

  // Ajouter la dernière bougie
  if (currentCandle) {
    candles.push(currentCandle as OHLCCandle);
  }

  return candles;
}
```

### Agrégation de Timeframes

```typescript
/**
 * Agrège des bougies d'un timeframe inférieur vers un supérieur
 * Ex: M1 -> H1, H1 -> D1
 */
export function aggregateCandles(
  candles: OHLCCandle[],
  targetTimeframe: number
): OHLCCandle[] {
  if (candles.length === 0) return [];

  const aggregated: OHLCCandle[] = [];
  let currentAggregate: Partial<OHLCCandle> | null = null;
  let aggregateStartTime = 0;

  for (const candle of candles) {
    const candleAggregateTime = 
      Math.floor(candle.timestamp / targetTimeframe) * targetTimeframe;

    if (candleAggregateTime !== aggregateStartTime) {
      if (currentAggregate) {
        aggregated.push(currentAggregate as OHLCCandle);
      }

      currentAggregate = {
        timestamp: candleAggregateTime,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: candle.volume
      };
      aggregateStartTime = candleAggregateTime;
    } else if (currentAggregate) {
      currentAggregate.high = Math.max(currentAggregate.high!, candle.high);
      currentAggregate.low = Math.min(currentAggregate.low!, candle.low);
      currentAggregate.close = candle.close;
      currentAggregate.volume = (currentAggregate.volume ?? 0) + candle.volume;
    }
  }

  if (currentAggregate) {
    aggregated.push(currentAggregate as OHLCCandle);
  }

  return aggregated;
}
```

## Gestion des Gaps (Données Manquantes)

### Détection des Gaps

```typescript
export function detectGaps(
  candles: OHLCCandle[],
  expectedTimeframe: number
): Gap[] {
  const gaps: Gap[] = [];

  for (let i = 1; i < candles.length; i++) {
    const expectedTime = candles[i - 1].timestamp + expectedTimeframe;
    const actualTime = candles[i].timestamp;

    if (actualTime > expectedTime) {
      gaps.push({
        from: candles[i - 1].timestamp,
        to: candles[i].timestamp,
        duration: actualTime - expectedTime
      });
    }
  }

  return gaps;
}
```

### Options de Traitement

```typescript
export interface GapHandlingOptions {
  strategy: 'skip' | 'fill' | 'interpolate';
  fillValue?: 'previous' | 'zero' | 'null';
}

export function handleGaps(
  candles: OHLCCandle[],
  timeframe: number,
  options: GapHandlingOptions
): OHLCCandle[] {
  if (options.strategy === 'skip') {
    return candles;
  }

  const filled: OHLCCandle[] = [];
  
  for (let i = 0; i < candles.length - 1; i++) {
    filled.push(candles[i]);

    const expectedNext = candles[i].timestamp + timeframe;
    const actualNext = candles[i + 1].timestamp;

    // Gap détecté
    if (actualNext > expectedNext) {
      const gapCandles = fillGap(
        candles[i],
        candles[i + 1],
        timeframe,
        options
      );
      filled.push(...gapCandles);
    }
  }

  filled.push(candles[candles.length - 1]);
  return filled;
}
```

## Gestion des Volumes

### Instruments avec/sans Volume

```typescript
export function hasVolumeSupport(instrument: Instrument): boolean {
  // Forex n'a généralement pas de volume réel
  const forexPattern = /^[A-Z]{6}$/;
  if (forexPattern.test(instrument)) return false;

  // Crypto, stocks, ETFs ont du volume
  return true;
}

export function normaliseVolume(
  volume: number | undefined,
  instrument: Instrument
): number {
  if (!hasVolumeSupport(instrument)) return 0;
  return volume ?? 0;
}
```

## Filtrage des Données

### Ignorer les Flats (Bougies sans mouvement)

```typescript
export function removeFlats(candles: OHLCCandle[]): OHLCCandle[] {
  return candles.filter(candle => {
    // Garder si il y a du mouvement
    return candle.high !== candle.low;
  });
}

export function removeFlatSequences(
  candles: OHLCCandle[],
  maxConsecutive: number = 3
): OHLCCandle[] {
  const result: OHLCCandle[] = [];
  let flatCount = 0;

  for (const candle of candles) {
    const isFlat = candle.high === candle.low;

    if (isFlat) {
      flatCount++;
      if (flatCount <= maxConsecutive) {
        result.push(candle);
      }
    } else {
      flatCount = 0;
      result.push(candle);
    }
  }

  return result;
}
```

## Performance et Optimisation

### Traitement par Batch

```typescript
export async function processBatches<T, R>(
  items: T[],
  batchSize: number,
  processor: (batch: T[]) => Promise<R[]>
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await processor(batch);
    results.push(...batchResults);
  }

  return results;
}

// Utilisation
const urls = generateUrls(config);
const data = await processBatches(urls, 10, async batch => {
  return Promise.all(batch.map(url => fetchData(url)));
});
```

### Streaming pour Grandes Quantités

```typescript
import { Transform } from 'stream';

export class CandleTransform extends Transform {
  constructor(private readonly timeframe: number) {
    super({ objectMode: true });
  }

  _transform(
    chunk: TickData,
    encoding: string,
    callback: (error?: Error, data?: OHLCCandle) => void
  ): void {
    try {
      // Traiter le tick
      const candle = this.processTickToCandle(chunk);
      callback(null, candle);
    } catch (error) {
      callback(error as Error);
    }
  }

  private processTickToCandle(tick: TickData): OHLCCandle {
    // Logique de transformation
  }
}

// Utilisation
const stream = createReadStream('ticks.json')
  .pipe(new CandleTransform(60000)) // 1 minute
  .pipe(createWriteStream('candles.json'));
```

## Validation de Cohérence

### Vérifications OHLC

```typescript
export function validateOHLCConsistency(candle: OHLCCandle): boolean {
  return (
    candle.high >= candle.open &&
    candle.high >= candle.close &&
    candle.high >= candle.low &&
    candle.low <= candle.open &&
    candle.low <= candle.close &&
    candle.volume >= 0
  );
}

export function sanitiseCandle(candle: OHLCCandle): OHLCCandle {
  const high = Math.max(candle.open, candle.high, candle.low, candle.close);
  const low = Math.min(candle.open, candle.high, candle.low, candle.close);

  return {
    ...candle,
    high,
    low,
    volume: Math.max(0, candle.volume)
  };
}
```

## Bonnes Pratiques

1. **Toujours valider les données entrantes**
2. **Gérer les cas limites (gaps, données manquantes)**
3. **Préserver l'immutabilité**
4. **Documenter les unités (millisecondes, secondes, etc.)**
5. **Tester avec des données réelles et edge cases**
6. **Optimiser pour les grandes quantités (streaming, batching)**
7. **Maintenir la cohérence OHLC**
8. **Logger les anomalies sans crasher**
