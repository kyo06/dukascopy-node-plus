# User Stories — v002

> **Statut de la spec :** draft
> <!-- Valeurs valides : draft | validated | in-progress | done — ne jamais laisser plusieurs valeurs sur cette ligne, un outil de synchro la parse. -->
> Date de création : 2026-07-24
> Dernière mise à jour : 2026-07-24

## 1. Contexte & objectif

<!-- 2-4 phrases : quel problème métier résout cette spec ? Pour qui ? Pourquoi maintenant ? -->

## 2. Périmètre

**Inclus dans cette version :**
- ...

**Explicitement exclu (hors périmètre) :**
- ...

## 3. Fonctionnalités métier

### US-001 — {{Titre court}}

**En tant que** {{rôle/persona}}
**Je veux** {{action}}
**Afin de** {{bénéfice/valeur}}

**Critères d'acceptation (Gherkin) :**
```gherkin
Scénario : {{nom du scénario}}
  Étant donné {{contexte}}
  Quand {{action}}
  Alors {{résultat attendu}}
```

**Priorité :** Must have | Should have | Could have | Won't have (MoSCoW)
**Complexité estimée :** XS | S | M | L | XL
**Dépendances :** {{US-XXX ou "aucune"}}

<!-- Dupliquer ce bloc US-00X pour chaque fonctionnalité métier -->

## 4. Spécifications techniques

### 4.1 Architecture / composants impactés
- ...

### 4.2 Modèle de données
<!-- Nouvelles entités, champs, migrations nécessaires -->
- ...

### 4.3 API / contrats d'interface
<!-- Endpoints, schémas de requête/réponse, événements -->
- ...

### 4.4 Contraintes non-fonctionnelles
- **Performance :** ...
- **Sécurité :** ...
- **Accessibilité :** ...
- **Compatibilité / rétrocompatibilité :** ...
- **Observabilité (logs, métriques, alerting) :** ...

### 4.5 Risques & points ouverts
| Risque / question ouverte | Impact | Mitigation / décision |
|---|---|---|
| ... | ... | ... |

## 5. Definition of Done
- [ ] Code revu et mergé
- [ ] Tests unitaires/intégration écrits et verts
- [ ] Documentation mise à jour
- [ ] Critères d'acceptation validés (US concernées)
- [ ] Pas de régression connue
