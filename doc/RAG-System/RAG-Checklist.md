# Checklist de Vérification du Système RAG

Cette checklist vous permet de vérifier que tous les composants du système RAG sont en place et fonctionnels.

## ✅ Phase 1: Fichiers et Structure

### Modules sources (obligatoires)

- [ ] `src/dyag/commands/create_rag.py` existe
- [ ] `src/dyag/rag_query.py` existe

**Vérification:**
```bash
ls -la src/dyag/commands/create_rag.py
ls -la src/dyag/rag_query.py
```

### Scripts exécutables (obligatoires)

- [ ] `scripts/index_chunks.py` existe
- [ ] `scripts/example_rag_complete.py` existe

**Vérification:**
```bash
ls -la scripts/index_chunks.py
ls -la scripts/example_rag_complete.py
```

### Scripts de test (optionnels)

- [ ] `test_create_rag.py` existe
- [ ] `example_create_rag.py` existe
- [ ] `generate_optimal_rag.py` existe

### Documentation (recommandée)

- [ ] `doc/rag-quick-start.md` existe ⭐
- [ ] `doc/rag-modules-guide.md` existe
- [ ] `doc/rag-chunks-algo.md` existe
- [ ] `doc/chunks-why.md` existe
- [ ] `doc/chunks-for-management.md` existe
- [ ] `doc/rag-system-summary.md` existe
- [ ] `doc/rag-architecture.puml` existe
- [ ] `doc/rag-checklist.md` existe (ce fichier)

**Vérification rapide:**
```bash
ls -la doc/rag-*.md
```

### Configuration (obligatoire)

- [ ] `requirements-rag.txt` existe
- [ ] `.env.example` existe
- [ ] `RAG_README.md` existe et est à jour

---

## ✅ Phase 2: Installation et Configuration

### Installation des dépendances

- [ ] Python 3.8+ installé
- [ ] Pip à jour

**Vérification:**
```bash
python --version  # Doit afficher 3.8 ou supérieur
pip --version
```

- [ ] Dépendances RAG installées

**Installation:**
```bash
pip install -r requirements-rag.txt
```

**Vérification:**
```bash
python -c "import chromadb; print(chromadb.__version__)"
python -c "import sentence_transformers; print(sentence_transformers.__version__)"
python -c "import openai; print(openai.__version__)"
```

**Résultat attendu:**
```
0.4.22
2.3.1
1.12.0
```

### Configuration de l'API OpenAI

- [ ] Compte OpenAI créé
- [ ] Clé API obtenue sur https://platform.openai.com/api-keys
- [ ] Fichier `.env` créé à la racine

**Création du .env:**
```bash
cp .env.example .env
# Éditez .env et ajoutez votre clé
```

**Contenu minimal de .env:**
```env
OPENAI_API_KEY=sk-proj-votre-cle-ici
```

**Vérification:**
```bash
# Vérifier que le fichier existe
ls -la .env

# Vérifier que la clé est définie (sans afficher la valeur)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if os.getenv('OPENAI_API_KEY') else 'MANQUANT')"
```

**Résultat attendu:** `OK`

---

## ✅ Phase 3: Données et Chunks

### Fichier source disponible

- [ ] Fichier source existe (JSON ou Markdown)

**Exemples de chemins:**
- `examples/test-mygusi/applicationsIA_mini_opt.md`
- `examples/test-mygusi/applicationsIA_mini_normalized.json`

**Vérification:**
```bash
ls -la examples/test-mygusi/applicationsIA_mini_opt.md
```

### Chunks générés

- [ ] Chunks JSONL générés

**Génération:**
```bash
python -m dyag.commands.create_rag \
    examples/test-mygusi/applicationsIA_mini_opt.md \
    applications_rag_optimal.jsonl
```

**Vérification:**
```bash
ls -lh applications_rag_optimal.jsonl
wc -l applications_rag_optimal.jsonl  # Doit afficher ~1628 lignes
```

**Résultat attendu:**
```
-rw-r--r-- 1 user user 1.8M applications_rag_optimal.jsonl
1628 applications_rag_optimal.jsonl
```

### Test du chunking

- [ ] Module de chunking fonctionne

**Test:**
```bash
python -c "
from dyag.commands.create_rag import RAGCreator
creator = RAGCreator()
print('Module de chunking: OK')
"
```

**Résultat attendu:** `Module de chunking: OK`

---

## ✅ Phase 4: Indexation

### Base ChromaDB créée

- [ ] ChromaDB installé correctement
- [ ] Chunks indexés dans ChromaDB

**Indexation:**
```bash
python scripts/index_chunks.py applications_rag_optimal.jsonl
```

**Résultat attendu:**
```
Connexion a ChromaDB: .\chroma_db
Chargement du modele d'embedding: all-MiniLM-L6-v2
Modele charge avec dimension: 384

Chargement des chunks depuis: applications_rag_optimal.jsonl
Chunks charges: 1628

Indexation de 1628 chunks...
...
Indexation terminee:
  - Indexes: 1628
  - Erreurs: 0
  - Taux de reussite: 100.0%
```

### Vérification de la base

- [ ] Répertoire `chroma_db/` existe
- [ ] Collection `applications` existe

**Vérification:**
```bash
ls -la chroma_db/

python -c "
import chromadb
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection('applications')
print(f'Chunks indexes: {collection.count()}')
"
```

**Résultat attendu:**
```
Chunks indexes: 1628
```

---

## ✅ Phase 5: Questions & Réponses

### Module de Q&A fonctionnel

- [ ] Module rag_query importable

**Test:**
```bash
python -c "
from dyag.rag_query import RAGQuerySystem
print('Module de Q&A: OK')
"
```

**Résultat attendu:** `Module de Q&A: OK`

### Initialisation du système

- [ ] RAGQuerySystem s'initialise sans erreur

**Test:**
```bash
python -c "
from dyag.rag_query import RAGQuerySystem
rag = RAGQuerySystem()
stats = rag.get_stats()
print(f'Chunks indexes: {stats[\"total_chunks\"]}')
print(f'Modele LLM: {stats[\"llm_model\"]}')
print('Initialisation: OK')
"
```

**Résultat attendu:**
```
Chunks indexes: 1628
Modele LLM: gpt-4o-mini
Initialisation: OK
```

### Test d'une question simple

- [ ] Question posée avec succès
- [ ] Réponse générée
- [ ] Sources citées

**Test:**
```bash
python -c "
from dyag.rag_query import RAGQuerySystem
rag = RAGQuerySystem()
result = rag.ask('Qui héberge GIDAF ?')
print('Question:', result['question'])
print('Réponse:', result['answer'][:100] + '...')
print('Sources:', len(result['sources']), 'chunks')
print('Tokens:', result['tokens_used'])
print('Test Q&A: OK')
"
```

**Résultat attendu:**
```
Question: Qui héberge GIDAF ?
Réponse: GIDAF est hébergé par le BRGM...
Sources: 5 chunks
Tokens: 342
Test Q&A: OK
```

### Mode interactif

- [ ] Mode interactif lance sans erreur

**Test:**
```bash
python -m dyag.rag_query
# Tapez Ctrl+C pour quitter après vérification
```

**Résultat attendu:**
```
Initialisation du systeme RAG...

Statistiques:
  - Chunks indexes: 1628
  - Modele LLM: gpt-4o-mini

Mode interactif - Posez vos questions (Ctrl+C pour quitter)
❓ Question: _
```

---

## ✅ Phase 6: Tests Avancés

### Test avec filtrage

- [ ] Filtrage par source_id fonctionne

**Test:**
```bash
python -c "
from dyag.rag_query import RAGQuerySystem
rag = RAGQuerySystem()
result = rag.ask(
    'Quelle est la description ?',
    filter_metadata={'source_id': '383'}
)
print('Filtrage: OK')
print('Sources:', result['sources'])
"
```

### Test avec paramètres personnalisés

- [ ] Paramètre n_chunks fonctionne
- [ ] Paramètre temperature fonctionne

**Test:**
```bash
python -c "
from dyag.rag_query import RAGQuerySystem
rag = RAGQuerySystem()

# Test n_chunks
result1 = rag.ask('Question test', n_chunks=10)
print(f'n_chunks=10: {len(result1[\"sources\"])} sources')

# Test temperature
result2 = rag.ask('Question test', temperature=0.0)
print(f'temperature=0.0: OK')

print('Parametres personnalises: OK')
"
```

### Test du script complet

- [ ] Script example_rag_complete.py s'exécute

**Test:**
```bash
python scripts/example_rag_complete.py
# Suivez les étapes du script
# Ctrl+C pour interrompre
```

---

## ✅ Phase 7: Documentation

### Lecture de la documentation

- [ ] `rag-quick-start.md` lu ⭐
- [ ] `rag-modules-guide.md` parcouru
- [ ] `rag-system-summary.md` consulté

### Compréhension du système

- [ ] Comprendre les 3 phases (chunking, indexation, Q&A)
- [ ] Savoir créer des chunks
- [ ] Savoir indexer dans ChromaDB
- [ ] Savoir poser des questions

---

## ✅ Phase 8: Optimisations (Optionnel)

### Performance

- [ ] Temps de réponse < 5 secondes
- [ ] Indexation terminée en < 5 minutes

**Si trop lent:**
- Utiliser `batch_size` plus grand pour indexation
- Réduire `n_chunks` pour Q&A
- Utiliser GPU pour embeddings

### Coûts

- [ ] Coût par question estimé
- [ ] Budget mensuel défini

**Estimation:**
```bash
python -c "
# Exemple: 500 questions/mois
questions_par_mois = 500
cout_par_question = 0.01  # USD
cout_mensuel = questions_par_mois * cout_par_question
print(f'Estimation mensuelle: ${cout_mensuel:.2f}')
"
```

### Monitoring

- [ ] Tokens utilisés trackés
- [ ] Logs activés si nécessaire

**Activer les logs:**
```python
from loguru import logger
logger.add("rag.log", rotation="1 day")
```

---

## 🎯 Checklist Rapide (Démarrage 5 min)

Pour un test rapide du système complet:

```bash
# 1. Installer (1 min)
pip install -r requirements-rag.txt

# 2. Configurer (30 sec)
cp .env.example .env
# Éditez .env avec votre clé API

# 3. Indexer (2 min)
python scripts/index_chunks.py applications_rag_optimal.jsonl

# 4. Tester (1 min)
python -m dyag.rag_query
# Posez une question: "Qui héberge GIDAF ?"
```

---

## 📊 Résumé de Vérification

Cochez toutes les cases pour confirmer que votre système est opérationnel:

**Essentiel (minimum viable):**
- [ ] Modules sources installés (create_rag.py, rag_query.py)
- [ ] Dépendances installées (requirements-rag.txt)
- [ ] Clé API OpenAI configurée (.env)
- [ ] Chunks générés (applications_rag_optimal.jsonl)
- [ ] ChromaDB indexée (1628 chunks)
- [ ] Test Q&A réussi

**Recommandé (meilleure expérience):**
- [ ] Documentation lue (rag-quick-start.md)
- [ ] Scripts de test exécutés
- [ ] Paramètres personnalisés testés
- [ ] Diagrammes d'architecture consultés

**Avancé (optimisations):**
- [ ] Logs configurés
- [ ] Coûts estimés
- [ ] Architecture hybride explorée
- [ ] Interface web créée

---

## 🆘 Dépannage

Si une case n'est pas cochée:

1. **Module manquant** → Vérifiez que tous les fichiers sont présents
2. **Dépendance manquante** → Réinstallez avec `pip install -r requirements-rag.txt`
3. **API OpenAI** → Vérifiez `.env` et validez la clé sur platform.openai.com
4. **Chunks non générés** → Exécutez `python -m dyag.commands.create_rag ...`
5. **ChromaDB vide** → Exécutez `python scripts/index_chunks.py ...`
6. **Q&A échoue** → Vérifiez les logs et la connexion OpenAI

Consultez `doc/rag-quick-start.md` section "Résolution de Problèmes".

---

## ✅ Validation Finale

Exécutez ce test complet pour valider l'ensemble du système:

```bash
# Test unitaire complet
python -c "
print('=== TEST COMPLET DU SYSTEME RAG ===\n')

# 1. Modules
print('1. Verification des modules...')
from dyag.commands.create_rag import RAGCreator
from dyag.rag_query import RAGQuerySystem
print('   ✓ Modules importes\n')

# 2. ChromaDB
print('2. Verification ChromaDB...')
import chromadb
client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_collection('applications')
count = collection.count()
print(f'   ✓ {count} chunks indexes\n')

# 3. RAG System
print('3. Verification RAG System...')
rag = RAGQuerySystem()
stats = rag.get_stats()
print(f'   ✓ Systeme initialise')
print(f'   ✓ Modele: {stats[\"llm_model\"]}\n')

# 4. Test Q&A
print('4. Test question/reponse...')
result = rag.ask('Test system')
print(f'   ✓ Reponse generee')
print(f'   ✓ Sources: {len(result[\"sources\"])} chunks')
print(f'   ✓ Tokens: {result[\"tokens_used\"]}\n')

print('=== SYSTEME OPERATIONNEL ===')
print('Tout est pret ! Consultez doc/rag-quick-start.md pour commencer.')
"
```

**Résultat attendu:**
```
=== TEST COMPLET DU SYSTEME RAG ===

1. Verification des modules...
   ✓ Modules importes

2. Verification ChromaDB...
   ✓ 1628 chunks indexes

3. Verification RAG System...
   ✓ Systeme initialise
   ✓ Modele: gpt-4o-mini

4. Test question/reponse...
   ✓ Reponse generee
   ✓ Sources: 5 chunks
   ✓ Tokens: 234

=== SYSTEME OPERATIONNEL ===
Tout est pret ! Consultez doc/rag-quick-start.md pour commencer.
```

---

## 📚 Prochaines Étapes

Une fois toutes les cases cochées:

1. **Explorez** → Testez différentes questions
2. **Personnalisez** → Ajustez les paramètres (n_chunks, temperature)
3. **Optimisez** → Consultez `doc/chunks-for-management.md` pour dashboards
4. **Déployez** → Créez une interface web avec Streamlit

🎉 **Félicitations ! Votre système RAG est opérationnel !**
