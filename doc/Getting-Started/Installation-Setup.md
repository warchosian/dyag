# 📦 Installation et Configuration DYAG

> Guide complet d'installation pour tous les cas d'usage

## Table des matières

- [Installation de base](#installation-de-base)
- [Configuration RAG](#configuration-rag)
- [Configuration Fine-Tuning](#configuration-fine-tuning)
- [Troubleshooting](#troubleshooting)

---

## Installation de base

### Prérequis système

| Composant | Version minimum | Recommandé |
|-----------|-----------------|------------|
| Python | 3.8+ | 3.10+ |
| RAM | 4 GB | 8 GB+ |
| Disque | 2 GB | 5 GB+ |

### Installation standard

```bash
# 1. Cloner le projet
git clone https://votre-repo/dyag.git
cd dyag

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements-rag.txt
```

### Installation développeur

Pour contribuer au projet :

```bash
# Installer avec les dépendances de développement
pip install -r requirements-dev.txt

# Installer les hooks pre-commit
pre-commit install

# Installer commitizen
pip install commitizen
```

Voir aussi : [Guide de développement](../Development/Versioning-Guide.md)

---

## Configuration RAG

### 1. Choisir un provider LLM

Créez un fichier `.env` à la racine :

#### Option A : Ollama (Gratuit, local)

```bash
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

**Installation d'Ollama** :
1. Télécharger depuis [ollama.ai](https://ollama.ai)
2. Installer et lancer : `ollama serve`
3. Télécharger un modèle : `ollama pull llama3.2`

**Avantages** : Gratuit, privé, pas de limite
**Inconvénients** : Nécessite ressources locales, plus lent

#### Option B : OpenAI (Payant, cloud)

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-votre-cle-ici
LLM_MODEL=gpt-4o-mini
```

**Obtenir une clé API** :
1. Créer un compte sur [platform.openai.com](https://platform.openai.com)
2. Ajouter des crédits ($5-10 minimum)
3. Créer une API key dans Settings > API Keys

**Avantages** : Rapide, qualité excellente
**Inconvénients** : Payant (~$0.15/1M tokens pour gpt-4o-mini)

#### Option C : Claude/Anthropic (Payant, cloud)

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
LLM_MODEL=claude-3-5-sonnet-20241022
```

**Avantages** : Excellente qualité, contexte large
**Inconvénients** : Payant, pas de fine-tuning

### 2. Préparer les données

Créez un fichier JSONL avec vos données :

```jsonl
{"id": "1", "nom": "Application 1", "description": "Description..."}
{"id": "2", "nom": "Application 2", "description": "Description..."}
```

Voir aussi : [Guide de chunking](../RAG-System/Chunking/Chunking-Strategy.md)

### 3. Indexer les données

```bash
# Générer les chunks
python generate_optimal_rag.py

# Indexer dans ChromaDB
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

### 4. Tester

```bash
python scripts/chat.py
```

Voir aussi : [RAG Quick Start](../RAG-System/RAG-Quick-Start.md)

---

## Configuration Fine-Tuning

### Prérequis

- ✅ RAG fonctionnel
- ✅ Compte OpenAI avec crédits ($5-20)
- ✅ Dataset de training (100+ exemples)

### Workflow

1. **Créer le dataset** :
   ```bash
   python scripts/prepare_finetuning_data.py --count 100
   ```

2. **Lancer le fine-tuning** :
   ```bash
   python scripts/finetune_model.py \
       --train data/finetuning/dataset_train.jsonl \
       --wait
   ```

3. **Tester le modèle** :
   ```bash
   python scripts/chat_hybrid.py \
       --finetuned-model ft:gpt-4o-mini-2024-07-18:org::xxxxx
   ```

Voir aussi : [Guide de fine-tuning](../Fine-Tuning/Fine-Tuning-Guide.md)

---

## Troubleshooting

### Erreur : "Module not found"

```bash
# Réinstaller les dépendances
pip install -r requirements-rag.txt --force-reinstall
```

### Erreur : "Collection not found"

```bash
# Indexer les chunks
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

### Erreur : "API key not found"

```bash
# Vérifier le fichier .env
cat .env

# Ou le créer
echo "OPENAI_API_KEY=votre-cle" > .env
```

### Ollama ne démarre pas

```bash
# Vérifier qu'Ollama est installé
ollama --version

# Lancer le serveur
ollama serve

# Télécharger un modèle
ollama pull llama3.2
```

### Performance lente

**Solutions** :
1. Utiliser un modèle plus léger (`llama3.2:1b` au lieu de `llama3.2`)
2. Réduire le nombre de chunks (`n_chunks=2` au lieu de 5)
3. Passer à un provider cloud (OpenAI/Claude)

---

## Vérification de l'installation

### Checklist complète

```bash
# 1. Python version
python --version  # Doit être 3.8+

# 2. Dépendances installées
pip list | grep -E "(chromadb|sentence-transformers|openai)"

# 3. Fichier .env existe
ls -la .env

# 4. Chunks indexés
ls -la chroma_db/

# 5. Test du chat
python scripts/chat.py
```

Si tous les tests passent : ✅ Installation réussie !

---

## Prochaines étapes

### Pour débuter
- 📖 [Guide de démarrage rapide](./Quick-Start-Guide.md)
- 🤖 [Utiliser le RAG](../RAG-System/RAG-Quick-Start.md)

### Pour approfondir
- 📚 [Architecture RAG](../RAG-System/RAG-System-Overview.md)
- 🎓 [Fine-Tuning](../Fine-Tuning/Fine-Tuning-Guide.md)

### Pour contribuer
- 🔧 [Guide de développement](../Development/Versioning-Guide.md)
- 📝 [Conventions de commit](../Development/Commitizen-Guide.md)

---

## Voir aussi

- [Documentation principale](../README.md)
- [Guide des providers LLM](../../GUIDE_PROVIDERS.md)
- [README RAG](../../RAG_README.md)
