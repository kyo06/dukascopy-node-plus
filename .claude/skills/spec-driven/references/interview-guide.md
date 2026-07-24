# Guide d'interview pour la création d'une spec

Objectif : cerner le besoin avant d'écrire `user-stories.md`. Ne jamais générer une spec directement à partir d'une demande courte et ambiguë — poser des questions ciblées d'abord, par lots de 2-4 questions maximum, pas 15 d'un coup.

## 1. Cadrage métier (à faire en premier)
- Quel problème utilisateur/métier cette fonctionnalité résout-elle ?
- Qui sont les utilisateurs/personas concernés ?
- Quel est le "happy path" principal, en une phrase ?
- Quelles sont les limites explicites (ce qui N'EST PAS dans le périmètre) ?
- Existe-t-il une fonctionnalité similaire existante dont il faut respecter les patterns ?

## 2. Critères d'acceptation (méthode INVEST)
Pour chaque fonctionnalité identifiée, vérifier qu'elle est :
- **I**ndépendante — peu de dépendances dures avec d'autres US
- **N**égociable — pas un contrat figé, discutable
- **V**alorisable — apporte une valeur claire à l'utilisateur
- **E**stimable — l'équipe peut estimer l'effort
- **S**mall — assez petite pour un sprint/une itération
- **T**estable — critères d'acceptation vérifiables (Gherkin recommandé)

Questions à poser :
- Comment sait-on que c'est "fini" et que ça marche ? (cas nominal + cas d'erreur)
- Quels sont les cas limites (edge cases) auxquels il faut penser ?
- Y a-t-il des règles de validation/business rules spécifiques ?

## 3. Spécifications techniques
- Y a-t-il des contraintes d'architecture existantes à respecter (stack, patterns, conventions du repo) ?
- Nouvelles entités/tables/champs nécessaires ? Migrations de données existantes à prévoir ?
- Nouveaux endpoints API ou modification de contrats existants (breaking change) ?
- Contraintes de performance (volumétrie, latence attendue) ?
- Contraintes de sécurité (auth, permissions, données sensibles, RGPD) ?
- Compatibilité ascendante requise ? Feature flag nécessaire ?
- Comment sera-ce observable en prod (logs, métriques, alerting) ?

## 4. Priorisation
- Si plusieurs fonctionnalités : lesquelles sont Must have vs Should/Could have (MoSCoW) ?
- Y a-t-il une contrainte de délai/date ?
- Y a-t-il des dépendances entre fonctionnalités qui imposent un ordre ?

## 5. Points ouverts
- Reste-t-il des décisions produit non tranchées ? Les lister explicitement dans la section "Risques & points ouverts" plutôt que de les deviner.
- Ne jamais inventer une règle métier non mentionnée : si une info manque et bloque réellement la rédaction, la marquer `TODO: à confirmer` plutôt que de supposer.

## Format des questions
Utiliser des questions fermées ou à choix quand c'est possible (plus rapide à répondre), garder les questions ouvertes pour le cadrage métier initial. Regrouper par thème, ne pas mélanger métier et technique dans la même salve.

## Anti-patterns à éviter
- Générer des US génériques ("En tant qu'utilisateur je veux utiliser le système") sans lien avec le besoin réel exprimé.
- Écrire des critères d'acceptation non testables ("le système doit être rapide" au lieu de "temps de réponse < 200ms p95").
- Oublier la section technique en ne listant que le métier (ou l'inverse).
- Valider une spec sans relire les points ouverts avec l'utilisateur.
