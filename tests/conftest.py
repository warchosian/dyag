"""
Configuration commune pour les tests pytest.
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_markdown():
    """Retourne un exemple de contenu Markdown."""
    return """# Titre principal

## Section 1

Ceci est un paragraphe de test.

### Sous-section

- Item 1
- Item 2
- Item 3

## Section 2

```python
def hello():
    print("Hello World")
```
"""


@pytest.fixture
def sample_markdown_with_graphviz():
    """Retourne un exemple de Markdown avec un diagramme Graphviz."""
    return """# Documentation avec diagramme

## Architecture

```dot
digraph G {
    A -> B;
    B -> C;
    C -> A;
}
```

## Description

Ceci est un exemple de diagramme.
"""


@pytest.fixture
def sample_markdown_with_plantuml():
    """Retourne un exemple de Markdown avec un diagramme PlantUML."""
    return """# Diagramme de séquence

```plantuml
@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi!
@enduml
```
"""


@pytest.fixture
def sample_markdown_with_mermaid():
    """Retourne un exemple de Markdown avec un diagramme Mermaid."""
    return """# Diagramme Mermaid

```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```
"""


@pytest.fixture
def sample_html():
    """Retourne un exemple de contenu HTML."""
    return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Test Document</title>
    <style>
        body { font-family: sans-serif; }
    </style>
</head>
<body>
    <h1>Titre principal</h1>
    <p>Ceci est un paragraphe.</p>

    <h2>Section 1</h2>
    <p>Contenu de la section 1.</p>

    <h3>Sous-section</h3>
    <p>Contenu de la sous-section.</p>

    <h2>Section 2</h2>
    <p>Contenu de la section 2.</p>
</body>
</html>"""


@pytest.fixture
def sample_svg():
    """Retourne un exemple de contenu SVG."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <circle cx="50" cy="50" r="40" fill="blue"/>
</svg>"""
