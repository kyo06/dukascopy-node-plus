---
name: Error Handling
description: Stratégies de gestion des erreurs et logging
tags: [errors, debugging, logging]
---

# Error Handling

## Hiérarchie des Erreurs

### Erreurs Personnalisées

```typescript
// Base error class
export class DukascopyError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'DukascopyError';
  }
}

// Erreurs spécifiques
export class ConfigValidationError extends DukascopyError {
  constructor(
    message: string,
    public readonly errors: ValidationError[]
  ) {
    super(message, 'CONFIG_VALIDATION_ERROR');
    this.name = 'ConfigValidationError';
  }
}

export class FetchError extends DukascopyError {
  constructor(
    message: string,
    public readonly url: string,
    public readonly statusCode?: number
  ) {
    super(message, 'FETCH_ERROR');
    this.name = 'FetchError';
  }
}
```

export class DecompressionError extends DukascopyError {
  constructor(message: string, cause?: Error) {
    super(message, 'DECOMPRESSION_ERROR', cause);
    this.name = 'DecompressionError';
  }
}
```

## Gestion des Erreurs Async

### Try-Catch avec Contexte

```typescript
export async function getHistoricalRates(config: Config): Promise<Output> {
  try {
    // Validation
    const validated = validateConfig(config);
    if (!validated.isValid) {
      throw new ConfigValidationError(
        'Invalid configuration',
        validated.errors
      );
    }

    // Processing
    return await processData(validated.config);
  } catch (error) {
    // Enrichir l'erreur avec contexte
    if (error instanceof ConfigValidationError) {
      throw error; // Déjà bien formatée
    }
    
    throw new DukascopyError(
      `Failed to get historical rates for ${config.instrument}`,
      'PROCESSING_ERROR',
      error as Error
    );
  }
}
```

### Retry Logic

```typescript
export async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const { maxRetries = 3, delay = 1000, backoff = 2 } = options;
  
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      
      if (attempt < maxRetries) {
        const waitTime = delay * Math.pow(backoff, attempt);
        await sleep(waitTime);
      }
    }
  }
  
  throw new DukascopyError(
    `Failed after ${maxRetries} retries`,
    'MAX_RETRIES_EXCEEDED',
    lastError!
  );
}
```

## Logging et Debugging

### Module Debug

```typescript
import debug from 'debug';

// Créer des loggers par module
const log = debug('dukascopy:buffer-fetcher');
const logError = debug('dukascopy:buffer-fetcher:error');

export class BufferFetcher {
  async fetch(url: string): Promise<Buffer> {
    log('Fetching %s', url);
    
    try {
      const response = await fetch(url);
      log('Response status: %d', response.status);
      
      if (!response.ok) {
        logError('Failed to fetch %s: %d', url, response.status);
        throw new FetchError('HTTP error', url, response.status);
      }
      
      const buffer = await response.buffer();
      log('Received %d bytes', buffer.length);
      
      return buffer;
    } catch (error) {
      logError('Error fetching %s: %O', url, error);
      throw error;
    }
  }
}

// Activation: DEBUG=dukascopy:* node script.js
```

### Niveaux de Log

```typescript
export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3
}

export class Logger {
  constructor(
    private readonly namespace: string,
    private readonly level: LogLevel = LogLevel.INFO
  ) {}

  error(message: string, ...args: unknown[]): void {
    if (this.level >= LogLevel.ERROR) {
      console.error(`[${this.namespace}] ERROR:`, message, ...args);
    }
  }

  warn(message: string, ...args: unknown[]): void {
    if (this.level >= LogLevel.WARN) {
      console.warn(`[${this.namespace}] WARN:`, message, ...args);
    }
  }

  info(message: string, ...args: unknown[]): void {
    if (this.level >= LogLevel.INFO) {
      console.info(`[${this.namespace}] INFO:`, message, ...args);
    }
  }

  debug(message: string, ...args: unknown[]): void {
    if (this.level >= LogLevel.DEBUG) {
      console.debug(`[${this.namespace}] DEBUG:`, message, ...args);
    }
  }
}
```

## Validation et Messages d'Erreur

### Messages Clairs et Actionnables

```typescript
// ✅ Bon - Message descriptif avec solution
throw new ConfigValidationError(
  'Invalid instrument "btcusx". Did you mean "btcusd"? ' +
  'See supported instruments at https://www.dukascopy-node.app/instruments'
);

// ❌ Éviter - Message vague
throw new Error('Invalid config');
```

### Agrégation des Erreurs de Validation

```typescript
export interface ValidationError {
  field: string;
  message: string;
  value?: unknown;
}

export function validateConfig(config: unknown): ValidationResult {
  const errors: ValidationError[] = [];

  if (!config || typeof config !== 'object') {
    errors.push({
      field: 'config',
      message: 'Configuration must be an object'
    });
    return { isValid: false, errors };
  }

  // Valider chaque champ
  if (!('instrument' in config)) {
    errors.push({
      field: 'instrument',
      message: 'Instrument is required'
    });
  }

  // Retourner toutes les erreurs en une fois
  return {
    isValid: errors.length === 0,
    errors
  };
}
```

## Bonnes Pratiques

1. **Créer des erreurs spécifiques par domaine**
2. **Inclure le contexte (URL, config, etc.)**
3. **Utiliser le module debug pour le développement**
4. **Messages d'erreur clairs et actionnables**
5. **Retry logic pour les erreurs réseau**
6. **Logger avant de throw**
7. **Ne pas catcher sans raison**
8. **Propager les erreurs avec contexte additionnel**
