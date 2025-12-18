# Architecture : Cohabitation RAG et Fine-Tuning

## Executive Summary

**OUI**, RAG et fine-tuning peuvent et **doivent** cohabiter sur ce projet. Ils sont **complémentaires** :

- **Fine-tuning** : Adapte le modèle LLM au domaine/style de vos applications
- **RAG** : Injecte des informations factuelles spécifiques et à jour dans le contexte

**Résultat optimal** = Fine-tuning du modèle + RAG pour les faits spécifiques

## 1. Comparaison RAG vs Fine-Tuning

### RAG (Retrieval Augmented Generation)
✅ **Avantages**
- Mise à jour facile (ajouter des chunks)
- Pas besoin de réentraîner
- Traçabilité des sources
- Faible coût
- Informations toujours à jour

❌ **Limites**
- Dépend de la qualité de la recherche vectorielle
- Contexte limité par la taille du prompt
- Ne "comprend" pas vraiment le domaine

### Fine-Tuning
✅ **Avantages**
- Modèle adapté au domaine
- Meilleure compréhension du vocabulaire métier
- Style de réponse cohérent
- Pas besoin de contexte externe

❌ **Limites**
- Coûteux (temps + argent)
- Nécessite beaucoup de données d'entraînement
- Difficile à mettre à jour (réentraînement)
- Peut "oublier" des informations générales

### Approche Hybride (RECOMMANDÉE)
🎯 **Fine-tuning** pour :
- Comprendre le vocabulaire métier (ex: GIDAF, MYGUSI, etc.)
- Style de réponse adapté (ton professionnel SI)
- Structure de réponse cohérente
- Compréhension des relations entre applications

🎯 **RAG** pour :
- Informations factuelles spécifiques (hébergeur, technologies)
- Données qui changent fréquemment
- Références précises (IDs d'applications)
- Nouvelles applications ajoutées

## 2. Architecture Proposée

### 2.1 Structure du projet réorganisée

```
dyag/
├── src/
│   └── dyag/
│       ├── commands/          # Commandes CLI existantes
│       ├── rag/              # Module RAG (NOUVEAU)
│       │   ├── __init__.py
│       │   ├── query.py      # RAGQuerySystem (ancien rag_query.py)
│       │   ├── indexer.py    # Indexation des chunks
│       │   └── embeddings.py # Gestion des embeddings
│       ├── finetuning/       # Module Fine-tuning (NOUVEAU)
│       │   ├── __init__.py
│       │   ├── dataset.py    # Préparation datasets
│       │   ├── trainer.py    # Entraînement
│       │   └── evaluator.py  # Évaluation du modèle
│       ├── llm/              # Module LLM (RÉORGANISÉ)
│       │   ├── __init__.py
│       │   ├── providers.py  # LLM providers (ancien llm_providers.py)
│       │   └── models.py     # Gestion des modèles fine-tunés
│       └── hybrid/           # Module Hybride (NOUVEAU)
│           ├── __init__.py
│           └── query.py      # Système hybride RAG + Fine-tuning
├── formation/                # Scripts de formation
│   ├── prompts.py
│   ├── multi_format_reader.py
│   └── finetuning_examples/  # Exemples de fine-tuning (NOUVEAU)
├── scripts/                  # Scripts utilitaires
│   ├── chat.py
│   ├── prepare_finetuning_data.py  # Préparer données (NOUVEAU)
│   └── finetune_model.py          # Lancer fine-tuning (NOUVEAU)
├── data/                     # Données (NOUVEAU)
│   ├── raw/                 # Données brutes
│   ├── processed/           # Données traitées
│   └── finetuning/         # Datasets de fine-tuning
│       ├── train.jsonl
│       ├── validation.jsonl
│       └── test.jsonl
├── models/                   # Modèles fine-tunés (NOUVEAU)
│   └── dyag-gpt-4o-mini-v1/
└── chroma_db/               # Base vectorielle (existant)
```

### 2.2 Workflow Hybride

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         v
┌─────────────────────────┐
│ Hybrid Query System     │
│ (RAG + Fine-tuned LLM)  │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    v         v
┌───────┐  ┌──────────────┐
│  RAG  │  │ Fine-tuned   │
│       │  │ LLM Provider │
│ 1. Search chunks       │
│ 2. Retrieve context    │
│                        │
│ 3. Send to fine-tuned  │──>│
│    model with context  │   │
└────────────────────────┘   │
                             │
                             v
                      ┌──────────────┐
                      │   Response   │
                      │  (Enhanced)  │
                      └──────────────┘
```

### 2.3 Implémentation du système hybride

```python
# src/dyag/hybrid/query.py
from typing import Dict, Optional
from ..rag.query import RAGQuerySystem
from ..llm.providers import LLMProviderFactory

class HybridQuerySystem:
    """
    Système hybride combinant RAG et modèle fine-tuné.

    Le modèle fine-tuné comprend le domaine métier.
    Le RAG fournit les informations factuelles spécifiques.
    """

    def __init__(
        self,
        use_finetuned: bool = True,
        finetuned_model_id: Optional[str] = None,
        **rag_kwargs
    ):
        # Initialiser le RAG
        self.rag = RAGQuerySystem(**rag_kwargs)

        # Si modèle fine-tuné disponible, l'utiliser
        if use_finetuned and finetuned_model_id:
            # Remplacer le provider LLM par le modèle fine-tuné
            self.rag.llm_provider = LLMProviderFactory.create_provider(
                provider='openai',  # OpenAI supporte les modèles fine-tunés
                model=finetuned_model_id  # ex: "ft:gpt-4o-mini-2024-07-18:org::id"
            )

    def ask(self, question: str, **kwargs) -> Dict:
        """
        Pose une question avec le système hybride.

        Le modèle fine-tuné reçoit le contexte RAG et génère
        une réponse adaptée au domaine métier.
        """
        # Déléguer au RAG qui utilisera automatiquement
        # le modèle fine-tuné si configuré
        return self.rag.ask(question, **kwargs)
```

## 3. Plan de mise en œuvre

### Phase 1 : Préparation des données de fine-tuning (1-2 jours)

#### 3.1 Créer un dataset de qualité

Le fine-tuning nécessite des exemples de conversations au format :
```jsonl
{"messages": [
  {"role": "system", "content": "Tu es un assistant spécialisé..."},
  {"role": "user", "content": "Qui héberge GIDAF ?"},
  {"role": "assistant", "content": "GIDAF est hébergé par..."}
]}
```

**Sources de données** :
1. Générer des Q&A synthétiques depuis vos chunks existants
2. Logs de questions réelles (si disponible)
3. Exemples manuels de bonnes réponses

#### 3.2 Script de préparation

```python
# scripts/prepare_finetuning_data.py
"""
Génère un dataset de fine-tuning depuis les chunks RAG.

Stratégie:
1. Pour chaque application, générer 5-10 questions types
2. Utiliser un LLM (GPT-4) pour générer les réponses
3. Valider la qualité
4. Splitter en train/validation/test (80/10/10)
"""
```

**Quantité recommandée** : 500-2000 exemples
- Minimum : 100 exemples (pour commencer)
- Optimal : 1000+ exemples (meilleure qualité)

### Phase 2 : Fine-tuning du modèle (2-4 heures selon provider)

#### 3.1 Providers supportant le fine-tuning

| Provider | Modèles | Coût | Temps |
|----------|---------|------|-------|
| **OpenAI** | gpt-4o-mini (recommandé)<br>gpt-4o<br>gpt-3.5-turbo | ~$0.80/1M tokens training<br>~$2.40/1M tokens usage | 10min-2h |
| **Anthropic** | ❌ Pas de fine-tuning public | - | - |
| **Ollama** | ✅ Fine-tuning local possible<br>(LLaMA, Mistral) | Gratuit | 2-12h |

**Recommandation** : Commencer avec **gpt-4o-mini** d'OpenAI
- Excellent rapport qualité/prix
- Rapide à entraîner
- API simple

#### 3.2 Script de fine-tuning

```python
# scripts/finetune_model.py
"""
Lance le fine-tuning sur OpenAI ou Ollama.

Usage:
    python scripts/finetune_model.py --provider openai --model gpt-4o-mini
    python scripts/finetune_model.py --provider ollama --model llama3.2
"""
```

### Phase 3 : Intégration hybride (1 jour)

1. **Créer le module hybride** : `src/dyag/hybrid/query.py`
2. **Adapter le chat** : Modifier `scripts/chat.py` pour utiliser le système hybride
3. **Tester** : Comparer RAG seul vs Hybride

#### 3.3 Chat hybride

```python
# scripts/chat.py (modifié)
from dyag.hybrid.query import HybridQuerySystem

# Mode hybride (RAG + fine-tuned)
rag = HybridQuerySystem(
    use_finetuned=True,
    finetuned_model_id="ft:gpt-4o-mini-2024-07-18:org::id"
)

# OU mode RAG classique
rag = HybridQuerySystem(use_finetuned=False)
```

### Phase 4 : Évaluation et itération (continu)

#### Métriques à suivre :
- **Précision** : Les réponses sont-elles factuellement correctes ?
- **Pertinence** : Les sources citées sont-elles pertinentes ?
- **Style** : Le ton est-il adapté (professionnel SI) ?
- **Complétude** : Les réponses sont-elles complètes ?

## 4. Estimation des coûts

### Fine-tuning OpenAI gpt-4o-mini

**Exemple avec 1000 exemples** :
- Dataset : ~500K tokens
- Training : $0.40 (500K tokens × $0.80/1M)
- **Usage** : $2.40/1M tokens (1.5× le prix de gpt-4o-mini standard)

**ROI** :
- Meilleure qualité de réponse
- Moins de contexte RAG nécessaire → moins de tokens
- Style cohérent → moins de prompt engineering

### Alternative gratuite : Ollama fine-tuning

- **Coût** : 0€ (local)
- **Temps** : 2-12h selon GPU
- **Qualité** : Variable selon modèle de base

## 5. Réorganisation nécessaire ?

### Option 1 : Réorganisation minimale (RECOMMANDÉE pour démarrer)

**Changements** :
1. Garder l'architecture actuelle
2. Ajouter juste :
   - `scripts/prepare_finetuning_data.py`
   - `scripts/finetune_model.py`
   - `data/finetuning/` directory
3. Modifier `RAGQuerySystem` pour accepter un `finetuned_model_id`

**Avantages** :
- Changements minimaux
- Pas de refactoring
- Démarrage rapide

### Option 2 : Réorganisation complète

**Changements** :
1. Restructurer selon l'architecture proposée (section 2.1)
2. Séparer RAG / Fine-tuning / Hybrid en modules
3. Meilleure séparation des responsabilités

**Avantages** :
- Architecture plus propre
- Scalabilité
- Maintenance facilitée

**Recommandation** : Commencer avec **Option 1**, puis migrer vers **Option 2** si le fine-tuning prouve sa valeur.

## 6. Exemple concret : Cas d'usage

### Scénario : "Qui héberge GIDAF ?"

#### Avec RAG seul :
```
User: Qui héberge GIDAF ?

[RAG] → Recherche chunks → Trouve "GIDAF est hébergé par SI-RAPP"
[GPT-4o-mini standard] + contexte → Répond

Réponse: "Selon les informations, GIDAF est hébergé par SI-RAPP."
```

**Problème** : Réponse générique, pas de contexte métier

#### Avec RAG + Fine-tuning :
```
User: Qui héberge GIDAF ?

[RAG] → Recherche chunks → Trouve "GIDAF est hébergé par SI-RAPP"
[GPT-4o-mini FINE-TUNÉ] + contexte → Répond avec compréhension métier

Réponse: "GIDAF (Gestion Intégrée des Applications et Flux) est hébergé
par SI-RAPP, la plateforme d'hébergement interne dédiée aux applications
critiques du SI. Cette application bénéficie d'un SLA élevé et d'une
supervision 24/7. [Source: chunk_383]"
```

**Gain** :
- Compréhension du vocabulaire (SI-RAPP, SLA)
- Contexte métier enrichi
- Style professionnel cohérent
- Informations complémentaires pertinentes

## 7. Prochaines étapes recommandées

### Étape 1 : Valider l'approche (1 jour)
1. ✅ Lire cette architecture
2. ✅ Décider : Option 1 (minimal) ou Option 2 (complet)
3. ✅ Valider le budget (fine-tuning OpenAI ~$5-20)

### Étape 2 : Préparation (2 jours)
1. Créer `scripts/prepare_finetuning_data.py`
2. Générer 100-200 exemples de Q&A
3. Valider la qualité manuellement

### Étape 3 : Premier fine-tuning (1 jour)
1. Créer `scripts/finetune_model.py`
2. Lancer le fine-tuning sur gpt-4o-mini
3. Récupérer le model ID

### Étape 4 : Intégration (1 jour)
1. Modifier `RAGQuerySystem` pour accepter le model ID
2. Tester avec `scripts/chat.py`
3. Comparer qualité RAG vs Hybride

### Étape 5 : Itération (continu)
1. Collecter les questions réelles
2. Enrichir le dataset
3. Re-fine-tuner périodiquement

## 8. FAQ

### Q: Faut-il ABSOLUMENT fine-tuner ?
**R:** Non. RAG seul fonctionne bien. Fine-tuning améliore la qualité mais n'est pas obligatoire.

### Q: Quel est le meilleur provider pour fine-tuning ?
**R:**
- **OpenAI gpt-4o-mini** : Meilleur rapport qualité/prix/simplicité
- **Ollama** : Gratuit mais plus complexe

### Q: Combien d'exemples faut-il ?
**R:** Minimum 100, optimal 500-1000+

### Q: Peut-on fine-tuner Claude/Anthropic ?
**R:** Non, pas de fine-tuning public. Utiliser OpenAI ou Ollama.

### Q: Le fine-tuning remplace-t-il le RAG ?
**R:** **NON**. Ils sont complémentaires :
- Fine-tuning = comprendre le domaine
- RAG = faits spécifiques et à jour

## Conclusion

✅ **OUI**, faites cohabiter RAG et fine-tuning
✅ **NON**, pas besoin de réorganisation majeure pour démarrer
✅ Commencer avec l'**Option 1** (minimal) et itérer
✅ Provider recommandé : **OpenAI gpt-4o-mini**
✅ Budget : ~$5-20 pour le premier fine-tuning

**Le meilleur système = RAG (faits) + Fine-tuning (compréhension métier)**
