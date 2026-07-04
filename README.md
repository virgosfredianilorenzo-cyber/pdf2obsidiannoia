# pdf2obsidiannoia

**PDF → Obsidian Markdown, sans IA.**

Application web locale qui convertit des PDF en Markdown formatté selon les conventions Obsidian — frontmatter YAML, table des matières cliquable, callouts `[!TYPE]`, wikilinks `[[concept]]` — sans aucun modèle de langage.

---

## Fonctionnalités

| Feature | Détail |
|---|---|
| **Frontmatter YAML** | `title`, `author`, `date_extraction`, `source`, `pages`, `tags`, `mode: obsidian-noia` |
| **Table des matières** | Liens `[[#heading]]` générés depuis la hiérarchie H1/H2/H3 |
| **Callouts Obsidian** | `Note:` / `Important:` / `Attention:` / `Exemple:` / `Conseil:` → `> [!TYPE]` |
| **Wikilinks** | Noms propres + phrases en gras → `[[concept]]` (stop-list FR/EN intégrée) |
| **Toggles** | Chaque feature activable/désactivable depuis l'interface |
| **Vault path** | Copie optionnelle du `.md` directement dans ton vault Obsidian |
| **Zero IA** | Conversion 100 % déterministe — pas d'Ollama, pas de clé API |

---

## Prérequis

- Linux (Ubuntu, Debian, Fedora…)
- Python 3.11 ou supérieur

Pour vérifier ta version de Python, ouvre un terminal et tape :

```bash
python3 --version
```

Si tu vois `Python 3.11.x` ou plus, tu es prêt. Sinon, installe Python depuis [python.org](https://www.python.org/downloads/).

---

## Installation

### Option A — Démarrage automatique (recommandé pour les débutants)

Le script `start.sh` fait tout automatiquement : il crée l'environnement virtuel, installe les dépendances, et lance l'application.

**1. Télécharge le projet**

```bash
git clone https://github.com/virgosfredianilorenzo-cyber/pdf2obsidiannoia.git
```

> Si tu n'as pas `git`, installe-le avec : `sudo apt install git` (Ubuntu/Debian) ou `sudo dnf install git` (Fedora).

**2. Entre dans le dossier du projet**

```bash
cd pdf2obsidiannoia
```

**3. Lance le script de démarrage**

```bash
bash start.sh
```

C'est tout. L'application démarre sur **http://localhost:8001**.

> La première fois, le script installe les dépendances — cela peut prendre une minute.  
> Les fois suivantes, il démarre directement.

---

### Option B — Installation manuelle avec environnement virtuel

Cette méthode te donne plus de contrôle. Un **environnement virtuel** (ou *venv*) est un dossier isolé qui contient les bibliothèques Python du projet, sans polluer ton système.

**1. Télécharge le projet**

```bash
git clone https://github.com/virgosfredianilorenzo-cyber/pdf2obsidiannoia.git
cd pdf2obsidiannoia
```

**2. Crée l'environnement virtuel**

```bash
python3 -m venv .venv
```

> Cela crée un dossier `.venv/` dans le projet. Tu ne le modifies jamais à la main.

**3. Active l'environnement virtuel**

```bash
source .venv/bin/activate
```

> Ton terminal affiche maintenant `(.venv)` au début de la ligne de commande — c'est le signe que l'environnement est actif.  
> Exemple : `(.venv) utilisateur@machine:~/pdf2obsidiannoia$`

**4. Mets à jour pip (optionnel mais conseillé)**

```bash
pip install --upgrade pip
```

**5. Installe les dépendances**

```bash
pip install -r requirements.txt
```

> Toutes les bibliothèques nécessaires sont listées dans `requirements.txt`. Pip les télécharge et les installe dans le `.venv/`.

**6. Lance l'application**

```bash
python app.py
```

L'application démarre sur **http://localhost:8001**.

**7. Quitter l'environnement virtuel**

Quand tu as fini, tu peux désactiver l'environnement virtuel avec :

```bash
deactivate
```

> Ton terminal revient à la normale (plus de `(.venv)` en début de ligne).

**La prochaine fois**, il suffit de réactiver le venv avant de lancer :

```bash
cd pdf2obsidiannoia
source .venv/bin/activate
python app.py
```

---

### Option C — Installer comme commande système (`pip install .`)

Cette méthode rend la commande `pdf2obsidiannoia` disponible partout dans ton terminal.

```bash
git clone https://github.com/virgosfredianilorenzo-cyber/pdf2obsidiannoia.git
cd pdf2obsidiannoia
pip install .
```

Puis lance simplement :

```bash
pdf2obsidiannoia
```

> **Note :** Sur certains systèmes, il faut utiliser un venv même pour `pip install .` (voir Option B, étapes 1 à 3, puis `pip install .`).

---

## Utilisation

1. Ouvre **http://localhost:8001** dans ton navigateur
2. Glisse un PDF dans la zone de dépôt (ou clique pour choisir)
3. Configure les options (langue, toggles, vault path)
4. Clique **Convertir en Obsidian MD**
5. Prévisualise en mode brut ou rendu
6. Télécharge le `.md` ou retrouve-le dans `./output/`

---

## Configuration

Édite `config.yaml` pour changer les valeurs par défaut :

```yaml
port: 8001
output_dir: ./output
vault_path: null        # ex: ~/Documents/Obsidian/MyVault
language: fr
wikilinks: true
callouts: true
toc: true
```

---

## Architecture

```
pdf2obsidiannoia/
├── app.py           # Serveur FastAPI — port 8001
├── extractor.py     # PDF → PDFDocument (pymupdf + pdfplumber)
├── converter.py     # Pipeline 4 passes (frontmatter → TOC → callouts → wikilinks)
├── callouts.py      # Regex callouts → > [!TYPE]
├── wikilinks.py     # Noms propres + phrases gras → [[wikilinks]]
├── formatter.py     # Assemblage .md + sauvegarde vault
├── config.yaml      # Configuration
├── pyproject.toml   # Package Python
├── start.sh         # Script de démarrage (crée le venv si absent)
├── static/
│   └── index.html   # Interface web
└── tests/           # 58 tests unitaires
```

### Pipeline de conversion

```
PDF → extractor → converter → formatter → .md
                     ↓
          ① Frontmatter YAML
          ② Table des matières [[#heading]]
          ③ Callouts [!TYPE]
          ④ Wikilinks [[concept]]
```

---

## Tests

```bash
pytest tests/ -v
```

58 tests couvrant : extraction, callouts, wikilinks, pipeline, formatter.

---

## Endpoints API

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Interface web |
| `POST` | `/api/convert` | Conversion PDF → MD |
| `GET` | `/api/download/{filename}` | Téléchargement du `.md` généré |

---

## Gestion d'erreurs

| Cas | Comportement |
|---|---|
| Fichier non-PDF | Rejeté côté client avant upload |
| PDF protégé par mot de passe | HTTP 400 avec message explicite |
| PDF scanné (image sans texte) | Avertissement dans la réponse, pas de crash |
| Vault path inexistant | Warning dans la réponse, `.md` sauvegardé localement |

---

## Licence

MIT
