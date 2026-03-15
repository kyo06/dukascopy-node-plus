---
name: Testing Guidelines
description: Guide pour écrire et organiser les tests avec Vitest
tags: [testing, vitest, quality]
---

# Testing Guidelines

## Structure des Tests

### Organisation

```
src/module-name/
├── index.ts
├── types.ts
├── module-name.test.ts          # Tests unitaires simples
└── tests/
    ├── module-name.test.ts      # Tests complexes
    ├── cases/                   # Cas de test réutilisables
    │   ├── case1.ts
    │   └── case2.ts
    └── fixtures/                # Données de test
        ├── sample_data.json
        └── expected_output.json
```

### Nommage des Fichiers

- Tests unitaires : `*.test.ts`
- Données de test : `sample_*.json` ou `*_fixture.json`
- Cas de test : noms descriptifs (`m1_to_h1.ts`, `tick_with_gaps.ts`)

## Écriture des Tests

### Structure de Base

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { functionToTest } from './index';

describe('ModuleName', () => {
  describe('functionToTest', () => {
    it('should handle valid input correctly', () => {
      const input = { /* ... */ };
      const result = functionToTest(input);
      
      expect(result).toBeDefined();
      expect(result.value).toBe(expected);
    });

    it('should throw error for invalid input', () => {
      const invalidInput = { /* ... */ };
      
      expect(() => functionToTest(invalidInput))
        .toThrow('Expected error message');
    });
  });
});
```

### Tests Asynchrones

```typescript
describe('async operations', () => {
  it('should fetch and process data', async () => {
    const result = await getHistoricalRates(config);
    
    expect(result).toBeDefined();
    expect(result.length).toBeGreaterThan(0);
  });

  it('should handle fetch errors', async () => {
    await expect(getHistoricalRates(invalidConfig))
      .rejects
      .toThrow('Validation failed');
  });
});
```

### Cas de Test Réutilisables

```typescript
// tests/cases/m1_to_h1.ts
export const m1ToH1TestCase = {
  description: 'Aggregate M1 data to H1 timeframe',
  input: [
    { timestamp: 1234567800000, open: 1.1, high: 1.2, low: 1.0, close: 1.15 },
    // ... more data
  ],
  expected: [
    { timestamp: 1234567800000, open: 1.1, high: 1.25, low: 1.0, close: 1.2 }
  ],
  config: {
    timeframe: 'h1',
    ignoreFlats: false
  }
};

// tests/aggregator.test.ts
import { m1ToH1TestCase } from './cases/m1_to_h1';

describe('Aggregator', () => {
  it(m1ToH1TestCase.description, () => {
    const result = aggregate(m1ToH1TestCase.input, m1ToH1TestCase.config);
    expect(result).toEqual(m1ToH1TestCase.expected);
  });
});
```

## Bonnes Pratiques

### 1. Tests Isolés

```typescript
// ✅ Bon - Chaque test est indépendant
describe('CacheManager', () => {
  let cacheManager: CacheManager;

  beforeEach(() => {
    cacheManager = new CacheManager({ folder: './test-cache' });
  });

  afterEach(async () => {
    await cacheManager.clear();
  });

  it('should store data', async () => {
    await cacheManager.set('key', data);
    const result = await cacheManager.get('key');
    expect(result).toEqual(data);
  });
});
```

### 2. Assertions Claires

```typescript
// ✅ Bon - Assertions spécifiques
expect(result).toHaveLength(10);
expect(result[0]).toMatchObject({
  timestamp: expect.any(Number),
  open: expect.any(Number)
});

// ❌ Éviter - Assertions trop générales
expect(result).toBeTruthy();
```

### 3. Mocking

```typescript
import { vi } from 'vitest';

describe('BufferFetcher', () => {
  it('should retry on failure', async () => {
    const mockFetch = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ buffer: () => Buffer.from('data') });

    global.fetch = mockFetch;

    const fetcher = new BufferFetcher({ retries: 2 });
    const result = await fetcher.fetch('http://example.com');

    expect(mockFetch).toHaveBeenCalledTimes(2);
    expect(result).toBeDefined();
  });
});
```

### 4. Tests de Validation

```typescript
describe('Config Validation', () => {
  it('should reject invalid instrument', () => {
    const config = {
      instrument: 'invalid',
      dates: { from: new Date(), to: new Date() }
    };

    const result = validateConfig(config);

    expect(result.isValid).toBe(false);
    expect(result.errors).toContainEqual(
      expect.objectContaining({
        field: 'instrument',
        message: expect.stringContaining('not supported')
      })
    );
  });
});
```

### 5. Tests de Snapshot (avec précaution)

```typescript
// Utiliser uniquement pour des structures stables
it('should generate correct URL structure', () => {
  const urls = generateUrls(config);
  expect(urls).toMatchSnapshot();
});
```

## Couverture de Code

### Objectifs

- Viser 80%+ de couverture pour les modules critiques
- 100% pour les validateurs et transformateurs de données
- Tester les cas limites et erreurs

### Exécution

```bash
# Tests avec couverture
npm run coverage

# Tests en mode watch (développement)
npm run test -- --watch

# Tests d'un fichier spécifique
npm run test -- buffer-fetcher.test.ts
```

## Données de Test

### Fixtures JSON

```typescript
// tests/sample_m1_data.json
[
  {
    "timestamp": 1234567800000,
    "open": 1.1234,
    "high": 1.1250,
    "low": 1.1200,
    "close": 1.1240,
    "volume": 1000
  }
]

// Utilisation
import sampleData from './tests/sample_m1_data.json';

it('should process sample data', () => {
  const result = processData(sampleData);
  expect(result).toBeDefined();
});
```

## Anti-Patterns à Éviter

```typescript
// ❌ Tests dépendants de l'ordre
it('should add item', () => { cache.add('key', 'value'); });
it('should retrieve item', () => { expect(cache.get('key')).toBe('value'); });

// ❌ Tests trop longs
it('should do everything', () => {
  // 100 lignes de test...
});

// ❌ Assertions multiples non liées
it('should work', () => {
  expect(a).toBe(1);
  expect(b).toBe(2);
  expect(c).toBe(3); // Si c échoue, on ne sait pas pourquoi
});

// ✅ Séparer en tests distincts
it('should set a correctly', () => expect(a).toBe(1));
it('should set b correctly', () => expect(b).toBe(2));
it('should set c correctly', () => expect(c).toBe(3));
```
