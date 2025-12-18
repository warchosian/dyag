# Contributing to Dyag

Merci de votre intérêt pour contribuer à Dyag! Ce document vous guidera à travers le processus de contribution.

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Configuration de l'environnement de développement](#configuration-de-lenvironnement-de-développement)
- [Processus de développement](#processus-de-développement)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Documentation](#documentation)
- [Soumission de Pull Requests](#soumission-de-pull-requests)

## Code de conduite

En participant à ce projet, vous acceptez de respecter notre code de conduite basé sur le respect mutuel et la courtoisie professionnelle.

## Comment contribuer

Il existe plusieurs façons de contribuer à Dyag :

### Rapporter des bugs

Si vous trouvez un bug, veuillez créer une [issue](https://github.com/warchosian/dyag/issues) avec :
- Un titre clair et descriptif
- Les étapes pour reproduire le bug
- Le comportement attendu vs le comportement observé
- Votre environnement (OS, version Python, version Dyag)
- Si possible, un exemple de code ou de fichier qui reproduit le problème

### Suggérer des améliorations

Pour suggérer une nouvelle fonctionnalité :
1. Vérifiez qu'elle n'existe pas déjà dans les [issues](https://github.com/warchosian/dyag/issues)
2. Créez une nouvelle issue avec le tag `enhancement`
3. Décrivez clairement :
   - Le problème que cela résoudrait
   - La solution proposée
   - Des exemples d'utilisation

### Contribuer du code

1. Fork le repository
2. Créez une branche pour votre fonctionnalité (`git checkout -b feat/amazing-feature`)
3. Committez vos changements en suivant les [conventions de commits](#conventions-de-commits)
4. Pushez vers votre fork (`git push origin feat/amazing-feature`)
5. Ouvrez une Pull Request

## Configuration de l'environnement de développement

### Prérequis

- Python 3.10 ou supérieur
- Poetry 1.4+
- Git
- (Optionnel) Graphviz pour les tests de diagrammes

### Installation

```bash
# Cloner le repository
git clone https://github.com/warchosian/dyag.git
cd dyag

# Installer les dépendances de développement
poetry install

# Installer les dépendances RAG (optionnel)
poetry install -E rag

# Activer l'environnement virtuel
poetry shell
```

### Configuration

1. Copiez `.env.example` vers `.env` :
```bash
cp .env.example .env
```

2. Configurez vos clés API si vous travaillez sur les fonctionnalités RAG :
```env
# Pour OpenAI
OPENAI_API_KEY=sk-...

# Pour Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Pour Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
```

## Processus de développement

### Structure du projet

```
dyag/
├── src/dyag/           # Code source
│   ├── commands/       # Commandes CLI
│   ├── rag_query.py    # Système RAG
│   ├── llm_providers.py# Providers LLM
│   └── main.py         # Point d'entrée
├── tests/              # Tests
│   ├── unit/           # Tests unitaires
│   └── integration/    # Tests d'intégration
├── doc/                # Documentation
└── examples/           # Exemples
```

### Workflow de développement

1. **Créez une branche** :
```bash
git checkout -b feat/your-feature
# ou
git checkout -b fix/your-bugfix
```

2. **Développez votre fonctionnalité** :
- Écrivez du code propre et documenté
- Ajoutez des tests
- Mettez à jour la documentation si nécessaire

3. **Testez** :
```bash
# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Tous les tests avec couverture
pytest --cov=src/dyag --cov-report=term-missing
```

4. **Formatez le code** :
```bash
# Formatter le code
black src/ tests/

# Vérifier le style
flake8 src/ tests/
```

5. **Committez** :
```bash
# Utiliser commitizen
cz commit

# Ou manuellement avec le format conventionnel
git commit -m "feat: add amazing feature"
```

## Standards de code

### Style de code

- Nous utilisons **Black** pour le formatage automatique
- **Flake8** pour la vérification du style
- **Type hints** encouragés pour les nouvelles fonctions
- **Docstrings** pour toutes les fonctions publiques

### Conventions de nommage

- **Fichiers** : snake_case (`rag_query.py`)
- **Classes** : PascalCase (`RAGQuerySystem`)
- **Fonctions/Variables** : snake_case (`prepare_rag_data`)
- **Constantes** : UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`)

### Conventions de commits

Nous utilisons les [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types** :
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation seulement
- `style:` Formatage (sans changement de code)
- `refactor:` Refactorisation
- `test:` Ajout/modification de tests
- `chore:` Tâches de maintenance

**Exemples** :
```bash
feat(rag): add support for Ollama provider
fix(md2html): correct diagram rendering on Windows
docs(readme): update RAG installation instructions
test(rag): add integration tests for query command
```

## Tests

### Écrire des tests

Chaque nouvelle fonctionnalité doit inclure des tests :

```python
# tests/unit/commands/test_my_feature.py
import pytest
from dyag.commands.my_feature import my_function

def test_my_function_basic():
    """Test basic functionality."""
    result = my_function("input")
    assert result == "expected_output"

def test_my_function_edge_case():
    """Test edge case."""
    with pytest.raises(ValueError):
        my_function("")
```

### Exécuter les tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/unit/commands/test_md2html.py

# Avec couverture
pytest --cov=src/dyag --cov-report=html

# Tests en mode verbose
pytest -v
```

### Couverture de code

- Visez **au moins 70%** de couverture pour les nouvelles fonctionnalités
- Les fonctionnalités critiques doivent avoir **>90%** de couverture
- Utilisez `--cov-report=html` pour voir les lignes non couvertes

## Documentation

### Documentation du code

Utilisez des docstrings Google-style :

```python
def my_function(param1: str, param2: int = 0) -> bool:
    """Brief description of the function.

    Longer description if needed, explaining what the function does,
    its algorithm, or any important details.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of the return value

    Raises:
        ValueError: When param1 is empty

    Example:
        >>> my_function("test", 42)
        True
    """
    pass
```

### Documentation utilisateur

- Mettez à jour `README.md` pour les nouvelles fonctionnalités
- Ajoutez des exemples dans `examples/`
- Mettez à jour `CHANGELOG.md` (géré par commitizen)

## Soumission de Pull Requests

### Avant de soumettre

- [ ] Les tests passent (`pytest`)
- [ ] Le code est formaté (`black src/ tests/`)
- [ ] Le style est conforme (`flake8 src/ tests/`)
- [ ] La documentation est à jour
- [ ] Les commits suivent les conventions
- [ ] Pas de conflits avec la branche `main`

### Template de PR

```markdown
## Description
Brief description of the changes

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Description of tests

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
```

### Review process

1. Un mainteneur reviewera votre PR
2. Des changements peuvent être demandés
3. Une fois approuvée, votre PR sera mergée
4. Elle apparaîtra dans la prochaine release

## Questions?

Si vous avez des questions :
- Ouvrez une [issue](https://github.com/warchosian/dyag/issues) avec le tag `question`
- Contactez les mainteneurs

## Remerciements

Merci de contribuer à Dyag! Chaque contribution, quelle que soit sa taille, est appréciée. 🎉
