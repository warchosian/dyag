# Rapport des Incohérences Documentation - DYAG v2.0.0

**Date**: 2025-12-28
**Statut**: ❌ Incohérences détectées

---

## 🔍 Problèmes Identifiés

### Problème 1: Underscores au lieu de Hyphens ❌

**Description**: La documentation utilise des underscores (`_`) dans les noms de commandes CLI, alors que les commandes réelles utilisent des hyphens (`-`).

**Commandes affectées**:
- ❌ `dyag prepare_rag` → ✅ `dyag prepare-rag`
- ❌ `dyag index_rag` → ✅ `dyag index-rag`
- ❌ `dyag query_rag` → ✅ `dyag query-rag`
- ❌ `dyag evaluate_rag` → ✅ `dyag evaluate-rag`
- ❌ `dyag create_rag` → ❓ **Commande inexistante** (voir Problème 2)

### Problème 2: Commande Inexistante ❌

**Description**: La documentation fait référence à une commande `dyag create_rag` (ou `create-rag`) qui **n'existe pas** dans le CLI.

**Commande correcte**: `dyag markdown-to-rag` (pipeline complet: Markdown -> Chunks -> ChromaDB)

**Confusion identifiée**:
- Docs utilisent: `dyag create_rag`
- Commande réelle: `dyag markdown-to-rag`

---

## 📋 Fichiers Affectés

### 1. doc/RAG_WORKFLOW_GUIDE.md
**Occurrences**: 22 lignes

**Problèmes**:
- Ligne 109: `dyag prepare_rag` → `prepare-rag`
- Ligne 115: `dyag index_rag` → `index-rag`
- Ligne 126: `dyag query_rag` → `query-rag`
- Ligne 132: `dyag evaluate_rag` → `evaluate-rag`
- Ligne 254: `dyag prepare_rag \` → `prepare-rag`
- Ligne 432: `dyag index_rag \` → `index-rag`
- Ligne 585-685: Multiples `dyag query_rag` → `query-rag`
- Ligne 705: `dyag create_rag \` → **`markdown-to-rag`**
- Ligne 732: `dyag evaluate_rag \` → `evaluate-rag`
- Ligne 836-850: Multiples occurrences
- Lignes 888-892: Tableau des commandes avec underscores

### 2. doc/FINETUNING_WORKFLOW_GUIDE.md
**Occurrences**: 5 lignes

**Problèmes**:
- Ligne 119: `dyag create_rag` → **`markdown-to-rag`**
- Ligne 143: `dyag evaluate_rag` → `evaluate-rag`
- Ligne 246: `dyag create_rag \` → **`markdown-to-rag`**
- Ligne 758: `dyag evaluate_rag \` → `evaluate-rag`
- Ligne 771: `dyag evaluate_rag \` → `evaluate-rag`

### 3. RAPPORT_COHERENCE_DOCUMENTATION.md
**Occurrences**: 5 lignes

**Problèmes**:
- Ligne 20: `dyag prepare_rag` → `prepare-rag`
- Ligne 21: `dyag index_rag` → `index-rag`
- Ligne 22: `dyag query_rag` → `query-rag`
- Ligne 23: `dyag evaluate_rag` → `evaluate-rag`
- Ligne 24: `dyag create_rag` → **`markdown-to-rag`**

### 4. RAPPORT_FINAL_PHASE1.md
**Occurrences**: 1 ligne

**Problèmes**:
- Ligne 298: `python -m dyag create-rag` → **`markdown-to-rag`**

---

## ✅ Commandes CLI Correctes (Référence)

### Commandes RAG
```bash
dyag prepare-rag           # Préparer un fichier Markdown pour RAG
dyag index-rag             # Indexer des chunks dans ChromaDB
dyag query-rag             # Interroger le système RAG
dyag evaluate-rag          # Évaluer le système RAG
dyag compare-rag           # Comparer deux résultats d'évaluation RAG
dyag markdown-to-rag       # Pipeline complet: Markdown -> Chunks -> ChromaDB (1 commande)
dyag test-rag              # Tester rapidement le RAG
dyag rag-stats             # Afficher les statistiques d'une collection RAG
```

### Commandes Fine-Tuning
```bash
dyag generate-training     # Générer des datasets d'entraînement
dyag finetune              # Fine-tuner un modèle avec LoRA
dyag query-finetuned       # Interroger un modèle fine-tuné
dyag evaluate-finetuned    # Évaluer un modèle fine-tuné
dyag compare-models        # Comparer RAG vs Fine-Tuning
```

---

## 📝 Actions Requises

### Action 1: Remplacer Underscores par Hyphens
Dans tous les fichiers affectés, remplacer:
- `prepare_rag` → `prepare-rag`
- `index_rag` → `index-rag`
- `query_rag` → `query-rag`
- `evaluate_rag` → `evaluate-rag`

### Action 2: Remplacer create_rag par markdown-to-rag
Dans tous les fichiers affectés, remplacer:
- `create_rag` → `markdown-to-rag`
- `create-rag` → `markdown-to-rag`

---

## 🔧 Plan de Correction

1. ✅ Créer ce rapport
2. ✅ Corriger doc/RAG_WORKFLOW_GUIDE.md (22 occurrences)
3. ✅ Corriger doc/FINETUNING_WORKFLOW_GUIDE.md (5 occurrences)
4. ✅ RAPPORT_COHERENCE_DOCUMENTATION.md (pas de correction nécessaire - c'est un rapport)
5. ✅ Corriger RAPPORT_FINAL_PHASE1.md (1 occurrence)
6. ✅ Vérifier autres fichiers .md (README.md et CHANGELOG_FINETUNING.md sont OK)
7. ⏳ Commit corrections

---

**Statut**: ✅ CORRECTIONS COMPLÉTÉES - PRÊT POUR COMMIT
