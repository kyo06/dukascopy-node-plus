# User Stories — v003

> **Statut de la spec :** draft
> Date de création : 2026-07-24
> Dernière mise à jour : 2026-07-24

## 1. Contexte & objectif

Suite à l'adoption du moteur JSON API upstream (v002), une revue a identifié plusieurs améliorations non bloquantes : hygiène git, dette de dépendances, robustesse de `gen:meta` face au rate-limit Dukascopy, un edge case potentiellement non testé dans `data-normaliser`, et un manque de traçabilité entre les décisions contradictoires de v001/v002. Cette spec regroupe ces points pour les traiter (ou les écarter explicitement) sans qu'ils se perdent.

## 2. Périmètre

**Inclus dans cette version :**
- Décider et éventuellement exécuter un rebase interactif pour séparer le commit `eeff88b` (mélange rewrite + fichiers hors-sujet).
- Ajouter une note dans `specs/CHANGELOG.md` expliquant le renversement de décision v001 → v002.
- Robustifier `gen:meta` (throttle/backoff) face au rate-limit 429 de l'API Dukascopy.
- Vérifier/ajouter un test pour `getPriceScale` (`src/data-normaliser/index.ts`) sur des `multiplier` en notation scientifique.
- Vérifier la couverture de test du comportement rate-limit/retry du `buffer-fetcher` sur le nouveau moteur JSON.
- Évaluer la migration de `standard-version` (deprecated) vers une alternative maintenue.
- Évaluer le bump `eslint`/`@typescript-eslint` vers une version plus récente que 9.39.5/8.46.2 quand compatible.

**Explicitement exclu (hors périmètre) :**
- Toute réécriture d'historique sur des commits déjà pushés vers un remote partagé (rien n'a été pushé à ce jour, donc rebase local reste possible, mais à confirmer avant action).
- Changement de moteur de données (le moteur JSON API de v002 reste acquis).

## 3. Fonctionnalités métier

### US-001 — Nettoyer l'historique du commit de migration

**En tant que** mainteneur du fork
**Je veux** que le commit de migration JSON API ne mélange pas des fichiers sans rapport
**Afin de** garder un historique git lisible et un `git bisect` fiable

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Décision documentée ou rebase effectué
  Étant donné le commit eeff88b (cherry-pick a567c90 + fichiers hors-sujet)
  Quand le mainteneur est consulté
  Alors soit un rebase interactif sépare le commit en parties cohérentes
  Soit la décision de ne pas réécrire l'historique est documentée avec la raison
```

**Priorité :** Could have
**Complexité estimée :** S
**Dépendances :** aucune

### US-002 — Tracer le renversement de décision v001 → v002

**En tant qu'** agent IA ou mainteneur relisant les specs plus tard
**Je veux** comprendre pourquoi v001 ("pas de bénéfice JSON identifié") a été suivie d'une v002 qui adopte le moteur JSON
**Afin de** ne pas percevoir cela comme une incohérence non expliquée

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Changelog explicite
  Étant donné specs/CHANGELOG.md
  Quand on consulte l'entrée v002
  Alors une ligne indique explicitement que le mainteneur est revenu sur la décision de v001, sans nouvelle analyse de bénéfice, par choix direct
```

**Priorité :** Should have
**Complexité estimée :** XS
**Dépendances :** aucune

### US-003 — Robustifier `gen:meta` face au rate-limit Dukascopy

**En tant que** mainteneur du fork
**Je veux** que `gen:meta` gère le rate-limit (429) de l'API Dukascopy sans échouer immédiatement
**Afin de** pouvoir régénérer `instruments-metadata.ts` en une seule exécution fiable

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Retry avec backoff sur 429
  Étant donné generate-data.ts qui interroge 1499 instruments séquentiellement
  Quand l'API répond 429 pour un instrument
  Alors le script attend (backoff) et retente au lieu d'abandonner immédiatement
  Et un throttle (délai minimal entre requêtes) limite la fréquence globale des appels
```

**Priorité :** Should have
**Complexité estimée :** M
**Dépendances :** aucune

### US-004 — Couvrir l'edge case `getPriceScale` (notation scientifique)

**En tant que** mainteneur du fork
**Je veux** un test unitaire sur `getPriceScale` avec un `multiplier` en notation scientifique (ex. `1e-5`)
**Afin de** garantir que le parsing string ne casse pas silencieusement sur ce format

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Multiplier en notation scientifique
  Étant donné getPriceScale(1e-5)
  Quand la fonction est appelée
  Alors elle retourne le scale attendu (5) sans lever d'exception
```

**Priorité :** Should have
**Complexité estimée :** XS
**Dépendances :** aucune

### US-005 — Vérifier la couverture retry/rate-limit du `buffer-fetcher`

**En tant que** mainteneur du fork
**Je veux** confirmer que le nouveau moteur JSON API a bien des tests sur le comportement retry/rate-limit HTTP
**Afin de** ne pas avoir perdu la couverture qu'avait l'ancien pipeline bi5

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Couverture confirmée ou comblée
  Étant donné src/buffer-fetcher/
  Quand on liste ses tests existants
  Alors soit un test retry/429 existe déjà et est identifié
  Soit un test est ajouté pour couvrir ce cas
```

**Priorité :** Should have
**Complexité estimée :** S
**Dépendances :** aucune

### US-006 — Évaluer dépendances vieillissantes/deprecated

**En tant que** mainteneur du fork
**Je veux** évaluer le remplacement de `standard-version` (deprecated) et le bump `eslint`/`@typescript-eslint`
**Afin de** limiter la dette technique sur l'outillage de release et de lint

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Décision consignée
  Étant donné standard-version deprecated et eslint 9.39.5 (10.7.0 disponible)
  Quand une évaluation est faite
  Alors une décision (migrer maintenant / reporter / ne pas migrer) est consignée avec la raison
```

**Priorité :** Could have
**Complexité estimée :** M
**Dépendances :** aucune

## 4. Spécifications techniques

### 4.1 Architecture / composants impactés
- `src/utils/instrument-meta-data/generate-data.ts` (US-003)
- `src/data-normaliser/index.ts` + ses tests (US-004)
- `src/buffer-fetcher/` + ses tests (US-005)
- `package.json` (devDependencies, script `release`) (US-006)
- `specs/CHANGELOG.md` (US-002)
- Historique git (US-001, hors code)

### 4.2 Modèle de données
Aucun changement.

### 4.3 API / contrats d'interface
Aucun changement d'API publique attendu.

### 4.4 Contraintes non-fonctionnelles
- **Performance :** `gen:meta` avec throttle sera plus lent en exécution totale mais plus fiable (US-003) — compromis à accepter.
- **Sécurité :** sans objet.
- **Compatibilité / rétrocompatibilité :** tout bump de dépendance (US-006) doit repasser par `bun run test`/`type-check`/`lint`/`build` avant validation.
- **Observabilité :** logs `debug` existants suffisent, pas de nouvel outil de monitoring prévu.

### 4.5 Risques & points ouverts
| Risque / question ouverte | Impact | Mitigation / décision |
|---|---|---|
| Rebase de `eeff88b` (US-001) modifie des SHA déjà mergés dans `master` local | Réécriture d'historique, à ne pas faire sans confirmation explicite | Ne pas exécuter sans accord direct du mainteneur ; rien n'a été pushé donc réversible localement |
| Throttle `gen:meta` (US-003) peut rendre le script très long (1499 instruments) | Temps d'exécution en forte hausse | Accepté comme compromis ; envisager un mode incrémental (ne refetch que les instruments manquants/périmés) si trop lent |
| Bump `eslint`/`@typescript-eslint` (US-006) peut introduire de nouvelles règles bloquantes | `bun run lint` pourrait casser après bump | Tester en isolation avant de committer, revenir en arrière si trop de faux positifs |

## 5. Definition of Done
- [ ] US-001 : décision consignée (rebase fait ou explicitement refusé avec raison)
- [ ] US-002 : `specs/CHANGELOG.md` mis à jour avec l'explication du renversement v001→v002
- [ ] US-003 : `gen:meta` gère le 429 (backoff/throttle), testé sur un sous-ensemble d'instruments
- [ ] US-004 : test `getPriceScale` notation scientifique ajouté et vert
- [ ] US-005 : couverture retry/rate-limit `buffer-fetcher` confirmée ou comblée
- [ ] US-006 : décision consignée sur `standard-version`/`eslint`/`@typescript-eslint`
- [ ] Aucune régression (`bun run test`/`type-check`/`lint`/`build` verts)
