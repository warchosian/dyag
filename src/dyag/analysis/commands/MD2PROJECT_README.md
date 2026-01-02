# md2project - Markdown to Project Structure

## Description

`md2project` est l'inverse de `project2md`. Il convertit un fichier Markdown (généré par `project2md`) en structure de projet réelle avec tous les fichiers et répertoires.

## Cas d'usage

1. **Restauration de projet** : Restaurer un projet depuis une sauvegarde Markdown
2. **Templates de projet** : Créer des templates de projets documentés
3. **Literate Programming** : Générer du code depuis de la documentation
4. **Partage de code** : Partager un projet entier dans un seul fichier Markdown
5. **Documentation interactive** : Créer des tutoriels qui génèrent du code fonctionnel

## Installation

```bash
pip install dyag
```

## Utilisation de base

### Générer un projet depuis un Markdown

```bash
dyag md2project project.md
```

Cela crée un répertoire avec le nom du projet contenant tous les fichiers.

### Spécifier le répertoire de sortie

```bash
dyag md2project project.md -o mon_projet/
```

### Mode dry-run (aperçu)

```bash
dyag md2project project.md --dry-run
```

Affiche ce qui serait créé sans créer les fichiers.

## Options

| Option | Description |
|--------|-------------|
| `-o, --output DIR` | Répertoire de sortie (défaut: nom du projet) |
| `-n, --dry-run` | Simuler sans créer les fichiers |
| `--overwrite` | Écraser fichiers et répertoires existants |
| `--merge` | Fusionner avec un répertoire existant |
| `--verbose` | Afficher la progression détaillée |

## Exemples

### 1. Workflow complet : Projet → Markdown → Projet

```bash
# Générer Markdown depuis projet existant
dyag project2md mon_projet/ -o backup.md

# Restaurer projet depuis Markdown
dyag md2project backup.md -o mon_projet_restored/
```

### 2. Template de projet

Créez `python_template.md` :

```markdown
# Projet : hello_world

**Fichiers** : 3 fichiers

## 📄 Contenu des fichiers

---
### 📄 `README.md` [100 octets]

```markdown
# Hello World

Simple Python project template.
```

---
### 📄 `main.py` [80 octets]

```python
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

---
### 📄 `requirements.txt` [0 octets]

```text
```

---
*Généré par dyag project2md*
```

Puis générez le projet :

```bash
dyag md2project python_template.md

# Crée:
# hello_world/
#   ├── README.md
#   ├── main.py
#   └── requirements.txt
```

### 3. Partage de code pour AI assistants

```bash
# Générer Markdown pour partage
dyag project2md src/ -o project_share.md

# L'utilisateur reçoit project_share.md
# Il peut le revoir, modifier dans un éditeur
# Puis restaurer le projet:
dyag md2project project_share.md
```

### 4. Fusion avec projet existant

```bash
# Ajouter des fichiers depuis Markdown sans écraser existants
dyag md2project new_files.md -o existing_project/ --merge
```

### 5. Mode verbeux pour débogage

```bash
dyag md2project complex_project.md --verbose
```

Affiche :
```
[INFO] Parsing Markdown: complex_project.md
[INFO] Project: complex_project
[INFO] Files found: 25
[INFO] Output directory: /path/to/complex_project
[INFO] Creating project structure...
[CREATE] README.md (1.234 bytes)
[CREATE] src/main.py (2.567 bytes)
[CREATE] tests/test_main.py (890 bytes)
...
[SUCCESS] Project created: /path/to/complex_project
[INFO] Created: 25 files
```

## Format Markdown attendu

Le Markdown doit être au format généré par `project2md` :

```markdown
# Projet : nom_projet

**Chemin** : `/path/to/project`
**Fichiers** : X fichiers

## 📁 Arborescence des fichiers
[tree structure]

---
## 📄 Contenu des fichiers

---
### 📄 `path/to/file.ext` [size octets]
<a id="anchor"></a>

> **Chemin relatif** : `path/to/file.ext`
> **Taille** : size octets
> **Lignes** : N
> **Type** : language

```language
file content here
```
```

## Fonctionnalités

### ✅ Parsing robuste

- **Backticks imbriqués** : Supporte 3, 4, 5+ backticks
- **Blocs collapsibles** : Extrait contenu dans `<details>`
- **Métadonnées** : Préserve language, taille, nombre de lignes
- **Chemins complexes** : Gère espaces, Unicode, chemins longs
- **Validation** : Vérifie cohérence et signale problèmes

### ✅ Création de structure

- **Répertoires imbriqués** : Crée automatiquement l'arborescence
- **Encodage UTF-8** : Fichiers créés en UTF-8
- **Préservation contenu** : Lignes vides, indentation conservées
- **Gestion erreurs** : Continue en cas d'erreur sur un fichier

### ✅ Modes de fonctionnement

| Mode | Description |
|------|-------------|
| **Normal** | Crée nouveau répertoire |
| **Dry-run** | Simule sans créer |
| **Overwrite** | Écrase répertoire existant |
| **Merge** | Fusionne avec existant |

## Architecture

```
dyag/analysis/
├── core/
│   └── md2project_parser.py    # Parser Markdown → ProjectStructure
└── commands/
    └── md2project.py            # CLI wrapper
```

### Classes principales

#### `Md2ProjectParser`
Parse le Markdown et extrait la structure de projet.

```python
from dyag.analysis.core.md2project_parser import Md2ProjectParser

parser = Md2ProjectParser(verbose=True)
project = parser.parse_file("project.md")

print(f"Project: {project.name}")
print(f"Files: {len(project.files)}")

for file in project.files:
    print(f"  - {file.path} ({file.language})")
```

#### `ProjectStructure`
Représente la structure complète du projet.

```python
from dyag.analysis.core.md2project_parser import ProjectStructure, FileEntry

project = ProjectStructure(
    name="my_project",
    files=[
        FileEntry(path="README.md", content="# Project", language="markdown"),
        FileEntry(path="src/main.py", content="def main(): pass", language="python"),
    ]
)

# Conversion en dict
data = project.to_dict()
```

#### `FileEntry`
Représente un fichier individuel.

```python
file = FileEntry(
    path="src/utils.py",
    content="def helper(): return True",
    language="python",
    size=30,
    lines=2
)
```

## Validation

Le parser valide automatiquement :

```python
parser = Md2ProjectParser()
project = parser.parse_file("project.md")

issues = parser.validate_structure(project)
if issues:
    for issue in issues:
        print(f"⚠️  {issue}")
```

Détecte :
- Fichiers manquants
- Fichiers vides
- Chemins invalides
- Incohérence nombre de fichiers

## Tests

Le module est testé avec **37 tests unitaires** (23 parser + 14 CLI) :

```bash
# Tests parser
pytest tests/unit/analysis/core/test_md2project_parser.py -v

# Tests CLI
pytest tests/unit/analysis/commands/test_md2project.py -v

# Couverture : 89% (parser) + 82% (CLI)
```

## Limitations

1. **Format strict** : Doit respecter le format `project2md`
2. **Pas de métadonnées Git** : Ne restaure pas l'historique Git
3. **Permissions** : Tous les fichiers créés avec permissions par défaut
4. **Fichiers binaires** : Ne peut pas restaurer de binaires

## Comparaison project2md ↔ md2project

| Fonctionnalité | project2md | md2project |
|----------------|------------|------------|
| **Direction** | Projet → Markdown | Markdown → Projet |
| **Input** | Répertoire | Fichier .md |
| **Output** | Fichier .md | Répertoire |
| **Filtrage** | .gitignore, .projectignore | N/A |
| **Binaires** | Ignore | N/A (seulement texte) |
| **Métadonnées** | Ajoute (taille, lignes, type) | Extrait |
| **Navigation** | Liens cliquables | N/A |

## Contribution

Le code est dans :
- `src/dyag/analysis/core/md2project_parser.py` - Parser
- `src/dyag/analysis/commands/md2project.py` - CLI
- `tests/unit/analysis/core/test_md2project_parser.py` - Tests parser
- `tests/unit/analysis/commands/test_md2project.py` - Tests CLI

## Voir aussi

- [`project2md`](./project2md.py) - Projet → Markdown
- [RAG commands](../../rag/commands/) - Indexation et recherche
- [Documentation DYAG](../../../README.md)

## Licence

Fait partie de DYAG - Voir LICENSE du projet principal.
