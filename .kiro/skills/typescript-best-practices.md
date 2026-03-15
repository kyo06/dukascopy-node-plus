---
name: TypeScript Best Practices
description: Bonnes pratiques TypeScript pour dukascopy-node-plus
tags: [typescript, code-quality]
---

# TypeScript Best Practices

## Configuration Stricte

Le projet utilise TypeScript en mode strict. Toujours respecter :

```typescript
// ✅ Bon - Types explicites pour les paramètres publics
export function processData(config: Config): Promise<Output> {
  // ...
}

// ❌ Éviter - Types implicites any
export function processData(config) {
  // ...
}
```

## Gestion des Types

### Exports de Types

- Définir les types dans `types.ts` pour les modules complexes
- Exporter tous les types publics depuis `index.ts`
- Utiliser des interfaces pour les objets de configuration

```typescript
// types.ts
export interface BufferFetcherConfig {
  url: string;
  retries?: number;
  timeout?: number;
}

// index.ts
export { BufferFetcherConfig } from './types';
```

### Types vs Interfaces

- **Interfaces** pour les configurations et contrats publics
- **Types** pour les unions, intersections, et utilitaires

```typescript
// ✅ Interface pour configuration
export interface Config {
  instrument: Instrument;
  dates: DateRange;
}

// ✅ Type pour unions
export type Format = 'json' | 'csv' | 'array';
export type Output = JsonOutput | CsvOutput | ArrayOutput;
```

## Gestion des Erreurs

```typescript
// ✅ Bon - Erreurs typées et descriptives
export class ConfigValidationError extends Error {
  constructor(
    message: string,
    public readonly errors: ValidationError[]
  ) {
    super(message);
    this.name = 'ConfigValidationError';
  }
}

// Utilisation
try {
  const data = await getHistoricalRates(config);
} catch (error) {
  if (error instanceof ConfigValidationError) {
    console.error('Validation failed:', error.errors);
  }
  throw error;
}
```

## Async/Await

- Toujours utiliser async/await plutôt que les Promises chaînées
- Gérer les erreurs avec try/catch
- Retourner des types Promise explicites

```typescript
// ✅ Bon
export async function fetchData(url: string): Promise<Buffer> {
  try {
    const response = await fetch(url);
    return await response.buffer();
  } catch (error) {
    throw new FetchError(`Failed to fetch ${url}`, error);
  }
}
```

## Null Safety

```typescript
// ✅ Utiliser optional chaining et nullish coalescing
const volume = data?.volume ?? 0;
const timeout = config.timeout ?? 5000;

// ✅ Type guards pour narrowing
function isTickData(data: unknown): data is TickData {
  return typeof data === 'object' && data !== null && 'timestamp' in data;
}
```

## Imports/Exports

```typescript
// ✅ Imports nommés et organisés
import { Config, Instrument } from './config';
import { validateConfig } from './config-validator';
import { processData } from './processor';

// ✅ Exports nommés (pas de default exports)
export { getHistoricalRates };
export { getRealTimeRates };
```

## Conventions de Nommage

- **Interfaces/Types**: PascalCase (`ConfigArrayItem`)
- **Fonctions/Variables**: camelCase (`getHistoricalRates`)
- **Constantes**: UPPER_SNAKE_CASE (`URL_ROOT`)
- **Fichiers**: kebab-case (`buffer-fetcher.ts`)
- **Enums**: PascalCase avec valeurs en lowercase

```typescript
export enum Timeframe {
  Tick = 'tick',
  M1 = 'm1',
  H1 = 'h1',
  D1 = 'd1'
}
```
