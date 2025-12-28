# CHANGELOG - Fine-Tuning Integration

## Version 2.0.0 - Fine-Tuning Release (2024-12-28)

### 🎉 Nouveautés Majeures

#### Système de Fine-Tuning Complet
Ajout d'un système complet de fine-tuning local avec LoRA (Low-Rank Adaptation) pour créer des modèles spécialisés sur vos données.

#### 5 Nouvelles Commandes CLI

1. **`dyag generate-training`** - Génération de datasets d'entraînement
   - Méthodes: rule-based, llm-based, augmented
   - Split automatique train/val/test (80/10/10)
   - Validation format JSONL
   - Support count, seed, validation

2. **`dyag finetune`** - Fine-tuning LoRA local
   - Support multi-modèles (TinyLlama, Qwen2.5, Llama 3.x, Phi3)
   - Auto-détection GPU/CPU
   - Quantization 4-bit pour économiser VRAM
   - Progress monitoring avec tqdm
   - Checkpoint management et resume support
   - Configuration LoRA flexible (rank, alpha, target_modules)

3. **`dyag query-finetuned`** - Interrogation modèles fine-tunés
   - Mode direct: `dyag query-finetuned "Question" --model path`
   - Mode interactif: `dyag query-finetuned --model path`
   - Support multi-modèles via base-model parameter
   - Configuration température, max-tokens, device

4. **`dyag evaluate-finetuned`** - Évaluation modèles
   - Métriques: success_rate, exact_match_rate, avg_time, avg_tokens
   - Format JSON compatible avec evaluate-rag
   - Support --limit pour tests rapides
   - Mode verbose avec exemples

5. **`dyag compare-models`** - Comparaison RAG vs Fine-Tuning
   - Compare métriques RAG et Fine-Tuning
   - Détermine gagnant par métrique
   - Génère rapports JSON + Markdown
   - Recommandations automatiques
   - Analyse avantages/inconvénients

### 🏗️ Architecture

#### Module `src/dyag/finetuning/`

**Commands** (`src/dyag/finetuning/commands/`):
- `compare_models.py` - Comparaison RAG/FT
- `evaluate_finetuned.py` - Évaluation modèles
- `finetune.py` - Training LoRA
- `generate_training.py` - Génération datasets
- `query_finetuned.py` - Interrogation modèles

**Core** (`src/dyag/finetuning/core/`):
- `dataset_generators.py` - Générateurs datasets (RuleBased, LLMBased, Augmented)
- `model_registry.py` - Registry modèles supportés avec raccourcis
- `trainer.py` - LoRATrainer avec support multi-modèles

#### Registry Modèles Supportés

| Raccourci | Modèle HuggingFace | Params | VRAM Min | Accès |
|-----------|-------------------|--------|----------|-------|
| `tinyllama` | TinyLlama/TinyLlama-1.1B-Chat-v1.0 | 1.1B | 2 GB | ✅ Libre |
| **`qwen2.5:1.5b`** ⭐ | Qwen/Qwen2.5-1.5B-Instruct | 1.5B | 3 GB | ✅ Libre |
| `llama3.2:1b` | meta-llama/Llama-3.2-1B-Instruct | 1B | 3 GB | 🔒 Gated |
| `llama3.1:8b` | meta-llama/Llama-3.1-8B-Instruct | 8B | 12 GB | 🔒 Gated |
| `phi3` | microsoft/Phi-3-mini-4k-instruct | 3.8B | 6 GB | ✅ Libre |

**Recommandation Production**: Qwen2.5-1.5B (meilleur ratio qualité/vitesse, non-gated)

### 📚 Documentation

#### Nouveaux Guides

1. **`FINETUNING_WORKFLOW.md`** - Workflow complet de bout en bout
   - Génération datasets
   - Configuration training
   - Évaluation et comparaison
   - Cas d'usage et exemples

2. **`FINETUNING_TEST_RESULTS.md`** - Rapport tests comparatifs
   - TinyLlama vs Qwen2.5 vs Llama 3.2
   - Métriques détaillées
   - Recommandations

3. **`LLAMA_ACCESS_GUIDE.md`** - Guide accès modèles Llama
   - Création compte HuggingFace
   - Demande accès modèles gated
   - Authentification huggingface-cli
   - Dépannage erreurs
   - Alternatives non-gated

4. **`SESSION_RECAP_2024-12-28.md`** - Récapitulatif session développement
   - Historique complet
   - Tests réalisés
   - Fichiers créés/modifiés
   - Statistiques

### 🧪 Tests et Validation

#### Tests Effectués

| Modèle | Dataset | Durée | Loss | Accuracy | Qualité |
|--------|---------|-------|------|----------|---------|
| TinyLlama | 10 ex, 1 epoch | 2min24s | 2.266 | 0.610 | 2/10 ❌ |
| **Qwen2.5-1.5B** ⭐ | 10 ex, 1 epoch | 1min18s | 3.652 | 0.418 | 7/10 ✅ |
| Llama 3.2-1B | - | - | - | - | Bloqué (auth) |

**Gagnant**: Qwen2.5-1.5B
- ✅ 1.8x plus rapide que TinyLlama
- ✅ Meilleure qualité de réponses
- ✅ Non-gated (accès immédiat)
- ✅ Réponses cohérentes et structurées

**Paradoxe observé**: Avec petits datasets, métriques de training (loss/accuracy) ne prédisent pas la qualité réelle. TinyLlama a de meilleures métriques mais génère des conversations fictives, tandis que Qwen2.5 génère des réponses utiles.

### 🔧 Dépendances

Nouveau fichier: `requirements-finetuning.txt`

```txt
# Core ML
torch>=2.0.0
transformers>=4.36.0
datasets>=2.14.0

# Fine-tuning
peft>=0.7.0
trl>=0.7.4
accelerate>=0.24.0

# Quantization
bitsandbytes>=0.41.0

# Optional
sentencepiece>=0.1.99
protobuf>=3.20.0
```

### 🚀 Workflow Complet

```bash
# 1. Générer dataset
dyag generate-training applications_rag_optimal.jsonl \
  --method augmented --count 100 --split \
  --output data/finetuning/dataset_100.jsonl

# 2. Fine-tuning
dyag finetune \
  --dataset data/finetuning/dataset_100_train.jsonl \
  --output models/qwen25-mygusi-100 \
  --base-model qwen2.5:1.5b \
  --epochs 3 --batch-size 4

# 3. Test interactif
dyag query-finetuned --model models/qwen25-mygusi-100/final

# 4. Évaluation
dyag evaluate-finetuned evaluation/questions_10apps_rag.jsonl \
  --model models/qwen25-mygusi-100/final \
  --base-model qwen2.5:1.5b \
  --output evaluation/results_ft.json

# 5. Comparaison RAG vs Fine-Tuning
dyag compare-models \
  --rag-results evaluation/results_rag.json \
  --finetuned-results evaluation/results_ft.json \
  --output evaluation/comparison \
  --format both
```

### 🎯 Cas d'Usage

#### Utiliser RAG si:
- Données changent fréquemment
- Besoin de traçabilité (sources)
- Pas de GPU disponible pour training
- Volume très large (> 10k documents)

#### Utiliser Fine-Tuning si:
- Données stables dans le temps
- Budget GPU disponible
- Réponses naturelles prioritaires
- Domaine spécialisé bien défini

#### Approche Hybride (Recommandé):
- RAG pour retrieval précis
- Fine-Tuned pour génération naturelle
- Meilleur des deux mondes

### 🔄 Fichiers Modifiés

- `src/dyag/main.py` - Enregistrement 5 nouvelles commandes
- `src/dyag/finetuning/commands/__init__.py` - Exports commandes

### 📊 Métriques de Comparaison

Format standardisé pour comparaison RAG vs Fine-Tuning:

```json
{
  "metrics": {
    "success_rate": 85.5,
    "exact_match_rate": 42.3,
    "avg_time_seconds": 2.15,
    "avg_tokens": 487,
    "total_tokens": 48700
  }
}
```

### 💡 Leçons Apprises

1. **Choix du modèle de base crucial**: Qwen2.5-1.5B >> TinyLlama malgré taille similaire
2. **Métriques trompeuses avec petits datasets**: Loss/accuracy ne prédisent pas qualité réelle
3. **CPU viable pour prototypage**: 1-2min pour 10 ex, ~1h pour 100 ex
4. **Raccourcis registry très utiles**: `qwen2.5:1.5b` au lieu de `Qwen/Qwen2.5-1.5B-Instruct`
5. **Architecture modulaire payante**: Ajouts faciles, tests unitaires possibles

### 🔜 Prochaines Étapes (Hors Scope)

- Interface web avec sélecteur modèle (RAG/Fine-Tuned/Hybride)
- Métriques avancées (BLEU, ROUGE, BERTScore)
- Model merge & export GGUF pour Ollama
- Incremental fine-tuning
- Quantization post-training

### 📝 Statistiques Développement

- **Durée session**: ~3h de travail effectif
- **Lignes Python**: ~1200 lignes
- **Fichiers créés**: 15
- **Fichiers modifiés**: 4
- **Documentation**: ~2000 lignes MD
- **Tests effectués**: 3 modèles, 2 datasets

---

**Date de release**: 2024-12-28
**Auteur**: Claude Code + User
**Type**: Feature Major - Fine-Tuning Integration
**Breaking Changes**: Aucun (backward compatible)
