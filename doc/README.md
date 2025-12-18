# 📚 Documentation DYAG

> Documentation complète du projet DYAG - Outil de manipulation de fichiers et système RAG pour applications SI

## 🚀 Démarrage rapide

**Nouveau sur le projet ?** Commencez ici :

1. 📖 **[Guide de démarrage rapide](./Getting-Started/Quick-Start-Guide.md)** ← Commencez ici !
2. 🔍 **[Aperçu du système RAG](./RAG-System/RAG-System-Overview.md)** - Comprendre le système
3. 💬 **[Utiliser le chat RAG](./RAG-System/RAG-Quick-Start.md)** - Poser des questions

**Installer et configurer** :
- [Installation et configuration](./Getting-Started/Installation-Setup.md)
- [Configuration des providers LLM](../GUIDE_PROVIDERS.md)

---

## 📑 Table des matières

### 1️⃣ Démarrage (`Getting-Started/`)

| Document | Description |
|----------|-------------|
| **[Guide de démarrage rapide](./Getting-Started/Quick-Start-Guide.md)** | Commencer avec DYAG en 5 minutes |
| **[Installation & Setup](./Getting-Started/Installation-Setup.md)** | Installation complète et configuration |

### 2️⃣ Système RAG (`RAG-System/`)

#### Architecture et concepts
| Document | Description |
|----------|-------------|
| **[Aperçu du système RAG](./RAG-System/RAG-System-Overview.md)** | Vue d'ensemble de l'architecture RAG |
| **[Architecture détaillée](./RAG-System/RAG-Architecture.md)** | Diagrammes et composants |
| **[Guide des modules](./RAG-System/RAG-Modules-Guide.md)** | Documentation des modules Python |

#### Guides pratiques
| Document | Description |
|----------|-------------|
| **[Quick Start RAG](./RAG-System/RAG-Quick-Start.md)** | Démarrer avec le RAG en 10 minutes |
| **[Checklist RAG](./RAG-System/RAG-Checklist.md)** | Vérifier que tout fonctionne |
| **[Créer un RAG](./RAG-System/Create-RAG-Guide.md)** | Guide complet de création |

#### Chunking (découpage de documents)
| Document | Description |
|----------|-------------|
| **[Stratégie de chunking](./RAG-System/Chunking/Chunking-Strategy.md)** | Pourquoi et comment découper |
| **[Comparaison des méthodes](./RAG-System/Chunking/Chunking-Comparison.md)** | Choisir la bonne méthode |
| **[Algorithme de chunking](./RAG-System/Chunking/Chunking-Algorithm.md)** | Détails techniques |
| **[Gestion des chunks](./RAG-System/Chunking/Chunking-Management.md)** | Gérer et optimiser |

### 3️⃣ Fine-Tuning (`Fine-Tuning/`)

| Document | Description |
|----------|-------------|
| **[Architecture RAG + Fine-Tuning](./Fine-Tuning/RAG-FineTuning-Architecture.md)** | Combiner RAG et fine-tuning |
| **[Guide de fine-tuning](./Fine-Tuning/Fine-Tuning-Guide.md)** | Tutoriel complet pas à pas |
| **[Dataset manuel](../data/finetuning/README.md)** | Utiliser le dataset de démonstration |

### 4️⃣ Outils et utilitaires (`Tools/`)

| Document | Description |
|----------|-------------|
| **[MD2HTML - Comparaison](./Tools/MD2HTML-Comparison.md)** | Convertir Markdown vers HTML |
| **[MCP Server](./Tools/MCP-Guide.md)** | Model Context Protocol |
| **[Claude Code](./Tools/Claude-Guide.md)** | Utiliser Claude Code |

### 5️⃣ Développement (`Development/`)

| Document | Description |
|----------|-------------|
| **[Guide de versioning](./Development/Versioning-Guide.md)** | Versioning et distribution |
| **[Commitizen](./Development/Commitizen-Guide.md)** | Commits conventionnels |
| **[Environnement Conda](./Development/Conda-Environment.md)** | Configuration de l'environnement |

### 6️⃣ Analyse et recherche (`Analysis/`)

Documentation technique et analyses approfondies.

---

## 🎯 Guides par cas d'usage

### Je veux... utiliser le RAG

1. **[Quick Start RAG](./RAG-System/RAG-Quick-Start.md)** - Démarrer rapidement
2. **[Poser des questions](./RAG-System/RAG-Quick-Start.md#mode-chat)** - Utiliser le chat
3. **[Comprendre les résultats](./RAG-System/RAG-System-Overview.md#fonctionnement)** - Interpréter les réponses

### Je veux... créer un nouveau RAG

1. **[Créer un RAG](./RAG-System/Create-RAG-Guide.md)** - Guide complet
2. **[Stratégie de chunking](./RAG-System/Chunking/Chunking-Strategy.md)** - Découper mes documents
3. **[Checklist RAG](./RAG-System/RAG-Checklist.md)** - Vérifier la qualité

### Je veux... améliorer mon RAG avec fine-tuning

1. **[Architecture hybride](./Fine-Tuning/RAG-FineTuning-Architecture.md)** - Comprendre RAG + Fine-tuning
2. **[Guide de fine-tuning](./Fine-Tuning/Fine-Tuning-Guide.md)** - Étapes pratiques
3. **[Dataset manuel](../data/finetuning/README.md)** - Exemples à enrichir

### Je veux... développer sur DYAG

1. **[Installation développeur](./Getting-Started/Installation-Setup.md#installation-développeur)** - Setup complet
2. **[Guide de versioning](./Development/Versioning-Guide.md)** - Conventions
3. **[Commitizen](./Development/Commitizen-Guide.md)** - Commits propres

---

## 📊 Architecture du projet

```
dyag/
├── src/dyag/           # Code source principal
│   ├── commands/       # Commandes CLI (md2html, img2pdf, etc.)
│   ├── rag/           # Système RAG (nouveau)
│   ├── finetuning/    # Fine-tuning (nouveau)
│   └── llm/           # Providers LLM
├── doc/               # 📚 Documentation (vous êtes ici)
│   ├── Getting-Started/
│   ├── RAG-System/
│   ├── Fine-Tuning/
│   ├── Tools/
│   └── Development/
├── scripts/           # Scripts utilitaires
│   ├── chat.py        # Chat RAG standard
│   ├── chat_hybrid.py # Chat RAG + fine-tuning
│   ├── prepare_finetuning_data.py
│   └── finetune_model.py
├── data/              # Données
│   └── finetuning/    # Datasets de fine-tuning
├── formation/         # Scripts de formation
└── chroma_db/        # Base vectorielle ChromaDB
```

---

## 🔗 Liens externes utiles

### Documentation officielle
- [OpenAI API](https://platform.openai.com/docs) - API et fine-tuning
- [Anthropic Claude](https://docs.anthropic.com) - Claude API
- [ChromaDB](https://docs.trychroma.com) - Base vectorielle
- [Sentence Transformers](https://www.sbert.net) - Embeddings

### Ressources RAG
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Chunking Strategies](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex)

### Fine-Tuning
- [OpenAI Fine-Tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Fine-Tuning Best Practices](https://platform.openai.com/docs/guides/fine-tuning/best-practices)

---

## 🆘 Aide et support

### Questions fréquentes

**Q: Comment démarrer rapidement ?**
→ Suivez le **[Guide de démarrage rapide](./Getting-Started/Quick-Start-Guide.md)**

**Q: Le RAG ne trouve pas de réponses**
→ Vérifiez la **[Checklist RAG](./RAG-System/RAG-Checklist.md)**

**Q: Je veux améliorer la qualité des réponses**
→ Consultez **[Architecture RAG + Fine-Tuning](./Fine-Tuning/RAG-FineTuning-Architecture.md)**

**Q: Comment configurer les providers LLM ?**
→ Voir **[GUIDE_PROVIDERS.md](../GUIDE_PROVIDERS.md)**

### Problèmes courants

| Problème | Solution |
|----------|----------|
| Erreur "Collection not found" | **[RAG Quick Start](./RAG-System/RAG-Quick-Start.md#indexation)** - Indexer les chunks |
| Erreur "API key not found" | **[Installation](./Getting-Started/Installation-Setup.md#configuration)** - Configurer .env |
| Réponses de mauvaise qualité | **[Chunking Strategy](./RAG-System/Chunking/Chunking-Strategy.md)** - Optimiser le chunking |
| Timeout avec Ollama | **[RAG Quick Start](./RAG-System/RAG-Quick-Start.md#providers)** - Réduire chunks ou changer provider |

---

## 📝 Contribuer à la documentation

### Ajouter un nouveau document

1. Choisir la bonne catégorie (`Getting-Started/`, `RAG-System/`, etc.)
2. Créer le fichier avec un nom descriptif (`Mon-Guide.md`)
3. Ajouter une entrée dans ce README.md
4. Ajouter des liens depuis/vers les documents connexes

### Conventions de nommage

- **Noms de fichiers** : `Pascal-Case-With-Dashes.md`
- **Titres** : Clairs et descriptifs
- **Liens** : Toujours relatifs (`./RAG-System/...` ou `../data/...`)

### Structure recommandée d'un document

```markdown
# Titre Principal

> Brève description (1-2 phrases)

## Table des matières
- [Section 1](#section-1)
- [Section 2](#section-2)

## Introduction
...

## Section 1
...

## Voir aussi
- [Document connexe 1](./chemin.md)
- [Document connexe 2](./chemin.md)
```

---

## 📅 Historique des versions

| Version | Date | Changements majeurs |
|---------|------|---------------------|
| v0.4.0 | 2024-12-07 | Ajout système RAG, providers LLM |
| v0.5.0 | 2024-12-08 | Ajout fine-tuning, réorganisation doc |

---

## 📄 Licence

Voir [LICENSE](../LICENSE) à la racine du projet.

---

<div align="center">

**[⬆ Retour en haut](#-documentation-dyag)**

Fait avec ❤️ pour faciliter la gestion du SI

</div>
