# 🚀 Guide de démarrage rapide DYAG

> Commencez à utiliser DYAG en 5 minutes !

## Table des matières

- [Qu'est-ce que DYAG ?](#quest-ce-que-dyag)
- [Installation rapide](#installation-rapide)
- [Premier lancement](#premier-lancement)
- [Prochaines étapes](#prochaines-étapes)

---

## Qu'est-ce que DYAG ?

**DYAG** est un outil polyvalent qui offre :

### 📄 Conversion de documents
- **Markdown → HTML** avec support des diagrammes
- **Images → PDF**
- **HTML → PDF**

### 🤖 Système RAG (Retrieval Augmented Generation)
- **Chat intelligent** pour interroger vos documents
- **Base vectorielle** pour recherche sémantique
- **Support multi-providers** : OpenAI, Claude, Ollama (gratuit)

### 🎓 Fine-Tuning (optionnel)
- **Modèles personnalisés** adaptés à votre domaine
- **Combinaison RAG + Fine-Tuning** pour des résultats optimaux

---

## Installation rapide

### Prérequis

- **Python 3.8+** installé
- **Git** (pour cloner le projet)

### Étape 1 : Cloner le projet

```bash
git clone https://votre-repo/dyag.git
cd dyag
```

### Étape 2 : Installer les dépendances

```bash
# Avec pip
pip install -r requirements-rag.txt

# Ou avec conda/poetry selon votre setup
poetry install
```

### Étape 3 : Configuration (optionnel pour RAG)

Créer un fichier `.env` à la racine :

```bash
# === Provider LLM (choisir un) ===

# Option 1 : Ollama (GRATUIT, local)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434

# Option 2 : OpenAI (nécessite API key)
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-proj-votre-cle-ici

# Option 3 : Claude (nécessite API key)
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
```

**Recommandation** : Démarrez avec **Ollama** (gratuit) !

---

## Premier lancement

### Option A : Utiliser les outils de conversion

```bash
# Convertir Markdown vers HTML
python -m dyag md2html mon-fichier.md

# Convertir images vers PDF
python -m dyag img2pdf image1.png image2.jpg --output resultat.pdf

# Compresser un PDF
python -m dyag compresspdf gros-fichier.pdf --output compresse.pdf
```

### Option B : Utiliser le système RAG

#### 1. Préparer vos données

Créez un fichier `mes_applications.jsonl` avec vos données :

```jsonl
{"id": "1", "nom": "GIDAF", "hebergeur": "SI-RAPP", "technologies": ["Java", "Oracle"]}
{"id": "2", "nom": "MYGUSI", "hebergeur": "SI-RAPP", "technologies": ["Java", "Angular"]}
```

Ou utilisez le fichier d'exemple fourni : `applications_rag_optimal.jsonl`

#### 2. Indexer les données

```bash
# Générer les chunks optimisés
python generate_optimal_rag.py

# Indexer dans ChromaDB
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

#### 3. Lancer le chat

```bash
python scripts/chat.py
```

Exemples de questions :
- "Qui héberge GIDAF ?"
- "Quelles applications utilisent Java ?"
- "Quelle est la description de MYGUSI ?"

---

## Résultat attendu

### Chat RAG en action

```
======================================================================
CHAT RAG - Posez vos questions sur les applications
======================================================================
Timeout configuré: 10 minutes

Initialisation...

       RAG OK !

Statistiques:
  - Chunks indexés: 1687
  - Modèle LLM: ollama/llama3.2

======================================================================
MODE CHAT INTERACTIF
======================================================================

Vous: Qui héberge GIDAF ?

[Recherche en cours...]
```