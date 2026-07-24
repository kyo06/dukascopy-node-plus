# spec-driven — README

Skill de *spec-driven development* : elle force un agent IA à **spécifier avant de coder** (`specs/vXXX/`), à garder cette spec vivante pendant l'implémentation (`tasks.md`, `sprint_status.md`), à synchroniser le fichier d'instructions de l'outil IA utilisé sur le projet, et à persister le contexte entre sessions via un `memory-bank/`.

Ce document liste des **prompts prêts à l'emploi** (à adapter à votre besoin) pour chaque étape du workflow, avec ce qu'ils déclenchent concrètement. Il complète `SKILL.md` (qui est la référence technique lue par l'agent) — ce README est plutôt destiné à un humain qui découvre la skill.

---

## Sommaire

- [Installation](#installation)
- [Vue d'ensemble du workflow](#vue-densemble-du-workflow)
- [Prompts — Phase 1 : créer une spec](#prompts--phase-1--créer-une-spec)
- [Prompts — Phase 2 : implémenter une spec](#prompts--phase-2--implémenter-une-spec)
- [Prompts — Memory bank](#prompts--memory-bank)
- [Prompts — Gestion multi-versions / clôture](#prompts--gestion-multi-versions--clôture)
- [Prompts — Cas particuliers / dépannage](#prompts--cas-particuliers--dépannage)
- [Référence des scripts](#référence-des-scripts)
- [Outils IA supportés](#outils-ia-supportés)
- [Bonnes pratiques et anti-patterns](#bonnes-pratiques-et-anti-patterns)
- [FAQ](#faq)

---

## Installation

Placer le dossier `spec-driven/` à l'emplacement "skills projet" reconnu par votre outil :

| Outil | Emplacement du dossier skill |
|---|---|
| Claude Code | `.claude/skills/spec-driven/` |
| GitHub Copilot | `.github/skills/spec-driven/` |
| Standard ouvert (Agent Skills) | `.agents/skills/spec-driven/` |
| Générique | `skills/spec-driven/` |

La skill se déclenche automatiquement dès que sa `description` (dans le frontmatter de `SKILL.md`) correspond à la demande — inutile de l'invoquer par un nom spécial, il suffit de formuler la demande normalement (voir les prompts ci-dessous).

---

## Vue d'ensemble du workflow

```
Prompt utilisateur
        │
        ▼
 Phase 1 — Créer une spec           Phase 2 — Appliquer une spec
 ┌───────────────────────┐          ┌────────────────────────────┐
 │ 1.1 Interview          │          │ 2.1 Charger le contexte     │
 │ 1.2 Scaffolding        │  ───▶    │ 2.2 Identifier l'outil IA   │
 │ 1.3 Détection skills   │          │ 2.3 Sync fichier instructions│
 │ 1.4 Remplissage        │          │ 2.4 Implémenter tâche/tâche │
 │ 1.5 Validation         │          │ 2.5 Memory bank             │
 └───────────────────────┘          │ 2.6 Fin de version           │
                                     └────────────────────────────┘
```

La Phase 1 ne se relance jamais par-dessus une spec déjà `validated`/`in-progress` : un besoin qui change fondamentalement crée une nouvelle version (`vXXX+1`).

---

## Prompts — Phase 1 : créer une spec

### Démarrer une spec à partir d'une idée courte
> "J'aimerais ajouter un système de notifications par email quand une commande est expédiée. Peux-tu me faire une spec pour ça ?"

**Déclenche :** l'interview structurée (`references/interview-guide.md`) — cadrage métier d'abord (problème résolu, persona, happy path, hors-périmètre), puis technique (architecture, données, API, contraintes), par lots de 2 à 4 questions. Rien n'est généré tant que l'interview n'est pas jugée suffisante.

### Démarrer une spec en donnant déjà beaucoup de détails
> "Je veux spécifier l'export CSV des transactions : filtrable par date et statut, limité aux comptes Pro, colonnes date/montant/statut/id, généré en asynchrone avec notification par email une fois prêt, RGPD : anonymiser les IBAN partiels."

**Déclenche :** interview allégée — l'agent ne repose pas les questions déjà répondues, comble seulement les trous (ex. volumétrie attendue, quota de génération) en confirmant les hypothèses prises.

### Explicitement demander le vocabulaire du domaine
> "Fais du spec-driven development pour la fonctionnalité X."
> "Crée une spec pour X."
> "On fait du SDD sur ce projet, commence par spécifier X."

**Déclenche :** la skill se reconnaît directement à ces formulations (elles font partie de sa `description`).

### Répondre à l'interview avec des choix fermés
Quand l'agent pose une question de priorisation MoSCoW ou de périmètre, il utilise en général un outil de choix à boutons (`ask_user_input_v0`) plutôt que d'attendre une réponse en texte libre — répondez simplement en cliquant/sélectionnant l'option.

### Demander explicitement le découpage en tâches et la détection de skills
> "Découpe cette spec en tâches, et regarde si on a déjà des skills dans le projet qui couvrent une partie du travail."

**Déclenche :** l'étape 1.3 (`scripts/detect_skills.py`) puis le remplissage de `tasks.md`, avec la colonne "Skill(s) recommandée(s)" renseignée **uniquement** si une skill détectée correspond vraiment (jamais inventée).

### Valider une spec
> "La spec me va, tu peux la passer en validated."

**Déclenche :** l'étape 1.5 — l'agent résume les US créées, la priorisation MoSCoW, et surtout les points ouverts / `TODO: à confirmer`, avant de passer le statut d'en-tête de `user-stories.md` de `draft` à `validated`. Sans cette confirmation explicite, le statut reste `draft`.

---

## Prompts — Phase 2 : implémenter une spec

### Démarrer l'implémentation
> "Implémente la spec v003."
> "Applique v002, en commençant par les tâches de type feature."
> "On code la fonctionnalité qu'on a spécifiée tout à l'heure."

**Déclenche :** l'étape 2.1 (lecture complète de `user-stories.md` + `tasks.md` de la version visée) puis 2.2 (question sur l'outil IA du projet, sauf si déjà configuré).

### Répondre à la question "quel outil IA utilisez-vous ?"
> "On utilise Claude Code et GitHub Copilot."
> "Cursor uniquement."
> "On n'a pas de fichier d'instructions particulier, utilise juste AGENTS.md."

**Déclenche :** l'étape 2.3 — `scripts/sync_agent_docs.py --tools <clés> --create-missing`, qui insère/actualise le bloc `<!-- SPEC-DRIVEN:START -->…<!-- SPEC-DRIVEN:END -->` dans le(s) fichier(s) correspondant(s) sans toucher au reste du contenu.

### Continuer une implémentation déjà en cours
> "Reprends où on en était sur v003."
> "Qu'est-ce qu'il reste à faire sur la spec active ?"

**Déclenche :** lecture de `memory-bank/activeContext.md` en premier (c'est la mémoire de travail persistante entre sessions), puis de `sprint_status.md` pour le détail tâche par tâche. Comme un bloc `SPEC-DRIVEN:START` existe déjà, l'agent ne repose pas la question de l'outil IA.

### Marquer une tâche comme terminée / en cours / bloquée
> "La tâche T-003-002 est terminée."
> "Je bloque sur T-003-004, la dépendance à l'API externe n'est pas encore prête."
> "Démarre T-003-005."

**Déclenche :** `scripts/update_task_status.py --task T-XXX-00Y --status done|in-progress|blocked|review|todo --note "..."` — met à jour `tasks.md`, journalise la session dans `sprint_status.md`, recalcule automatiquement le pourcentage d'avancement.

### Demander un état des lieux
> "Où en est-on sur cette spec ? Combien de tâches restent ?"

**Déclenche :** lecture de `sprint_status.md` (section "Résumé" + "Avancement par fonctionnalité").

### Terminer une session de travail sans avoir tout fini
> "On s'arrête là pour aujourd'hui, sauvegarde l'avancement."

**Déclenche :** mise à jour de statut même partielle (`in-progress`/`blocked`) puis synchronisation du memory-bank (étape 2.5), pour que la prochaine session — potentiellement sans aucun contexte de conversation — reparte du bon point.

---

## Prompts — Memory bank

### Initialiser le memory bank sur un projet qui n'en a pas encore
> "Ce projet n'a pas de memory-bank, initialise-le."

**Déclenche :** `scripts/init_memory_bank.py --project-name "<nom>"` — non destructif, ne crée que les fichiers manquants parmi `projectbrief.md`, `productContext.md`, `systemPatterns.md`, `techContext.md`, `activeContext.md`, `progress.md`.

### Resynchroniser le memory bank
> "Synchronise le memory bank avec l'état actuel de la spec."

**Déclenche :** `scripts/sync_memory_bank.py --spec-dir specs/vXXX` — ne réécrit que la section `<!-- SYNC:START -->…<!-- SYNC:END -->` d'`activeContext.md` et `progress.md` ; le reste (décisions, focus manuel) n'est jamais touché automatiquement.

### Enrichir le contexte à la main
> "Note dans le memory bank qu'on a décidé d'utiliser PostgreSQL plutôt que MongoDB, et pourquoi."

**Déclenche :** édition manuelle (`str_replace`) de `memory-bank/systemPatterns.md` (section "Décisions techniques clés") — en dehors des blocs `SYNC`, donc jamais écrasée par une resynchronisation automatique.

---

## Prompts — Gestion multi-versions / clôture

### Créer une nouvelle version parce que le besoin a changé
> "En fait on veut aussi gérer les notifications SMS en plus de l'email, ça change pas mal de choses — fais une nouvelle version de la spec."

**Déclenche :** `scripts/new_spec.py` crée `v(N+1)` plutôt que de modifier rétroactivement une version déjà `validated`/`in-progress`.

### Clôturer une version
> "Toutes les tâches de v002 sont faites et les critères d'acceptation sont validés, clos la version."

**Déclenche :** l'étape 2.6 — statut global `completed` dans `sprint_status.md`, statut d'en-tête `done` dans `user-stories.md`, puis un dernier `sync_memory_bank.py` pour que `progress.md` reflète la clôture.

### Consulter l'historique des specs
> "Rappelle-moi ce qu'on avait décidé dans v001."

**Déclenche :** lecture de `specs/CHANGELOG.md` puis de `specs/v001/user-stories.md` si besoin de détail.

---

## Prompts — Cas particuliers / dépannage

### Voir quels outils IA et hooks sont déjà configurés sur le projet (sans rien modifier)
> "Regarde ce qui est déjà configuré comme outil IA sur ce repo avant de me demander."

**Déclenche :** `scripts/sync_agent_docs.py --detect` (lecture seule) — liste les fichiers d'instructions et hooks JSON déjà présents, sert de contexte à la question posée ensuite, ne remplace jamais la confirmation explicite de l'utilisateur.

### Lister les outils supportés
> "Quels outils IA sont supportés pour la synchro des instructions ?"

**Déclenche :** `scripts/sync_agent_docs.py --list-tools`.

### Ajouter un outil non supporté
> "On utilise aussi [Outil Z], son fichier d'instructions est `INSTRUCTIONS-Z.md`. Ajoute-le à la skill."

**Déclenche :** édition de `TOOL_MAP` (et `HOOKS_MAP` si l'outil a des hooks) dans `scripts/sync_agent_docs.py`, plutôt qu'une gestion manuelle ponctuelle.

### Resynchroniser le compteur d'avancement après avoir rempli tasks.md
> "Je viens de remplir tasks.md avec les vraies tâches, remets à jour le compteur d'avancement."

**Déclenche :** `scripts/update_task_status.py --recount-only` — recalcule `Avancement` sans changer le statut d'aucune tâche ni journaliser d'entrée.

### Vouloir imposer une règle du workflow de façon automatique (hooks)
> "Je veux qu'un commit soit bloqué si sprint_status.md n'a pas été mis à jour depuis le dernier changement de code."

**Déclenche :** la skill n'écrit **jamais** de hook elle-même (hors de son périmètre), mais indique où le créer selon l'outil (voir tableau ci-dessous), et traite cette demande comme une tâche technique classique.

---

## Référence des scripts

Tous les scripts sont en Python 3 standard (aucune dépendance externe). Tous acceptent `--root <racine-du-projet>` (défaut : dossier courant) sauf `update_task_status.py` qui prend `--spec-dir` directement.

| Script | Rôle | Options clés |
|---|---|---|
| `new_spec.py` | Scaffold `specs/vXXX/` (numérotation auto, jamais d'écrasement) | `--name "<titre>"` |
| `detect_skills.py` | Détecte les `SKILL.md` du projet | `--json` (sortie structurée) |
| `sync_agent_docs.py` | Synchronise le(s) fichier(s) d'instructions IA | `--list-tools`, `--detect` (lecture seule), `--tools <clés>`, `--create-missing`, `--version vXXX` |
| `update_task_status.py` | Change le statut d'une tâche + journalise | `--task`, `--status`, `--note`, `--recount-only` |
| `init_memory_bank.py` | Crée `memory-bank/` (non destructif) | `--project-name "<nom>"` |
| `sync_memory_bank.py` | Resynchronise `activeContext.md`/`progress.md` | `--spec-dir specs/vXXX` |

Exemples complets :

```bash
# Créer une spec
python3 scripts/new_spec.py --root . --name "Notifications email"

# Détecter les skills du projet, en JSON
python3 scripts/detect_skills.py --root . --json

# Voir ce qui est déjà configuré (lecture seule)
python3 scripts/sync_agent_docs.py --root . --detect

# Synchroniser Claude Code + Copilot pour la version v003
python3 scripts/sync_agent_docs.py --root . --version v003 --tools claude,copilot --create-missing

# Marquer une tâche comme terminée
python3 scripts/update_task_status.py --spec-dir specs/v003 --task T-003-001 --status done --note "Endpoint livré"

# Resynchroniser juste le compteur d'avancement
python3 scripts/update_task_status.py --spec-dir specs/v003 --recount-only

# Initialiser puis synchroniser le memory bank
python3 scripts/init_memory_bank.py --root . --project-name "Mon Projet"
python3 scripts/sync_memory_bank.py --root . --spec-dir specs/v003
```

---

## Outils IA supportés

Format **moderne** utilisé en priorité pour une création ; l'**ancien format** reste détecté et mis à jour s'il existe déjà, mais n'est plus recréé.

| Outil | Fichier(s) d'instructions | Hooks JSON (automatisation déterministe) |
|---|---|---|
| Claude Code | `CLAUDE.md` | `.claude/settings.json` (clé `"hooks"`) |
| AGENTS.md (standard ouvert : Codex, Jules, ...) | `AGENTS.md` | dépend de l'outil qui le lit |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/hooks/*.json` (Preview) |
| Cursor | `.cursor/rules/spec-driven.mdc` (moderne) · `.cursorrules` (ancien) | `.cursor/hooks.json` |
| Windsurf | `.windsurf/rules/spec-driven.md` (moderne) · `.windsurfrules` (ancien) | `.windsurf/hooks.json` |
| Cline | `.clinerules/spec-driven.md` (moderne) · `.clinerules` (ancien) | non documenté à ce jour |
| Gemini CLI / Code Assist | `GEMINI.md` | `.gemini/settings.json` (clé `"hooks"`) |

`python3 scripts/sync_agent_docs.py --list-tools` affiche toujours la version la plus à jour de ce tableau.

**Important :** l'outil est toujours **confirmé explicitement avec l'utilisateur** avant la première synchronisation — jamais deviné depuis les fichiers déjà présents. `--detect` peut servir de contexte informatif à la question posée, sans jamais s'y substituer.

---

## Bonnes pratiques et anti-patterns

✅ **À faire :**
- Toujours passer par l'interview avant de générer `user-stories.md`, même pour une demande qui semble simple.
- Marquer une tâche `blocked` plutôt que de la laisser silencieusement `todo` si elle ne peut pas avancer.
- Terminer toute session de travail par une mise à jour de `sprint_status.md`, même partielle.
- Créer une nouvelle version de spec si le besoin change fondamentalement, plutôt que de modifier une version déjà validée.

❌ **À éviter :**
- Générer une spec à partir d'une seule phrase ambiguë sans interview.
- Halluciner une règle métier non mentionnée — la noter `TODO: à confirmer` à la place.
- Inventer une skill dans la colonne "Skill(s) recommandée(s)" de `tasks.md` qui n'a pas été trouvée par `detect_skills.py`.
- Deviner l'outil IA du projet à partir des fichiers présents lors de la toute première synchronisation.
- Faire créer un hook par cette skill — les hooks sont hors périmètre, seule leur localisation est documentée.

---

## FAQ

**Q : Que se passe-t-il si je demande d'implémenter une fonctionnalité alors qu'aucune spec n'existe ?**
L'agent ne saute jamais directement à la Phase 2 : il propose d'abord de créer la spec (Phase 1) pour toute fonctionnalité non triviale.

**Q : Puis-je éditer les fichiers `specs/vXXX/*.md` à la main entre deux sessions ?**
Oui, ce sont des fichiers Markdown normaux. Seules les zones balisées (`<!-- SPEC-DRIVEN:START -->`, `<!-- SYNC:START -->`) sont réécrites automatiquement par les scripts ; le reste est à éditer librement.

**Q : Que se passe-t-il si deux outils IA sont utilisés sur le même projet (ex. Claude Code + Copilot) ?**
`sync_agent_docs.py --tools claude,copilot` met à jour les deux fichiers d'instructions en une seule commande, avec le même contenu de bloc.

**Q : Le memory bank remplace-t-il `sprint_status.md` ?**
Non : `sprint_status.md` est le détail tâche par tâche d'**une** version de spec ; le memory bank est une vue transversale et persistante (spec active, décisions, contexte produit/technique) qui survit même entre deux specs différentes.
