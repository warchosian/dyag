# Dyag

**Dyag** - Outil puissant de manipulation de fichiers et conversion avec support des diagrammes et système RAG intégré.

[![Version](https://img.shields.io/badge/version-0.8.0-blue.svg)](https://github.com/warchosian/dyag/releases/tag/v0.8.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-133%20passing-success.svg)](https://github.com/warchosian/dyag)
[![Coverage](https://img.shields.io/badge/coverage-21%25-yellow.svg)](https://github.com/warchosian/dyag)

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Commandes disponibles](#-commandes-disponibles)
- [Utilisation](#-utilisation)
- [Système RAG](#-système-rag)
- [Configuration](#-configuration)
- [Contribution](#-contribution)
- [License](#-license)

## ✨ Fonctionnalités

### Conversion de documents
- **Markdown → HTML** avec support des diagrammes (Graphviz, PlantUML, Mermaid)
- **HTML → Markdown** avec préservation de la structure
- **HTML → PDF** avec rendu haute qualité
- **Images → PDF** avec compression optimale

### Manipulation de documents
- **Table des matières** automatique (HTML et Markdown)
- **Fusion** de documents HTML/Markdown
- **Aplatissement** de structures WikiSI et dossiers
- **Interactivité** HTML avec navigation améliorée
- **Compression PDF** avancée

### Système RAG (v0.6.0+)
- **Indexation sémantique** avec ChromaDB et Sentence Transformers
- **Multi-providers LLM** : OpenAI, Anthropic/Claude, Ollama
- **Q&A intelligent** sur vos documents
- **Évaluation** de la qualité du système RAG
- **Préparation** automatique de datasets
- **Génération de questions/réponses** pour RAG et fine-tuning (v0.8.0) 🆕

### Génération de documentation
- **Project → Markdown** : documentation automatique de projets
- **Analyse** de code et structure

## 🚀 Installation

### Prérequis
- **Python 3.10+**
- **Poetry** (recommandé) ou **pip**

### Installation de base

```bash
# Via Poetry (recommandé)
poetry install

# Via pip
pip install -e .
```

### Installation des dépendances RAG (optionnel)

Si vous souhaitez utiliser les fonctionnalités RAG (Retrieval-Augmented Generation) pour l'indexation et la recherche de documents, vous avez deux options :

#### Option 1 : Via Poetry (recommandé)

```bash
poetry install -E rag
```

Cette commande installe dyag avec toutes les dépendances RAG définies dans `pyproject.toml`.

#### Option 2 : Via pip (alternative)

```bash
pip install -r requirements-rag.txt
```

Cette méthode est utile si :
- Vous utilisez conda ou un autre gestionnaire d'environnement
- Vous rencontrez des conflits de dépendances avec Poetry
- Vous préférez une installation directe sans Poetry

**Note**: En raison d'incompatibilités temporaires entre Poetry 2.2+ et certaines dépendances RAG (notamment `packaging`), l'option 2 peut être plus fiable dans certains environnements.

### Dépendances pour les diagrammes

Pour le rendu des diagrammes, vous aurez besoin :
- **Graphviz** (local) : https://graphviz.org/download/
- **PlantUML** et **Mermaid** : utilisent Kroki en ligne (aucune installation requise)

## 📚 Commandes disponibles

### Conversion de documents

| Commande | Description |
|----------|-------------|
| `dyag md2html` | Convertir Markdown vers HTML avec support des diagrammes (Graphviz, PlantUML, Mermaid) |
| `dyag html2md` | Convertir HTML vers Markdown |
| `dyag html2pdf` | Convertir HTML vers PDF |
| `dyag img2pdf` | Convertir des images en PDF |

### Manipulation de documents

| Commande | Description |
|----------|-------------|
| `dyag add_toc4md` | Ajouter une table des matières à un fichier Markdown |
| `dyag add_toc4html` | Ajouter une table des matières à un fichier HTML |
| `dyag concat_html` | Concaténer plusieurs fichiers HTML |
| `dyag merge_html` | Fusionner des fichiers HTML d'un dossier |
| `dyag merge_md` | Fusionner des fichiers Markdown d'un dossier |
| `dyag flatten_html` | Aplatir une structure HTML en un seul fichier |
| `dyag flatten_md` | Aplatir une structure Markdown en un seul fichier |
| `dyag flatten_wikisi` | Aplatir une structure WikiSI |
| `dyag make_interactive` | Rendre un fichier HTML interactif |
| `dyag compresspdf` | Compresser un fichier PDF |

### Génération de documentation

| Commande | Description |
|----------|-------------|
| `dyag project2md` | Générer une documentation Markdown d'un projet |

### Système RAG (Retrieval-Augmented Generation)

| Commande | Description |
|----------|-------------|
| `dyag prepare_rag` | Préparer les données pour le système RAG |
| `dyag index_rag` | Indexer les documents dans ChromaDB |
| `dyag query_rag` | Interroger le système RAG |
| `dyag evaluate_rag` | Évaluer la qualité du système RAG |
| `dyag create_rag` | Créer un dataset pour le RAG |
| `dyag markdown-to-rag` | Pipeline complet Markdown → RAG |
| `dyag generate-questions` | Générer des questions/réponses pour RAG et fine-tuning 🆕 |
| `dyag analyze_training` | Analyser les données d'entraînement |

### Manipulation JSON

| Commande | Description |
|----------|-------------|
| `dyag parkjson2md` | Convertir JSON parc applicatif vers Markdown |
| `dyag parkjson2json` | Filtrer et extraire données JSON |

## 💡 Utilisation

### Exemples de base

```bash
# Convertir un fichier Markdown en HTML avec diagrammes
dyag md2html input.md -o output.html -v

# Convertir HTML en PDF
dyag html2pdf document.html -o document.pdf

# Ajouter une table des matières
dyag add_toc4md README.md -o README_with_toc.md

# Générer la documentation d'un projet
dyag project2md /path/to/project -o project_doc.md

# Compresser un PDF
dyag compresspdf large.pdf -o compressed.pdf
```

### Aide pour chaque commande

```bash
dyag <commande> -h
```

Exemple :
```bash
dyag md2html -h
```

## 🤖 Système RAG

Le système RAG (Retrieval-Augmented Generation) permet d'interroger intelligemment vos documents en utilisant :
- **ChromaDB** pour le stockage vectoriel
- **Sentence Transformers** pour les embeddings sémantiques
- **Multi-providers LLM** : OpenAI GPT-4, Anthropic Claude, Ollama (local)

### Configuration RAG

Créez un fichier `.env` à la racine du projet :

```env
# Provider LLM (openai, anthropic, claude, ou ollama)
LLM_PROVIDER=openai

# Clés API (selon le provider)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Configuration Ollama (si utilisé)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=300

# Modèle d'embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Base ChromaDB
CHROMA_PATH=./chroma_db
```

### Workflow RAG

```bash
# 1. Préparer les données
dyag prepare_rag documents/ -o prepared/

# 2. Indexer dans ChromaDB
dyag index_rag prepared/ --collection my_docs

# 3. Interroger
dyag query_rag "Comment fonctionne X ?" --collection my_docs

# 4. Évaluer (optionnel)
dyag evaluate_rag dataset.jsonl --collection my_docs
```

### Génération de Questions/Réponses (v0.8.0) 🆕

La commande `generate-questions` permet de générer automatiquement des paires question/réponse depuis des documents Markdown structurés. Cas d'usage :
- **Évaluation RAG** : Créer des datasets de test
- **Fine-tuning** : Préparer des données d'entraînement pour LLMs

#### Formats de sortie

- **`rag`** : Format pour évaluation RAG (avec métadonnées)
- **`finetuning`** : Format OpenAI/Anthropic pour fine-tuning
- **`simple`** : Format prompt/completion minimal
- **`all`** : Génère les 3 formats simultanément

#### Exemples d'utilisation

```bash
# Générer questions pour évaluation RAG
dyag generate-questions applications.md --format rag

# Générer dataset pour fine-tuning
dyag generate-questions applications.md \
  --format finetuning \
  --output dataset_ft.jsonl \
  --questions-per-section 5

# Générer tous les formats
dyag generate-questions applications.md --format all

# Options avancées
dyag generate-questions applications.md \
  --format rag \
  --categories status,domains,contacts \
  --difficulty easy,medium \
  --questions-per-section 3 \
  --verbose
```

#### Workflow complet RAG + Fine-tuning

```bash
# 1. Générer questions depuis documentation
dyag generate-questions apps.md --format all --output eval/questions

# 2. Créer base RAG
dyag markdown-to-rag apps.md --collection apps_rag

# 3. Évaluer RAG
dyag evaluate-rag eval/questions_rag.jsonl --collection apps_rag

# 4. Fine-tuner un modèle (OpenAI)
openai api fine_tunes.create \
  -t eval/questions_finetuning.jsonl \
  -m gpt-3.5-turbo
```

### Providers LLM supportés

- **OpenAI** : GPT-4, GPT-3.5-turbo
- **Anthropic/Claude** : Claude 3.5 Sonnet, Claude 3 Opus
- **Ollama** : Llama 2, Mistral, et autres modèles locaux

## ⚙️ Configuration

### Variables d'environnement

Dyag peut être configuré via un fichier `.env` :

```env
# RAG Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PATH=./chroma_db

# Diagram rendering
KROKI_URL=https://kroki.io
```

### MCP Server

Dyag peut être utilisé comme serveur MCP (Model Context Protocol) :

```bash
dyag-mcp
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src/dyag --cov-report=term-missing

# Tests spécifiques
pytest tests/unit/
pytest tests/integration/
```

**Couverture actuelle** : 33% (139 tests passent)

## 🤝 Contribution

Les contributions sont les bienvenues!

### Développement

```bash
# Cloner le projet
git clone https://github.com/warchosian/dyag.git
cd dyag

# Installer en mode développement
poetry install
poetry install -E rag

# Lancer les tests
pytest

# Formater le code
black src/ tests/
flake8 src/ tests/
```

### Commits conventionnels

Ce projet utilise [Commitizen](https://commitizen-tools.github.io/commitizen/) pour les commits :

```bash
# Faire un commit
cz commit

# Bump de version
cz bump
```

Format des commits :
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage
- `refactor:` refactorisation
- `test:` ajout de tests
- `chore:` tâches diverses

## 📝 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🔗 Liens

- **Repository** : https://github.com/warchosian/dyag
- **Issues** : https://github.com/warchosian/dyag/issues
- **Releases** : https://github.com/warchosian/dyag/releases
- **Documentation** : https://github.com/warchosian/dyag/tree/main/doc

## 📜 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des versions.

### Versions récentes

- **v0.6.0** (2025-01-16) - Système RAG complet avec multi-providers LLM
- **v0.5.0** (2025-01-16) - Migration Python 3.10 + intégration RAG
- **v0.4.0** (2025-12-07) - Release initiale avec conversion Markdown/HTML/PDF

## 👤 Auteur

**MARCHAL Hervé**
- Email: herve.marchal@developpement-durable.gouv.fr
- GitHub: [@warchosian](https://github.com/warchosian)

---

**Dyag** - De la documentation à portée de commande! 📚✨
