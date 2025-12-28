# Guide : Obtenir l'Accès aux Modèles Llama (Meta)

Les modèles Llama de Meta (Llama 3.2, Llama 3.1, etc.) sont des **modèles "gated"** sur HuggingFace, ce qui signifie qu'ils nécessitent :
1. Un compte HuggingFace
2. Une demande d'accès approuvée
3. Une authentification via token

## Étape 1 : Créer un Compte HuggingFace

Si vous n'avez pas encore de compte :

1. Allez sur https://huggingface.co/join
2. Créez un compte (gratuit)
3. Vérifiez votre email

## Étape 2 : Demander l'Accès aux Modèles Llama

### Pour Llama 3.2-1B-Instruct

1. Visitez : https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
2. Cliquez sur **"Request Access"** ou **"Demander l'accès"**
3. Acceptez les conditions d'utilisation de Meta
4. Soumettez la demande

**Délai d'approbation** : Généralement quelques minutes à quelques heures (parfois instantané)

### Pour Llama 3.1-8B-Instruct

1. Visitez : https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
2. Même processus que ci-dessus

**Note** : Une fois approuvé pour un modèle Llama, vous avez généralement accès à tous les modèles de la même famille.

## Étape 3 : Créer un Token d'Accès

1. Allez dans vos paramètres : https://huggingface.co/settings/tokens
2. Cliquez sur **"New token"** ou **"Nouveau token"**
3. Donnez un nom au token (ex: "dyag-finetuning")
4. Sélectionnez le type : **"Read"** (lecture seule suffit)
5. Cliquez sur **"Generate token"**
6. **IMPORTANT** : Copiez le token immédiatement (vous ne pourrez plus le voir après)

Format du token : `hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

## Étape 4 : Authentification sur Votre Machine

### Option A : Via CLI (Recommandé)

```bash
# Installer huggingface_hub si pas déjà fait
pip install -U huggingface_hub

# Se connecter avec votre token
huggingface-cli login

# Collez votre token quand demandé
# Token: hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Le token sera sauvegardé dans `~/.cache/huggingface/token` et utilisé automatiquement.

### Option B : Via Variable d'Environnement

Ajoutez dans votre `.env` :

```bash
HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Puis chargez-le avant d'utiliser DYAG :

```bash
# Linux/Mac
export HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Windows PowerShell
$env:HF_TOKEN="hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Windows CMD
set HF_TOKEN=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Option C : Programmatiquement

Dans votre code Python :

```python
from huggingface_hub import login

login(token="hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
```

## Étape 5 : Vérifier l'Accès

Testez que vous avez accès :

```bash
python -c "
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-1B-Instruct')
print('[OK] Accès confirmé à Llama 3.2-1B-Instruct')
"
```

Si vous voyez `[OK] Accès confirmé`, tout fonctionne !

Si vous voyez une erreur 401 ou "gated repo", réessayez les étapes précédentes.

## Étape 6 : Utiliser avec DYAG

Une fois l'accès configuré, utilisez normalement :

```bash
# Fine-tuning Llama 3.2
dyag finetune \
  --dataset data/finetuning/dataset_100_train.jsonl \
  --output models/llama32-mygusi-100 \
  --base-model llama3.2:1b \
  --epochs 3 --batch-size 4

# Ou avec le chemin complet
dyag finetune \
  --dataset data/finetuning/dataset_100_train.jsonl \
  --output models/llama32-mygusi-100 \
  --base-model meta-llama/Llama-3.2-1B-Instruct \
  --epochs 3 --batch-size 4
```

## Dépannage

### Erreur : "401 Client Error: Unauthorized"

**Cause** : Token manquant ou invalide

**Solution** :
1. Vérifiez que vous êtes connecté : `huggingface-cli whoami`
2. Reconnectez-vous : `huggingface-cli login`
3. Vérifiez que le token a les permissions "Read"

### Erreur : "Cannot access gated repo"

**Cause** : Accès au modèle pas encore approuvé

**Solution** :
1. Vérifiez votre email pour confirmation
2. Visitez à nouveau la page du modèle
3. Attendez quelques heures si la demande est récente
4. Contactez le support HuggingFace si > 24h

### Erreur : "Repository not found"

**Cause** : Nom du modèle incorrect

**Solution** : Vérifiez l'orthographe exacte sur HuggingFace

## Alternatives aux Modèles Gated

Si vous voulez éviter le processus d'authentification, utilisez des modèles non-gated :

| Modèle Gated | Alternative Non-Gated | Qualité |
|--------------|----------------------|---------|
| Llama 3.2-1B | Qwen2.5-1.5B ✅ | Similaire voire meilleure |
| Llama 3.1-8B | Qwen2.5-7B | Similaire |
| Llama 3.1-8B | Mistral-7B-Instruct-v0.2 | Similaire |

**Recommandation** : Utilisez **Qwen2.5-1.5B** (`qwen2.5:1.5b` dans DYAG) comme alternative à Llama 3.2.

## Modèles Llama Disponibles

Une fois l'accès obtenu, vous aurez accès à :

- **Llama 3.2-1B** : Modèle léger (1B params)
- **Llama 3.2-3B** : Modèle moyen (3B params)
- **Llama 3.1-8B** : Modèle puissant (8B params)
- **Llama 3.1-70B** : Très puissant (70B params, nécessite multi-GPU)

Dans DYAG, utilisez les raccourcis :
- `llama3.2:1b` → Llama-3.2-1B-Instruct
- `llama3.1:8b` → Llama-3.1-8B-Instruct

## Conditions d'Utilisation

Les modèles Llama de Meta sont soumis à des conditions :

- ✅ **Usage commercial autorisé** (sous conditions)
- ✅ **Modifications autorisées**
- ✅ **Distribution autorisée**
- ⚠️ **Attribution requise**
- ⚠️ **Restrictions sur certains usages** (voir licence)

Lisez la licence complète : https://ai.meta.com/llama/license/

## FAQ

### Dois-je payer pour accéder aux modèles Llama ?

Non, l'accès est **gratuit**. Seule l'utilisation via HuggingFace Inference API (cloud) est payante.

### Le token expire-t-il ?

Les tokens HuggingFace n'expirent pas par défaut, sauf si vous les révoquez manuellement.

### Puis-je partager mon token ?

❌ Non, les tokens sont personnels. Chaque utilisateur doit créer son propre token.

### Combien de temps prend l'approbation ?

Généralement **quelques minutes à quelques heures**. Parfois instantané.

### Puis-je utiliser les modèles offline après téléchargement ?

Oui, une fois téléchargés dans le cache HuggingFace (`~/.cache/huggingface/`), vous pouvez les utiliser offline.

### Où sont stockés les modèles téléchargés ?

**Linux/Mac** : `~/.cache/huggingface/hub/`
**Windows** : `C:\Users\<username>\.cache\huggingface\hub\`

Vous pouvez changer avec la variable d'environnement `HF_HOME`.

## Support

- Documentation HuggingFace : https://huggingface.co/docs
- Forum HuggingFace : https://discuss.huggingface.co/
- Llama Meta : https://ai.meta.com/llama/

---

**Dernière mise à jour** : 28 décembre 2024
