# Guide Complet : Créer un RAG de Qualité avec Dyag

Ce guide vous accompagne pas-à-pas dans la création d'un système RAG (Retrieval-Augmented Generation) de haute qualité à partir de données JSON d'applications, en utilisant Dyag via CLI et MCP.

## 📋 Table des matières

- [Introduction](#introduction)
- [Prérequis](#prérequis)
- [Vue d'ensemble du workflow](#vue-densemble-du-workflow)
- [Étape 1 : Analyse des données source](#étape-1--analyse-des-données-source)
- [Étape 2 : Préparation et chunking des données](#étape-2--préparation-et-chunking-des-données)
- [Étape 3 : Indexation dans ChromaDB](#étape-3--indexation-dans-chromadb)
- [Étape 4 : Configuration du LLM](#étape-4--configuration-du-llm)
- [Étape 5 : Interrogation du RAG](#étape-5--interrogation-du-rag)
- [Étape 6 : Évaluation de la qualité](#étape-6--évaluation-de-la-qualité)
- [Étape 7 : Amélioration itérative](#étape-7--amélioration-itérative)
- [Annexes](#annexes)

---

## Introduction

Ce guide couvre **deux workflows** pour créer un système RAG :

1. **Workflow JSON** (original) : À partir de `applicationsIA_mini_normalized.json`
2. **Workflow Markdown** (nouveau) : À partir de `applicationsIA_mini_opt.md` ✨

Les deux workflows aboutissent au même résultat : un système RAG capable de répondre intelligemment à des questions sur les applications du système d'information français.

> 📝 **Journal de réalisation** : Consultez `doc/RAG_WORKFLOW_JOURNAL.md` pour un exemple complet d'indexation réussie avec le workflow Markdown.

### Qu'est-ce qu'un RAG de qualité ?

Un RAG de qualité doit :
- ✅ Retrouver les informations pertinentes (haute précision)
- ✅ Générer des réponses exactes et contextualisées
- ✅ Citer ses sources avec précision
- ✅ Gérer l'absence d'information gracieusement
- ✅ Être rapide et efficace

---

## Prérequis

### Installation

```bash
# Installation de base
poetry install

# Installation avec support RAG
poetry install -E rag
# ou
pip install -r requirements-rag.txt
```

### Configuration

Créez un fichier `.env` à la racine du projet :

```env
# Provider LLM (choisissez-en un)
LLM_PROVIDER=ollama  # GRATUIT - Local
# LLM_PROVIDER=openai  # Payant
# LLM_PROVIDER=anthropic  # Payant

# Configuration Ollama (GRATUIT)
LLM_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=300

# Ou OpenAI (Payant ~$0.01/question)
# OPENAI_API_KEY=sk-proj-votre-clé

# Ou Anthropic (Payant ~$0.015/question)
# ANTHROPIC_API_KEY=sk-ant-votre-clé

# Configuration ChromaDB
CHROMA_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Installation d'Ollama (recommandé - GRATUIT)

```bash
# Windows/Mac/Linux
# Téléchargez depuis https://ollama.com/download

# Puis installez un modèle
ollama pull llama3.2

# Vérifiez qu'Ollama fonctionne
ollama list
```

---

## Vue d'ensemble du workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    WORKFLOW RAG COMPLET                      │
└─────────────────────────────────────────────────────────────┘

1. 📊 ANALYSE DES DONNÉES
   └─> Comprendre la structure JSON

2. 🔧 PRÉPARATION & CHUNKING
   └─> dyag prepare-rag
       - Normalisation des données
       - Découpage en chunks optimaux
       - Nettoyage et enrichissement

3. 📇 INDEXATION
   └─> dyag index-rag
       - Création des embeddings
       - Stockage dans ChromaDB
       - Indexation vectorielle

4. ⚙️ CONFIGURATION LLM
   └─> Choix du provider (Ollama/OpenAI/Anthropic)
       - Configuration .env
       - Test de connexion

5. 💬 INTERROGATION
   └─> dyag query-rag
       - Recherche sémantique
       - Génération de réponse
       - Citations des sources

6. 📊 ÉVALUATION
   └─> dyag evaluate-rag
       - Création dataset de test
       - Métriques de qualité
       - Analyse des erreurs

7. 🔄 AMÉLIORATION
   └─> Itération sur le chunking
       - Ajustement des paramètres
       - Ré-indexation
       - Re-test
```

---

## Étape 1 : Analyse des données source

### 1.1 Examen de la structure JSON

**Commande CLI :**
```bash
# Examiner le fichier JSON
cat examples/test-mygusi/applicationsIA_mini_normalized.json | python -m json.tool | head -100
```

**Structure des données :**
```json
{
  "applicationsia mini": [
    {
      "id": 1238,
      "nom": "6tzen",
      "nom long": "outil national de dematerialisation...",
      "statut si": "en production",
      "descriptif": "la dematerialisation des procedures...",
      "domaines et sous domaines": [...],
      "sites": [...],
      "acteurs": [...],
      "contacts": [...]
    }
  ]
}
```

### 1.2 Statistiques du dataset

**Commande CLI :**
```bash
# Compter le nombre d'applications
python -c "import json; data=json.load(open('examples/test-mygusi/applicationsIA_mini_normalized.json')); print(f'Nombre d\\'applications: {len(data[\"applicationsia mini\"])}')"
```

**📊 Utilisation via MCP :**
```json
{
  "tool": "dyag_analyze_training",
  "arguments": {
    "applications": "examples/test-mygusi/applicationsIA_mini_normalized.json",
    "training": "training_data.jsonl"
  }
}
```
*Note: Cette commande MCP existe déjà*

### 1.3 Comprendre les champs clés

Les champs les plus importants pour le RAG :
- **`nom`** : Nom court de l'application (identifiant principal)
- **`nom long`** : Description complète du nom
- **`descriptif`** : Texte riche contenant les détails fonctionnels
- **`domaines et sous domaines`** : Contexte métier
- **`statut si`** : État actuel (production, construction, etc.)
- **`sites`** : URLs de l'application
- **`acteurs`** : Organisations responsables

**💡 Conseil :** Ces champs seront utilisés pour créer des chunks riches et contextualisés.

---

## Étape 2 : Préparation et chunking des données

### 2.1 Comprendre le chunking optimal

Le chunking est **crucial** pour la qualité du RAG. Un bon chunk doit :
- Contenir une information **complète et autonome**
- Avoir une **taille optimale** (500-2000 tokens)
- Préserver le **contexte**
- Éviter les **coupures au milieu d'une phrase**

### 2.2 Stratégies de chunking pour les applications

Pour notre fichier JSON d'applications, nous avons **3 stratégies** :

#### Stratégie A : Un chunk par application (recommandé pour petites applications)
```
Chunk = {
  "nom": "6tzen",
  "descriptif": "...",
  "domaines": "transports routiers",
  ...
}
```

#### Stratégie B : Chunks par section (recommandé pour grandes applications)
```
Chunk 1 = Informations générales (nom, statut, domaine)
Chunk 2 = Descriptif détaillé
Chunk 3 = Acteurs et contacts
Chunk 4 = Sites et URLs
```

#### Stratégie C : Hybride avec overlap
```
Chunk 1 = [Infos générales + début descriptif]
Chunk 2 = [fin Infos générales + descriptif complet + début acteurs] (overlap)
Chunk 3 = [descriptif + acteurs + sites] (overlap)
```

### 2.3 Préparation avec dyag

**Commande CLI :**
```bash
# Créer les chunks avec la stratégie optimale
dyag prepare-rag \
  examples/test-mygusi/applicationsIA_mini_normalized.json \
  --output prepared/applications_chunks.jsonl \
  --chunk-strategy semantic \
  --chunk-size 1000 \
  --overlap 200 \
  --add-context \
  --verbose
```

**Paramètres expliqués :**
- `--chunk-strategy semantic` : Découpage intelligent par sections sémantiques
- `--chunk-size 1000` : Taille cible de ~1000 tokens par chunk
- `--overlap 200` : 200 tokens de chevauchement entre chunks
- `--add-context` : Ajoute le nom de l'application à chaque chunk
- `--verbose` : Affiche les détails du traitement

**📊 Utilisation via MCP :**
```json
{
  "tool": "dyag_prepare_rag",
  "arguments": {
    "input": "examples/test-mygusi/applicationsIA_mini_normalized.json",
    "output": "prepared/applications_chunks.jsonl",
    "chunk_strategy": "semantic",
    "chunk_size": 1000,
    "overlap": 200,
    "add_context": true,
    "verbose": true
  }
}
```
*⚠️ Note: Cette commande MCP **n'existe pas encore** et doit être ajoutée*

### 2.4 Vérification des chunks créés

**Commande CLI :**
```bash
# Examiner les chunks créés
head -5 prepared/applications_chunks.jsonl

# Compter les chunks
wc -l prepared/applications_chunks.jsonl

# Vérifier la taille moyenne des chunks
python -c "
import json
chunks = [json.loads(line) for line in open('prepared/applications_chunks.jsonl')]
avg_len = sum(len(c['content']) for c in chunks) / len(chunks)
print(f'Nombre de chunks: {len(chunks)}')
print(f'Taille moyenne: {avg_len:.0f} caractères')
print(f'Min: {min(len(c[\"content\"]) for c in chunks)}')
print(f'Max: {max(len(c[\"content\"]) for c in chunks)}')
"
```

**Résultat attendu :**
```
Nombre de chunks: 45
Taille moyenne: 850 caractères
Min: 400
Max: 1500
```

**💡 Conseil :** Si la taille moyenne est trop grande (>1500), réduisez `--chunk-size`. Si trop petite (<500), augmentez-la.

---

## Étape 2.5 : Alternative - Workflow Markdown (NOUVEAU) ✨

Si vous avez déjà un fichier Markdown optimisé (comme `applicationsIA_mini_opt.md`), vous pouvez utiliser directement `prepare-rag` pour le chunker.

### Avantages du workflow Markdown
- ✅ Pas besoin de convertir JSON → Markdown
- ✅ Chunking automatique avec gestion du chevauchement
- ✅ Export JSON automatique pour l'indexation
- ✅ Plus rapide si le Markdown existe déjà

### Commande de préparation Markdown

**Commande CLI :**
```bash
# Créer le répertoire
mkdir -p prepared

# Chunker le fichier Markdown
dyag prepare-rag examples/test-mygusi/applicationsIA_mini_opt.md \
  --output prepared/applicationsIA_mini_chunks.jsonl \
  --chunk size \
  --chunk-size 1000 \
  --chunk-overlap 200 \
  --extract-json \
  --verbose
```

**Paramètres expliqués :**
- `--chunk size` : Découpage par taille de caractères (recommandé pour Markdown long)
- `--chunk section` : Alternative pour découper par sections Markdown (# headers)
- `--chunk-size 1000` : Taille cible par chunk
- `--chunk-overlap 200` : Chevauchement entre chunks pour préserver le contexte
- `--extract-json` : Génère aussi un fichier JSON avec métadonnées
- `--verbose` : Affiche la progression

**Résultat attendu :**
```
✓ 1010 chunks créés
  Taille moyenne: 6244 caractères
  Fichiers générés:
  - prepared/applicationsIA_mini_chunks.jsonl (Markdown nettoyé)
  - prepared/applicationsIA_mini_chunks.json (Métadonnées + chunks)
```

### ⚠️ Problème connu : IDs numériques

Le fichier JSON généré contient des IDs numériques qui doivent être convertis en strings pour ChromaDB.

**Script de correction :**
```python
import json

# Charger le JSON
with open('prepared/applicationsIA_mini_chunks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Convertir les IDs en strings
for chunk in data['chunks']:
    chunk['id'] = f'chunk_{chunk["id"]}'

# Sauvegarder le JSON corrigé
with open('prepared/applicationsIA_mini_chunks_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✓ Fichier corrigé créé: prepared/applicationsIA_mini_chunks_fixed.json")
```

**Résultat :**
```
✓ Fichier corrigé créé: prepared/applicationsIA_mini_chunks_fixed.json
  IDs: chunk_0, chunk_1, chunk_2...
```

### Vérification de la structure

```bash
python -c "
import json
data = json.load(open('prepared/applicationsIA_mini_chunks_fixed.json', 'r', encoding='utf-8'))
print(f'Chunks: {len(data[\"chunks\"])}')
print(f'First chunk ID: {data[\"chunks\"][0][\"id\"]}')
print(f'ID type: {type(data[\"chunks\"][0][\"id\"])}')
"
```

**Résultat attendu :**
```
Chunks: 1010
First chunk ID: chunk_0
ID type: <class 'str'>
```

💡 **Note** : Une fois le JSON corrigé, passez directement à l'étape 3 (Indexation) en utilisant `prepared/applicationsIA_mini_chunks_fixed.json`

---

## Étape 3 : Indexation dans ChromaDB

### 3.1 Comprendre l'indexation vectorielle

L'indexation transforme vos chunks en **vecteurs numériques** (embeddings) qui capturent leur sens sémantique. Dyag utilise :
- **Sentence Transformers** (all-MiniLM-L6-v2 par défaut)
- **ChromaDB** pour le stockage vectoriel
- **Recherche par similarité cosinus**

### 3.2 Première indexation

**Commande CLI :**
```bash
# Indexer les chunks dans ChromaDB
dyag index-rag \
  prepared/applications_chunks.jsonl \
  --collection applications_ia \
  --chroma-path ./chroma_db \
  --embedding-model all-MiniLM-L6-v2 \
  --batch-size 100 \
  --reset \
  --verbose
```

**Paramètres expliqués :**
- `--collection applications_ia` : Nom de la collection ChromaDB
- `--chroma-path ./chroma_db` : Où stocker la base vectorielle
- `--embedding-model all-MiniLM-L6-v2` : Modèle d'embeddings (léger et rapide)
- `--batch-size 100` : Indexer par batches de 100 chunks
- `--reset` : Efface la collection si elle existe (⚠️ attention en production!)
- `--verbose` : Affiche la progression

**📊 Utilisation via MCP :**
```json
{
  "tool": "dyag_index_rag",
  "arguments": {
    "input": "prepared/applications_chunks.jsonl",
    "collection": "applications_ia",
    "chroma_path": "./chroma_db",
    "embedding_model": "all-MiniLM-L6-v2",
    "batch_size": 100,
    "reset": true
  }
}
```
*✅ Cette commande MCP existe déjà*

### 3.3 Vérification de l'indexation

**Commande CLI (Python) :**
```python
# Vérifier que l'indexation a fonctionné
python -c "
import chromadb
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection('applications_ia')
print(f'Nombre de documents indexés: {collection.count()}')

# Tester une recherche simple
results = collection.query(
    query_texts=['application transport routier'],
    n_results=3
)
print(f'\\nTop 3 résultats pour \"application transport routier\":')
for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0]), 1):
    print(f'{i}. Distance: {dist:.3f}')
    print(f'   Extrait: {doc[:100]}...')
"
```

**Résultat attendu :**
```
Nombre de documents indexés: 45

Top 3 résultats pour "application transport routier":
1. Distance: 0.234
   Extrait: Application 6tzen - outil national de dematerialisation des demarches des transports routiers...
2. Distance: 0.456
   Extrait: Application RNTR - registre national des transports routiers...
3. Distance: 0.578
   Extrait: ...
```

**💡 Conseil :** Une distance < 0.5 indique une bonne similarité sémantique.

---

## Étape 4 : Configuration du LLM

### 4.1 Choix du provider

| Provider | Coût | Qualité | Vitesse | Setup |
|----------|------|---------|---------|-------|
| **Ollama** (local) | **GRATUIT** | ⭐⭐⭐⭐ | ⭐⭐⭐ | Facile |
| **OpenAI GPT-4** | ~$0.01/question | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Très facile |
| **Anthropic Claude** | ~$0.015/question | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Facile |

**Recommandation :** Commencez avec **Ollama** (gratuit) pour le développement et les tests.

### 4.2 Configuration Ollama (GRATUIT)

```bash
# 1. Installer Ollama
# Windows/Mac/Linux : https://ollama.com/download

# 2. Installer un modèle
ollama pull llama3.2

# 3. Vérifier qu'il fonctionne
ollama run llama3.2 "Bonjour"

# 4. Configurer .env
echo "LLM_PROVIDER=ollama" >> .env
echo "LLM_MODEL=llama3.2" >> .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env
```

### 4.3 Configuration OpenAI (PAYANT)

```bash
# 1. Obtenir une clé API sur https://platform.openai.com/api-keys

# 2. Configurer .env
echo "LLM_PROVIDER=openai" >> .env
echo "OPENAI_API_KEY=sk-proj-votre-clé" >> .env
```

### 4.4 Configuration Anthropic Claude (PAYANT)

```bash
# 1. Obtenir une clé API sur https://console.anthropic.com/

# 2. Configurer .env
echo "LLM_PROVIDER=anthropic" >> .env
echo "ANTHROPIC_API_KEY=sk-ant-votre-clé" >> .env
```

### 4.5 Test de configuration

**Commande CLI :**
```bash
# Tester la connexion LLM
python -c "
from dyag.llm_providers import LLMProviderFactory
provider = LLMProviderFactory.create_provider()
print(f'Provider: {provider.get_model_name()}')
response = provider.generate('Dis bonjour en une phrase')
print(f'Réponse: {response}')
"
```

**Résultat attendu :**
```
Provider: llama3.2 (Ollama)
Réponse: Bonjour ! Comment puis-je vous aider aujourd'hui ?
```

---

## Étape 5 : Interrogation du RAG

### 5.1 Première requête simple

**Commande CLI :**
```bash
# Poser une question au RAG
dyag query-rag \
  "Qu'est-ce que l'application 6tzen ?" \
  --collection applications_ia \
  --n-chunks 5 \
  --verbose
```

**Paramètres expliqués :**
- `"Qu'est-ce que l'application 6tzen ?"` : La question
- `--collection applications_ia` : Collection ChromaDB à interroger
- `--n-chunks 5` : Récupérer les 5 chunks les plus pertinents
- `--verbose` : Afficher les chunks récupérés et la source

**📊 Utilisation via MCP :**
```json
{
  "tool": "dyag_rag_query",
  "arguments": {
    "question": "Qu'est-ce que l'application 6tzen ?",
    "collection": "applications_ia",
    "n_chunks": 5
  }
}
```
*✅ Cette commande MCP existe déjà*

**Résultat attendu :**
```
╔══════════════════════════════════════════════════════════════╗
║                    RÉSULTATS DE LA REQUÊTE RAG               ║
╚══════════════════════════════════════════════════════════════╝

Question: Qu'est-ce que l'application 6tzen ?

───────────────────────────────────────────────────────────────
Chunks récupérés (5):
───────────────────────────────────────────────────────────────

[1] Distance: 0.234 | Source: application_1238
Application 6tzen - outil national de dematerialisation des
demarches des transports routiers. Statut: en production.
La dematerialisation des procedures administratives du registre
des entreprises de transport par route...

[2] Distance: 0.456 | Source: application_1238_descriptif
Descriptif détaillé: la dematerialisation s'inscrit dans le
cadre du programme gouvernemental de simplification...

───────────────────────────────────────────────────────────────
Réponse générée:
───────────────────────────────────────────────────────────────

L'application 6tzen est l'outil national de dématérialisation
des démarches des transports routiers, actuellement en production.
Elle permet aux entreprises de transport routier d'effectuer leurs
démarches administratives en ligne, incluant les demandes
d'autorisation d'exercer, le renouvellement de licences, et les
demandes de copies conformes.

Les principaux avantages pour les usagers sont:
- Gain de temps lors du remplissage des dossiers
- Suivi simplifié de l'état des demandes
- Instruction facilitée grâce aux échanges en ligne
- Diminution globale des délais de traitement

Source: application_1238
```

### 5.2 Questions avancées

**Exemples de questions à tester :**

```bash
# Question sur le statut
dyag query-rag "Quelles applications sont en production ?" --collection applications_ia

# Question sur un domaine métier
dyag query-rag "Liste les applications du domaine biodiversité" --collection applications_ia

# Question comparative
dyag query-rag "Quelle est la différence entre 6tzen et SINP ?" --collection applications_ia

# Question avec contexte
dyag query-rag "Qui sont les acteurs responsables de 6tzen ?" --collection applications_ia
```

### 5.3 Ajuster le nombre de chunks

Le paramètre `--n-chunks` (ou `n_chunks` pour MCP) est crucial :

- **3 chunks** : Rapide, risque de manquer du contexte
- **5 chunks** : ⭐ **Recommandé** - Bon équilibre
- **10 chunks** : Plus de contexte, mais plus lent et risque de "bruit"
- **20 chunks** : Maximum, pour questions très larges

**Test de sensibilité :**
```bash
# Tester avec différents nombres de chunks
for n in 3 5 10; do
  echo "=== Test avec $n chunks ==="
  dyag query-rag "Qu'est-ce que 6tzen ?" --collection applications_ia --n-chunks $n
done
```

---

## Étape 6 : Évaluation de la qualité

### 6.1 Créer un dataset d'évaluation

Un bon dataset d'évaluation contient des paires question/réponse de référence.

**Format JSONL attendu :**
```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "Qu'est-ce que 6tzen ?"}, {"role": "assistant", "content": "L'application 6tzen est..."}]}
```

**Commande CLI pour créer le dataset :**
```bash
# Créer un dataset d'évaluation automatiquement
dyag markdown-to-rag \
  examples/test-mygusi/applicationsIA_mini_normalized.json \
  --output evaluation/test_dataset.jsonl \
  --num-questions 20 \
  --question-types factual,comparative,listing \
  --verbose
```

**📊 Utilisation via MCP :**
```json
{
  "tool": "dyag_create_rag",
  "arguments": {
    "input": "examples/test-mygusi/applicationsIA_mini_normalized.json",
    "output": "evaluation/test_dataset.jsonl",
    "num_questions": 20,
    "question_types": ["factual", "comparative", "listing"]
  }
}
```
*⚠️ Note: Cette commande MCP **n'existe pas encore** et doit être ajoutée*

### 6.2 Évaluation avec le dataset

**Commande CLI :**
```bash
# Évaluer le RAG sur le dataset de test
dyag evaluate-rag \
  evaluation/test_dataset.jsonl \
  --collection applications_ia \
  --output evaluation/results.json \
  --metrics all \
  --verbose
```

**📊 Utilisation via MCP :**
```json
{
  "tool": "dyag_evaluate_rag",
  "arguments": {
    "dataset": "evaluation/test_dataset.jsonl",
    "collection": "applications_ia",
    "output": "evaluation/results.json"
  }
}
```
*✅ Cette commande MCP existe déjà*

**Résultat attendu :**
```json
{
  "total_questions": 20,
  "correct_answers": 17,
  "accuracy": 0.85,
  "average_confidence": 0.78,
  "average_retrieval_time_ms": 145,
  "average_generation_time_ms": 2340,
  "metrics": {
    "factual_accuracy": 0.90,
    "completeness": 0.82,
    "relevance": 0.88
  },
  "errors": [
    {
      "question": "Combien d'applications sont en construction ?",
      "expected": "5 applications",
      "got": "Je ne trouve pas cette information",
      "reason": "Missing aggregation capability"
    }
  ]
}
```

### 6.3 Analyse des résultats

**Métriques clés :**

| Métrique | Cible | Signification |
|----------|-------|---------------|
| **Accuracy** | >80% | % de réponses correctes |
| **Precision** | >75% | % d'informations pertinentes dans la réponse |
| **Recall** | >70% | % d'informations importantes retrouvées |
| **Latence** | <3s | Temps de réponse total |

**Commande pour visualiser les erreurs :**
```bash
# Examiner les erreurs
python -c "
import json
results = json.load(open('evaluation/results.json'))
print(f'Taux de réussite: {results[\"accuracy\"]*100:.1f}%')
print(f'\\nErreurs ({len(results[\"errors\"])}):\\n')
for err in results['errors']:
    print(f'Q: {err[\"question\"]}')
    print(f'Attendu: {err[\"expected\"]}')
    print(f'Obtenu: {err[\"got\"]}')
    print(f'Raison: {err[\"reason\"]}\\n')
"
```

---

## Étape 7 : Amélioration itérative

### 7.1 Identifier les problèmes courants

Basé sur l'évaluation, vous pouvez avoir :

**Problème 1 : Retrieval incomplet**
- Symptôme : Réponses type "Je ne trouve pas cette information"
- Solution : Augmenter `--n-chunks` ou améliorer le chunking

**Problème 2 : Réponses hors sujet**
- Symptôme : Le RAG répond à côté de la question
- Solution : Améliorer les prompts système ou changer de modèle LLM

**Problème 3 : Informations fragmentées**
- Symptôme : Réponses incomplètes ou décousues
- Solution : Augmenter `--overlap` dans le chunking

**Problème 4 : Latence élevée**
- Symptôme : >5s par requête
- Solution : Réduire `--n-chunks` ou utiliser un modèle plus rapide

### 7.2 Cycle d'amélioration

```bash
# 1. Analyser les résultats d'évaluation
cat evaluation/results.json

# 2. Ajuster le chunking si nécessaire
dyag prepare-rag \
  examples/test-mygusi/applicationsIA_mini_normalized.json \
  --output prepared/applications_chunks_v2.jsonl \
  --chunk-size 800 \        # Réduit de 1000
  --overlap 300 \            # Augmenté de 200
  --chunk-strategy semantic

# 3. Ré-indexer
dyag index-rag \
  prepared/applications_chunks_v2.jsonl \
  --collection applications_ia_v2 \
  --reset

# 4. Re-tester
dyag evaluate-rag \
  evaluation/test_dataset.jsonl \
  --collection applications_ia_v2 \
  --output evaluation/results_v2.json

# 5. Comparer les résultats
python -c "
import json
v1 = json.load(open('evaluation/results.json'))
v2 = json.load(open('evaluation/results_v2.json'))
print(f'V1 Accuracy: {v1[\"accuracy\"]*100:.1f}%')
print(f'V2 Accuracy: {v2[\"accuracy\"]*100:.1f}%')
print(f'Amélioration: {(v2[\"accuracy\"] - v1[\"accuracy\"])*100:+.1f}%')
"
```

### 7.3 Matrice d'optimisation

| Si le problème est... | Alors ajuster... | Valeur suggérée |
|----------------------|------------------|-----------------|
| Retrieval faible | `--n-chunks` | 5 → 10 |
| Trop de bruit | `--n-chunks` | 10 → 5 |
| Chunks trop grands | `--chunk-size` | 1000 → 700 |
| Chunks trop petits | `--chunk-size` | 700 → 1200 |
| Fragmentation | `--overlap` | 200 → 400 |
| Latence élevée | `--n-chunks` et `--chunk-size` | Réduire les deux |
| Qualité LLM faible | Provider | Ollama → GPT-4 |

---

## Annexes

### Annexe A : Commandes MCP disponibles

#### Commandes actuellement disponibles

| Commande CLI | Commande MCP | Status |
|--------------|--------------|---------|
| `dyag prepare-rag` | `dyag_prepare_rag` | ⚠️ **À ajouter** |
| `dyag index-rag` | `dyag_index_rag` | ✅ Disponible |
| `dyag query-rag` | `dyag_rag_query` | ✅ Disponible |
| `dyag evaluate-rag` | `dyag_evaluate_rag` | ✅ Disponible |
| `dyag markdown-to-rag` | `dyag_create_rag` | ⚠️ **À ajouter** |
| `dyag analyze_training` | `dyag_analyze_training` | ✅ Disponible |

#### Nouvelles commandes proposées (détails dans le Journal)

Après analyse du workflow réel d'indexation (voir `doc/RAG_WORKFLOW_JOURNAL.md`), voici les **8 modules prioritaires** à développer :

| Module | Priorité | Problème résolu | MCP |
|--------|----------|-----------------|-----|
| `dyag fix-chunk-ids` | ✨ P0 | Conversion manuelle IDs numériques → strings | `dyag_fix_chunk_ids` |
| `dyag markdown-to-rag` | ✨ P0 | Pipeline 3 étapes → 1 commande | `dyag_markdown_to_rag` |
| `dyag test-rag` | ✨ P0 | Erreurs Unicode Windows | `dyag_test_rag` |
| `dyag create-eval-dataset` | ⭐ P1 | Création manuelle dataset | `dyag_create_eval_dataset` |
| `dyag rag-stats` | ⭐ P1 | Pas de vue d'ensemble système | `dyag_rag_stats` |
| `dyag validate-chunks` | 📋 P2 | Détection tardive problèmes | `dyag_validate_chunks` |
| `dyag compare-rag` | 📊 P2 | Comparaison configurations | `dyag_compare_rag` |
| `dyag export-rag` / `import-rag` | 💾 P2 | Sauvegarde/partage | `dyag_export_rag` |

**Exemple de workflow simplifié avec les nouveaux modules** :
```bash
# Au lieu de 7 étapes manuelles actuelles
dyag markdown-to-rag file.md --collection name --chunk-size 1000 --reset
dyag rag-stats --collection name
dyag create-eval-dataset --collection name --output eval.jsonl --num-questions 50
dyag test-rag --collection name --question "..." --no-emoji
dyag evaluate-rag eval.jsonl --collection name
```

📖 **Voir** : `doc/RAG_WORKFLOW_JOURNAL.md` pour les spécifications détaillées de chaque module

### Annexe B : Structure des fichiers générés

```
projet/
├── examples/
│   └── test-mygusi/
│       └── applicationsIA_mini_normalized.json  # ← Source
├── prepared/
│   ├── applications_chunks.jsonl                # ← Chunks
│   └── applications_chunks_v2.jsonl             # ← Chunks optimisés
├── chroma_db/                                   # ← Base vectorielle
│   ├── applications_ia/
│   └── applications_ia_v2/
├── evaluation/
│   ├── test_dataset.jsonl                       # ← Questions de test
│   ├── results.json                             # ← Résultats v1
│   └── results_v2.json                          # ← Résultats v2
└── .env                                         # ← Configuration
```

### Annexe C : Troubleshooting

**Problème : "No module named 'chromadb'"**
```bash
# Solution:
pip install -r requirements-rag.txt
```

**Problème : "Collection not found"**
```bash
# Solution: Ré-indexer
dyag index-rag prepared/applications_chunks.jsonl --collection applications_ia --reset
```

**Problème : "Ollama connection refused"**
```bash
# Solution: Vérifier qu'Ollama est démarré
ollama list
# Si non démarré, lancer:
ollama serve
```

**Problème : "OpenAI API key not found"**
```bash
# Solution: Vérifier .env
cat .env | grep OPENAI_API_KEY
# Si absent:
echo "OPENAI_API_KEY=sk-proj-votre-clé" >> .env
```

### Annexe D : Optimisations avancées

#### D.1 Utiliser un meilleur modèle d'embeddings

```bash
# Modèle plus performant mais plus lourd
dyag index-rag \
  prepared/applications_chunks.jsonl \
  --collection applications_ia_advanced \
  --embedding-model all-mpnet-base-v2 \  # Plus précis
  --reset
```

#### D.2 Chunking hybride personnalisé

```python
# Script Python personnalisé pour chunking avancé
from dyag.commands.prepare_rag import prepare_for_rag

# Charger les données
import json
data = json.load(open('examples/test-mygusi/applicationsIA_mini_normalized.json'))

# Chunking personnalisé
chunks = []
for app in data['applicationsia mini']:
    # Chunk 1: Vue d'ensemble
    chunk1 = {
        'id': f"app_{app['id']}_overview",
        'content': f"Application: {app['nom']}\\n{app.get('nom long', '')}\\nStatut: {app.get('statut si', '')}",
        'metadata': {'app_id': app['id'], 'type': 'overview'}
    }
    chunks.append(chunk1)

    # Chunk 2: Descriptif détaillé
    if 'descriptif' in app:
        chunk2 = {
            'id': f"app_{app['id']}_descriptif",
            'content': f"Application {app['nom']}: {app['descriptif']}",
            'metadata': {'app_id': app['id'], 'type': 'descriptif'}
        }
        chunks.append(chunk2)

# Sauvegarder
import jsonlines
with jsonlines.open('prepared/custom_chunks.jsonl', 'w') as writer:
    writer.write_all(chunks)
```

#### D.3 Ré-ranking des résultats

```python
# Implémenter un ré-ranking personnalisé
from dyag.rag_query import RAGQuerySystem

rag = RAGQuerySystem(collection_name='applications_ia')
question = "Qu'est-ce que 6tzen ?"

# Récupérer plus de chunks (20 au lieu de 5)
results = rag.query(question, n_chunks=20)

# Ré-ranker avec un score personnalisé
def rerank_score(chunk, question):
    # Score basé sur la présence de mots-clés importants
    keywords = ['6tzen', 'transport', 'routier', 'dematerialisation']
    score = sum(1 for kw in keywords if kw.lower() in chunk.lower())
    return score

# Trier et prendre le top 5
reranked = sorted(results, key=lambda c: rerank_score(c['content'], question), reverse=True)[:5]
```

---

## 🎯 Checklist de réussite

Votre RAG est de qualité si :

- [ ] **Accuracy ≥ 80%** sur le dataset de test
- [ ] **Latence < 3s** par requête (moyenne)
- [ ] **Précision des sources** : Toutes les réponses citent correctement les sources
- [ ] **Gestion des absences** : Répond "Je ne sais pas" quand l'info n'existe pas
- [ ] **Pas d'hallucinations** : Ne répond que sur les données indexées
- [ ] **Consistance** : Même question = même réponse (à variations stylistiques près)
- [ ] **Scalabilité** : Fonctionne avec 100+ applications

---

## 📚 Ressources complémentaires

- [Documentation ChromaDB](https://docs.trychroma.com/)
- [Sentence Transformers Models](https://www.sbert.net/docs/pretrained_models.html)
- [Guide Ollama](https://ollama.com/library)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)

---

**Dernière mise à jour** : 2025-01-16
**Version du guide** : 1.0
**Auteur** : Équipe Dyag

---

**Dyag** - RAG de qualité, commande par commande! 🚀📚
