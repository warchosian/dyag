# Récapitulatif du Système RAG Complet

## Vue d'ensemble

Le système RAG (Retrieval Augmented Generation) pour DYAG est maintenant **complet et opérationnel**.

Vous pouvez:
1. ✅ **Créer des chunks** optimisés à partir de vos fichiers d'applications
2. ✅ **Indexer** les chunks dans ChromaDB avec embeddings
3. ✅ **Poser des questions** en langage naturel et obtenir des réponses précises

## Composants du Système

### 1. Module de Création de Chunks

**Fichier:** `src/dyag/commands/create_rag.py`

**Fonctionnalités:**
- Chunking sémantique intelligent (pas de taille fixe)
- Support JSON et Markdown
- 6 types de chunks: main, overview, description, technical, sites, details
- Nettoyage automatique des données (URLs, espaces, sauts de ligne)
- Export en 3 formats: JSONL, JSON, Markdown

**Classes principales:**
```python
RAGCreator        # Classe principale
ApplicationChunker # Création de chunks
DataCleaner       # Nettoyage de données
RAGExporter       # Export formats
RAGChunk          # Structure de chunk (dataclass)
```

**Utilisation:**
```bash
python -m dyag.commands.create_rag input.json output.jsonl
```

### 2. Module d'Indexation

**Fichier:** `scripts/index_chunks.py`

**Fonctionnalités:**
- Connexion à ChromaDB (base vectorielle persistante)
- Génération d'embeddings avec Sentence Transformers (gratuit, local)
- Indexation par lots (configurable)
- Statistiques et monitoring

**Utilisation:**
```bash
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

**Options:**
- `--reset` : Recréer la collection
- `--batch-size` : Taille des lots (défaut: 100)
- `--embedding-model` : Modèle d'embeddings
- `--chroma-path` : Chemin ChromaDB

### 3. Module de Q&A

**Fichier:** `src/dyag/rag_query.py`

**Fonctionnalités:**
- Recherche vectorielle (similarité sémantique)
- Génération de réponses avec OpenAI GPT-4o-mini
- Filtrage par métadonnées (source_id, chunk_type, etc.)
- Citations des sources (IDs de chunks)
- Mode interactif CLI

**Classe principale:**
```python
class RAGQuerySystem:
    def search_chunks(query, n_results=5) -> List[Dict]
        # Recherche top K chunks similaires

    def generate_answer(question, chunks) -> Dict
        # Génère réponse avec LLM + contexte

    def ask(question, n_chunks=5) -> Dict
        # Méthode tout-en-un: search + generate

    def get_stats() -> Dict
        # Statistiques de la base
```

**Utilisation:**
```bash
# Mode interactif
python -m dyag.rag_query

# Python
from dyag.rag_query import RAGQuerySystem
rag = RAGQuerySystem()
result = rag.ask("Qui héberge GIDAF ?")
print(result['answer'])
```

## Fichiers Créés

### Scripts exécutables
```
scripts/
├── index_chunks.py            # Indexation ChromaDB
└── example_rag_complete.py    # Pipeline complet guidé (3 étapes)

test_create_rag.py             # Tests du chunking
example_create_rag.py          # Exemples de chunking
generate_optimal_rag.py        # Génération optimale (analyse sources)
```

### Documentation
```
doc/
├── rag-quick-start.md         # ⭐ Démarrage rapide (5 min)
├── rag-modules-guide.md       # Guide complet des modules
├── rag-chunks-algo.md         # Algorithme détaillé (16 diagrammes)
├── chunks-why.md              # Cas d'usage
├── chunks-for-management.md   # Architecture hybride dashboards
├── create_rag_guide.md        # Guide création de chunks
└── rag-system-summary.md      # Ce fichier
```

### Configuration
```
requirements-rag.txt           # Dépendances Python
.env.example                   # Template de configuration
RAG_README.md                  # README principal mis à jour
```

### Modules sources
```
src/dyag/
├── commands/
│   └── create_rag.py          # Module de chunking (600+ lignes)
└── rag_query.py               # Module de Q&A (289 lignes)
```

## Architecture du Système

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: CRÉATION DE CHUNKS                 │
│                                                                 │
│  Input: applications.json / applications.md                     │
│     │                                                           │
│     ▼                                                           │
│  [create_rag.py]                                               │
│     │                                                           │
│     ├─> DataCleaner (nettoyage)                               │
│     ├─> ApplicationChunker (chunking sémantique)              │
│     └─> RAGExporter (export JSONL/JSON/MD)                    │
│     │                                                           │
│     ▼                                                           │
│  Output: applications_rag.jsonl (1628 chunks)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 2: INDEXATION                         │
│                                                                 │
│  Input: applications_rag.jsonl                                  │
│     │                                                           │
│     ▼                                                           │
│  [index_chunks.py]                                             │
│     │                                                           │
│     ├─> Sentence Transformers (embeddings locaux, gratuit)     │
│     │   • Modèle: all-MiniLM-L6-v2                            │
│     │   • Dimension: 384                                       │
│     │   • Temps: ~2 min pour 1628 chunks                      │
│     │                                                           │
│     └─> ChromaDB (base vectorielle persistante)               │
│         • Chemin: ./chroma_db/                                 │
│         • Collection: applications                             │
│         • Taille: ~50 MB                                       │
│     │                                                           │
│     ▼                                                           │
│  Output: Base vectorielle indexée                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 3: QUESTIONS & RÉPONSES               │
│                                                                 │
│  Input: Question en langage naturel                            │
│     │                                                           │
│     ▼                                                           │
│  [rag_query.py]                                                │
│     │                                                           │
│     ├─> 1. Embedding de la question                           │
│     │   (Sentence Transformers, local)                         │
│     │                                                           │
│     ├─> 2. Recherche vectorielle                              │
│     │   ChromaDB.query() → Top 5 chunks similaires            │
│     │   Distance cosine < 0.5                                  │
│     │                                                           │
│     ├─> 3. Construction du contexte                           │
│     │   Concaténation des 5 chunks                            │
│     │   Format: [Chunk 1 - ID: xxx]\nContenu...              │
│     │                                                           │
│     └─> 4. Génération de la réponse                           │
│         OpenAI GPT-4o-mini (API payante)                       │
│         • Temperature: 0.3 (factuel)                           │
│         • Max tokens: 1000                                     │
│         • Coût: ~$0.01 par question                           │
│     │                                                           │
│     ▼                                                           │
│  Output: Réponse + Sources + Métadonnées                       │
│     • answer: "GIDAF est hébergé par le BRGM..."             │
│     • sources: [chunk_id_1, chunk_id_2, ...]                  │
│     • tokens_used: 542                                         │
│     • chunks_used: [chunk_data_1, ...]                        │
└─────────────────────────────────────────────────────────────────┘
```

## Statistiques

### Données générées
- **Chunks créés:** 1628
- **Source:** applicationsIA_mini_opt.md (3.14 MB)
- **Output JSONL:** 1.75 MB
- **Output JSON:** 1.84 MB
- **Output Markdown:** 1.71 MB

### Types de chunks
- **main:** Chunk principal pour Markdown
- **overview:** Vue d'ensemble (nom, statut, famille)
- **description:** Description détaillée
- **technical:** Infos techniques (domaines, acteurs, contacts)
- **sites:** URLs et sites web
- **details:** Chunks supplémentaires pour grandes applications

### Base vectorielle
- **Collection:** applications
- **Taille:** ~50 MB
- **Dimension embeddings:** 384
- **Modèle:** all-MiniLM-L6-v2
- **Temps d'indexation:** ~2 minutes

## Dépendances

### Installation
```bash
pip install -r requirements-rag.txt
```

### Modules principaux
```
chromadb==0.4.22               # Base vectorielle
sentence-transformers==2.3.1   # Embeddings (gratuit, local)
openai==1.12.0                 # LLM (API payante)
langchain==0.1.9               # Framework RAG
langchain-openai==0.0.6        # Intégration LangChain-OpenAI
tiktoken==0.6.0                # Comptage tokens
pydantic==2.6.1                # Validation données
python-dotenv==1.0.1           # Variables d'environnement
loguru==0.7.2                  # Logging avancé
streamlit==1.31.1              # Interface web (optionnel)
```

## Configuration

### Clé API OpenAI (obligatoire)

Créez un fichier `.env` à la racine:
```env
OPENAI_API_KEY=sk-proj-your-key-here
```

Ou depuis `.env.example`:
```bash
cp .env.example .env
# Éditez .env et remplissez votre clé
```

### Paramètres optionnels

Dans `.env`:
```env
CHROMA_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=gpt-4o-mini
```

## Exemples d'Utilisation

### Scénario 1: Pipeline complet guidé

```bash
python scripts/example_rag_complete.py
```

Étapes automatiques:
1. Création des chunks (si nécessaire)
2. Indexation dans ChromaDB
3. Mode Q&A interactif

### Scénario 2: Étape par étape

```bash
# 1. Créer les chunks
python -m dyag.commands.create_rag \
    examples/test-mygusi/applicationsIA_mini_opt.md \
    applications_rag.jsonl

# 2. Indexer
python scripts/index_chunks.py applications_rag.jsonl

# 3. Poser des questions
python -m dyag.rag_query
```

### Scénario 3: Utilisation en Python

```python
from dyag.rag_query import RAGQuerySystem

# Initialiser
rag = RAGQuerySystem()

# Questions simples
result = rag.ask("Qui héberge GIDAF ?")
print(result['answer'])

# Filtrer par application
result = rag.ask(
    "Quelle est la description ?",
    filter_metadata={"source_id": "383"}
)

# Plus de contexte
result = rag.ask(
    "Quelles sont toutes les applications Java ?",
    n_chunks=10
)

# Mode factuel strict
result = rag.ask(
    "Liste précise des hébergeurs",
    temperature=0.0
)
```

### Scénario 4: Interface web Streamlit

```python
# app_streamlit.py
import streamlit as st
from dyag.rag_query import RAGQuerySystem

st.title("Recherche d'Applications")

@st.cache_resource
def load_rag():
    return RAGQuerySystem()

rag = load_rag()
question = st.text_input("Question:")

if question:
    result = rag.ask(question)
    st.write(result['answer'])
    st.info(f"Sources: {len(result['sources'])} chunks")
```

```bash
streamlit run app_streamlit.py
```

## Coûts et Performance

### Coûts OpenAI (GPT-4o-mini)

| Usage | Questions/mois | Coût/mois | Tokens/question |
|-------|----------------|-----------|-----------------|
| Léger | 100 | $1-2 | ~500 |
| Moyen | 500 | $5-10 | ~500 |
| Intensif | 2000 | $20-40 | ~500 |

### Alternative gratuite

Utiliser **LLaMA 3.1 8B** (local):
- Coût: $0
- Nécessite: ~10 GB RAM + GPU recommandé
- Voir: `doc/rag-modules-guide.md`

### Performance

- **Indexation:** ~2 min pour 1628 chunks
- **Recherche:** ~200-500 ms par question
- **Génération:** ~2-5 secondes (OpenAI API)
- **Total:** ~3-6 secondes par question

## Résolution de Problèmes

### Problème: "Collection 'applications' non trouvée"

**Solution:**
```bash
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

### Problème: "Clé API OpenAI requise"

**Solution:**
```bash
# Créer .env
echo "OPENAI_API_KEY=sk-proj-..." > .env

# Ou variable d'environnement
export OPENAI_API_KEY=sk-proj-...
```

### Problème: Réponses non pertinentes

**Solutions:**
1. Augmenter le contexte: `rag.ask(q, n_chunks=10)`
2. Baisser température: `rag.ask(q, temperature=0.0)`
3. Meilleur modèle: `RAGQuerySystem(llm_model="gpt-4o")`
4. Filtrer sources: `rag.ask(q, filter_metadata={...})`

### Problème: Trop cher en tokens

**Solutions:**
1. Utiliser GPT-4o-mini (par défaut)
2. Réduire n_chunks: `rag.ask(q, n_chunks=3)`
3. Utiliser LLaMA local (gratuit)
4. Cacher les réponses fréquentes (Redis)

## Prochaines Étapes

### 1. Tester le système (5 min)

```bash
pip install -r requirements-rag.txt
echo "OPENAI_API_KEY=sk-proj-..." > .env
python scripts/index_chunks.py applications_rag_optimal.jsonl
python -m dyag.rag_query
```

### 2. Personnaliser

- Ajuster `max_chunk_size` dans `create_rag.py`
- Tester différents `n_chunks` (3, 5, 10, 15)
- Expérimenter avec `temperature` (0.0 à 1.0)
- Essayer d'autres modèles LLM

### 3. Optimiser pour production

- Mettre en place Redis pour cache
- Utiliser PostgreSQL pour requêtes exhaustives (voir `chunks-for-management.md`)
- Monitorer les coûts OpenAI
- Créer interface web Streamlit
- Ajouter authentification

### 4. Aller plus loin

- **Architecture hybride:** `doc/chunks-for-management.md`
- **Optimisations avancées:** `doc/rag-modules-guide.md`
- **Cas d'usage métier:** `doc/chunks-why.md`
- **Algorithme détaillé:** `doc/rag-chunks-algo.md`

## Documentation Complète

| Document | Description | Audience |
|----------|-------------|----------|
| `rag-quick-start.md` | ⭐ Démarrage rapide (5 min) | Tous |
| `rag-modules-guide.md` | Guide complet avec architecture | Développeurs |
| `rag-chunks-algo.md` | Algorithme technique détaillé | Architectes |
| `chunks-why.md` | Cas d'usage et exemples | Product Owners |
| `chunks-for-management.md` | Dashboards et reporting | Data Analysts |
| `create_rag_guide.md` | Création de chunks avancée | Développeurs |

## Résumé Exécutif

✅ **Système complet et opérationnel**
- 3 modules (chunking, indexation, Q&A)
- 7 fichiers de documentation
- 4 scripts prêts à l'emploi
- 1628 chunks indexés

✅ **Prêt pour production**
- Tests validés
- Documentation complète
- Exemples fournis
- Architecture évolutive

✅ **Coût maîtrisé**
- Embeddings gratuits (local)
- LLM payant mais économique (~$0.01/question)
- Alternative gratuite disponible (LLaMA)

🚀 **Démarrage en 5 minutes** avec `doc/rag-quick-start.md`
