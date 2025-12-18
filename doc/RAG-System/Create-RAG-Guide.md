# Guide d'utilisation du module create_rag

## Vue d'ensemble

Le module `create_rag` permet de transformer des fichiers JSON ou Markdown contenant des données d'applications en formats optimisés pour les systèmes RAG (Retrieval Augmented Generation).

## Caractéristiques principales

### 1. Nettoyage intelligent des données
- Restauration des URLs normalisées
- Suppression des séquences `r n` et normalisation des sauts de ligne
- Nettoyage des espaces multiples
- Préservation de la structure sémantique

### 2. Chunking sémantique
Le module crée plusieurs types de chunks pour chaque application :

- **Overview** : Vue d'ensemble avec nom, statut, famille, portée géographique
- **Description** : Description détaillée de l'application
- **Technical** : Informations techniques (domaines, acteurs, contacts)
- **Sites** : URLs et sites web associés

### 3. Métadonnées enrichies
Chaque chunk contient :
- ID unique généré par hash
- ID de l'application source
- Titre descriptif
- Contenu nettoyé
- Métadonnées structurées (domaines, statut, URLs, etc.)
- Type de chunk

### 4. Formats d'export multiples
- **JSONL** (JSON-Lines) : Un chunk par ligne, optimal pour le traitement stream
- **JSON** : Tableau de chunks, facile à manipuler
- **Markdown** : Format lisible avec frontmatter YAML

## Installation

Le module est intégré dans le package DYAG. Aucune installation supplémentaire requise.

## Utilisation

### Utilisation en ligne de commande

```bash
# Format JSONL (recommandé pour RAG)
python -m dyag.commands.create_rag input.json output.jsonl

# Format JSON
python -m dyag.commands.create_rag input.json output.json json

# Format Markdown
python -m dyag.commands.create_rag input.md output.md markdown

# Avec taille de chunk personnalisée (en caractères)
python -m dyag.commands.create_rag input.json output.jsonl jsonl 2000
```

### Utilisation en Python

#### Exemple basique

```python
from dyag.commands.create_rag import create_rag_from_file

# Conversion simple
create_rag_from_file(
    input_file='data/applications.json',
    output_file='data/applications_rag.jsonl',
    output_format='jsonl',
    max_chunk_size=1500
)
```

#### Exemple avancé

```python
from dyag.commands.create_rag import RAGCreator
from pathlib import Path

# Créer une instance du créateur
creator = RAGCreator(max_chunk_size=1500)

# Traiter un fichier JSON
chunk_count = creator.process_json_file(
    input_path='data/applications.json',
    output_path='data/applications_rag.jsonl',
    output_format='jsonl'
)

print(f"{chunk_count} chunks créés")

# Traiter un fichier Markdown
chunk_count = creator.process_markdown_file(
    input_path='data/applications.md',
    output_path='data/applications_rag.json',
    output_format='json'
)
```

#### Chunking personnalisé

```python
from dyag.commands.create_rag import ApplicationChunker
import json

# Créer un chunker
chunker = ApplicationChunker(max_chunk_size=2000)

# Charger une application
with open('app.json', 'r', encoding='utf-8') as f:
    app_data = json.load(f)

# Créer des chunks
chunks = chunker.chunk_application_from_json(app_data)

# Accéder aux chunks
for chunk in chunks:
    print(f"ID: {chunk.id}")
    print(f"Type: {chunk.chunk_type}")
    print(f"Titre: {chunk.title}")
    print(f"Taille: {len(chunk.content)} caractères")
    print(f"Métadonnées: {chunk.metadata}")
    print("---")
```

## Structure des chunks

### Chunk JSONL
```json
{
  "id": "1238_overview_a3f2",
  "source_id": "1238",
  "title": "6Tzen - Vue d'ensemble",
  "content": "# 6Tzen\n**Nom complet**: Outil national de dématérialisation...",
  "metadata": {
    "id": 1238,
    "nom": "6tzen",
    "statut si": "en production",
    "domaines_metier": ["Transports routiers"],
    "urls": ["https://demarches.developpement-durable.gouv.fr/"]
  },
  "chunk_type": "overview"
}
```

### Chunk Markdown
```markdown
---
id: 1238_overview_a3f2
source_id: 1238
type: overview
metadata: {"id": 1238, "nom": "6tzen", ...}
---

# 6Tzen - Vue d'ensemble

**Nom complet**: Outil national de dématérialisation...
```

## Paramètres de configuration

### max_chunk_size
Taille maximale d'un chunk en caractères (défaut: 1000)

**Recommandations** :
- **500-1000** : Pour des embeddings très précis, modèles avec contexte limité
- **1000-1500** : Équilibre entre précision et contexte (recommandé)
- **1500-2000** : Pour préserver plus de contexte, modèles avec grand contexte
- **>2000** : Peut réduire la précision du RAG

### output_format
Format de sortie du fichier RAG

**Formats disponibles** :
- **jsonl** : Recommandé pour l'ingestion dans des bases vectorielles
- **json** : Facile à manipuler, bon pour l'analyse
- **markdown** : Lisible par l'humain, bon pour la documentation

## Cas d'usage

### 1. Préparation pour base vectorielle

```python
from dyag.commands.create_rag import create_rag_from_file

# Créer des chunks optimisés pour ChromaDB, Pinecone, etc.
create_rag_from_file(
    input_file='applications.json',
    output_file='applications_vectors.jsonl',
    output_format='jsonl',
    max_chunk_size=1000
)

# Ensuite, dans votre code d'ingestion :
import json

with open('applications_vectors.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        # Générer embedding
        embedding = model.encode(chunk['content'])
        # Insérer dans la base vectorielle
        vector_db.insert(
            id=chunk['id'],
            embedding=embedding,
            metadata=chunk['metadata'],
            text=chunk['content']
        )
```

### 2. Documentation interactive

```python
# Créer une version Markdown lisible
create_rag_from_file(
    input_file='applications.json',
    output_file='applications_doc.md',
    output_format='markdown',
    max_chunk_size=2000
)
```

### 3. Analyse de corpus

```python
from dyag.commands.create_rag import RAGCreator
import json

creator = RAGCreator()
chunk_count = creator.process_json_file(
    'applications.json',
    'applications_analysis.json',
    'json'
)

# Analyser les chunks
with open('applications_analysis.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

# Statistiques
print(f"Total chunks: {len(chunks)}")
print(f"Types: {set(c['chunk_type'] for c in chunks)}")
print(f"Taille moyenne: {sum(len(c['content']) for c in chunks) / len(chunks):.0f} caractères")
```

## Optimisations pour RAG

### 1. Choix du format source

**JSON normalisé** (recommandé) :
- ✓ Structure claire
- ✓ Métadonnées facilement extractibles
- ✓ Meilleure qualité de chunks

**Markdown** :
- ✓ Préserve le formatage
- ✓ Lisible par l'humain
- ⚠ Nécessite parsing plus complexe

### 2. Taille optimale des chunks

Testez différentes tailles selon votre cas d'usage :

```python
for size in [500, 1000, 1500, 2000]:
    create_rag_from_file(
        'applications.json',
        f'rag_{size}.jsonl',
        max_chunk_size=size
    )
    # Évaluez la qualité de récupération
```

### 3. Enrichissement des métadonnées

Les métadonnées suivantes sont automatiquement extraites :
- ID de l'application
- Nom et nom long
- Statut SI
- Portée géographique
- Domaines métier
- URLs
- Dates de création/modification

Vous pouvez filtrer les résultats RAG sur ces métadonnées pour améliorer la précision.

## Tests

Exécutez les tests inclus :

```bash
python test_create_rag.py
```

Cela va :
1. Convertir les exemples JSON et Markdown
2. Générer différents formats (JSONL, JSON, Markdown)
3. Afficher des statistiques sur les fichiers générés
4. Montrer des exemples de chunks

## Dépannage

### Fichiers trop volumineux

Si le fichier source est très gros (>100MB), traitez-le par morceaux :

```python
import json
from dyag.commands.create_rag import ApplicationChunker, RAGExporter

chunker = ApplicationChunker(max_chunk_size=1500)
exporter = RAGExporter()

# Traitement par batch
with open('large_file.json', 'r') as f:
    data = json.load(f)

batch_size = 100
all_chunks = []

for i in range(0, len(data['applications']), batch_size):
    batch = data['applications'][i:i+batch_size]
    for app in batch:
        chunks = chunker.chunk_application_from_json(app)
        all_chunks.extend(chunks)

    # Sauvegarder périodiquement
    if len(all_chunks) > 1000:
        exporter.export_jsonl(all_chunks, f'output_batch_{i}.jsonl')
        all_chunks = []
```

### Encodage des caractères

Tous les fichiers sont traités en UTF-8. Si vous rencontrez des problèmes :

```python
# Forcer l'encodage UTF-8
import codecs

with codecs.open('input.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)
```

### URLs mal formées

Le module restaure automatiquement les URLs normalisées, mais si nécessaire :

```python
from dyag.commands.create_rag import DataCleaner

cleaner = DataCleaner()
restored_url = cleaner.restore_url('https demarches gouv fr')
# Résultat: 'https://demarches.gouv.fr'
```

## Meilleures pratiques

1. **Préférez JSONL pour les gros volumes** : Permet le traitement stream
2. **Ajustez max_chunk_size selon votre modèle** : Testez pour trouver l'optimum
3. **Conservez les métadonnées** : Essentielles pour le filtrage
4. **Validez les chunks** : Vérifiez la qualité avant l'ingestion
5. **Versionnez vos exports** : Gardez une trace des paramètres utilisés

## Intégration avec des frameworks RAG

### LangChain

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import json

# Charger les chunks
chunks = []
with open('applications_rag.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunks.append(json.loads(line))

# Créer le vector store
texts = [c['content'] for c in chunks]
metadatas = [c['metadata'] for c in chunks]

vectorstore = Chroma.from_texts(
    texts=texts,
    metadatas=metadatas,
    embedding=OpenAIEmbeddings()
)
```

### LlamaIndex

```python
from llama_index import Document, VectorStoreIndex
import json

# Charger les chunks
documents = []
with open('applications_rag.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunk = json.loads(line)
        doc = Document(
            text=chunk['content'],
            metadata=chunk['metadata'],
            doc_id=chunk['id']
        )
        documents.append(doc)

# Créer l'index
index = VectorStoreIndex.from_documents(documents)
```

## API Reference

Voir les docstrings dans le code pour une référence complète de l'API.

Classes principales :
- `RAGCreator` : Classe principale
- `ApplicationChunker` : Création de chunks
- `DataCleaner` : Nettoyage de données
- `RAGExporter` : Export dans différents formats
- `RAGChunk` : Structure de données d'un chunk

## Support

Pour toute question ou problème, consultez la documentation du projet DYAG ou ouvrez une issue sur le dépôt GitLab.
