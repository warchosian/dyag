# Guide Complet : Fine-tuning de Modèles LLM avec Dyag

Ce guide vous accompagne pas-à-pas dans le fine-tuning de modèles de langage (LLM) à partir de vos données d'applications, en utilisant Dyag. Complémentaire au guide RAG, il vous permet de choisir la meilleure approche pour votre cas d'usage.

## 📋 Table des matières

- [Introduction](#introduction)
- [RAG vs Fine-tuning : Quelle approche choisir ?](#rag-vs-fine-tuning--quelle-approche-choisir-)
- [Prérequis](#prérequis)
- [Vue d'ensemble du workflow](#vue-densemble-du-workflow)
- [Étape 1 : Préparation des données d'entraînement](#étape-1--préparation-des-données-dentraînement)
- [Étape 2 : Création du dataset de fine-tuning](#étape-2--création-du-dataset-de-fine-tuning)
- [Étape 3 : Validation et nettoyage du dataset](#étape-3--validation-et-nettoyage-du-dataset)
- [Étape 4 : Fine-tuning avec OpenAI](#étape-4--fine-tuning-avec-openai)
- [Étape 5 : Fine-tuning local avec Ollama/LoRA](#étape-5--fine-tuning-local-avec-ollama-lora)
- [Étape 6 : Évaluation du modèle fine-tuné](#étape-6--évaluation-du-modèle-fine-tuné)
- [Étape 7 : Comparaison RAG vs Fine-tuning](#étape-7--comparaison-rag-vs-fine-tuning)
- [Annexes](#annexes)

---

## Introduction

Le **fine-tuning** consiste à adapter un modèle pré-entraîné (GPT, Llama, etc.) à vos données spécifiques. Contrairement au RAG qui récupère des informations, le fine-tuning **encode les connaissances directement dans les poids du modèle**.

### Quand utiliser le fine-tuning ?

✅ **Utilisez le fine-tuning si :**
- Vous avez **beaucoup de données** (>1000 exemples)
- Les données changent **rarement** (mise à jour trimestrielle/annuelle)
- Vous voulez un **style de réponse spécifique** (ton, format)
- Vous avez besoin de **latence très faible** (pas de récupération)
- Vous avez un **budget** pour l'entraînement

❌ **N'utilisez PAS le fine-tuning si :**
- Vos données changent **fréquemment** (quotidien/hebdomadaire)
- Vous avez **peu de données** (<500 exemples)
- Vous voulez **mettre à jour facilement** les connaissances
- Vous avez un **budget limité**
- Vous voulez **tracer les sources** des réponses

---

## RAG vs Fine-tuning : Quelle approche choisir ?

| Critère | RAG | Fine-tuning | Recommandation |
|---------|-----|-------------|----------------|
| **Données** | 50+ documents | 1000+ exemples QA | RAG pour petits corpus |
| **Mise à jour** | Instantanée | Ré-entraînement complet | RAG pour données dynamiques |
| **Coût** | ~$0/mois (Ollama) | $50-500/entraînement | RAG pour budget limité |
| **Latence** | 2-5s | 0.5-2s | Fine-tuning si latence critique |
| **Traçabilité** | ✅ Sources citées | ❌ Boîte noire | RAG pour audit/compliance |
| **Style** | Dépend du prompt | ✅ Appris | Fine-tuning pour style spécifique |
| **Précision** | 80-90% | 85-95% | Fine-tuning si données suffisantes |

### 💡 Approche hybride (recommandée)

La meilleure approche combine souvent les deux :
1. **Fine-tuning** pour le style et les connaissances de base
2. **RAG** pour les détails spécifiques et les mises à jour fréquentes

Exemple : Modèle fine-tuné sur le jargon du domaine + RAG pour les applications spécifiques.

---

## Prérequis

### Installation

```bash
# Installation de base
poetry install

# Installation avec support RAG/Fine-tuning
poetry install -E rag
pip install -r requirements-finetuning.txt
```

### Outils requis

| Outil | Usage | Installation |
|-------|-------|--------------|
| **OpenAI API** | Fine-tuning cloud (payant) | Clé API OpenAI |
| **Ollama** | Fine-tuning local (gratuit) | https://ollama.com |
| **unsloth** | Accélération LoRA (optionnel) | `pip install unsloth` |
| **wandb** | Monitoring (optionnel) | `pip install wandb` |

### Configuration

```bash
# Créer .env
cat > .env << EOF
# Fine-tuning OpenAI
OPENAI_API_KEY=sk-proj-votre-clé

# Fine-tuning local
WANDB_API_KEY=votre-clé-wandb  # Optionnel

# Modèle de base pour fine-tuning local
BASE_MODEL=llama3.2
EOF
```

---

## Vue d'ensemble du workflow

```
┌──────────────────────────────────────────────────────────────┐
│              WORKFLOW FINE-TUNING COMPLET                     │
└──────────────────────────────────────────────────────────────┘

1. 📊 PRÉPARATION DES DONNÉES
   └─> Analyser applicationsIA_mini_normalized.json
       - Identifier les champs clés
       - Comprendre la structure

2. 🔨 CRÉATION DU DATASET
   └─> dyag create_rag
       - Génération automatique de questions/réponses
       - Format OpenAI compatible (.jsonl)
       - Validation de la qualité

3. ✅ VALIDATION & NETTOYAGE
   └─> dyag analyze_training
       - Vérification du format
       - Détection d'anomalies
       - Statistiques du dataset

4. ☁️ FINE-TUNING OPENAI
   └─> Utiliser l'API OpenAI
       - Upload du dataset
       - Lancement de l'entraînement
       - Monitoring des métriques

5. 💻 FINE-TUNING LOCAL (LORA)
   └─> Ollama + LoRA
       - Configuration de l'environnement
       - Entraînement adapté
       - Export du modèle

6. 📈 ÉVALUATION
   └─> dyag evaluate_rag (avec modèle fine-tuné)
       - Métriques de performance
       - Comparaison avec baseline
       - Analyse des erreurs

7. 🔄 AMÉLIORATION ITÉRATIVE
   └─> Cycle d'optimisation
       - Ajuster hyperparamètres
       - Enrichir le dataset
       - Re-tester
```

---

## Étape 1 : Préparation des données d'entraînement

### 1.1 Analyse du fichier source

**Commande CLI :**
```bash
# Examiner la structure
python -c "
import json
data = json.load(open('examples/test-mygusi/applicationsIA_mini_normalized.json'))
apps = data['applicationsia mini']

print(f'📊 Statistiques:')
print(f'  Nombre total d\\'applications: {len(apps)}')
print(f'  Applications en production: {sum(1 for a in apps if a.get(\"statut si\") == \"en production\")}')
print(f'  Applications avec descriptif: {sum(1 for a in apps if a.get(\"descriptif\"))}')

# Analyser les champs disponibles
all_fields = set()
for app in apps:
    all_fields.update(app.keys())

print(f'\\n📋 Champs disponibles ({len(all_fields)}):')
for field in sorted(all_fields):
    count = sum(1 for a in apps if field in a and a[field])
    print(f'  - {field}: {count}/{len(apps)} ({count/len(apps)*100:.0f}%)')
"
```

**Résultat attendu :**
```
📊 Statistiques:
  Nombre total d'applications: 45
  Applications en production: 28
  Applications avec descriptif: 42

📋 Champs disponibles (15):
  - nom: 45/45 (100%)
  - nom long: 43/45 (96%)
  - descriptif: 42/45 (93%)
  - statut si: 45/45 (100%)
  - domaines et sous domaines: 40/45 (89%)
  - sites: 38/45 (84%)
  - acteurs: 35/45 (78%)
  - contacts: 30/45 (67%)
  ...
```

### 1.2 Identifier les patterns de questions

Pour un bon dataset de fine-tuning, il faut couvrir différents types de questions :

| Type de question | Exemple | Champs utilisés |
|------------------|---------|-----------------|
| **Définition** | "Qu'est-ce que {nom} ?" | nom, nom long, descriptif |
| **Statut** | "Quel est le statut de {nom} ?" | nom, statut si |
| **Domaine** | "Dans quel domaine est {nom} ?" | nom, domaines et sous domaines |
| **Acteurs** | "Qui gère {nom} ?" | nom, acteurs |
| **Sites** | "Où trouver {nom} ?" | nom, sites |
| **Comparative** | "Différence entre {nom1} et {nom2} ?" | Tous |
| **Listing** | "Liste des applications {critère}" | statut si, domaines |

### 1.3 Calculer la taille nécessaire du dataset

**Règle générale :**
- **Minimum viable** : 100 exemples (pour fine-tuning léger)
- **Bon** : 500-1000 exemples
- **Optimal** : 2000-5000 exemples
- **Enterprise** : 10000+ exemples

**Pour notre cas (45 applications) :**
```
Nombre d'exemples = Nb applications × Nb types de questions × Variations

Exemple :
45 apps × 7 types × 3 variations = 945 exemples
```

✅ C'est suffisant pour un bon fine-tuning !

---

## Étape 2 : Création du dataset de fine-tuning

### 2.1 Génération automatique avec dyag

**Commande CLI :**
```bash
# Créer le dataset de fine-tuning
dyag create_rag \
  examples/test-mygusi/applicationsIA_mini_normalized.json \
  --output training/finetuning_dataset.jsonl \
  --num-questions 1000 \
  --question-types all \
  --format openai \
  --add-negatives \
  --verbose
```

**Paramètres expliqués :**
- `--num-questions 1000` : Générer 1000 paires question/réponse
- `--question-types all` : Tous les types (définition, statut, domaine, etc.)
- `--format openai` : Format compatible OpenAI fine-tuning API
- `--add-negatives` : Ajouter des exemples négatifs (questions sans réponse)
- `--verbose` : Afficher la progression

**Format OpenAI généré :**
```json
{"messages": [{"role": "system", "content": "Tu es un assistant expert en applications du système d'information français."}, {"role": "user", "content": "Qu'est-ce que l'application 6tzen ?"}, {"role": "assistant", "content": "L'application 6tzen est l'outil national de dématérialisation des démarches des transports routiers. Elle est actuellement en production et permet aux entreprises de transport routier d'effectuer leurs démarches administratives en ligne."}]}
{"messages": [{"role": "system", "content": "Tu es un assistant expert en applications du système d'information français."}, {"role": "user", "content": "Quel est le statut de 8-SINP ?"}, {"role": "assistant", "content": "L'application 8-SINP (plateformes régionales SINP habilitées) est actuellement en construction."}]}
```

### 2.2 Split train/validation/test

**Commande CLI :**
```bash
# Séparer en train (80%), validation (10%), test (10%)
python -c "
import json
import random

# Charger le dataset
lines = open('training/finetuning_dataset.jsonl').readlines()
random.shuffle(lines)

# Split
n = len(lines)
train_size = int(0.8 * n)
val_size = int(0.1 * n)

train = lines[:train_size]
val = lines[train_size:train_size+val_size]
test = lines[train_size+val_size:]

# Sauvegarder
with open('training/train.jsonl', 'w') as f:
    f.writelines(train)
with open('training/validation.jsonl', 'w') as f:
    f.writelines(val)
with open('training/test.jsonl', 'w') as f:
    f.writelines(test)

print(f'✅ Dataset séparé:')
print(f'  Train: {len(train)} exemples')
print(f'  Validation: {len(val)} exemples')
print(f'  Test: {len(test)} exemples')
"
```

**Résultat attendu :**
```
✅ Dataset séparé:
  Train: 800 exemples
  Validation: 100 exemples
  Test: 100 exemples
```

---

## Étape 3 : Validation et nettoyage du dataset

### 3.1 Analyse de la couverture

**Commande CLI :**
```bash
# Analyser la couverture des applications
dyag analyze_training \
  examples/test-mygusi/applicationsIA_mini_normalized.json \
  training/train.jsonl \
  --verbose
```

**Résultat attendu :**
```
╔══════════════════════════════════════════════════════════════╗
║              ANALYSE DE COUVERTURE DU TRAINING               ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistiques globales:
  Applications totales: 45
  Applications couvertes: 43 (95.6%)
  Applications non couvertes: 2
    - ID 1523: Application XYZ
    - ID 1789: Application ABC

📈 Distribution des types de questions:
  Définition: 215 (26.9%)
  Statut: 180 (22.5%)
  Domaine: 165 (20.6%)
  Acteurs: 120 (15.0%)
  Sites: 80 (10.0%)
  Comparative: 40 (5.0%)

⚠️  Recommandations:
  [1] Ajouter des exemples pour les applications non couvertes
  [2] Équilibrer les types de questions (plus de comparatives)
  [3] Vérifier la qualité des descriptifs trop courts (<50 caractères)
```

### 3.2 Validation du format

**Commande CLI :**
```bash
# Valider le format OpenAI
python -c "
import json

errors = []
for i, line in enumerate(open('training/train.jsonl'), 1):
    try:
        data = json.loads(line)

        # Vérifier la structure
        if 'messages' not in data:
            errors.append(f'Ligne {i}: Pas de clé \"messages\"')
            continue

        messages = data['messages']
        if len(messages) < 2:
            errors.append(f'Ligne {i}: Moins de 2 messages')

        # Vérifier les rôles
        roles = [m['role'] for m in messages]
        if 'user' not in roles or 'assistant' not in roles:
            errors.append(f'Ligne {i}: Rôles manquants')

    except json.JSONDecodeError:
        errors.append(f'Ligne {i}: JSON invalide')

if errors:
    print(f'❌ {len(errors)} erreurs trouvées:')
    for err in errors[:10]:  # Afficher les 10 premières
        print(f'  {err}')
else:
    print('✅ Format valide! Aucune erreur détectée.')
"
```

### 3.3 Nettoyage des duplicatas

**Commande CLI :**
```bash
# Détecter et supprimer les duplicatas
python -c "
import json
from collections import defaultdict

seen = set()
unique_lines = []
duplicates = 0

for line in open('training/train.jsonl'):
    data = json.loads(line)
    # Créer une clé unique basée sur la question
    key = data['messages'][1]['content']  # Question de l'user

    if key not in seen:
        seen.add(key)
        unique_lines.append(line)
    else:
        duplicates += 1

# Sauvegarder la version nettoyée
with open('training/train_clean.jsonl', 'w') as f:
    f.writelines(unique_lines)

print(f'✅ Nettoyage terminé:')
print(f'  Lignes originales: {len(unique_lines) + duplicates}')
print(f'  Duplicatas supprimés: {duplicates}')
print(f'  Lignes uniques: {len(unique_lines)}')
"
```

---

## Étape 4 : Fine-tuning avec OpenAI

### 4.1 Vérifier les prérequis

```bash
# Installer OpenAI CLI
pip install openai

# Vérifier la clé API
python -c "
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ Clé API OpenAI valide')
"
```

### 4.2 Upload du dataset

```bash
# Upload training file
python -c "
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Upload train
train_file = client.files.create(
    file=open('training/train_clean.jsonl', 'rb'),
    purpose='fine-tune'
)
print(f'📤 Train file uploaded: {train_file.id}')

# Upload validation
val_file = client.files.create(
    file=open('training/validation.jsonl', 'rb'),
    purpose='fine-tune'
)
print(f'📤 Validation file uploaded: {val_file.id}')

# Sauvegarder les IDs
with open('training/file_ids.txt', 'w') as f:
    f.write(f'TRAIN_FILE_ID={train_file.id}\\n')
    f.write(f'VAL_FILE_ID={val_file.id}\\n')
"
```

### 4.3 Lancer le fine-tuning

```bash
# Créer le job de fine-tuning
python -c "
from openai import OpenAI
import os

# Lire les IDs
with open('training/file_ids.txt') as f:
    ids = dict(line.strip().split('=') for line in f)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Créer le fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=ids['TRAIN_FILE_ID'],
    validation_file=ids['VAL_FILE_ID'],
    model='gpt-3.5-turbo',  # ou 'gpt-4o-mini-2024-07-18'
    hyperparameters={
        'n_epochs': 3,
        'batch_size': 4,
        'learning_rate_multiplier': 2.0
    }
)

print(f'🚀 Fine-tuning job créé: {job.id}')
print(f'   Modèle de base: {job.model}')
print(f'   Status: {job.status}')

# Sauvegarder le job ID
with open('training/job_id.txt', 'w') as f:
    f.write(job.id)
"
```

**Coût estimé :**
- GPT-3.5-turbo : ~$8 pour 800 exemples × 3 epochs
- GPT-4o-mini : ~$15 pour 800 exemples × 3 epochs

### 4.4 Monitoring du fine-tuning

```bash
# Surveiller la progression
python -c "
from openai import OpenAI
import os
import time

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Lire le job ID
job_id = open('training/job_id.txt').read().strip()

print('📊 Monitoring du fine-tuning (Ctrl+C pour arrêter)\\n')

while True:
    job = client.fine_tuning.jobs.retrieve(job_id)

    print(f'Status: {job.status}')
    if job.status == 'succeeded':
        print(f'✅ Fine-tuning terminé!')
        print(f'   Modèle fine-tuné: {job.fine_tuned_model}')

        # Sauvegarder le modèle ID
        with open('training/finetuned_model.txt', 'w') as f:
            f.write(job.fine_tuned_model)
        break
    elif job.status in ['failed', 'cancelled']:
        print(f'❌ Fine-tuning échoué: {job.status}')
        break

    time.sleep(30)  # Vérifier toutes les 30s
"
```

### 4.5 Tester le modèle fine-tuné

```bash
# Tester avec quelques questions
python -c "
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Lire le modèle fine-tuné
model_id = open('training/finetuned_model.txt').read().strip()

print(f'🧪 Test du modèle fine-tuné: {model_id}\\n')

questions = [
    'Qu\\'est-ce que l\\'application 6tzen ?',
    'Quel est le statut de 8-SINP ?',
    'Liste les applications du domaine biodiversité'
]

for q in questions:
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {'role': 'system', 'content': 'Tu es un assistant expert en applications SI.'},
            {'role': 'user', 'content': q}
        ]
    )

    print(f'Q: {q}')
    print(f'R: {response.choices[0].message.content}\\n')
"
```

---

## Étape 5 : Fine-tuning local avec Ollama/LoRA

### 5.1 Préparer l'environnement

```bash
# Installer les dépendances
pip install unsloth transformers datasets peft bitsandbytes

# Vérifier GPU (optionnel mais recommandé)
nvidia-smi
```

### 5.2 Convertir le dataset au format Alpaca

```python
# Script de conversion : convert_to_alpaca.py
import json

def convert_to_alpaca(input_file, output_file):
    """Convertit du format OpenAI au format Alpaca."""
    alpaca_data = []

    for line in open(input_file):
        data = json.loads(line)
        messages = data['messages']

        # Extraire instruction et réponse
        instruction = messages[1]['content']  # user message
        output = messages[2]['content']       # assistant message
        system = messages[0]['content'] if messages[0]['role'] == 'system' else ''

        alpaca_data.append({
            'instruction': instruction,
            'input': system,
            'output': output
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(alpaca_data, f, ensure_ascii=False, indent=2)

    print(f'✅ Converti {len(alpaca_data)} exemples vers {output_file}')

# Convertir
convert_to_alpaca('training/train_clean.jsonl', 'training/train_alpaca.json')
convert_to_alpaca('training/validation.jsonl', 'training/val_alpaca.json')
```

### 5.3 Fine-tuning avec unsloth (LoRA)

```python
# Script : finetune_local.py
from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Charger le modèle de base
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-3b",  # ou "unsloth/mistral-7b"
    max_seq_length=2048,
    dtype=torch.float16,
    load_in_4bit=True,  # Quantization 4-bit pour économiser la RAM
)

# 2. Configurer LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # Rank LoRA
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
)

# 3. Charger le dataset
dataset = load_dataset("json", data_files={
    "train": "training/train_alpaca.json",
    "validation": "training/val_alpaca.json"
})

# 4. Créer le trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    dataset_text_field="output",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=500,  # Ajuster selon la taille du dataset
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        output_dir="models/finetuned_llama",
        optim="adamw_8bit",
        save_strategy="steps",
        save_steps=100,
        evaluation_strategy="steps",
        eval_steps=100,
    ),
)

# 5. Lancer l'entraînement
print("🚀 Démarrage du fine-tuning local...")
trainer.train()

# 6. Sauvegarder le modèle
model.save_pretrained("models/finetuned_llama_final")
tokenizer.save_pretrained("models/finetuned_llama_final")
print("✅ Modèle sauvegardé dans models/finetuned_llama_final")
```

**Lancer :**
```bash
python finetune_local.py
```

**Temps estimé :**
- GPU RTX 3090 : 30-60 minutes
- GPU T4 (Colab) : 1-2 heures
- CPU : Non recommandé (>10 heures)

### 5.4 Export vers Ollama

```bash
# Créer un Modelfile pour Ollama
cat > Modelfile.applications << 'EOF'
FROM models/finetuned_llama_final

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM """
Tu es un assistant expert en applications du système d'information français.
Tu réponds de manière précise et concise aux questions sur les applications.
"""
EOF

# Créer le modèle Ollama
ollama create applications-ia -f Modelfile.applications

# Tester
ollama run applications-ia "Qu'est-ce que 6tzen ?"
```

---

## Étape 6 : Évaluation du modèle fine-tuné

### 6.1 Évaluation automatique avec dyag

**Commande CLI (OpenAI) :**
```bash
# Tester avec le modèle fine-tuné OpenAI
export FINETUNED_MODEL=$(cat training/finetuned_model.txt)

python -c "
import os
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['LLM_MODEL'] = os.environ['FINETUNED_MODEL']
" && dyag evaluate_rag \
  training/test.jsonl \
  --collection applications_ia \
  --output evaluation/finetuned_results.json \
  --verbose
```

**Commande CLI (Ollama local) :**
```bash
# Tester avec le modèle Ollama fine-tuné
export LLM_PROVIDER=ollama
export LLM_MODEL=applications-ia

dyag evaluate_rag \
  training/test.jsonl \
  --collection applications_ia \
  --output evaluation/finetuned_local_results.json \
  --verbose
```

### 6.2 Comparaison baseline vs fine-tuned

```bash
# Comparer les résultats
python -c "
import json

# Charger les résultats
baseline = json.load(open('evaluation/baseline_results.json'))  # RAG ou modèle non fine-tuné
finetuned = json.load(open('evaluation/finetuned_results.json'))

print('📊 Comparaison Baseline vs Fine-tuned\\n')
print(f'{\"Métrique\":<25} {\"Baseline\":>12} {\"Fine-tuned\":>12} {\"Δ\":>8}')
print('-' * 60)

metrics = ['accuracy', 'precision', 'recall', 'f1_score']
for metric in metrics:
    b_val = baseline.get(metric, 0)
    f_val = finetuned.get(metric, 0)
    delta = f_val - b_val

    print(f'{metric.capitalize():<25} {b_val:>11.1%} {f_val:>11.1%} {delta:>+7.1%}')

print('\\n⏱️  Latence')
b_time = baseline.get('average_generation_time_ms', 0)
f_time = finetuned.get('average_generation_time_ms', 0)
print(f'Baseline: {b_time:.0f}ms')
print(f'Fine-tuned: {f_time:.0f}ms')
print(f'Amélioration: {(b_time-f_time)/b_time*100:+.1f}%')
"
```

**Résultat attendu :**
```
📊 Comparaison Baseline vs Fine-tuned

Métrique                      Baseline   Fine-tuned        Δ
------------------------------------------------------------
Accuracy                         82.0%        91.5%    +9.5%
Precision                        78.5%        89.2%   +10.7%
Recall                           75.3%        88.8%   +13.5%
F1_score                         76.9%        89.0%   +12.1%

⏱️  Latence
Baseline: 2340ms
Fine-tuned: 1850ms
Amélioration: +20.9%
```

### 6.3 Analyse qualitative

```bash
# Examiner les prédictions sur le test set
python -c "
import json

results = json.load(open('evaluation/finetuned_results.json'))
errors = results.get('errors', [])

print(f'❌ Erreurs ({len(errors)}) :\\n')
for i, err in enumerate(errors[:5], 1):  # Top 5
    print(f'{i}. Question: {err[\"question\"]}')
    print(f'   Attendu: {err[\"expected\"][:100]}...')
    print(f'   Obtenu: {err[\"got\"][:100]}...')
    print(f'   Raison: {err.get(\"reason\", \"N/A\")}\\n')
"
```

---

## Étape 7 : Comparaison RAG vs Fine-tuning

### 7.1 Test côte à côte

```bash
# Créer un script de comparaison
cat > compare_approaches.py << 'EOF'
from dyag.rag_query import RAGQuerySystem
from openai import OpenAI
import os

questions = [
    "Qu'est-ce que l'application 6tzen ?",
    "Quel est le statut de 8-SINP ?",
    "Liste les applications du domaine biodiversité"
]

# RAG
print("🔍 RAG (avec Ollama)")
rag = RAGQuerySystem(collection_name='applications_ia')
for q in questions:
    result = rag.query(q, n_chunks=5)
    print(f"Q: {q}")
    print(f"R: {result['answer'][:200]}...\n")

# Fine-tuned
print("\n🎯 Fine-tuned (OpenAI)")
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = open('training/finetuned_model.txt').read().strip()

for q in questions:
    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': q}]
    )
    print(f"Q: {q}")
    print(f"R: {response.choices[0].message.content[:200]}...\n")
EOF

python compare_approaches.py
```

### 7.2 Tableau de décision

```
┌────────────────────────────────────────────────────────────────┐
│              QUAND UTILISER QUELLE APPROCHE ?                   │
├────────────────────────────────────────────────────────────────┤
│ Votre situation                    │ Recommandation            │
├────────────────────────────────────┼──────────────────────────┤
│ • <50 applications                 │ ❌ NI l'un NI l'autre     │
│ • Peu de questions                 │ → Utiliser GPT-4 direct   │
├────────────────────────────────────┼──────────────────────────┤
│ • 50-200 applications              │ ✅ RAG                    │
│ • Mises à jour fréquentes          │                           │
│ • Budget limité                    │                           │
├────────────────────────────────────┼──────────────────────────┤
│ • 200-1000 applications            │ ✅ RAG + Fine-tuning      │
│ • Style spécifique requis          │ → Fine-tuning pour style  │
│ • Budget moyen                     │ → RAG pour connaissances  │
├────────────────────────────────────┼──────────────────────────┤
│ • >1000 applications               │ ✅ Fine-tuning            │
│ • Données stables                  │ → Avec RAG optionnel      │
│ • Latence critique                 │ → pour mises à jour       │
│ • Budget élevé                     │                           │
└────────────────────────────────────┴──────────────────────────┘
```

---

## Annexes

### Annexe A : Hyperparamètres recommandés

#### OpenAI Fine-tuning

| Paramètre | Petit dataset (<500) | Moyen (500-2000) | Grand (>2000) |
|-----------|---------------------|------------------|---------------|
| **n_epochs** | 5-10 | 3-5 | 1-3 |
| **batch_size** | 2-4 | 4-8 | 8-16 |
| **learning_rate_multiplier** | 2.0 | 1.5 | 1.0 |

#### LoRA Local

| Paramètre | Petit dataset | Moyen | Grand |
|-----------|--------------|--------|-------|
| **r** (rank) | 8 | 16 | 32 |
| **lora_alpha** | 16 | 32 | 64 |
| **lora_dropout** | 0.1 | 0.05 | 0.01 |
| **learning_rate** | 3e-4 | 2e-4 | 1e-4 |

### Annexe B : Checklist qualité du dataset

Avant de lancer le fine-tuning, vérifiez :

- [ ] **Taille minimale** : >100 exemples (idéal >500)
- [ ] **Format valide** : Tous les JSONs sont bien formés
- [ ] **Pas de duplicatas** : Questions uniques
- [ ] **Couverture** : >90% des applications représentées
- [ ] **Équilibre** : Chaque type de question représenté
- [ ] **Qualité** : Réponses précises et complètes
- [ ] **Longueur** : Réponses ni trop courtes (<20 mots) ni trop longues (>200 mots)
- [ ] **Négatifs** : Inclut des exemples "Je ne sais pas"
- [ ] **Split** : Train/Val/Test séparés (80/10/10)

### Annexe C : Coûts estimés (2025)

| Provider | Setup | Training (1000 exemples) | Inference |
|----------|-------|-------------------------|-----------|
| **Ollama** | Gratuit | Gratuit (GPU local) | Gratuit |
| **OpenAI GPT-3.5-turbo** | $0 | ~$8 | ~$0.002/requête |
| **OpenAI GPT-4o-mini** | $0 | ~$15 | ~$0.005/requête |
| **Anthropic Claude** | N/A | Non disponible | ~$0.015/requête |

### Annexe D : Ressources

**Fine-tuning OpenAI :**
- https://platform.openai.com/docs/guides/fine-tuning

**Unsloth (LoRA rapide) :**
- https://github.com/unslothai/unsloth

**Datasets :**
- https://huggingface.co/datasets

**Monitoring :**
- https://wandb.ai/

---

## 🎯 Checklist de succès

Votre modèle fine-tuné est prêt si :

- [ ] **Accuracy > 85%** sur le test set
- [ ] **Latence < 2s** par requête
- [ ] **Pas d'hallucinations** majeures
- [ ] **Style cohérent** avec vos attentes
- [ ] **Coût acceptable** (training + inference)
- [ ] **Déployable** (API accessible ou modèle local)
- [ ] **Maintenable** (process de ré-entraînement documenté)

---

**Dernière mise à jour** : 2025-01-16
**Version du guide** : 1.0
**Auteur** : Équipe Dyag

---

**Dyag** - Fine-tuning de qualité, étape par étape! 🎯🚀
