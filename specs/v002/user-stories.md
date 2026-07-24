# User Stories — v002

> **Statut de la spec :** validated
> Date de création : 2026-07-24
> Dernière mise à jour : 2026-07-24

## 1. Contexte & objectif

v001 avait conclu (avec confirmation du mainteneur) que le fork restait sur son pipeline bi5/LZMA et n'adoptait pas le rewrite JSON API d'upstream (`a567c90`). Le mainteneur est revenu sur cette décision : il souhaite désormais adopter le moteur JSON API upstream dans le fork, tout en conservant les deux fonctionnalités qui justifient l'existence du fork (streaming API, instrument-metadata API), avec tests à jour et version bumpée à `1.2.6`.

## 2. Périmètre

**Inclus dans cette version :**
- Cherry-pick du commit upstream `a567c90` (engine rewrite JSON API) sur une branche dédiée `feat/json-api-engine`.
- Résolution des conflits (`package.json`, `src/cli/tests/cli.test.ts`) en conservant le versioning et le branding propres au fork.
- Suppression du pipeline bi5/LZMA (`src/decompressor/`, dépendances `lzma-purejs-requirejs`, `node-fetch`, `python-struct`).
- Vérification que `getHistoricalRatesToStream` (streaming API) et `instrumentMetaData`/`InstrumentMetaData` (instrument-metadata API) restent fonctionnels sur le nouveau moteur.
- Passage de la suite de tests complète (Vitest) et `type-check` au vert.
- Bump de version à `1.2.6`.
- Mise à jour de `CLAUDE.md` (architecture) pour refléter le nouveau pipeline.

**Explicitement exclu (hors périmètre) :**
- Merge de la branche `feat/json-api-engine` vers `master` (décision séparée, à confirmer).
- Régénération de `instruments-metadata.ts` via `gen:meta` (nouvelle snapshot brute présente mais non régénérée dans cette session).
- Correction du gap pré-existant `eslint` manquant en devDependency (hors scope, déjà présent sur `master` avant ce travail).
- Push vers un remote quelconque.

## 3. Fonctionnalités métier

### US-001 — Adopter le moteur JSON API upstream

**En tant que** mainteneur du fork
**Je veux** remplacer le pipeline bi5/LZMA par le moteur JSON API d'upstream
**Afin de** bénéficier du moteur maintenu par upstream sans perdre les fonctionnalités propres au fork

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Cherry-pick isolé sur branche dédiée
  Étant donné le commit upstream a567c90 (engine rewrite json api)
  Quand il est cherry-pické (no-commit) sur feat/json-api-engine
  Alors seuls package.json et src/cli/tests/cli.test.ts sont en conflit
  Et les deux sont résolus manuellement en conservant version/branding du fork
```

**Priorité :** Must have
**Complexité estimée :** L
**Dépendances :** aucune

### US-002 — Préserver streaming API et instrument-metadata API

**En tant que** consommateur du fork
**Je veux** que `getHistoricalRatesToStream` et `instrumentMetaData` continuent de fonctionner après la migration
**Afin de** ne pas casser les deux raisons d'être du fork

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Streaming toujours fonctionnel
  Étant donné le nouveau moteur JSON API
  Quand getHistoricalRatesToStream est appelé
  Alors les tests dédiés au streaming passent (10/10)

Scénario : Export instrument-metadata inchangé
  Étant donné src/index.ts
  Quand on vérifie les exports
  Alors instrumentMetaData et InstrumentMetaData sont toujours exportés
```

**Priorité :** Must have
**Complexité estimée :** M
**Dépendances :** US-001

### US-003 — Mettre à jour tests et version du package

**En tant que** mainteneur du fork
**Je veux** que la suite de tests soit adaptée au nouveau moteur et la version bumpée
**Afin de** publier une release cohérente `1.2.6`

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Suite de tests verte
  Étant donné la branche feat/json-api-engine
  Quand npm run test est exécuté
  Alors tous les tests passent (132/132)

Scénario : Version bumpée
  Étant donné package.json
  Quand on lit le champ version
  Alors il vaut 1.2.6
```

**Priorité :** Must have
**Complexité estimée :** S
**Dépendances :** US-001

## 4. Spécifications techniques

### 4.1 Architecture / composants impactés
- `src/processor/index.ts` — `decompress` remplacé par `JSON.parse(buffer.toString('utf8'))`.
- `src/buffer-fetcher/` — détection buffer vide adaptée au JSON (`times` array), gestion `isMutableDataUrl`.
- `src/data-normaliser/` — réécrit : normalisation par colonnes JSON (`DataResponse`/`CandleResponse`/`TickResponse`), décodage `multiplier`/scale, `assertColumnLengths`.
- `src/decompressor/` — supprimé entièrement.
- `src/url-generator/` — génère désormais des URLs JSON API au lieu de chemins bi5.
- `src/getHistoricalRatesToStream.ts` — inchangé (fichier propre au fork, aucun conflit au cherry-pick), compatibilité confirmée par les tests.
- `src/index.ts` — inchangé, exports `instrumentMetaData`/`InstrumentMetaData` intacts.
- `src/__mocks__/` — mocks `.bi5` binaires remplacés par `fixtures/` + `handlers.ts` (JSON, MSW).

### 4.2 Modèle de données
Nouvelles formes JSON : `DataResponse` (base), `CandleResponse` (opens/highs/lows/closes/volumes + shift), `TickResponse` (asks/bids/askVolumes/bidVolumes). Toutes en delta-encodé par rapport à une valeur de base + `multiplier` pour le prix.

### 4.3 API / contrats d'interface
Aucun changement d'API publique (`src/index.ts` inchangé). Contrat de sortie CLI JSON assoupli dans les tests (vérifie présence + `timestamp` fini, plus de comparaison byte-exacte).

### 4.4 Contraintes non-fonctionnelles
- **Performance :** non mesurée dans cette session (pas de benchmark bi5 vs JSON API).
- **Sécurité :** sans objet.
- **Compatibilité / rétrocompatibilité :** dépendances `lzma-purejs-requirejs`, `node-fetch`, `python-struct` supprimées ; aucune API publique cassée.
- **Observabilité :** logs `debug` inchangés.

### 4.5 Risques & points ouverts
| Risque / question ouverte | Impact | Mitigation / décision |
|---|---|---|
| `eslint` manquant en devDependency (pré-existant sur `master`) | `npm run lint` échoue | Non corrigé dans cette version — signalé au mainteneur, hors scope |
| `feat/json-api-engine` non mergée sur `master` | Travail non livré | Décision de merge à prendre séparément avec le mainteneur |
| `gen:meta` non relancé malgré nouvelle snapshot brute (`raw-meta-data-2026-07-13.json`) | `instruments-metadata.ts` pourrait être désynchronisé de la snapshot | À confirmer si régénération nécessaire avant merge |
| `package-lock.json` modifié par `npm install --legacy-peer-deps` | Diff lockfile non revu en détail | À vérifier avant commit/merge |

## 5. Definition of Done
- [x] Cherry-pick `a567c90` appliqué sur `feat/json-api-engine`, conflits résolus
- [x] `npm run type-check` vert
- [x] `npm run test` vert (132/132)
- [x] Version bumpée à `1.2.6`
- [x] `CLAUDE.md` mis à jour (architecture)
- [ ] Merge vers `master` (décision séparée, non faite)
- [ ] `gen:meta` relancé si nécessaire (à confirmer)
