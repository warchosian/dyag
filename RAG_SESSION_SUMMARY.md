# Session RAG - Résumé et Analyse

**Date**: 2025-12-20
**Source**: `applicationsIA_mini_1-10.md`
**Base RAG**: `chroma_db_10apps`

---

## ✅ Réalisations

### 1. Documentation Créée
- **RAG_WORKFLOW_10APPS.md** - Guide complet du workflow RAG
  - Stratégies de chunking expliquées
  - Approches de génération Q/R (manuelle, semi-auto, auto)
  - Métriques d'évaluation détaillées
  - Scénarios de test

### 2. Base RAG Créée
```bash
Collection: applications_10apps
Database: ./chroma_db_10apps/
Chunks: 88
Stratégie: markdown-headers
Embedding: all-MiniLM-L6-v2 (dimension 384)
Temps création: 28 secondes
Taux réussite: 100%
```

### 3. Premier Test de Requête
**Question**: "Quel est le statut de l'application 6Tzen ?"

**Chunks récupérés**: chunk_29, chunk_20, chunk_26

**Réponse LLM**: ❌ Incorrect - Le système n'a pas trouvé l'information

---

## 🔍 Problème Identifié: Récupération Sémantique

### Symptôme
Le système RAG a récupéré des chunks qui ne contiennent pas l'information sur 6Tzen, bien que cette information existe dans le document source.

### Causes Possibles

#### 1. Chunking par Headers Trop Granulaire
**Hypothèse**: Le découpage par headers (`## Titre`) peut créer trop de petits chunks séparés.

**Exemple de problème**:
```markdown
# 6Tzen

## Description
...

## Domaines métier
...

## Sites web
...
```

Avec le chunking par headers, chaque section `##` devient un chunk séparé. Une requête sur "statut de 6Tzen" pourrait ne pas matcher la section "Description" si elle ne contient pas le mot "statut".

#### 2. Manque de Contexte dans les Chunks
Les chunks trop petits peuvent manquer de contexte pour le matching sémantique.

**Solution**: Inclure le titre parent (h1) dans chaque chunk de section (h2).

#### 3. Embeddings Ne Capturent Pas la Structure
Le modèle `all-MiniLM-L6-v2` est excellent pour la sémantique mais peut ne pas bien gérer les structures type "clé: valeur".

**Exemple**:
```markdown
**Statut:** En production
```

L'embedding de cette ligne pourrait ne pas bien matcher avec "quel est le statut".

---

## 🎯 Solutions Proposées

### Solution 1: Améliorer le Chunking

#### Option A: Inclure le Contexte Parent
Modifier la stratégie pour que chaque chunk de section inclue le titre de l'application:

```python
# Au lieu de:
chunk = "## Domaines métier\n\n- Transports routiers"

# Faire:
chunk = "# 6Tzen\n\n## Domaines métier\n\n- Transports routiers"
```

#### Option B: Chunks Plus Larges
Utiliser `--chunk-mode section` ou `--chunk-mode size` avec une taille plus grande:

```bash
python -m dyag markdown-to-rag \
  examples/test-mygusi/applicationsIA_mini_1-10.md \
  --collection applications_10apps_v2 \
  --chroma-path ./chroma_db_10apps \
  --chunk-mode size \
  --chunk-size 1500 \
  --chunk-overlap 300 \
  --reset --verbose
```

#### Option C: Une Application = Un Chunk
Pour seulement 10 applications, chaque application complète pourrait être un chunk:

```bash
# Custom script
python scripts/create_app_chunks.py \
  --input applicationsIA_mini_1-10.md \
  --output chunks_by_app.json
```

### Solution 2: Améliorer les Requêtes

#### Expansion de Requête
Au lieu de "Quel est le statut de 6Tzen ?", essayer:
- "6Tzen statut production construction"
- "Application 6Tzen informations métadonnées"
- "6Tzen en production ou en construction"

#### Metadata Filtering
Si les chunks ont des métadonnées (app_id, app_name), filtrer d'abord:

```python
results = collection.query(
    query_texts=[query],
    n_results=5,
    where={"app_name": "6Tzen"}
)
```

### Solution 3: Évaluation Systématique

Créer un dataset de questions et mesurer la performance:

```jsonl
{"question": "Quel est le statut de 6Tzen ?", "expected_chunks": ["chunk_6tzen_metadata"], "expected_answer": "En production"}
{"question": "Quels sont les domaines métier de 6Tzen ?", "expected_chunks": ["chunk_6tzen_domaines"], "expected_answer": "Transports routiers"}
```

Puis évaluer:
```bash
python -m dyag evaluate-rag \
  evaluation/questions_10apps.jsonl \
  --collection applications_10apps \
  --chroma-path ./chroma_db_10apps
```

---

## 📋 Prochaines Étapes Recommandées

### Étape 1: Analyse des Chunks Existants
```bash
# Inspecter les chunks créés
python scripts/inspect_chunks.py \
  --collection applications_10apps \
  --chroma-path ./chroma_db_10apps
```

Vérifier:
- Taille moyenne des chunks
- Distribution du contenu
- Présence du contexte (titre application)

### Étape 2: Recréer avec Meilleure Stratégie

Tester 3 versions:

**Version 1: Size-based avec overlap**
```bash
# Chunks de 1500 caractères, overlap 300
python -m dyag markdown-to-rag \
  examples/test-mygusi/applicationsIA_mini_1-10.md \
  --collection apps_size1500 \
  --chroma-path ./chroma_db_tests \
  --chunk-mode size \
  --chunk-size 1500 \
  --chunk-overlap 300 \
  --reset --verbose
```

**Version 2: Section-based**
```bash
python -m dyag markdown-to-rag \
  examples/test-mygusi/applicationsIA_mini_1-10.md \
  --collection apps_sections \
  --chroma-path ./chroma_db_tests \
  --chunk-mode section \
  --reset --verbose
```

**Version 3: Par application (custom)**
```python
# Script personnalisé
for app in applications:
    chunk = f"# {app['name']}\n\n{app['full_content']}"
    add_to_collection(chunk, metadata={"app_id": app['id']})
```

### Étape 3: Tester et Comparer

Créer 10 questions de base (1 par application):
```python
questions = [
    "Quel est le statut de 6Tzen ?",
    "Quels sont les domaines métier de 6Tzen ?",
    "Quelle est la date de mise en production de 6Tzen ?",
    # ... pour chaque application
]
```

Tester sur les 3 versions et comparer:
- Recall@3
- Precision@3
- Qualité des réponses

### Étape 4: Optimiser la Meilleure Version

Une fois la meilleure stratégie identifiée:
1. Créer dataset complet (50-100 questions)
2. Évaluation formelle
3. Ajustement des paramètres (n_chunks, embedding model, etc.)

---

## 📊 Métriques Actuelles

| Métrique | Valeur | Objectif |
|----------|--------|----------|
| Chunks créés | 88 | - |
| Temps indexation | 28s | < 60s ✅ |
| Recall@3 (test 1 question) | 0% | > 80% ❌ |
| Precision@3 (test 1 question) | 0% | > 70% ❌ |

**Statut**: 🔴 Système créé mais récupération inefficace

---

## 💡 Recommandation Immédiate

**Action**: Recréer la base avec `--chunk-mode size --chunk-size 1500 --chunk-overlap 300`

**Rationale**:
- Chunks plus larges = plus de contexte
- Overlap = pas de perte d'information aux frontières
- Plus robuste que headers pour ce type de document

**Commande**:
```bash
python -m dyag markdown-to-rag \
  examples/test-mygusi/applicationsIA_mini_1-10.md \
  --collection applications_10apps \
  --chroma-path ./chroma_db_10apps \
  --chunk-mode size \
  --chunk-size 1500 \
  --chunk-overlap 300 \
  --reset --verbose
```

Puis retester la même question.

---

## 📝 Notes Techniques

### Structure du Document Source
```markdown
# Applications du ministère...

# 6Tzen
**Nom complet:** ...
**ID:** 1238
**Statut:** En production  ← Information recherchée

## Description
...

## Domaines métier
...
```

### Chunks Attendus (Idéal)
Pour une requête sur "statut de 6Tzen", les chunks pertinents devraient être:
1. Section complète "6Tzen" avec métadonnées (nom, ID, statut, portée)
2. Section "Description" de 6Tzen (contexte)
3. Autres sections de 6Tzen si pertinentes

### Chunks Réellement Récupérés
- chunk_29, chunk_20, chunk_26
- À investiguer: quel contenu ont ces chunks ?

---

## 🔧 Outils à Créer

### 1. Script d'Inspection de Chunks
```python
# scripts/inspect_chunks.py
# Affiche le contenu des chunks d'une collection
# Usage: python scripts/inspect_chunks.py --collection NAME --chunk-ids 29,20,26
```

### 2. Script de Génération de Questions
```python
# scripts/generate_qa_dataset.py
# Génère automatiquement des Q/R depuis le markdown structuré
# Usage: python scripts/generate_qa_dataset.py --input FILE --output JSONL
```

### 3. Script de Comparaison de Stratégies
```python
# scripts/compare_chunking_strategies.py
# Compare plusieurs stratégies de chunking sur le même dataset
# Usage: python scripts/compare_chunking_strategies.py --input FILE --questions JSONL
```

---

## 📚 Ressources

- **Document workflow**: RAG_WORKFLOW_10APPS.md
- **Base RAG**: chroma_db_10apps/
- **Source**: examples/test-mygusi/applicationsIA_mini_1-10.md
- **Collection**: applications_10apps

---

**Conclusion**: Le pipeline RAG est fonctionnel mais nécessite un ajustement de la stratégie de chunking pour améliorer la récupération sémantique. La prochaine étape consiste à recréer la base avec une stratégie size-based plus robuste et retester.
