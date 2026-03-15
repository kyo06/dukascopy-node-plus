---
name: Code Style Guide
description: Standards de formatage et style de code
tags: [style, prettier, eslint]
---

# Code Style Guide

## Configuration Automatique

Le projet utilise Prettier et ESLint pour maintenir un style cohérent.

### Avant de Committer

```bash
# Formater le code
npm run format

# Vérifier le linting
npm run lint

# Vérifier les types
npm run type-check
```

## Règles Prettier

```json
{
  "printWidth": 100,
  "useTabs": false,
  "tabWidth": 2,
  "singleQuote": true,
  "trailingComma": "none",
  "arrowParens": "avoid"
}
```

### Exemples

```typescript
// ✅ Bon - Single quotes, no trailing comma
const config = {
  instrument: 'btcusd',
  timeframe: 'm1',
  format: 'json'
};

// ✅ Bon - Arrow parens évités pour un seul paramètre
const process = data => data.map(item => item.value);

// ✅ Bon - Ligne max 100 caractères
const result = await getHistoricalRates({
  instrument: 'eurusd',
  dates: { from: startDate, to: endDate }
});
```

## Règles ESLint

### Semicolons

```typescript
// ✅ Toujours utiliser des semicolons
const value = 10;
export function process() {
  return value;
}
```

### Console Statements

```typescript
// ⚠️ Warning - console.log en production
console.log('Debug info'); // Éviter

// ✅ Utiliser le module debug
import debug from 'debug';
const log = debug('dukascopy:module-name');
log('Debug info'); // OK
```

### Unused Variables

```typescript
// ⚠️ Warning - Variables non utilisées
const unused = 10; // Éviter

// ✅ Préfixer avec underscore si intentionnel
const _reserved = 10;

// ✅ Ou utiliser eslint-disable si nécessaire
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const forFutureUse = 10;
```

## Organisation du Code

### Ordre des Imports

```typescript
// 1. Imports externes
import { format } from 'date-fns';
import debug from 'debug';

// 2. Imports internes (modules du projet)
import { Config } from './config';
import { validateConfig } from './config-validator';

// 3. Imports de types
import type { Instrument, Timeframe } from './types';
```

### Ordre dans les Fichiers

```typescript
// 1. Imports
import { ... } from '...';

// 2. Types et interfaces
export interface Config {
  // ...
}

// 3. Constantes
const DEFAULT_TIMEOUT = 5000;
export const URL_ROOT = 'https://...';

// 4. Fonctions utilitaires privées
function helperFunction() {
  // ...
}

// 5. Fonctions/classes publiques
export class MainClass {
  // ...
}

export function mainFunction() {
  // ...
}
```

## Commentaires

### Documentation des Fonctions Publiques

```typescript
/**
 * Télécharge les données historiques de marché depuis Dukascopy
 * 
 * @param config - Configuration incluant l'instrument, dates et format
 * @returns Données formatées selon le format spécifié
 * @throws {ConfigValidationError} Si la configuration est invalide
 * @throws {FetchError} Si le téléchargement échoue
 * 
 * @example
 * ```typescript
 * const data = await getHistoricalRates({
 *   instrument: 'btcusd',
 *   dates: { from: new Date('2023-01-01'), to: new Date('2023-01-02') },
 *   timeframe: 'h1',
 *   format: 'json'
 * });
 * ```
 */
export async function getHistoricalRates(config: Config): Promise<Output> {
  // ...
}
```

### Commentaires Inline

```typescript
// ✅ Bon - Explique le "pourquoi", pas le "quoi"
// Dukascopy utilise des timestamps en millisecondes depuis epoch
const timestamp = date.getTime();

// ❌ Éviter - Redondant avec le code
// Assigne la valeur 10 à x
const x = 10;
```

### TODOs et FIXMEs

```typescript
// TODO: Ajouter support pour les timeframes personnalisés
// FIXME: Gérer le cas où les données sont partielles
// NOTE: Cette logique doit rester synchronisée avec le backend Dukascopy
```

## Nommage

### Variables et Fonctions

```typescript
// ✅ Descriptif et camelCase
const historicalData = await fetchData();
const isValidConfig = validateConfig(config);
const hasVolume = checkVolumeSupport(instrument);

// ❌ Éviter - Noms courts et non descriptifs
const d = await fetch();
const x = validate(c);
```

### Constantes

```typescript
// ✅ UPPER_SNAKE_CASE pour les vraies constantes
export const MAX_RETRIES = 3;
export const DEFAULT_TIMEOUT = 5000;
export const URL_ROOT = 'https://datafeed.dukascopy.com';

// ✅ camelCase pour les objets de configuration
export const defaultConfig = {
  retries: MAX_RETRIES,
  timeout: DEFAULT_TIMEOUT
};
```

### Types et Interfaces

```typescript
// ✅ PascalCase, noms descriptifs
export interface HistoricalRatesConfig {
  instrument: Instrument;
  dates: DateRange;
  timeframe: Timeframe;
}

export type OutputFormat = 'json' | 'csv' | 'array';

// ✅ Suffixes pour clarifier le type
export type FetchCallback = (data: Buffer) => void;
export type ValidationResult = { isValid: boolean; errors: Error[] };
```

### Fichiers et Dossiers

```typescript
// ✅ kebab-case
buffer-fetcher.ts
config-validator/
output-formatter.ts

// ❌ Éviter
BufferFetcher.ts
configValidator/
output_formatter.ts
```

## Patterns à Suivre

### Destructuring

```typescript
// ✅ Bon - Destructuring pour clarté
const { instrument, timeframe, format } = config;
const { from, to } = config.dates;

// ✅ Avec valeurs par défaut
const { retries = 3, timeout = 5000 } = options;
```

### Template Literals

```typescript
// ✅ Bon - Template literals pour interpolation
const url = `${URL_ROOT}/${instrument}/${year}/${month}`;
const message = `Failed to fetch data for ${instrument}`;

// ❌ Éviter - Concaténation
const url = URL_ROOT + '/' + instrument + '/' + year;
```

### Optional Chaining

```typescript
// ✅ Bon - Safe navigation
const volume = data?.candles?.[0]?.volume ?? 0;
const name = config.instrument?.metadata?.name;

// ❌ Éviter - Vérifications manuelles
const volume = data && data.candles && data.candles[0] 
  ? data.candles[0].volume 
  : 0;
```

### Array Methods

```typescript
// ✅ Bon - Méthodes fonctionnelles
const prices = candles.map(c => c.close);
const highPrices = candles.filter(c => c.high > threshold);
const total = prices.reduce((sum, price) => sum + price, 0);

// ✅ Bon - Early return
const validCandles = candles.filter(c => {
  if (!c.timestamp) return false;
  if (c.high < c.low) return false;
  return true;
});
```

## Anti-Patterns à Éviter

```typescript
// ❌ Magic numbers
if (data.length > 100) { /* ... */ }

// ✅ Constantes nommées
const MAX_DATA_POINTS = 100;
if (data.length > MAX_DATA_POINTS) { /* ... */ }

// ❌ Nested ternaries
const result = a ? b ? c : d : e;

// ✅ If/else ou fonction
const result = getResult(a, b, c, d, e);

// ❌ Mutation d'objets
config.instrument = 'btcusd';

// ✅ Immutabilité
const newConfig = { ...config, instrument: 'btcusd' };
```
