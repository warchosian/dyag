# Tests Unitaires DYAG

Ce répertoire contient les tests unitaires pour le projet DYAG.

## Structure des Tests

```
tests/
├── conftest.py                      # Fixtures communes pour tous les tests
├── unit/                            # Tests unitaires
│   └── commands/                    # Tests pour les commandes
│       ├── test_md2html.py         # Tests pour md2html
│       ├── test_add_toc.py         # Tests pour add_toc
│       └── test_html2pdf.py        # Tests pour html2pdf
└── integration/                     # Tests d'intégration (à venir)
```

## Installation des Dépendances de Test

Les dépendances de test sont gérées par Poetry. Pour les installer :

```bash
poetry install --with dev
```

Ou si vous utilisez pip :

```bash
pip install pytest pytest-cov pytest-mock
```

## Lancer les Tests

### Lancer tous les tests

```bash
poetry run pytest
```

ou

```bash
pytest
```

### Lancer les tests avec couverture de code

```bash
poetry run pytest --cov=src/dyag --cov-report=html
```

Cela générera un rapport de couverture dans le répertoire `htmlcov/`.

### Lancer les tests en mode verbeux

```bash
poetry run pytest -v
```

### Lancer un fichier de test spécifique

```bash
poetry run pytest tests/unit/commands/test_md2html.py
```

### Lancer une classe de test spécifique

```bash
poetry run pytest tests/unit/commands/test_md2html.py::TestExtractCodeBlocks
```

### Lancer un test spécifique

```bash
poetry run pytest tests/unit/commands/test_md2html.py::TestExtractCodeBlocks::test_extract_single_graphviz_block
```

### Lancer les tests avec filtrage par nom

```bash
poetry run pytest -k "graphviz"
```

## Fixtures Disponibles

Les fixtures communes sont définies dans `conftest.py` :

- **temp_dir** : Crée un répertoire temporaire pour les tests
- **sample_markdown** : Retourne un exemple de contenu Markdown
- **sample_markdown_with_graphviz** : Markdown avec diagramme Graphviz
- **sample_markdown_with_plantuml** : Markdown avec diagramme PlantUML
- **sample_markdown_with_mermaid** : Markdown avec diagramme Mermaid
- **sample_html** : Retourne un exemple de contenu HTML
- **sample_svg** : Retourne un exemple de contenu SVG

## Couverture de Code

La configuration pytest dans `pyproject.toml` inclut automatiquement la couverture de code lors de l'exécution des tests.

Pour voir la couverture dans le terminal :

```bash
poetry run pytest --cov=src/dyag --cov-report=term-missing
```

Pour générer un rapport HTML :

```bash
poetry run pytest --cov=src/dyag --cov-report=html
```

Le rapport sera disponible dans `htmlcov/index.html`.

## Tests par Module

### test_md2html.py

Tests pour le module de conversion Markdown vers HTML avec support des diagrammes :
- Extraction de blocs de code
- Conversion Graphviz/PlantUML/Mermaid vers SVG
- Nettoyage du contenu SVG
- Conversion Markdown basique vers HTML
- Génération de documents HTML complets

### test_add_toc.py

Tests pour le module d'ajout de table des matières :
- Extraction des titres HTML
- Génération d'IDs uniques
- Création de la TOC hiérarchique
- Ajout de liens retour vers la TOC
- Injection de CSS

### test_html2pdf.py

Tests pour le module de conversion HTML vers PDF :
- Validation des entrées
- Conversion avec Playwright
- Orientations portrait/paysage
- Gestion des erreurs

## Bonnes Pratiques

1. **Isolation** : Chaque test doit être indépendant et ne pas dépendre d'autres tests
2. **Fixtures** : Utilisez les fixtures pour éviter la duplication de code
3. **Mocking** : Mockez les dépendances externes (subprocess, réseau, système de fichiers)
4. **Noms descriptifs** : Utilisez des noms de tests clairs et descriptifs
5. **Assertions claires** : Une assertion par concept testé quand c'est possible
6. **Nettoyage** : Les fixtures temp_dir nettoient automatiquement après elles

## Ajouter de Nouveaux Tests

Pour ajouter de nouveaux tests :

1. Créez un nouveau fichier `test_*.py` dans le répertoire approprié
2. Importez les modules à tester
3. Créez des classes de test avec le préfixe `Test`
4. Créez des méthodes de test avec le préfixe `test_`
5. Utilisez les fixtures disponibles ou créez-en de nouvelles dans `conftest.py`

Exemple :

```python
import pytest

class TestMyFeature:
    """Tests pour ma nouvelle fonctionnalité."""

    def test_something(self, temp_dir):
        """Test de quelque chose."""
        # Arrange
        # Act
        # Assert
        assert True
```

## CI/CD

Les tests peuvent être intégrés dans un pipeline CI/CD :

```yaml
# Exemple pour GitHub Actions
- name: Run tests
  run: |
    poetry install --with dev
    poetry run pytest --cov=src/dyag --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [Documentation pytest-cov](https://pytest-cov.readthedocs.io/)
- [Documentation pytest-mock](https://pytest-mock.readthedocs.io/)
