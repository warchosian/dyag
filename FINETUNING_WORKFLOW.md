# Workflow Fine-Tuning DYAG

## Vue d'ensemble

Le système de fine-tuning DYAG permet de créer des modèles personnalisés adaptés à vos données spécifiques. Le workflow complet comporte 3 étapes principales :

1. **Générer un dataset d'entraînement** (`dyag generate-training`)
2. **Fine-tuner un modèle** (`dyag finetune`)
3. **Interroger le modèle fine-tuné** (`dyag query-finetuned`)

## Prérequis

### Dépendances Python

```bash
pip install transformers peft trl accelerate bitsandbytes datasets
```

### Matériel

- **CPU** : Fonctionnel mais TRÈS lent (test : 2min24s pour 10 exemples)
- **GPU** : Fortement recommandé (10-100x plus rapide)
  - Minimum 4GB VRAM (TinyLlama)
  - 8GB+ recommandé (Llama 3.2:1b)

## Étape 1 : Générer un Dataset d'Entraînement

### Commande de base

```bash
dyag generate-training INPUT --output OUTPUT \
  --method rule-based \
  --count 100 \
  --split
```

### Méthodes disponibles

- **rule-based** : Génération basée sur des règles (rapide)
- **llm-based** : Génération via LLM (plus naturel)
- **augmented** : Augmentation de données (variation)

### Exemple pratique

```bash
# Générer 100 exemples avec split train/val/test
dyag generate-training applications_rag_optimal.jsonl \
  --method rule-based \
  --count 100 \
  --split \
  --output data/finetuning/dataset_100.jsonl

# Résultat :
#   data/finetuning/dataset_100_train.jsonl (80 exemples)
#   data/finetuning/dataset_100_val.jsonl   (10 exemples)
#   data/finetuning/dataset_100_test.jsonl  (10 exemples)
```

### Format du dataset

Le fichier JSONL doit contenir des objets avec un champ `messages` :

```json
{
  "messages": [
    {"role": "system", "content": "Tu es un assistant qui répond aux questions sur les applications MYGUSI."},
    {"role": "user", "content": "Qu'est-ce que GIDAF ?"},
    {"role": "assistant", "content": "GIDAF est une application de gestion des dossiers administratifs et financiers."}
  ]
}
```

## Étape 2 : Fine-Tuner un Modèle

### Commande de base

```bash
dyag finetune \
  --dataset data/finetuning/dataset_100_train.jsonl \
  --output models/mon-modele \
  --base-model tinyllama \
  --epochs 3
```

### Modèles supportés

| Raccourci | Modèle HuggingFace | Params | VRAM Min | Utilisation |
|-----------|-------------------|--------|----------|-------------|
| `tinyllama` | TinyLlama/TinyLlama-1.1B-Chat-v1.0 | 1.1B | 2 GB | Tests rapides, CPU OK |
| `llama3.2:1b` | meta-llama/Llama-3.2-1B-Instruct | 1B | 3 GB | Production légère |
| `llama3.1:8b` | meta-llama/Llama-3.1-8B-Instruct | 8B | 12 GB | Production avancée |

### Paramètres importants

- `--epochs` : Nombre de passes sur le dataset (défaut : 3)
- `--batch-size` : Taille du batch (défaut : 4, réduire si VRAM insuffisant)
- `--lora-rank` : Rank LoRA (défaut : 16, augmenter pour plus de capacité)
- `--lora-alpha` : Alpha LoRA (défaut : 32)
- `--device` : Device à utiliser (`auto`, `cuda`, `cpu`)
- `--force-cpu` : Forcer l'utilisation du CPU (très lent)

### Exemples pratiques

#### Test rapide (CPU acceptable)

```bash
dyag finetune \
  --dataset data/finetuning/test_dataset_train.jsonl \
  --output models/test-tinyllama \
  --base-model tinyllama \
  --epochs 1 \
  --batch-size 1 \
  --force-cpu
```

**Durée estimée** : 2-5 minutes pour 10 exemples sur CPU

#### Production (GPU recommandé)

```bash
dyag finetune \
  --dataset data/finetuning/dataset_1000_train.jsonl \
  --output models/llama32-mygusi \
  --base-model llama3.2:1b \
  --epochs 3 \
  --batch-size 4
```

**Durée estimée** : 1-2h sur GPU pour 1000 exemples

### Gestion d'erreurs courantes

#### Pas de GPU détecté

```
[AVERTISSEMENT] Pas de GPU détecté - utilisation du CPU (très lent)
```

**Solution** : Ajouter `--force-cpu` pour confirmer ou utiliser Google Colab

#### VRAM insuffisant

```
CUDA out of memory
```

**Solution** : Réduire `--batch-size 2` ou `--batch-size 1`

#### Dataset invalide

```
[ERREUR] Impossible de lire le dataset
```

**Solution** : Vérifier le format JSONL et la structure des messages

## Étape 3 : Interroger le Modèle Fine-Tuné

### Mode question directe

```bash
dyag query-finetuned "Qu'est-ce que GIDAF ?" \
  --model models/llama32-mygusi/final \
  --base-model llama3.2:1b
```

### Mode interactif

```bash
dyag query-finetuned \
  --model models/llama32-mygusi/final \
  --base-model llama3.2:1b
```

Puis tapez vos questions dans le prompt interactif :

```
❯ Question: Qu'est-ce que GIDAF ?
[ANSWER] GIDAF est une application...

❯ Question: Qui héberge GIDAF ?
[ANSWER] GIDAF est hébergé par...

❯ Question: exit
```

### Paramètres avancés

- `--temperature` : Créativité (0-1, défaut : 0.7)
- `--max-tokens` : Longueur max de réponse (défaut : 500)
- `--device` : Device (`auto`, `cuda`, `cpu`)
- `-v, --verbose` : Afficher les détails (tokens, etc.)

## Workflow Complet - Exemple Testé

Voici un exemple complet qui a été validé :

```bash
# 1. Créer un dataset de test (10 exemples)
python -c "
import json
examples = [
    {'messages': [
        {'role': 'system', 'content': 'Tu es un assistant qui répond aux questions sur les applications MYGUSI.'},
        {'role': 'user', 'content': 'Qu\'est-ce que GIDAF ?'},
        {'role': 'assistant', 'content': 'GIDAF est une application de gestion des dossiers administratifs et financiers.'}
    ]},
    # ... 9 autres exemples
]
with open('data/finetuning/test_dataset_train.jsonl', 'w', encoding='utf-8') as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + '\n')
"

# 2. Fine-tuner le modèle (2min24s sur CPU)
dyag finetune \
  --dataset data/finetuning/test_dataset_train.jsonl \
  --output models/test-tinyllama \
  --base-model tinyllama \
  --epochs 1 \
  --batch-size 1 \
  --force-cpu

# 3. Interroger le modèle
dyag query-finetuned "Qu'est-ce que GIDAF ?" \
  --model models/test-tinyllama/final \
  --base-model tinyllama
```

## Résultats de Training

Après le training, vous verrez :

```
[OK] Training termine en 0:02:24.142878
Modele sauvegarde: models/test-tinyllama/final

======================================================================
TRAINING TERMINÉ
======================================================================
Modèle sauvegardé: models/test-tinyllama

Résultats:
  duration: 0:02:24.142878
  output_path: models/test-tinyllama/final
  epochs: 1
```

### Métriques affichées

- `train_loss` : Perte d'entraînement (plus bas = mieux)
- `mean_token_accuracy` : Précision moyenne sur les tokens
- `train_samples_per_second` : Vitesse d'entraînement
- `num_tokens` : Nombre total de tokens traités

## Structure des Fichiers de Sortie

Après le fine-tuning, la structure suivante est créée :

```
models/mon-modele/
├── final/
│   ├── adapter_config.json      # Configuration LoRA
│   ├── adapter_model.safetensors # Poids LoRA (< 100 MB)
│   ├── tokenizer_config.json
│   └── ...
└── checkpoint-XXX/              # Checkpoints intermédiaires (si epochs > 1)
```

**Note** : Seul l'adapter LoRA est sauvegardé (< 100 MB), pas le modèle de base complet.

## Approche Progressive Recommandée

Pour une comparaison équitable avec RAG :

### Phase 1 : Test Initial (13 apps)

```bash
# Dataset : 100 exemples, 1 epoch, TinyLlama
dyag generate-training examples/test-mygusi/applicationsIA_mini_opt_1-13.md \
  --method rule-based --count 100 --split \
  --output data/finetuning/dataset_13apps.jsonl

dyag finetune \
  --dataset data/finetuning/dataset_13apps_train.jsonl \
  --output models/tinyllama-13apps \
  --base-model tinyllama --epochs 1 --batch-size 2

# Durée : ~30min CPU
```

### Phase 2 : Validation Intermédiaire (10 apps)

```bash
# Dataset : 100 exemples, 2 epochs, Llama 3.2:1b
dyag generate-training examples/test-mygusi/applicationsIA_mini_1-10.md \
  --method augmented --count 100 --split \
  --output data/finetuning/dataset_10apps.jsonl

dyag finetune \
  --dataset data/finetuning/dataset_10apps_train.jsonl \
  --output models/llama32-10apps \
  --base-model llama3.2:1b --epochs 2 --batch-size 4

# Durée : ~1-2h GPU
```

### Phase 3 : Production (1008 apps)

```bash
# Dataset : 1000 exemples, 3 epochs, Llama 3.2:1b
dyag generate-training applications_rag_optimal.jsonl \
  --method augmented --count 1000 --split \
  --output data/finetuning/dataset_1008.jsonl

dyag finetune \
  --dataset data/finetuning/dataset_1008_train.jsonl \
  --output models/llama32-mygusi-1008 \
  --base-model llama3.2:1b --epochs 3 --batch-size 4

# Durée : ~4-8h GPU
```

## Comparaison RAG vs Fine-Tuning

| Critère | RAG | Fine-Tuning |
|---------|-----|-------------|
| **Setup initial** | Rapide (minutes) | Lent (heures) |
| **Mise à jour données** | Instantané (re-index) | Nécessite re-training |
| **Précision** | Dépend du retrieval | Dépend du dataset |
| **Tokens consommés** | Élevé (context + answer) | Bas (answer seule) |
| **Coût inférence** | Moyen (API calls) | Bas (local) |
| **Transparence** | ✅ Sources tracées | ❌ Boîte noire |
| **Réponses naturelles** | Parfois robotiques | Plus fluides |
| **GPU requis** | Non | Oui (pour training) |

### Cas d'usage recommandés

**Utiliser RAG si** :
- Les données changent fréquemment
- Besoin de transparence (sources)
- Pas de GPU disponible
- Volume très large (> 10k documents)

**Utiliser Fine-Tuning si** :
- Données stables
- Budget GPU disponible
- Réponses naturelles prioritaires
- Domaine spécialisé bien défini

**Utiliser les deux (Hybride)** :
- RAG pour retrieval précis
- Fine-Tuned pour génération naturelle
- Meilleur des deux mondes

## Dépannage

### Problème : SFTTrainer API incompatible

```python
TypeError: SFTTrainer.__init__() got an unexpected keyword argument 'tokenizer'
```

**Solution** : Version TRL 0.26+ utilise `processing_class` au lieu de `tokenizer`. Le code a été mis à jour.

### Problème : ImportError transformers/peft/trl

```
ImportError: No module named 'peft'
```

**Solution** :
```bash
pip install transformers peft trl accelerate bitsandbytes
```

### Problème : Training très lent sur CPU

**Solution** :
1. Utiliser Google Colab avec GPU gratuit
2. Réduire taille dataset pour test
3. Réduire epochs et batch_size

## Prochaines Étapes

### Fonctionnalités à venir

- [ ] `dyag evaluate-finetuned` : Évaluation automatique
- [ ] `dyag compare-models` : Comparaison RAG vs Fine-Tuning
- [ ] `dyag merge-lora` : Merger adapter avec base model
- [ ] `dyag export-gguf` : Export pour Ollama
- [ ] Interface web pour sélection modèle

### Pour aller plus loin

- Expérimenter avec différents modèles de base
- Augmenter le nombre d'exemples (> 1000)
- Ajuster les hyperparamètres LoRA
- Essayer différentes méthodes de génération de dataset

## Support

Pour toute question ou problème :

1. Vérifier ce guide
2. Consulter les logs détaillés avec `--verbose`
3. Tester avec un petit dataset d'abord
4. Vérifier la configuration GPU/CUDA

---

**Dernière mise à jour** : Test validé avec TinyLlama, 10 exemples, 1 epoch, CPU (2min24s)
**Version TRL testée** : 0.26.2
**Version Transformers testée** : Compatible avec TRL 0.26+
