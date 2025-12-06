# Guide de Test DYAG

Ce guide explique comment configurer et lancer les tests unitaires pour le projet DYAG.

## Installation des Dépendances

### Option 1 : Avec Poetry (Recommandé)

Si vous utilisez Poetry pour gérer le projet :

```bash
poetry install --with dev
```

Cela installera automatiquement toutes les dépendances de développement incluant pytest, pytest-cov, et pytest-mock.

### Option 2 : Avec pip

Si vous préférez utiliser pip directement :

```bash
pip install pytest pytest-cov pytest-mock
```

Ou installez toutes les dépendances depuis le fichier pyproject.toml :

```bash
pip install -e ".[dev]"
```

## Lancer les Tests

### Méthode Simple (Scripts fournis)

#### Sous Windows

Double-cliquez sur `run_tests.bat` ou exécutez dans le terminal :

```cmd
run_tests.bat
```

Le script vous proposera plusieurs options :
1. Lancer tous les tests
2. Lancer les tests avec couverture
3. Lancer les tests en mode verbeux
4. Lancer les tests avec couverture HTML

#### Sous Linux/Mac

```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Méthode Manuelle

#### Avec Poetry

```bash
# Tous les tests
poetry run pytest

# Avec couverture
poetry run pytest --cov=src/dyag --cov-report=term-missing

# Mode verbeux
poetry run pytest -v

# Couverture HTML
poetry run pytest --cov=src/dyag --cov-report=html
```

#### Avec pytest directement

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=src/dyag --cov-report=term-missing

# Mode verbeux
pytest -v

# Couverture HTML
pytest --cov=src/dyag --cov-report=html
```

## Vérifier l'Installation

Pour vérifier que pytest est correctement installé :

```bash
pytest --version
```

Vous devriez voir quelque chose comme :
```
pytest 7.x.x
```

## Structure des Tests

Les tests sont organisés comme suit :

```
tests/
├── conftest.py              # Fixtures communes
├── unit/                    # Tests unitaires
│   └── commands/
│       ├── test_md2html.py
│       ├── test_add_toc.py
│       └── test_html2pdf.py
└── README.md               # Documentation détaillée
```

## Exemples de Commandes Utiles

### Lancer un fichier de test spécifique

```bash
pytest tests/unit/commands/test_md2html.py
```

### Lancer une classe de test spécifique

```bash
pytest tests/unit/commands/test_md2html.py::TestExtractCodeBlocks
```

### Lancer un test spécifique

```bash
pytest tests/unit/commands/test_md2html.py::TestExtractCodeBlocks::test_extract_single_graphviz_block
```

### Lancer les tests qui correspondent à un mot-clé

```bash
pytest -k "graphviz"
```

### Voir les tests disponibles sans les exécuter

```bash
pytest --collect-only
```

### Mode watch (re-exécuter les tests à chaque modification)

```bash
pip install pytest-watch
ptw
```

## Rapport de Couverture

Après avoir lancé les tests avec l'option `--cov-report=html`, ouvrez le fichier :

```
htmlcov/index.html
```

dans votre navigateur pour voir un rapport détaillé de la couverture de code.

## Résolution de Problèmes

### "pytest: command not found"

Assurez-vous que pytest est installé :

```bash
pip install pytest
```

Ou si vous utilisez Poetry :

```bash
poetry install --with dev
```

### "ModuleNotFoundError: No module named 'dyag'"

Assurez-vous d'être dans le répertoire racine du projet et que le package est installé :

```bash
pip install -e .
```

Ou avec Poetry :

```bash
poetry install
```

### Les tests échouent avec des erreurs d'import

Vérifiez que vous êtes dans le bon répertoire et que la structure du projet est correcte :

```bash
# Doit afficher la structure attendue
ls -la
```

### Erreurs de permissions sur run_tests.sh (Linux/Mac)

Donnez les permissions d'exécution :

```bash
chmod +x run_tests.sh
```

## Intégration Continue (CI/CD)

### Exemple pour GitHub Actions

Créez `.github/workflows/tests.yml` :

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install poetry
        poetry install --with dev

    - name: Run tests with coverage
      run: |
        poetry run pytest --cov=src/dyag --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Exemple pour GitLab CI

Créez `.gitlab-ci.yml` :

```yaml
test:
  image: python:3.8
  before_script:
    - pip install poetry
    - poetry install --with dev
  script:
    - poetry run pytest --cov=src/dyag --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Meilleures Pratiques

1. **Lancez les tests avant chaque commit**
   ```bash
   pytest
   ```

2. **Vérifiez la couverture régulièrement**
   ```bash
   pytest --cov=src/dyag --cov-report=term-missing
   ```

3. **Utilisez le mode verbeux pour déboguer**
   ```bash
   pytest -v -s
   ```

4. **Isolez les tests qui échouent**
   ```bash
   pytest tests/unit/commands/test_md2html.py::TestExtractCodeBlocks::test_extract_single_graphviz_block -v
   ```

## Ressources Supplémentaires

- [Documentation pytest](https://docs.pytest.org/)
- [Documentation pytest-cov](https://pytest-cov.readthedocs.io/)
- [Documentation pytest-mock](https://pytest-mock.readthedocs.io/)
- [Guide de test Python](https://realpython.com/pytest-python-testing/)

## Support

Pour plus d'informations sur les tests, consultez le fichier `tests/README.md`.

Pour des questions spécifiques au projet DYAG, consultez le README principal du projet.
