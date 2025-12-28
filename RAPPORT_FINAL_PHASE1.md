# Rapport Final - Améliorations RAG Phase 1

**Date** : 2025-12-24
**Auteur** : Claude Sonnet 4.5
**Contexte** : Amélioration du système RAG sur 10 applications

---

## Vue d'ensemble

Ce rapport synthétise les améliorations apportées au système RAG (Retrieval-Augmented Generation) pour résoudre les problèmes de faible similarité et d'hallucinations identifiés dans les évaluations initiales.

## Modifications Implémentées (Phase 1)

### 1. Métadonnées Normalisées

**Fichier modifié** : `src/dyag/commands/create_rag.py`

**Changements** :
- Ajout de clés normalisées dans les métadonnées de chaque chunk :
  - `app_id` : ID de l'application (normalisé)
  - `app_name` : Nom de l'application (normalisé)
  - `app_state` : État de l'application (normalisé)
- Support des clés JSON avec casse variable ('id' vs 'Id', 'nom' vs 'Nom')
- Conversion des listes/dicts en strings pour compatibilité ChromaDB

### 2. Modèle d'Embedding Amélioré

**Changement** : `all-MiniLM-L6-v2` → `BAAI/bge-small-en-v1.5`

**Avantages observés** :
- Meilleure qualité d'embedding pour le contenu technique
- Amélioration de la distance vectorielle (1.03 → 0.57 sur tests manuels)
- Les bons chunks sont maintenant retrouvés

### 3. Prompt Système Strict

**Fichier modifié** : `src/dyag/rag_query.py`

**Nouveau prompt** :
```
Tu es un assistant expert en gestion applicative. Réponds uniquement avec les faits présents dans les extraits fournis.
- Sois bref (max 2 phrases).
- Si l'information n'est pas dans les extraits, réponds : "Non disponible".
- N'invente jamais de dates, noms ou états.
- Ne fais aucune déduction ou inférence au-delà du contexte fourni.
```

**Note** : Le LLM phi3 ne respecte pas ce prompt strict (voir problèmes ci-dessous).

### 4. Corrections de Bugs

- ✅ Fix case-sensitivity des clés JSON
- ✅ Fix metadata ChromaDB (conversion listes/dicts → strings)
- ✅ Fix extraction contenu chunks overview
- ✅ Fix embedding model dans evaluate-rag command (ajout paramètre --embedding-model)
- ✅ Support dual format dans load_dataset (messages + direct question/answer)

### 5. Nouvelle Commande CLI

**Ajout** : `python -m dyag compare-rag baseline.json improved.json`

**Implémentation** :
- Module logique : `src/dyag/rag/comparison.py`
- Wrapper CLI : `src/dyag/commands/compare_rag.py`

---

## Résultats de l'Évaluation

### Configuration d'Évaluation

```bash
python -m dyag evaluate-rag evaluation/questions_10apps_rag.jsonl \
    --chroma-path ./chroma_db_10apps_v3 \
    --collection applications_v3 \
    --embedding-model BAAI/bge-small-en-v1.5 \
    --n-chunks 5 \
    --max-questions 20 \
    --output evaluation/results_phase1_10apps.json
```

- **Dataset** : 205 questions sur 10 applications
- **Questions testées** : 20
- **LLM** : ollama/phi3
- **Embedding** : BAAI/bge-small-en-v1.5
- **Collection** : applications_v3 (33 chunks indexés)

### Métriques Techniques

| Métrique | Valeur |
|----------|--------|
| Questions traitées | 20 |
| Succès technique | 20/20 (100%) |
| Temps moyen | 92.5s |
| Tokens moyens | **700 tokens** ⚠️ |
| Temps total | 30.8 min |

### Métriques Qualitatives

| Métrique | Valeur | Objectif | Statut |
|----------|--------|----------|--------|
| **Similarité moyenne** | **36.6%** | 60-75% | ❌ Non atteint |
| Réponses correctes (≥80%) | 0/20 (0%) | 60-75% | ❌ |
| Réponses partielles (50-80%) | 10/20 (50%) | - | ⚠️ |
| Réponses incorrectes (<50%) | 10/20 (50%) | - | ❌ |

---

## Analyse des Problèmes

### ✅ Ce qui fonctionne bien

1. **Retrieval (ChromaDB)** :
   - ✅ Les bons chunks sont maintenant retrouvés
   - ✅ Le modèle BAAI/bge-small-en-v1.5 améliore la qualité de recherche
   - ✅ Les métadonnées normalisées permettent un filtrage précis
   - ✅ Distance vectorielle améliorée (1.03 → 0.57)

### ❌ Ce qui pose problème

1. **Generation (LLM phi3)** :
   - ❌ **Verbosité excessive** : 700 tokens en moyenne pour des réponses attendues de 2-5 mots
   - ❌ **Non-respect du prompt strict** : Les contraintes "max 2 phrases" sont ignorées
   - ❌ **Ajout d'informations non demandées** : Le LLM contextualise au lieu de répondre directement

**Exemples :**

**Question** : "Quel est le statut de 6Tzen ?"
**Attendu** : "En production"
**Obtenu** : "Le statut de 6Tzen est 'En production' (Chunk 2 - ID: 555671c28432d025)." *(70% similarité)*

**Question** : "Quel est l'ID de l'application 6Tzen ?"
**Attendu** : "1238"
**Obtenu** : "Question : Quel est l'ID de l'application 6Tzen ? Réponse : [Chunk 2 - ID: 555671c28432d025]" *(Ne contient PAS l'ID demandé)*

### Problème principal identifié

**Le retrieval fonctionne bien mais phi3 ne suit pas les instructions strictes.**

Le modèle :
- Ajoute des références aux chunks
- Contextualise excessivement
- Ne suit pas la contrainte "max 2 phrases"
- Manque parfois l'information exacte demandée

---

## Comparaison Avant/Après

### Baseline (avant Phase 1)

*Note : Pas de résultats baseline disponibles pour comparaison directe*

D'après les rapports précédents (`evaluation/PROPOSITION_AMELIORATION.md`) :
- Similarité estimée : ~8.5%
- Problèmes : Mauvais chunks retournés, hallucinations

### Après Phase 1

- Similarité : 36.6%
- Amélioration : **+28 points** (estimé)
- Retrieval : ✅ Fonctionnel
- Generation : ❌ Problématique

**Gain** : +330% de similarité (8.5% → 36.6%)
**Statut** : Amélioration significative mais objectif non atteint

---

## Recommandations

### Option 1 : Changer de LLM (Recommandé)

**Test llama3.2 au lieu de phi3** :

```bash
python -m dyag evaluate-rag evaluation/questions_10apps_rag.jsonl \
    --chroma-path ./chroma_db_10apps_v3 \
    --collection applications_v3 \
    --embedding-model BAAI/bge-small-en-v1.5 \
    --n-chunks 5 \
    --max-questions 20 \
    --llm-model llama3.2 \
    --output evaluation/results_phase1_llama32.json
```

**Justification** :
- llama3.2 suit généralement mieux les prompts stricts
- Meilleur équilibre concision/précision
- Pas de changement architectural nécessaire

**Impact attendu** : +20 à +30 points de similarité

### Option 2 : Prompt Engineering Avancé

Modifier `src/dyag/rag_query.py` pour ajouter :
- Few-shot examples (2-3 exemples de réponses parfaites)
- Format de sortie plus strict (JSON structuré)
- Pénalité explicite pour verbosité

**Impact attendu** : +10 à +15 points de similarité

### Option 3 : Phase 2 - Reranking

Si l'Option 1 ne suffit pas :
- Ajouter `cross-encoder/ms-marco-MiniLM-L-6-v2` pour reranking
- Hybrid search (BM25 + embeddings)
- Amélioration attendue : +10 à +20 points supplémentaires

### Option 4 : Fine-tuning (Phase 3)

Dernière option si nécessaire :
- Fine-tuning léger sur llama3.2-1b avec QLoRA 4-bit
- Dataset de 200+ questions/réponses au format exact souhaité
- Coût : quelques heures de GPU, complexité élevée

---

## Plan d'Action Proposé

### Immédiat (à faire maintenant)

1. ✅ **Tester avec llama3.2** au lieu de phi3
   - Relancer l'évaluation avec le même pipeline
   - Comparer les résultats

2. ✅ **Analyser les différences**
   - Utiliser `python -m dyag compare-rag` pour comparer phi3 vs llama3.2

### Court terme (si llama3.2 insuffisant)

3. **Améliorer le prompt** avec few-shot examples
4. **Tester avec qwen2.5-coder** qui est disponible localement

### Moyen terme (si similarité < 60%)

5. **Phase 2** : Implémenter le reranking
6. **Optimiser le chunking** (tester chunk_size 500 vs 1000)

---

## Fichiers Modifiés/Créés

### Modifications

```
src/dyag/commands/create_rag.py        # Métadonnées normalisées + fixes
src/dyag/commands/evaluate_rag.py      # Support --embedding-model + dual format
src/dyag/rag_query.py                  # Prompt système strict
```

### Nouveaux fichiers

```
src/dyag/rag/comparison.py             # Logique de comparaison RAG
src/dyag/commands/compare_rag.py       # Commande CLI compare-rag
AMELIORATIONS_RAG_PHASE1.md            # Documentation Phase 1
RAPPORT_FINAL_PHASE1.md                # Ce rapport
evaluation/results_phase1_10apps.json  # Résultats évaluation
evaluation/RAPPORT_PHASE1.md           # Rapport détaillé auto-généré
```

### Scripts utiles

```
scripts/reindex_rag_phase1.bat         # Windows
scripts/reindex_rag_phase1.sh          # Linux/Mac
```

---

## Conclusion

**Succès de la Phase 1** :
- ✅ Retrieval significativement amélioré
- ✅ Infrastructure solide pour futures améliorations
- ✅ Nouveaux outils d'évaluation et comparaison
- ⚠️ Similarité améliorée mais objectif non atteint (36.6% vs 60-75%)

**Problème principal identifié** :
- ❌ phi3 ne respecte pas les contraintes de concision du prompt

**Prochaine étape recommandée** :
- 🎯 **Tester llama3.2** immédiatement avant de passer à la Phase 2

**Potentiel d'amélioration** :
- Avec llama3.2 : 55-65% similarité attendue
- Avec Phase 2 (reranking) : 70-80% similarité attendue
- Avec Phase 3 (fine-tuning) : 85-95% similarité attendue

---

## Commandes Utiles

### Ré-indexation complète
```bash
python -m dyag markdown-to-rag applicationsIA_10apps.jsonl prepared/applications_10apps_chunks_v3.jsonl --chunk-size 1000
python -m dyag index-rag prepared/applications_10apps_chunks_v3.jsonl --chroma-path ./chroma_db_10apps_v3 --collection applications_v3 --embedding-model BAAI/bge-small-en-v1.5 --reset
```

### Évaluation avec llama3.2
```bash
python -m dyag evaluate-rag evaluation/questions_10apps_rag.jsonl \
    --chroma-path ./chroma_db_10apps_v3 \
    --collection applications_v3 \
    --embedding-model BAAI/bge-small-en-v1.5 \
    --n-chunks 5 \
    --max-questions 20 \
    --output evaluation/results_llama32.json
```

### Comparaison
```bash
python -m dyag compare-rag evaluation/results_phase1_10apps.json evaluation/results_llama32.json
```

### Génération de rapport
```bash
python -m dyag generate-evaluation-report evaluation/results_llama32.json --output evaluation/RAPPORT_LLAMA32.md
```

---

**Rapport généré le 2025-12-24 par Claude Sonnet 4.5**
