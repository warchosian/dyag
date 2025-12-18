# Guide Pratique : Fine-Tuning pour DYAG

## Guide rapide en 4 étapes

### Étape 1 : Préparer les données (30 min)

```bash
# Générer 100 exemples de Q&A depuis vos chunks
python scripts/prepare_finetuning_data.py --count 100

# Ou 500 exemples pour meilleure qualité (recommandé)
python scripts/prepare_finetuning_data.py --count 500 --output data/finetuning/dataset.jsonl
```

**Ce qui se passe** :
- Lit vos chunks RAG existants
- Génère des questions variées (qui héberge ?, quelles technologies ?, etc.)
- Utilise GPT-4o-mini pour générer les réponses
- Split automatiquement en train/validation/test (80/10/10%)

**Coût estimé** : ~$0.10-0.50 selon le nombre d'exemples

**Sortie** :
```
data/finetuning/
├── dataset_train.jsonl       # 80 exemples (pour 100 total)
├── dataset_validation.jsonl  # 10 exemples
└── dataset_test.jsonl        # 10 exemples
```

### Étape 2 : Lancer le fine-tuning (10 min - 2h)

```bash
# Lancer le fine-tuning sur gpt-4o-mini
python scripts/finetune_model.py \
    --train data/finetuning/dataset_train.jsonl \
    --validation data/finetuning/dataset_validation.jsonl \
    --suffix "dyag-v1" \
    --wait
```

**Ce qui se passe** :
- Upload les fichiers vers OpenAI
- Crée un job de fine-tuning
- Attend la fin (10min-2h selon taille dataset)
- Affiche le model ID final

**Coût estimé** :
- 100 exemples : ~$0.50
- 500 exemples : ~$2-5
- 1000 exemples : ~$10-20

**Sortie** :
```
✓ FINE-TUNING TERMINÉ AVEC SUCCÈS

Modèle fine-tuné: ft:gpt-4o-mini-2024-07-18:org::abc123
Tokens entraînés: 50000
```

### Étape 3 : Tester le modèle (5 min)

```bash
# Lancer le chat avec le modèle fine-tuné
python scripts/chat_hybrid.py \
    --finetuned-model ft:gpt-4o-mini-2024-07-18:org::abc123
```

**Comparer avec RAG standard** :
```bash
# Terminal 1 : RAG standard
python scripts/chat.py

# Terminal 2 : RAG + Fine-tuning
python scripts/chat_hybrid.py --finetuned-model ft:gpt-4o-mini-2024-07-18:org::abc123
```

### Étape 4 : Évaluer et itérer (continu)

Posez les mêmes questions aux deux systèmes et comparez :
- **Précision** : Les faits sont-ils corrects ?
- **Style** : Le ton est-il professionnel/métier ?
- **Complétude** : Les réponses sont-elles détaillées ?

Si besoin, améliorez le dataset et relancez le fine-tuning.

---

## Workflows détaillés

### Workflow 1 : Premier fine-tuning rapide (100 exemples)

**Objectif** : Tester rapidement si le fine-tuning apporte de la valeur

**Temps** : 1-2h total
**Coût** : ~$1-2

```bash
# 1. Préparer 100 exemples (30 min)
python scripts/prepare_finetuning_data.py --count 100

# 2. Lancer le fine-tuning (20-40 min)
python scripts/finetune_model.py \
    --train data/finetuning/dataset_train.jsonl \
    --wait

# 3. Noter le model ID
# ex: ft:gpt-4o-mini-2024-07-18:org::abc123

# 4. Tester immédiatement
python scripts/chat_hybrid.py \
    --finetuned-model ft:gpt-4o-mini-2024-07-18:org::abc123
```

**Questions de test** :
```
1. Qui héberge GIDAF ?
2. Quelles technologies utilise MYGUSI ?
3. Liste les applications hébergées par SI-RAPP
```

**Critères de succès** :
- [ ] Le modèle comprend le vocabulaire métier (SI-RAPP, etc.)
- [ ] Les réponses sont factuellement correctes
- [ ] Le style est professionnel

### Workflow 2 : Fine-tuning de production (500+ exemples)

**Objectif** : Créer un modèle de qualité production

**Temps** : 1 journée
**Coût** : ~$5-20

```bash
# 1. Préparer 500 exemples de qualité (2-3h)
python scripts/prepare_finetuning_data.py --count 500

# 2. Vérifier manuellement la qualité (30 min)
# Ouvrir data/finetuning/dataset_train.jsonl
# Vérifier 20-30 exemples aléatoires
# Corriger si nécessaire

# 3. Lancer le fine-tuning avec validation (1-2h)
python scripts/finetune_model.py \
    --train data/finetuning/dataset_train.jsonl \
    --validation data/finetuning/dataset_validation.jsonl \
    --suffix "dyag-prod-v1" \
    --epochs 3 \
    --wait

# 4. Évaluer sur le dataset de test
python scripts/evaluate_finetuned.py \
    --model ft:gpt-4o-mini-2024-07-18:org::abc123 \
    --test data/finetuning/dataset_test.jsonl
```

### Workflow 3 : Itération et amélioration

**Objectif** : Améliorer un modèle existant

```bash
# 1. Collecter les échecs du modèle actuel
# - Questions mal répondues
# - Feedbacks utilisateurs

# 2. Créer des exemples supplémentaires ciblés
# Éditer manuellement data/finetuning/corrections.jsonl

# 3. Fusionner avec dataset existant
cat data/finetuning/dataset_train.jsonl \
    data/finetuning/corrections.jsonl \
    > data/finetuning/dataset_v2_train.jsonl

# 4. Re-fine-tuner
python scripts/finetune_model.py \
    --train data/finetuning/dataset_v2_train.jsonl \
    --suffix "dyag-v2" \
    --wait

# 5. Comparer v1 vs v2
python scripts/compare_models.py \
    --model1 ft:gpt-4o-mini:org::v1 \
    --model2 ft:gpt-4o-mini:org::v2 \
    --test data/finetuning/dataset_test.jsonl
```

---

## Commandes utiles

### Gestion des jobs de fine-tuning

```bash
# Lister tous les jobs
python scripts/finetune_model.py --list

# Vérifier le statut d'un job
python scripts/finetune_model.py --status ft-job-abc123

# Attendre la fin d'un job en cours
python scripts/finetune_model.py --status ft-job-abc123 --wait
```

### Gestion des modèles

```bash
# Lister tous les modèles fine-tunés
python scripts/finetune_model.py --list-models

# Tester un modèle spécifique
python scripts/chat_hybrid.py --finetuned-model ft:gpt-4o-mini-2024-07-18:org::abc123
```

### Préparation de données avancée

```bash
# Générer plus d'exemples d'entraînement (80%)
python scripts/prepare_finetuning_data.py \
    --count 1000 \
    --train-ratio 0.85 \
    --val-ratio 0.10

# Utiliser un fichier de chunks différent
python scripts/prepare_finetuning_data.py \
    --chunks mon_fichier_chunks.jsonl \
    --count 500
```

---

## Troubleshooting

### Erreur : "File not found: applications_rag_optimal.jsonl"

**Cause** : Pas de chunks générés

**Solution** :
```bash
python scripts/generate_optimal_rag.py
```

### Erreur : "OPENAI_API_KEY not found"

**Cause** : Clé API non configurée

**Solution** :
```bash
# Créer/éditer .env
echo "OPENAI_API_KEY=sk-proj-votre-cle" >> .env
```

### Erreur : "Fine-tuning job failed"

**Cause** : Dataset invalide (format JSONL incorrect)

**Solution** :
```bash
# Valider le format JSONL
python -m json.tool data/finetuning/dataset_train.jsonl > /dev/null

# Si erreur, régénérer le dataset
python scripts/prepare_finetuning_data.py --count 100
```

### Le modèle fine-tuné donne des réponses génériques

**Cause** : Pas assez d'exemples ou exemples de mauvaise qualité

**Solutions** :
1. Augmenter le nombre d'exemples (500-1000+)
2. Vérifier manuellement la qualité du dataset
3. Ajouter plus de diversité dans les questions
4. Augmenter le nombre d'epochs (--epochs 5)

### Coût trop élevé

**Cause** : Trop de tokens dans le dataset

**Solutions** :
1. Réduire la longueur des réponses générées
2. Utiliser moins de chunks par exemple
3. Commencer avec 100 exemples au lieu de 500
4. Utiliser Ollama (gratuit mais plus complexe)

---

## Format du dataset

### Structure attendue (JSONL)

Chaque ligne est un objet JSON avec ce format :

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Tu es un assistant spécialisé..."
    },
    {
      "role": "user",
      "content": "Qui héberge GIDAF ?"
    },
    {
      "role": "assistant",
      "content": "GIDAF est hébergé par SI-RAPP... [chunk_383]"
    }
  ]
}
```

### Bonnes pratiques

✅ **À FAIRE** :
- Varier les types de questions
- Inclure le vocabulaire métier dans les réponses
- Citer les sources ([chunk_xxx])
- Garder un ton professionnel cohérent
- Utiliser 100-1000 exemples

❌ **À ÉVITER** :
- Réponses trop courtes (<50 mots)
- Réponses trop longues (>500 mots)
- Informations non vérifiées
- Incohérences de style
- Moins de 50 exemples

---

## Estimation des coûts

### OpenAI gpt-4o-mini fine-tuning

| Exemples | Tokens | Coût Training | Coût Usage/1M | Total (100k Q&A) |
|----------|--------|---------------|---------------|------------------|
| 100      | ~50k   | $0.40         | $2.40/1M      | ~$240            |
| 500      | ~250k  | $2.00         | $2.40/1M      | ~$240            |
| 1000     | ~500k  | $4.00         | $2.40/1M      | ~$240            |

**Notes** :
- Training : one-time cost
- Usage : 1.5× le prix de gpt-4o-mini standard ($1.60/1M)
- ROI positif si >1000 requêtes

### Alternative : Ollama (gratuit)

**Avantages** :
- Coût : 0€
- Contrôle total
- Pas de limite de tokens

**Inconvénients** :
- Nécessite GPU (ou très lent sur CPU)
- Setup plus complexe
- Qualité variable selon modèle

---

## Comparaison RAG vs Hybride

### Exemple concret : "Qui héberge GIDAF ?"

#### RAG seul (gpt-4o-mini standard)

```
Selon les informations disponibles, GIDAF est hébergé par SI-RAPP.
[Source: chunk_383]
```

**Score** : 3/5
- ✅ Factuel
- ✅ Source citée
- ❌ Pas de contexte métier
- ❌ Réponse minimale

#### RAG + Fine-tuning

```
GIDAF (Gestion Intégrée des Applications et Flux) est hébergé par
SI-RAPP, la plateforme d'hébergement interne dédiée aux applications
critiques du système d'information.

Cette application bénéficie d'un environnement d'hébergement sécurisé
avec un SLA élevé et une supervision 24/7. SI-RAPP assure également
la gestion des sauvegardes et la haute disponibilité.

[Sources: chunk_383, chunk_385]
```

**Score** : 5/5
- ✅ Factuel et précis
- ✅ Sources citées
- ✅ Contexte métier enrichi
- ✅ Vocabulaire professionnel (SLA, supervision)
- ✅ Informations complémentaires pertinentes

---

## Checklist de mise en production

### Avant le fine-tuning
- [ ] Chunks RAG générés et indexés
- [ ] OPENAI_API_KEY configurée
- [ ] Budget alloué (~$5-20)
- [ ] Objectifs de qualité définis

### Pendant le fine-tuning
- [ ] Dataset de qualité vérifié (20-30 exemples manuellement)
- [ ] Train/validation/test split correct
- [ ] Job lancé avec validation dataset
- [ ] Statut surveillé

### Après le fine-tuning
- [ ] Model ID sauvegardé
- [ ] Tests de qualité effectués (10-20 questions)
- [ ] Comparaison RAG vs Hybride documentée
- [ ] Décision go/no-go production
- [ ] Model ID ajouté à la configuration

### En production
- [ ] Monitoring des réponses
- [ ] Collecte des feedbacks utilisateurs
- [ ] Dataset d'amélioration maintenu
- [ ] Re-fine-tuning périodique (tous les 3-6 mois)

---

## Prochaines étapes

### Court terme (cette semaine)
1. ✅ Lire l'architecture RAG/Fine-tuning
2. ⬜ Générer 100 exemples de test
3. ⬜ Lancer premier fine-tuning
4. ⬜ Évaluer la qualité

### Moyen terme (ce mois)
1. ⬜ Générer 500 exemples de qualité
2. ⬜ Fine-tuning de production
3. ⬜ Intégrer dans le chat principal
4. ⬜ Collecter feedbacks utilisateurs

### Long terme (3-6 mois)
1. ⬜ Enrichir le dataset (1000+ exemples)
2. ⬜ Re-fine-tuner avec données réelles
3. ⬜ Automatiser la collecte de feedbacks
4. ⬜ Pipeline CI/CD de fine-tuning

---

## Ressources

### Documentation OpenAI
- [Fine-tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Pricing](https://openai.com/api/pricing/)
- [Best Practices](https://platform.openai.com/docs/guides/fine-tuning/best-practices)

### Documentation DYAG
- [Architecture RAG/Fine-tuning](./ARCHITECTURE_RAG_FINETUNING.md)
- [Guide Providers](../GUIDE_PROVIDERS.md)
- [README RAG](../RAG_README.md)

### Scripts du projet
- `scripts/prepare_finetuning_data.py` : Préparer les données
- `scripts/finetune_model.py` : Lancer le fine-tuning
- `scripts/chat_hybrid.py` : Chat avec modèle fine-tuné

---

## FAQ

### Q: Le fine-tuning est-il obligatoire ?
**R:** Non. RAG seul fonctionne bien. Fine-tuning améliore la qualité mais n'est pas nécessaire.

### Q: Combien coûte un fine-tuning ?
**R:** ~$1-2 pour 100 exemples, ~$5-20 pour 500-1000 exemples sur OpenAI.

### Q: Combien de temps prend le fine-tuning ?
**R:** 10min-2h selon la taille du dataset. Préparation : 30min-3h.

### Q: Faut-il re-fine-tuner régulièrement ?
**R:** Oui, tous les 3-6 mois ou quand de nouvelles applications sont ajoutées.

### Q: Peut-on fine-tuner Claude ?
**R:** Non, Anthropic n'offre pas de fine-tuning public. Utiliser OpenAI.

### Q: Le fine-tuning fonctionne-t-il avec Ollama ?
**R:** Oui, mais c'est plus complexe. OpenAI est recommandé pour commencer.

### Q: Combien d'exemples faut-il ?
**R:** Minimum 50, recommandé 100-200 pour tester, 500-1000+ pour production.

### Q: Le modèle fine-tuné peut-il "oublier" ?
**R:** Oui (catastrophic forgetting). Assurez-vous d'avoir des exemples variés.

### Q: Comment mesurer l'amélioration ?
**R:** Testez les deux systèmes (RAG vs Hybride) sur les mêmes questions et comparez.



## Exemple :

