# Guide de Démarrage Rapide - Système RAG

Guide pour mettre en place et utiliser le système de Questions & Réponses avec RAG en **5 minutes**.

## Prérequis

1. **Python 3.8+** installé
2. **Clé API OpenAI** (pour les réponses du LLM)
   - Obtenez une clé sur: https://platform.openai.com/api-keys
   - Coût estimé: ~$0.01 par question (avec GPT-4o-mini)

## Installation - 3 étapes

### Étape 1: Installer les dépendances

```bash
pip install -r requirements-rag.txt
```

Ceci installe:
- `chromadb` - Base vectorielle
- `sentence-transformers` - Embeddings (gratuit, local)
- `openai` - Client LLM
- `langchain` - Framework RAG
- `streamlit` - Interface web (optionnel)

**Temps:** ~2 minutes

### Étape 2: Configurer la clé API OpenAI

Créez un fichier `.env` à la racine du projet:

```env
OPENAI_API_KEY=sk-proj-...votre_cle_ici...
```

**Temps:** 30 secondes

### Étape 3: Indexer vos chunks

```bash
# Depuis la racine du projet
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

Sortie attendue:
```
Connexion a ChromaDB: .\chroma_db
Chargement du modele d'embedding: all-MiniLM-L6-v2
Modele charge avec dimension: 384

Chargement des chunks depuis: applications_rag_optimal.jsonl
Chunks charges: 1628

Indexation de 1628 chunks...
Lot 1/17: 100 chunks indexes
Lot 2/17: 100 chunks indexes
...
Lot 17/17: 28 chunks indexes

Indexation terminee:
  - Indexes: 1628
  - Erreurs: 0
  - Taux de reussite: 100.0%
```

**Temps:** ~2 minutes (selon votre machine)

## Utilisation

### Option A: Mode interactif simple

```bash
python -m dyag.rag_query
```

```
Initialisation du systeme RAG...

Statistiques:
  - Chunks indexes: 1628
  - Modele LLM: gpt-4o-mini

==============================================================
Mode interactif - Posez vos questions (Ctrl+C pour quitter)
==============================================================

❓ Question: Qui héberge GIDAF ?

🔍 Recherche en cours...

💬 Réponse:
GIDAF est hébergé par le BRGM (Bureau de Recherches Géologiques et Minières).
Source: [Chunk a1b2c3d4]

📊 Métadonnées:
  - Sources: 5 chunks
  - Tokens: 342
  - IDs: a1b2c3d4, e5f6g7h8, i9j0k1l2...
```

### Option B: Script Python

```python
from dyag.rag_query import RAGQuerySystem

# Initialiser
rag = RAGQuerySystem()

# Poser une question
result = rag.ask("Quelles sont les applications en Java ?")

# Afficher la réponse
print(result['answer'])

# Accéder aux métadonnées
print(f"Sources: {len(result['sources'])} chunks")
print(f"Tokens utilisés: {result['tokens_used']}")
print(f"Chunks: {result['sources']}")
```

### Option C: Script complet avec guide

```bash
python scripts/example_rag_complete.py
```

Ce script vous guide à travers:
1. Création des chunks (si nécessaire)
2. Indexation
3. Mode Q&A interactif

## Exemples de questions

### Questions simples

```
Qui héberge GIDAF ?
Quelle est la description de MYGUSI ?
Quel est le gestionnaire de WIKISI ?
```

### Questions complexes

```
Quelles sont toutes les applications hébergées par le BRGM ?
Liste les applications utilisant Java comme technologie.
Quels sont les services web disponibles pour les applications de gestion ?
```

### Questions analytiques

```
Combien d'applications utilisent Oracle comme base de données ?
Quelles sont les principales technologies utilisées dans le SI ?
Qui sont les principaux hébergeurs d'applications ?
```

## Filtrage par application

Pour poser une question sur une **application spécifique**:

```python
# Uniquement sur l'application ID 383 (GIDAF)
result = rag.ask(
    "Quelle est la description ?",
    filter_metadata={"source_id": "383"}
)
```

## Personnalisation

### Changer le nombre de chunks

```python
# Utiliser 10 chunks au lieu de 5 (par défaut)
result = rag.ask(
    "Ma question",
    n_chunks=10  # Plus de contexte = réponses plus complètes
)
```

### Ajuster la créativité

```python
# Temperature = 0 (précis) à 1 (créatif)
result = rag.ask(
    "Ma question",
    temperature=0.0  # Réponses très factuelles
)
```

### Utiliser un autre modèle LLM

```python
rag = RAGQuerySystem(
    llm_model="gpt-4o"  # Plus précis mais plus cher
)
```

## Interface Web (Optionnel)

Créez `app_streamlit.py`:

```python
import streamlit as st
from dyag.rag_query import RAGQuerySystem

st.title("Recherche d'Applications - RAG")

# Initialiser (avec cache)
@st.cache_resource
def load_rag():
    return RAGQuerySystem()

rag = load_rag()

# Interface
question = st.text_input("Posez votre question:")

if question:
    with st.spinner("Recherche en cours..."):
        result = rag.ask(question)

    st.subheader("Réponse:")
    st.write(result['answer'])

    st.subheader("Sources:")
    st.write(f"{len(result['sources'])} chunks utilisés")
    st.write(f"Tokens: {result['tokens_used']}")

    with st.expander("Voir les chunks sources"):
        for i, chunk in enumerate(result['chunks_used'], 1):
            st.write(f"**Chunk {i}** (ID: {chunk['id']})")
            st.write(chunk['content'][:300] + "...")
```

Lancez avec:
```bash
streamlit run app_streamlit.py
```

## Coûts Estimés

Avec **GPT-4o-mini** (modèle par défaut):

| Usage | Questions/mois | Coût/mois |
|-------|----------------|-----------|
| Léger | 100 | $1-2 |
| Moyen | 500 | $5-10 |
| Intensif | 2000 | $20-40 |

**Gratuit (local):**
- Remplacez OpenAI par **LLaMA 3.1 8B** (voir `rag-modules-guide.md`)
- Nécessite ~10 GB RAM et GPU recommandé

## Résolution de Problèmes

### Erreur: "Collection 'applications' non trouvée"

```bash
# Réindexer les chunks
python scripts/index_chunks.py applications_rag_optimal.jsonl --reset
```

### Erreur: "Clé API OpenAI requise"

```bash
# Vérifier le fichier .env
cat .env

# Ou définir la variable d'environnement
export OPENAI_API_KEY=sk-proj-...
```

### Erreur: "No module named 'chromadb'"

```bash
# Réinstaller les dépendances
pip install -r requirements-rag.txt
```

### Réponses non pertinentes

1. **Augmenter le nombre de chunks:**
   ```python
   result = rag.ask("Question", n_chunks=10)
   ```

2. **Baisser la température:**
   ```python
   result = rag.ask("Question", temperature=0.0)
   ```

3. **Utiliser un meilleur modèle:**
   ```python
   rag = RAGQuerySystem(llm_model="gpt-4o")
   ```

## Commandes Utiles

```bash
# Réindexer complètement
python scripts/index_chunks.py applications_rag_optimal.jsonl --reset

# Indexer avec un autre modèle d'embedding
python scripts/index_chunks.py applications_rag_optimal.jsonl \
    --embedding-model all-mpnet-base-v2

# Mode Q&A avec statistiques
python -m dyag.rag_query

# Script complet guidé
python scripts/example_rag_complete.py
```

## Architecture Simplifiée

```
┌─────────────┐
│  Question   │
│  utilisateur│
└──────┬──────┘
       │
       ▼
┌──────────────────┐      ┌─────────────┐
│  1. Embedding    │─────>│ ChromaDB    │
│  (local, gratuit)│      │ 1628 chunks │
└──────────────────┘      └──────┬──────┘
                                 │
                                 │ Top 5 chunks
                                 │ similaires
                                 ▼
                          ┌─────────────┐
                          │ 2. Contexte │
                          │  (5 chunks) │
                          └──────┬──────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │ 3. OpenAI   │
                          │  GPT-4o-mini│
                          │  (payant)   │
                          └──────┬──────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │  Réponse    │
                          │  + Sources  │
                          └─────────────┘
```

## Prochaines Étapes

1. **Testez avec vos propres questions** pour valider la pertinence
2. **Ajustez les paramètres** (n_chunks, temperature) selon vos besoins
3. **Consultez la documentation avancée** dans `rag-modules-guide.md`
4. **Explorez l'architecture hybride** dans `chunks-for-management.md`

## Support

- **Documentation complète:** `doc/rag-modules-guide.md`
- **Algorithme de chunking:** `doc/rag-chunks-algo.md`
- **Use cases:** `doc/chunks-why.md`
- **Dashboard management:** `doc/chunks-for-management.md`
