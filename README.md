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

- Linux
- Python 3.11+

---

## Installation

```bash
git clone https://github.com/virgosfredianilorenzo-cyber/pdf2obsidiannoia.git
cd pdf2obsidiannoia
pip install .
```

Ou sans installer le package :

```bash
git clone https://github.com/virgosfredianilorenzo-cyber/pdf2obsidiannoia.git
cd pdf2obsidiannoia
bash start.sh
```

---

## Utilisation

### Via le script de démarrage

```bash
bash start.sh
```

### Via la commande CLI (après `pip install .`)

```bash
pdf2obsidiannoia
```

L'application démarre sur **http://localhost:8001**.

1. Glisser un PDF dans la zone de dépôt (ou cliquer pour choisir)
2. Configurer les options (langue, toggles, vault path)
3. Cliquer **Convertir en Obsidian MD**
4. Prévisualiser en mode brut ou rendu
5. Télécharger le `.md` ou le retrouver dans `./output/`

---

## Configuration

Éditer `config.yaml` pour changer les valeurs par défaut :

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
