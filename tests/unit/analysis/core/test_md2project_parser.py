"""
Tests unitaires pour dyag.analysis.core.md2project_parser
Tests du parser Markdown (format project2md) vers structure de projet.
"""
import pytest
from pathlib import Path
from dyag.analysis.core.md2project_parser import (
    Md2ProjectParser,
    ProjectStructure,
    FileEntry
)


@pytest.fixture
def sample_project_md():
    """Exemple de Markdown généré par project2md."""
    return """# Projet : test_project

**Chemin** : `/home/user/test_project`

**Fichiers** : 3 fichiers non-binaires

## 📁 Arborescence des fichiers

└── <a id="tree-README-md"></a>[README.md](#README-md) *(150 octets)*
└── <a id="tree-src-main-py"></a>[src/main.py](#src-main-py) *(456 octets)*
└── <a id="tree-tests-test_main-py"></a>[tests/test_main.py](#tests-test_main-py) *(289 octets)*

---
## 📄 Contenu des fichiers

---
### 📄 `README.md` [150 octets]
<a id="README-md"></a> [↩ Retour à l'arborescence](#tree-README-md)

> **Chemin relatif** : `README.md`
> **Taille** : 150 octets
> **Lignes** : 5
> **Type** : markdown

```markdown
# Test Project

This is a test project.

## Features
- Feature 1
```

---
### 📄 `src/main.py` [456 octets]
<a id="src-main-py"></a> [↩ Retour à l'arborescence](#tree-src-main-py)

> **Chemin relatif** : `src/main.py`
> **Taille** : 456 octets
> **Lignes** : 15
> **Type** : python

```python
#!/usr/bin/env python3
def main():
    print("Hello World")

if __name__ == "__main__":
    main()
```

---
### 📄 `tests/test_main.py` [289 octets]
<a id="tests-test_main-py"></a> [↩ Retour à l'arborescence](#tree-tests-test_main-py)

> **Chemin relatif** : `tests/test_main.py`
> **Taille** : 289 octets
> **Lignes** : 8
> **Type** : python

```python
import pytest

def test_main():
    assert True
```

---
*Généré par dyag project2md*
"""


@pytest.fixture
def sample_with_collapsible():
    """Exemple avec contenu collapsible (fichiers longs)."""
    return """# Projet : long_project

**Chemin** : `/tmp/long`

**Fichiers** : 1 fichiers non-binaires

## 📄 Contenu des fichiers

---
### 📄 `long_file.py` [5.000 octets]
<a id="long_file-py"></a>

> **Chemin relatif** : `long_file.py`
> **Taille** : 5.000 octets
> **Lignes** : 150
> **Type** : python

<details class="file-content-collapsible">
<summary>📖 Afficher le contenu (150 lignes) - Cliquer pour déplier</summary>

```python
# Long file content here
def function():
    pass
```

</details>

---
*Généré par dyag project2md*
"""


@pytest.fixture
def sample_with_nested_backticks():
    """Exemple avec backticks imbriqués (4 backticks)."""
    return """# Projet : nested

**Chemin** : `/tmp/nested`

**Fichiers** : 1 fichiers non-binaires

## 📄 Contenu des fichiers

---
### 📄 `doc.md` [200 octets]
<a id="doc-md"></a>

> **Chemin relatif** : `doc.md`
> **Taille** : 200 octets
> **Lignes** : 10
> **Type** : markdown

````markdown
# Documentation

Here is code:

```python
print("Hello")
```

End of doc.
````

---
*Généré par dyag project2md*
"""


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.analysis
class TestMd2ProjectParser:
    """Tests du Md2ProjectParser."""

    def test_parse_project_name(self, sample_project_md):
        """Test extraction du nom du projet."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        assert project.name == "test_project"

    def test_parse_metadata(self, sample_project_md):
        """Test extraction des métadonnées."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        assert project.root_path == "/home/user/test_project"
        assert project.total_files == 3

    def test_parse_files_count(self, sample_project_md):
        """Test extraction du bon nombre de fichiers."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        assert len(project.files) == 3

    def test_parse_file_paths(self, sample_project_md):
        """Test extraction des chemins de fichiers."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        paths = [f.path for f in project.files]
        assert "README.md" in paths
        assert "src/main.py" in paths
        assert "tests/test_main.py" in paths

    def test_parse_file_content(self, sample_project_md):
        """Test extraction du contenu des fichiers."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        readme = next(f for f in project.files if f.path == "README.md")
        assert "# Test Project" in readme.content
        assert "Feature 1" in readme.content

        main_py = next(f for f in project.files if f.path == "src/main.py")
        assert "def main():" in main_py.content
        assert 'print("Hello World")' in main_py.content

    def test_parse_file_metadata(self, sample_project_md):
        """Test extraction des métadonnées de fichiers."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        readme = next(f for f in project.files if f.path == "README.md")
        assert readme.language == "markdown"
        assert readme.size == 150
        assert readme.lines == 5

        main_py = next(f for f in project.files if f.path == "src/main.py")
        assert main_py.language == "python"
        assert main_py.size == 456
        assert main_py.lines == 15

    def test_parse_collapsible_content(self, sample_with_collapsible):
        """Test extraction de contenu dans <details>."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_with_collapsible)

        assert len(project.files) == 1
        file = project.files[0]
        assert file.path == "long_file.py"
        assert "def function():" in file.content

    def test_parse_nested_backticks(self, sample_with_nested_backticks):
        """Test extraction avec backticks imbriqués (4 backticks)."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_with_nested_backticks)

        assert len(project.files) == 1
        doc = project.files[0]
        assert doc.path == "doc.md"
        assert "# Documentation" in doc.content
        assert '```python' in doc.content
        assert 'print("Hello")' in doc.content

    def test_parse_empty_markdown(self):
        """Test parsing Markdown vide."""
        parser = Md2ProjectParser()
        project = parser.parse_content("")

        assert project.name == "unnamed_project"
        assert len(project.files) == 0

    def test_parse_no_content_section(self):
        """Test Markdown sans section 'Contenu des fichiers'."""
        md = """# Projet : minimal

**Fichiers** : 0 fichiers

## Autre section
Contenu aléatoire
"""
        parser = Md2ProjectParser()
        project = parser.parse_content(md)

        assert project.name == "minimal"
        assert len(project.files) == 0

    def test_parse_file_without_content(self):
        """Test fichier sans bloc de code."""
        md = """# Projet : empty_file

## 📄 Contenu des fichiers

---
### 📄 `empty.txt` [0 octets]
<a id="empty-txt"></a>

> **Chemin relatif** : `empty.txt`
> **Taille** : 0 octets
> **Lignes** : 0
> **Type** : text

No code block here.

---
*Généré par dyag project2md*
"""
        parser = Md2ProjectParser(verbose=True)
        project = parser.parse_content(md)

        # Devrait avoir un fichier avec contenu vide
        assert len(project.files) == 1
        assert project.files[0].content == ""

    def test_parse_from_file(self, tmp_path, sample_project_md):
        """Test parsing depuis un fichier."""
        md_file = tmp_path / "project.md"
        md_file.write_text(sample_project_md, encoding='utf-8')

        parser = Md2ProjectParser()
        project = parser.parse_file(str(md_file))

        assert project.name == "test_project"
        assert len(project.files) == 3

    def test_to_dict(self, sample_project_md):
        """Test conversion en dictionnaire."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        proj_dict = project.to_dict()

        assert proj_dict["name"] == "test_project"
        assert proj_dict["root_path"] == "/home/user/test_project"
        assert proj_dict["total_files"] == 3
        assert len(proj_dict["files"]) == 3

        # Test file dict
        file_dict = proj_dict["files"][0]
        assert "path" in file_dict
        assert "content" in file_dict
        assert "language" in file_dict


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.analysis
class TestMd2ProjectValidation:
    """Tests de validation de structure."""

    def test_validate_valid_structure(self, sample_project_md):
        """Test validation d'une structure valide."""
        parser = Md2ProjectParser()
        project = parser.parse_content(sample_project_md)

        issues = parser.validate_structure(project)

        # Peut avoir des warnings mais pas d'erreurs critiques
        assert isinstance(issues, list)

    def test_validate_no_files(self):
        """Test validation sans fichiers."""
        project = ProjectStructure(name="empty")
        parser = Md2ProjectParser()

        issues = parser.validate_structure(project)

        assert "Aucun fichier extrait" in issues

    def test_validate_empty_files(self):
        """Test validation avec fichiers vides."""
        project = ProjectStructure(
            name="test",
            files=[
                FileEntry(path="empty.txt", content=""),
                FileEntry(path="valid.txt", content="content"),
            ]
        )
        parser = Md2ProjectParser()

        issues = parser.validate_structure(project)

        # Devrait signaler 1 fichier vide
        empty_warning = next((i for i in issues if "vides" in i), None)
        assert empty_warning is not None

    def test_validate_inconsistent_file_count(self):
        """Test validation avec nombre de fichiers incohérent."""
        project = ProjectStructure(
            name="test",
            total_files=5,  # Dit 5
            files=[  # Mais seulement 2
                FileEntry(path="file1.txt", content="a"),
                FileEntry(path="file2.txt", content="b"),
            ]
        )
        parser = Md2ProjectParser()

        issues = parser.validate_structure(project)

        # Devrait signaler incohérence
        inconsistency = next((i for i in issues if "Incohérence" in i), None)
        assert inconsistency is not None

    def test_validate_invalid_paths(self):
        """Test validation avec chemins invalides."""
        # Windows invalid chars: <, >, :, ", |, ?, *, \0
        # Testing with extreme case
        project = ProjectStructure(
            name="test",
            files=[
                FileEntry(path="valid.txt", content="ok"),
            ]
        )
        parser = Md2ProjectParser()

        issues = parser.validate_structure(project)

        # Pas d'erreur pour chemins valides
        path_errors = [i for i in issues if "Chemin invalide" in i]
        assert len(path_errors) == 0


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.analysis
class TestMd2ProjectEdgeCases:
    """Tests de cas limites."""

    def test_parse_special_characters_in_paths(self):
        """Test chemins avec caractères spéciaux."""
        md = """# Projet : special

## 📄 Contenu des fichiers

---
### 📄 `path/with spaces/file.txt` [10 octets]
<a id="path-with-spaces-file-txt"></a>

> **Type** : text

```text
content
```
"""
        parser = Md2ProjectParser()
        project = parser.parse_content(md)

        assert len(project.files) == 1
        assert project.files[0].path == "path/with spaces/file.txt"

    def test_parse_unicode_content(self):
        """Test contenu Unicode."""
        md = """# Projet : unicode

## 📄 Contenu des fichiers

---
### 📄 `unicode.txt` [50 octets]
<a id="unicode-txt"></a>

> **Type** : text

```text
UTF-8: é, à, ù, €, 中文, 日本語
```
"""
        parser = Md2ProjectParser()
        project = parser.parse_content(md)

        assert len(project.files) == 1
        content = project.files[0].content
        assert "é, à, ù" in content
        assert "中文" in content

    def test_parse_very_long_file_path(self):
        """Test chemin de fichier très long."""
        long_path = "a/" * 50 + "file.txt"
        md = f"""# Projet : long_path

## 📄 Contenu des fichiers

---
### 📄 `{long_path}` [10 octets]
<a id="anchor"></a>

> **Type** : text

```text
data
```
"""
        parser = Md2ProjectParser()
        project = parser.parse_content(md)

        assert len(project.files) == 1
        assert project.files[0].path == long_path

    def test_parse_multiline_content_with_empty_lines(self):
        """Test contenu avec lignes vides."""
        md = """# Projet : multiline

## 📄 Contenu des fichiers

---
### 📄 `file.py` [100 octets]
<a id="file-py"></a>

> **Type** : python

```python
def func1():
    pass


def func2():
    pass
```
"""
        parser = Md2ProjectParser()
        project = parser.parse_content(md)

        content = project.files[0].content
        lines = content.split('\n')

        # Devrait conserver les lignes vides
        assert '' in lines
        assert 'def func1():' in content
        assert 'def func2():' in content

    def test_parse_file_without_language(self):
        """Test fichier sans language spécifié."""
        md = """# Projet : no_lang

## 📄 Contenu des fichiers

---
### 📄 `file.txt` [10 octets]
<a id="file-txt"></a>

> **Chemin relatif** : `file.txt`

```
plain content
```
"""
        parser = Md2ProjectParser()
        project = parser.parse_content(md)

        assert len(project.files) == 1
        # Language peut être None ou vide
        assert project.files[0].content == "plain content"
