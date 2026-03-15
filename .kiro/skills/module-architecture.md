---
name: Module Architecture
description: Patterns d'architecture et organisation des modules
tags: [architecture, patterns, modules]
---

# Module Architecture

## Principes de Base

### Séparation des Responsabilités

Chaque module a une responsabilité unique et bien définie :

- **buffer-fetcher** : Récupération HTTP uniquement
- **decompressor** : Décompression LZMA uniquement
- **data-normaliser** : Normalisation des données uniquement
- **output-formatter** : Formatage de sortie uniquement

### Structure Standard d'un Module

```
module-name/
├── index.ts           # Point d'entrée, exports publics
├── types.ts           # Types et interfaces (optionnel)
├── module-name.test.ts # Tests unitaires
└── tests/             # Tests complexes et fixtures (optionnel)
```

## Patterns d'Implémentation

### 1. Module Fonctionnel Simple

Pour les utilitaires et transformations simples :

```typescript
// url-generator/index.ts
import type { Config } from '../config';

export const URL_ROOT = 'https://datafeed.dukascopy.com';

/**
 * Génère les URLs pour télécharger les données
 */
export function generateUrls(config: Config): string[] {
  const { instrument, dates, timeframe } = config;
  const urls: string[] = [];
  
  // Logique de génération
  
  return urls;
}

// Export simple, pas de classe nécessaire
```

### 2. Module avec Classe et État

Pour les modules nécessitant une configuration ou un état :

```typescript
// cache-manager/index.ts
import type { CacheConfig } from './types';

export class CacheManager {
  private readonly folder: string;
  private readonly enabled: boolean;

  constructor(config: CacheConfig = {}) {
    this.folder = config.folder ?? '.cache';
    this.enabled = config.enabled ?? true;
  }

  async get(key: string): Promise<Buffer | null> {
    if (!this.enabled) return null;
    // Logique de récupération
  }

  async set(key: string, data: Buffer): Promise<void> {
    if (!this.enabled) return;
    // Logique de stockage
  }

  async clear(): Promise<void> {
    // Logique de nettoyage
  }
}

// Export de la classe et des types
export type { CacheConfig } from './types';
```

### 3. Module avec Surcharges TypeScript

Pour les fonctions avec différents types de retour selon les paramètres :

```typescript
// getHistoricalRates.ts
import {
  Config,
  ConfigArrayItem,
  ConfigArrayTickItem,
  ConfigJsonItem,
  ConfigJsonTickItem,
  ConfigCsvItem
} from './config';

// Surcharges pour un typage précis
export async function getHistoricalRates(config: ConfigArrayItem): Promise<ArrayItem[]>;
export async function getHistoricalRates(config: ConfigArrayTickItem): Promise<ArrayTickItem[]>;
export async function getHistoricalRates(config: ConfigJsonItem): Promise<JsonItem[]>;
export async function getHistoricalRates(config: ConfigJsonTickItem): Promise<JsonItemTick[]>;
export async function getHistoricalRates(config: ConfigCsvItem): Promise<string>;
export async function getHistoricalRates(config: Config): Promise<Output>;

// Implémentation
export async function getHistoricalRates(config: Config): Promise<Output> {
  // Logique de traitement
}
```

### 4. Module avec Streaming

Pour le traitement de grandes quantités de données :

```typescript
// getHistoricalRatesToStream.ts
import { Readable } from 'stream';
import { Config } from './config';

/**
 * Retourne un stream Node.js pour traiter les données progressivement
 * Idéal pour les gros datasets (> 10,000 items)
 */
export function getHistoricalRatesToStream(config: ConfigArrayItem): Readable;
export function getHistoricalRatesToStream(config: ConfigJsonItem): Readable;
export function getHistoricalRatesToStream(config: ConfigCsvItem): Readable;
export function getHistoricalRatesToStream(config: Config): Readable;

export function getHistoricalRatesToStream(config: Config): Readable {
  const stream = new Readable({
    objectMode: true,
    async read(_size) {}
  });

  // Fetch et stream des données
  bufferFetcher
    .fetch(urls)
    .then(bufferredData => {
      const processedData = processData({ ... });
      
      // Stream les données
      processedData.forEach(item => {
        stream.push(item);
      });
      
      stream.push(null); // Signal de fin
    })
    .catch(err => {
      stream.emit('error', err);
      stream.push(null);
    });

  return stream;
}
```

### 5. Module avec Factory Pattern

Pour créer des instances configurées :

```typescript
// processor/index.ts
import type { ProcessorConfig } from './types';

export interface Processor {
  process(data: Buffer): Promise<ProcessedData>;
}

class DefaultProcessor implements Processor {
  constructor(private config: ProcessorConfig) {}
  
  async process(data: Buffer): Promise<ProcessedData> {
    // Implémentation
  }
}

class StreamProcessor implements Processor {
  constructor(private config: ProcessorConfig) {}
  
  async process(data: Buffer): Promise<ProcessedData> {
    // Implémentation streaming
  }
}

export function createProcessor(config: ProcessorConfig): Processor {
  return config.useStream 
    ? new StreamProcessor(config)
    : new DefaultProcessor(config);
}
```

## Gestion des Dépendances

### Injection de Dépendances

```typescript
// ✅ Bon - Dépendances injectables
export class BufferFetcher {
  constructor(
    private readonly config: FetchConfig,
    private readonly cache?: CacheManager
  ) {}

  async fetch(url: string): Promise<Buffer> {
    // Vérifier le cache si disponible
    if (this.cache) {
      const cached = await this.cache.get(url);
      if (cached) return cached;
    }
    
    // Fetch et cache
    const data = await this.fetchFromNetwork(url);
    await this.cache?.set(url, data);
    
    return data;
  }
}

// Utilisation
const fetcher = new BufferFetcher(config, cacheManager);
```

### Composition vs Héritage

```typescript
// ✅ Bon - Composition
export class DataProcessor {
  constructor(
    private readonly fetcher: BufferFetcher,
    private readonly decompressor: Decompressor,
    private readonly normaliser: DataNormaliser
  ) {}

  async process(url: string): Promise<NormalisedData> {
    const buffer = await this.fetcher.fetch(url);
    const decompressed = await this.decompressor.decompress(buffer);
    return this.normaliser.normalise(decompressed);
  }
}

// ❌ Éviter - Héritage profond
class BaseProcessor { }
class AdvancedProcessor extends BaseProcessor { }
class SpecialProcessor extends AdvancedProcessor { }
```

## Pipeline Pattern

Pour le traitement séquentiel des données :

```typescript
// processor/index.ts
export async function processData(config: Config): Promise<Output> {
  // 1. Validation
  const validatedConfig = await validateConfig(config);
  
  // 2. Génération des URLs
  const urls = generateUrls(validatedConfig);
  
  // 3. Récupération des données
  const buffers = await fetchBuffers(urls);
  
  // 4. Décompression
  const decompressed = await decompressBuffers(buffers);
  
  // 5. Normalisation
  const normalised = normaliseData(decompressed, validatedConfig);
  
  // 6. Agrégation (si nécessaire)
  const aggregated = aggregateData(normalised, validatedConfig);
  
  // 7. Formatage
  return formatOutput(aggregated, validatedConfig);
}
```

## Gestion des Erreurs

### Erreurs Personnalisées par Module

```typescript
// buffer-fetcher/errors.ts
export class FetchError extends Error {
  constructor(
    message: string,
    public readonly url: string,
    public readonly statusCode?: number,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'FetchError';
  }
}

// buffer-fetcher/index.ts
export class BufferFetcher {
  async fetch(url: string): Promise<Buffer> {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new FetchError(
          `HTTP ${response.status}`,
          url,
          response.status
        );
      }
      return await response.buffer();
    } catch (error) {
      if (error instanceof FetchError) throw error;
      throw new FetchError('Network error', url, undefined, error as Error);
    }
  }
}
```

### Propagation des Erreurs

```typescript
// ✅ Bon - Laisser les erreurs remonter avec contexte
export async function processData(config: Config): Promise<Output> {
  try {
    const validated = validateConfig(config);
    return await fetchAndProcess(validated);
  } catch (error) {
    if (error instanceof ConfigValidationError) {
      // Erreur de validation - ajouter contexte
      throw new ProcessingError('Invalid configuration', { cause: error });
    }
    // Autres erreurs - propager
    throw error;
  }
}
```

## Exports Publics

### index.ts comme Interface Publique

```typescript
// module/index.ts - Exports publics uniquement
export { MainClass } from './main-class';
export { helperFunction } from './helpers';
export type { PublicConfig, PublicResult } from './types';

// Ne pas exporter les détails d'implémentation
// ❌ export { InternalHelper } from './internal';
```

### Barrel Exports

```typescript
// config/index.ts - Agrégation des exports
export { defaultConfig } from './default-config';
export { Instrument } from './instruments';
export { Timeframe } from './timeframes';
export { Format } from './format';
export { Price } from './price-types';

export type {
  Config,
  ConfigArrayItem,
  ConfigJsonItem,
  ConfigCsvItem
} from './types';
```

## Patterns Avancés

### Builder Pattern pour Configuration Complexe

```typescript
// config/builder.ts
export class ConfigBuilder {
  private config: Partial<Config> = {};

  instrument(value: Instrument): this {
    this.config.instrument = value;
    return this;
  }

  dates(from: Date, to: Date): this {
    this.config.dates = { from, to };
    return this;
  }

  timeframe(value: Timeframe): this {
    this.config.timeframe = value;
    return this;
  }

  build(): Config {
    const validated = validateConfig(this.config);
    if (!validated.isValid) {
      throw new ConfigValidationError('Invalid config', validated.errors);
    }
    return validated.config;
  }
}

// Utilisation
const config = new ConfigBuilder()
  .instrument('btcusd')
  .dates(new Date('2023-01-01'), new Date('2023-01-02'))
  .timeframe('h1')
  .build();
```

### Strategy Pattern pour Formats Multiples

```typescript
// output-formatter/strategies.ts
interface FormatStrategy {
  format(data: NormalisedData): string | object | Array<unknown>;
}

class JsonStrategy implements FormatStrategy {
  format(data: NormalisedData): object {
    return data.map(item => ({
      timestamp: item.timestamp,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close
    }));
  }
}

class CsvStrategy implements FormatStrategy {
  format(data: NormalisedData): string {
    const header = 'timestamp,open,high,low,close\n';
    const rows = data.map(item => 
      `${item.timestamp},${item.open},${item.high},${item.low},${item.close}`
    ).join('\n');
    return header + rows;
  }
}

// output-formatter/index.ts
export function formatOutput(data: NormalisedData, format: Format): Output {
  const strategies: Record<Format, FormatStrategy> = {
    json: new JsonStrategy(),
    csv: new CsvStrategy(),
    array: new ArrayStrategy()
  };

  const strategy = strategies[format];
  return strategy.format(data);
}
```

## Bonnes Pratiques

1. **Un module = Une responsabilité**
2. **Interfaces publiques minimales**
3. **Dépendances explicites (pas de globals)**
4. **Testabilité (injection de dépendances)**
5. **Documentation des exports publics**
6. **Gestion d'erreurs cohérente**
7. **Types exportés avec implémentations**
