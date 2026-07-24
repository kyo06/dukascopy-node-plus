---
name: spec-driven
description: Crée et fait vivre des spécifications versionnées (specs/vXXX/) avant d'implémenter du code — user stories métier + techniques, tâches liées aux skills déjà présentes dans le projet, suivi d'avancement — puis synchronise le fichier d'instructions IA du projet (CLAUDE.md, AGENTS.md, .github/copilot-instructions.md, .cursor/rules/*.mdc, .windsurf/rules/*.md, .clinerules/*.md, GEMINI.md, en confirmant l'outil avec l'utilisateur) et un memory-bank/ persistant entre sessions. Connaît aussi l'emplacement des hooks JSON de chaque outil (.claude/settings.json, .github/hooks/*.json, .cursor/hooks.json, .windsurf/hooks.json, .gemini/settings.json) pour orienter l'utilisateur vers une automatisation déterministe si besoin. Utiliser dès que l'utilisateur demande de "créer une spec", "spécifier une fonctionnalité", "faire du spec-driven development"/"SDD", parle de user stories/tasks.md/sprint status/memory bank, ou veut "appliquer"/"implémenter" une spec vXXX. Se déclenche aussi pour toute fonctionnalité non triviale sur un projet ayant déjà un dossier specs/.
---

# Spec-Driven Development

Cette skill structure le travail en deux phases distinctes et toujours dans cet ordre :

1. **Créer une spec** (`specs/vXXX/`) — interview de l'utilisateur, détection des skills du projet, puis génération des 3 fichiers.
2. **Appliquer une spec** — implémenter le code en suivant `tasks.md`, en tenant `tasks.md` et `sprint_status.md` à jour, en synchronisant le(s) fichier(s) d'instructions IA du projet (outil confirmé avec l'utilisateur) et le memory-bank.

Ne jamais sauter l'étape 1 pour aller directement à l'étape 2 si aucune spec n'existe pour le besoin exprimé.

## Arborescence produite

```
<projet>/
├── specs/
│   ├── CHANGELOG.md              # historique des versions de spec
│   ├── v001/
│   │   ├── user-stories.md       # fonctionnalités métier + specs techniques
│   │   ├── tasks.md               # backlog de tâches actionnables (référence les skills projet)
│   │   └── sprint_status.md       # avancement + journal de sessions
│   └── v002/
│       └── ...
├── memory-bank/                  # contexte persistant entre sessions (voir Étape 2.5)
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── activeContext.md          # section auto-synchronisée avec la spec active
│   └── progress.md                # section auto-synchronisée avec la spec active
├── CLAUDE.md / AGENTS.md / .github/copilot-instructions.md / .cursor/rules/spec-driven.mdc / ...
│                                  # bloc SPEC-DRIVEN inséré après confirmation de l'outil utilisé
```

Chaque nouvelle demande de spec crée une **nouvelle version** (`v001`, `v002`, ...). On ne modifie jamais rétroactivement une version déjà `validated` ou `in-progress` : si le besoin change fondamentalement, on crée `vXXX+1`. Une version peut néanmoins être complétée tant qu'elle est en `draft`.

---

## Phase 1 — Créer une spec

### Étape 1.1 — Interview (OBLIGATOIRE avant de générer quoi que ce soit)

Ne jamais générer `user-stories.md` à partir d'une simple phrase de l'utilisateur. Toujours mener une interview structurée d'abord, en s'appuyant sur `references/interview-guide.md` (méthode INVEST, MoSCoW, Gherkin, cadrage métier puis technique). Lire ce fichier avant de commencer l'interview si ce n'est pas déjà fait.

Règles :
- Poser les questions par petits lots thématiques (2-4 questions), jamais tout d'un coup.
- Utiliser `ask_user_input_v0` quand c'est pertinent pour des choix fermés (priorité MoSCoW, périmètre inclus/exclu, oui/non sur une contrainte).
- Commencer par le cadrage métier (problème résolu, persona, happy path, hors-périmètre) avant de creuser le technique (architecture, données, API, contraintes non-fonctionnelles).
- Ne jamais halluciner une règle métier non mentionnée : si un point reste flou après l'interview, le noter explicitement en `TODO: à confirmer` dans la section "Risques & points ouverts" plutôt que de deviner.
- Si l'utilisateur a déjà donné énormément de détails dans sa demande initiale (specs déjà quasi complètes), ne pas reposer des questions déjà répondues — combler seulement les trous, en confirmant les hypothèses prises.

### Étape 1.2 — Scaffolding des fichiers

Une fois l'interview suffisante, scaffolder la structure avec le script (ne jamais créer les fichiers `vXXX/` manuellement à la main, le script gère la numérotation et évite les collisions) :

```bash
python3 <chemin-de-la-skill>/scripts/new_spec.py --root <racine-du-projet> --name "Nom court de la fonctionnalité"
```

Le script détecte automatiquement le prochain numéro de version (`v001` si `specs/` n'existe pas encore, sinon `vXXX+1`), crée `specs/vXXX/{user-stories.md,tasks.md,sprint_status.md}` à partir des templates, et met à jour `specs/CHANGELOG.md`. Il affiche la version créée sur sa dernière ligne de sortie (utile pour la récupérer par script).

### Étape 1.3 — Détecter les skills déjà présentes dans le projet

Avant de remplir `tasks.md`, détecter les skills existantes du projet (skills Claude/Copilot/autres déjà installées, ex. `.claude/skills/`, `.github/skills/`, `.agents/skills/`, `skills/`) pour pouvoir les référencer dans les tâches plutôt que de réinventer un traitement déjà couvert par une skill existante :

```bash
python3 <chemin-de-la-skill>/scripts/detect_skills.py --root <racine-du-projet>
```

Coller le résultat dans la section "Skills du projet détectées" de `tasks.md`. Ensuite, pour chaque tâche du backlog, remplir la colonne "Skill(s) recommandée(s)" **uniquement** si une skill détectée correspond réellement au besoin de la tâche (ex. tâche "générer le rapport PDF mensuel" → skill `pdf` si elle est détectée). Ne jamais inventer une skill qui n'a pas été trouvée par le script — laisser `-` sinon.

### Étape 1.4 — Remplir le contenu

Les fichiers créés contiennent des placeholders (`{{Titre}}`, `US-001`, etc.) et des commentaires HTML expliquant comment les dupliquer. Éditer directement ces fichiers avec les réponses de l'interview :

- **`user-stories.md`** : une section `### US-00X` par fonctionnalité métier (format Given/When/Then en Gherkin pour les critères d'acceptation), puis la section 4 "Spécifications techniques" (architecture, modèle de données, API, contraintes non-fonctionnelles, risques).
- **`tasks.md`** : découper chaque US en tâches actionnables (`T-{{VERSION_NUM}}-001`, ...), typées (feature/tech/test/doc), liées à leur US, ordonnées par dépendance, colonne "Skill(s) recommandée(s)" renseignée selon l'étape 1.3.
- **`sprint_status.md`** : laisser tel quel à ce stade (statut `not-started`, avancement 0%) — il sera mis à jour pendant la phase 2.

Utiliser `str_replace` pour éditer ces fichiers section par section plutôt que de tout réécrire d'un coup.

Une fois `tasks.md` rempli avec les vraies tâches (le template en contient 2 d'exemple à remplacer/dupliquer), resynchroniser tout de suite le compteur d'avancement de `sprint_status.md` pour qu'il reflète le nombre réel de tâches dès le départ (sinon il reste à "0/{{TOTAL_TASKS}}" jusqu'à la première mise à jour de statut en phase 2) :

```bash
python3 <chemin-de-la-skill>/scripts/update_task_status.py --spec-dir specs/vXXX --recount-only
```

### Étape 1.5 — Validation avec l'utilisateur

Avant de considérer la spec comme `validated`, résumer à l'utilisateur les US créées, la priorisation MoSCoW, et surtout **les points ouverts / TODO à confirmer**. Ne passer le statut de `draft` à `validated` dans l'en-tête de `user-stories.md` qu'après confirmation explicite de l'utilisateur.

---

## Phase 2 — Appliquer une spec (implémentation)

Déclenchée quand l'utilisateur demande d'"implémenter", "appliquer", "démarrer" une spec `vXXX`, ou simplement de coder une fonctionnalité alors qu'une spec existe déjà pour elle.

### Étape 2.1 — Charger le contexte
Lire `specs/vXXX/user-stories.md` et `specs/vXXX/tasks.md` en entier avant de coder quoi que ce soit. Ne jamais implémenter une fonctionnalité qui dévie des critères d'acceptation sans le signaler à l'utilisateur.

### Étape 2.2 — Identifier l'outil IA du projet (demander, ne jamais deviner)
Avant de toucher un quelconque fichier d'instructions, **demander explicitement à l'utilisateur** quel(s) outil(s) IA sont utilisés sur ce projet — ne jamais choisir à sa place ni se fier uniquement à l'autodétection de fichiers existants pour la toute première synchronisation. Utiliser `ask_user_input_v0` (multi_select) avec les options : Claude Code, GitHub Copilot, Cursor, Windsurf, Cline, Gemini CLI, AGENTS.md (standard générique), Autre/plusieurs. `python3 <chemin-de-la-skill>/scripts/sync_agent_docs.py --list-tools` donne la liste exacte des clés supportées (fichier d'instructions + emplacement des hooks JSON) si besoin de les rappeler.

Optionnel avant de poser la question : `python3 <chemin-de-la-skill>/scripts/sync_agent_docs.py --root <racine-du-projet> --detect` liste en lecture seule les fichiers d'instructions et les hooks déjà présents dans le projet (ex. `.github/copilot-instructions.md` + `.github/hooks/*.json` détectés). C'est un signal utile à mentionner à l'utilisateur dans la question elle-même (ex. "j'ai trouvé un `.github/copilot-instructions.md`, c'est bien Copilot que vous utilisez ?"), mais ça ne dispense jamais de sa confirmation explicite — `--detect` ne modifie rien et ne choisit rien à sa place.

Si le projet a déjà un bloc `SPEC-DRIVEN:START` existant dans un fichier (donc déjà configuré lors d'une session précédente), ne pas reposer la question — resynchroniser directement ce(s) fichier(s).

### Étape 2.3 — Synchroniser le(s) fichier(s) d'instructions IA
Une fois l'outil confirmé, synchroniser avec la clé correspondante :

```bash
python3 <chemin-de-la-skill>/scripts/sync_agent_docs.py --root <racine-du-projet> --version vXXX --tools claude,copilot --create-missing
```

`--tools` accepte une liste de clés séparées par des virgules (`claude`, `agents`, `copilot`, `cursor`, `windsurf`, `cline`, `gemini`). Le script met à jour uniquement le bloc délimité par `<!-- SPEC-DRIVEN:START -->` / `<!-- SPEC-DRIVEN:END -->`, sans toucher au reste du fichier. `--create-missing` crée le fichier s'il n'existe pas encore pour l'outil choisi.

Sans `--tools` (mode de repli), le script se contente de mettre à jour les fichiers déjà présents — à réserver aux resynchronisations rapides sur un projet déjà configuré, pas au premier setup.

Si le projet utilise un outil non listé, l'ajouter dans `TOOL_MAP` du script (voir commentaires dans le fichier) plutôt que de le gérer manuellement.

### Étape 2.4 — Implémenter tâche par tâche
Suivre l'ordre de `tasks.md`, en utilisant les skills recommandées par tâche (colonne "Skill(s) recommandée(s)") quand elles s'appliquent. Pour chaque tâche démarrée/terminée, mettre à jour son statut et journaliser la session :

```bash
python3 <chemin-de-la-skill>/scripts/update_task_status.py \
  --spec-dir specs/vXXX --task T-XXX-00Y --status done \
  --note "Description courte de ce qui a été fait"
```

Statuts valides : `todo`, `in-progress`, `blocked`, `review`, `done`. Ce script met à jour la ligne correspondante dans `tasks.md`, ajoute une entrée dans le journal des sessions de `sprint_status.md`, et recalcule automatiquement le pourcentage d'avancement global.

Ne jamais laisser `sprint_status.md` désynchronisé de l'état réel du code : une session de travail se termine toujours par une mise à jour de statut, même partielle (`in-progress`/`blocked`), pas seulement quand tout est `done`.

### Étape 2.5 — Memory bank : initialiser puis synchroniser
Le memory-bank (`memory-bank/`) persiste le contexte projet entre les sessions — indispensable car un agent IA ne garde pas le contexte d'une conversation à l'autre. Au premier passage sur le projet (une seule fois) :

```bash
python3 <chemin-de-la-skill>/scripts/init_memory_bank.py --root <racine-du-projet> --project-name "<nom du projet>"
```

Non destructif : ne crée que les fichiers manquants. Puis, après chaque mise à jour de statut de tâche (étape 2.4) et en fin de session, synchroniser `activeContext.md` et `progress.md` avec l'état réel de la spec :

```bash
python3 <chemin-de-la-skill>/scripts/sync_memory_bank.py --root <racine-du-projet> --spec-dir specs/vXXX
```

Seule la section balisée `<!-- SYNC:START -->` / `<!-- SYNC:END -->` de chaque fichier est réécrite ; le reste (focus actuel, décisions, notes manuelles) doit être édité à la main via `str_replace` quand c'est pertinent. `sync_agent_docs.py` insère déjà une consigne pour que tout agent IA lise `activeContext.md` en premier à chaque session — ne pas la dupliquer ailleurs.

### Étape 2.6 — Fin de version
Quand toutes les tâches d'une version sont `done` et que la Definition of Done de `user-stories.md` est cochée, passer le statut global dans `sprint_status.md` à `completed`, le statut d'en-tête de `user-stories.md` à `done`, et lancer une dernière fois `sync_memory_bank.py` pour que `progress.md` reflète la clôture.

---

## Compatibilité multi-outils

Cette skill vise la compatibilité la plus large possible côté "fichiers d'instructions IA", avec pour chaque outil le format **moderne recommandé** (utilisé en priorité pour une création) et l'**ancien format** encore lu par l'outil (utilisé s'il est déjà présent, jamais recréé) :

| Outil | Fichier(s) d'instructions | Hooks JSON (automatisation déterministe) |
|---|---|---|
| Claude Code | `CLAUDE.md` | `.claude/settings.json` (clé `"hooks"`) |
| AGENTS.md (standard ouvert : Codex, Jules, ...) | `AGENTS.md` | dépend de l'outil qui le lit — pas d'emplacement standard |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/hooks/*.json` (un fichier par hook, fonctionnalité en Preview) |
| Cursor | `.cursor/rules/spec-driven.mdc` (moderne) · `.cursorrules` (ancien, à plat) | `.cursor/hooks.json` |
| Windsurf | `.windsurf/rules/spec-driven.md` (moderne) · `.windsurfrules` (ancien, à plat) | `.windsurf/hooks.json` |
| Cline | `.clinerules/spec-driven.md` (moderne, dossier) · `.clinerules` (ancien fichier à plat) | aucun système de hooks documenté à ce jour — uniquement des règles |
| Gemini CLI / Code Assist | `GEMINI.md` | `.gemini/settings.json` (clé `"hooks"`) |

`python3 <chemin-de-la-skill>/scripts/sync_agent_docs.py --list-tools` affiche toujours la version à jour de ce tableau (source de vérité : `TOOL_MAP`/`HOOKS_MAP` dans le script), à préférer à cette table si elles divergent un jour.

L'outil réellement utilisé est **toujours confirmé avec l'utilisateur** (étape 2.2) plutôt que deviné depuis les fichiers présents dans le repo — `--detect` peut néanmoins servir de contexte informatif avant de poser la question. Le bloc inséré (`templates/agent-instructions-block.md`) est du Markdown simple sans syntaxe spécifique à un outil, donc il reste lisible/utile même pour un outil non explicitement listé — l'ajouter dans `TOOL_MAP` (et, le cas échéant, `HOOKS_MAP`) du script pour qu'il soit maintenu automatiquement ensuite.

Cette skill ne crée ni ne modifie jamais de hook (ni pour Claude Code, ni pour Copilot, ni pour aucun autre outil) : les hooks sont une automatisation à part, hors du périmètre du spec-driven development. L'emplacement des hooks est seulement documenté pour que l'agent puisse orienter l'utilisateur s'il souhaite, de sa propre initiative, faire respecter une règle du workflow spec-driven de façon déterministe (ex. un hook qui bloque un commit si `sprint_status.md` n'a pas été mis à jour depuis le dernier changement de code) — dans ce cas, écrire ce hook est une tâche distincte, à traiter comme n'importe quelle autre tâche technique, pas une action automatique de cette skill.

Les scripts sont en Python 3 standard (aucune dépendance externe) pour fonctionner sur tout environnement où Python est disponible.

## Fichiers de la skill

- `README.md` — documentation humaine : liste de prompts d'exemple pour chaque étape du workflow, référence des scripts, tableau des outils supportés, FAQ. Ce `SKILL.md` reste la référence technique lue par l'agent ; le `README.md` est un point d'entrée pour un humain qui découvre la skill.
- `references/interview-guide.md` — méthodologie de l'interview (INVEST, MoSCoW, Gherkin, anti-patterns). À lire avant toute interview.
- `templates/user-stories.template.md`, `templates/tasks.template.md`, `templates/sprint_status.template.md` — templates utilisés par `new_spec.py`.
- `templates/agent-instructions-block.md` — bloc inséré par `sync_agent_docs.py` (inclut la consigne memory-bank).
- `templates/memory-bank/*.template.md` — 6 templates memory-bank utilisés par `init_memory_bank.py`.
- `scripts/new_spec.py` — scaffold une nouvelle version de spec.
- `scripts/detect_skills.py` — détecte les skills déjà présentes dans le projet (`.claude/skills/`, `.github/skills/`, `.agents/skills/`, `skills/`, puis fallback récursif) pour enrichir `tasks.md`.
- `scripts/sync_agent_docs.py` — synchronise le(s) fichier(s) d'instructions IA choisis par l'utilisateur avec la spec active ; `--list-tools` liste les outils supportés (instructions + hooks) ; `--detect` liste en lecture seule ce qui existe déjà dans le projet.
- `scripts/update_task_status.py` — met à jour le statut d'une tâche + journalise la session ; `--recount-only` resynchronise juste le compteur d'avancement sans changer de statut ni journaliser.
- `scripts/init_memory_bank.py` — initialise `memory-bank/` (non destructif).
- `scripts/sync_memory_bank.py` — synchronise `activeContext.md`/`progress.md` avec l'état de la spec active.
