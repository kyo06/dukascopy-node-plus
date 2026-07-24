# User Stories — v001

> **Statut de la spec :** validated
> Date de création : 2026-07-24
> Dernière mise à jour : 2026-07-24

## 1. Contexte & objectif

`dukascopy-node-plus` is a fork of `Leo4815162342/dukascopy-node`, created to add a streaming API (`getHistoricalRatesToStream`) and an instrument-metadata exposition API (`instrumentMetaData` export) that upstream lacked. The fork's maintainer wants to check for commit discrepancy against upstream and pull in anything useful.

Investigation (`git fetch upstream` + `git log master..upstream/master`) found upstream is only 3 commits ahead of the fork's merge-base, and 2 of those are version-bump releases. The 3rd, `a567c90 feat: engine rewrite via json api (#257)`, is a full architecture rewrite: it replaces the bi5-download + LZMA-decompress engine with a JSON API, deletes all `.bi5` mock fixtures (194 files changed, -1.28M lines net), and rewrites large parts of `config/instruments-metadata`. The fork's stream API and instrument-metadata API are both built directly on the bi5/LZMA pipeline (`buffer-fetcher` → `decompressor` → `data-normaliser`) upstream just deleted.

Decision (confirmed with maintainer): the fork does **not** adopt the JSON-API rewrite — re-porting the stream API and instrument-metadata API onto a new engine is out of scope for a "sync". Instead this spec covers verifying there's nothing else worth pulling from upstream, and formally documenting why the fork diverges here so a future session doesn't re-litigate this or accidentally merge the rewrite commit.

## 2. Périmètre

**Inclus dans cette version :**
- Confirm upstream `master` has no other unmerged commits worth pulling besides the engine-rewrite commit and its two release bumps.
- Document the fork's intentional divergence point (commit `a567c90` / upstream 1.47.0+) and why it's not being merged.
- Record the fork's two deliberate additions (stream API, instrument-metadata API) and the modules they depend on, so a future re-evaluation of the JSON-API rewrite knows what would need re-porting.
- Keep the `upstream` git remote already added (`https://github.com/Leo4815162342/dukascopy-node.git`) for future re-checks.

**Explicitement exclu (hors périmètre) :**
- Porting/adapting the JSON-API engine rewrite into the fork.
- Any cherry-pick or merge of upstream commits into `master` (none were found worth merging).
- Changing the fork's package name, branding, or repo metadata.

## 3. Fonctionnalités métier

### US-001 — Vérifier l'absence de commits upstream à récupérer

**En tant que** mainteneur du fork
**Je veux** comparer l'historique de `master` avec `upstream/master`
**Afin de** m'assurer que je ne rate aucun correctif ou amélioration utile avant de décider explicitement d'ignorer le reste

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Aucun commit utile en dehors du rewrite
  Étant donné le remote "upstream" pointant vers Leo4815162342/dukascopy-node
  Quand on liste "git log master..upstream/master"
  Alors la liste ne contient que a567c90 (engine rewrite) et ses deux commits de release (1.47.0, 1.49.0)
  Et aucun commit de correctif isolé n'est identifié comme mergeable indépendamment du rewrite
```

**Priorité :** Must have
**Complexité estimée :** XS
**Dépendances :** aucune

### US-002 — Documenter la divergence intentionnelle

**En tant que** mainteneur du fork (ou tout agent IA travaillant sur ce repo plus tard)
**Je veux** trouver une trace écrite expliquant pourquoi le fork n'a pas suivi le rewrite JSON-API d'upstream
**Afin de** ne pas re-enquêter sur le même sujet à chaque session, et de ne pas fusionner accidentellement `a567c90`

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : Lecture de la divergence documentée
  Étant donné specs/v001/user-stories.md validée
  Quand un agent IA ou le mainteneur consulte la section "Spécifications techniques"
  Alors il trouve le commit de divergence (a567c90), la raison (rewrite incompatible avec le pipeline bi5/LZMA dont dépendent stream API et instrument-metadata API), et les modules concernés
```

**Priorité :** Must have
**Complexité estimée :** XS
**Dépendances :** US-001

## 4. Spécifications techniques

### 4.1 Architecture / composants impactés

Aucun changement de code. Documentation uniquement. Modules du fork qui dépendent du pipeline bi5/LZMA qu'upstream a supprimé (donc qui bloquent une adoption du rewrite sans réécriture) :
- `src/buffer-fetcher/` — fetch HTTP des buffers `.bi5`
- `src/decompressor/` — décompression LZMA (`lzma-purejs-requirejs`, `python-struct`)
- `src/data-normaliser/` — normalisation des données décompressées
- `src/getHistoricalRatesToStream.ts` — API stream, construite sur `processData` (voir `src/processor/index.ts`) qui orchestre les modules ci-dessus
- `src/config/instruments-metadata.ts` + `instrumentMetaData` export (`src/index.ts`) — API d'exposition des métadonnées d'instruments

### 4.2 Modèle de données
Aucun changement.

### 4.3 API / contrats d'interface
Aucun changement d'API. Le point de divergence upstream (commit `a567c90`, tags upstream 1.47.0 → 1.49.0) est documenté mais non appliqué.

### 4.4 Contraintes non-fonctionnelles
- **Performance :** sans objet.
- **Sécurité :** sans objet.
- **Accessibilité :** sans objet.
- **Compatibilité / rétrocompatibilité :** le fork continue de fonctionner sur le pipeline bi5/LZMA existant ; aucune régression possible puisqu'aucun code ne change.
- **Observabilité :** sans objet.

### 4.5 Risques & points ouverts
| Risque / question ouverte | Impact | Mitigation / décision |
|---|---|---|
| Dukascopy pourrait un jour désactiver l'ancien endpoint bi5 au profit du JSON API | Le fork casserait sans avertissement | Non traité dans cette version — TODO: à confirmer si un monitoring de disponibilité de l'ancien endpoint est souhaité |
| Le rewrite upstream pourrait contenir des correctifs de bugs "cachés" dans le diff massif (ex. dans `range.ts`) | Le fork pourrait manquer un fix ponctuel noyé dans le rewrite | Non investigué en détail (194 fichiers) — TODO: à confirmer si une revue fine du diff de `src/utils/range.ts` est souhaitée dans une version future |
| Adopter le rewrite plus tard nécessiterait de re-porter stream API + instrument-metadata API from scratch | Effort important si décidé plus tard | Décision explicite du mainteneur de ne pas le faire maintenant ; à réévaluer en nouvelle version (v002+) si le besoin change |

**Précisions apportées après relecture croisée (2026-07-24) :**
- Le merge-base du fork (`5d1b3f1`) correspond à `v1.46.4-1-g5d1b3f1` côté upstream — le fork contient donc déjà tout l'historique upstream jusqu'à 1.46.4. L'écart réel depuis la divergence n'est **pas** un retard de 47 versions cumulées : ce sont uniquement 2 commits de version bump (1.47.0, 1.49.0) et un seul commit substantiel, `a567c90` (le rewrite JSON API). Il n'y a donc pas de dette de correctifs/fonctionnalités accumulée à rattraper en dehors de ce commit unique.
- `src/index.ts` exporte déjà `instrumentMetaData` (minuscule) **et** l'alias `InstrumentMetaData` (majuscule) — ligne 31 et ligne 52. Aucun problème d'export côté fork lui-même ; un souci d'import ne peut survenir que si une application consommatrice pointe directement sur le package upstream au lieu de ce fork.
- Conclusion : rebaser sur `a567c90` ne rattraperait aucun correctif manqué (il n'y en a pas), le seul enjeu est d'adopter ou non le nouveau moteur JSON API — et ce n'est pas un "patch trivial à réappliquer" : `getHistoricalRatesToStream` et `instrumentMetaData` devraient être ré-implémentés sur un mécanisme de fetch totalement différent (JSON API au lieu de bi5/LZMA), pas juste rejoués par-dessus un diff. Réévaluer via une future v002 si un bénéfice concret du moteur JSON (fiabilité, perf) est identifié.

## 5. Definition of Done
- [x] `git log master..upstream/master` revu intégralement (fait — voir US-001)
- [x] Divergence documentée dans cette spec (fait — voir section 4.1 et 4.5)
- [x] Aucune modification de code nécessaire pour cette version
- [x] Statut de la spec passé à `validated` après confirmation du mainteneur
- [x] Pas de régression connue
