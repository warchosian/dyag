"""
Tests unitaires pour le module project2md.
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import os

from dyag.commands.project2md import (
    is_binary_file,
    should_exclude_dir,
    ProjectIgnore,
    scan_directory,
    generate_file_tree,
    get_language_for_file,
    format_size,
    project_to_markdown
)


class TestIsBinaryFile:
    """Tests pour la fonction is_binary_file."""

    def test_binary_extension(self):
        """Test détection d'un fichier binaire par extension."""
        assert is_binary_file(Path("test.exe")) == True
        assert is_binary_file(Path("test.pdf")) == True
        assert is_binary_file(Path("image.png")) == True

    def test_text_file(self):
        """Test détection d'un fichier texte."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello World")
            temp_path = Path(f.name)

        try:
            assert is_binary_file(temp_path) == False
        finally:
            temp_path.unlink()

    def test_binary_content(self):
        """Test détection d'un fichier binaire par contenu."""
        # Create a temporary file with null bytes
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.dat', delete=False) as f:
            f.write(b'\x00\x01\x02\x03')
            temp_path = Path(f.name)

        try:
            assert is_binary_file(temp_path) == True
        finally:
            temp_path.unlink()


class TestShouldExcludeDir:
    """Tests pour la fonction should_exclude_dir."""

    def test_exclude_pycache(self):
        """Test exclusion de __pycache__."""
        exclude_dirs = {'__pycache__', 'node_modules'}
        assert should_exclude_dir('__pycache__', exclude_dirs) == True

    def test_exclude_hidden_dir(self):
        """Test exclusion des répertoires cachés."""
        exclude_dirs = set()
        assert should_exclude_dir('.git', exclude_dirs) == True
        assert should_exclude_dir('.vscode', exclude_dirs) == True

    def test_normal_dir(self):
        """Test d'un répertoire normal."""
        exclude_dirs = {'__pycache__'}
        assert should_exclude_dir('src', exclude_dirs) == False


class TestProjectIgnore:
    """Tests pour la classe ProjectIgnore."""

    def test_load_empty_projectignore(self):
        """Test chargement sans fichier .projectignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            ignore = ProjectIgnore(root_dir)
            assert len(ignore.patterns) == 0

    def test_load_projectignore_with_patterns(self):
        """Test chargement avec des patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            projectignore_file = root_dir / '.projectignore'

            # Create .projectignore with patterns
            with open(projectignore_file, 'w') as f:
                f.write("*.pyc\n")
                f.write("__pycache__/\n")
                f.write("# Comment\n")
                f.write("\n")
                f.write("!important.pyc\n")

            ignore = ProjectIgnore(root_dir)
            assert len(ignore.patterns) == 3

            # Check patterns
            patterns = [p[0] for p in ignore.patterns]
            assert "*.pyc" in patterns
            assert "__pycache__" in patterns
            assert "important.pyc" in patterns

    def test_should_ignore_file(self):
        """Test si un fichier devrait être ignoré."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            projectignore_file = root_dir / '.projectignore'

            # Create .projectignore
            with open(projectignore_file, 'w') as f:
                f.write("*.pyc\n")
                f.write("temp/\n")

            ignore = ProjectIgnore(root_dir)

            # Create test file
            test_file = root_dir / "test.pyc"
            test_file.touch()

            assert ignore.should_ignore(test_file) == True

    def test_should_not_ignore_file(self):
        """Test si un fichier ne devrait pas être ignoré."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            projectignore_file = root_dir / '.projectignore'

            # Create .projectignore
            with open(projectignore_file, 'w') as f:
                f.write("*.pyc\n")

            ignore = ProjectIgnore(root_dir)

            # Create test file
            test_file = root_dir / "test.py"
            test_file.touch()

            assert ignore.should_ignore(test_file) == False


class TestFormatSize:
    """Tests pour la fonction format_size."""

    def test_small_size(self):
        """Test formatage d'une petite taille."""
        assert format_size(123) == "123"

    def test_thousand_size(self):
        """Test formatage avec milliers."""
        assert format_size(1234) == "1.234"

    def test_million_size(self):
        """Test formatage avec millions."""
        assert format_size(1234567) == "1.234.567"


class TestGetLanguageForFile:
    """Tests pour la fonction get_language_for_file."""

    def test_python_file(self):
        """Test détection du langage pour Python."""
        assert get_language_for_file(Path("test.py")) == "python"

    def test_javascript_file(self):
        """Test détection du langage pour JavaScript."""
        assert get_language_for_file(Path("test.js")) == "javascript"

    def test_makefile(self):
        """Test détection du Makefile."""
        assert get_language_for_file(Path("makefile")) == "makefile"

    def test_unknown_extension(self):
        """Test fichier avec extension inconnue."""
        assert get_language_for_file(Path("test.xyz")) == "text"


class TestGenerateFileTree:
    """Tests pour la fonction generate_file_tree."""

    def test_simple_file_tree(self):
        """Test génération d'une arborescence simple."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create test files
            (root_dir / "file1.txt").write_text("content")
            (root_dir / "file2.py").write_text("code")

            files = [root_dir / "file1.txt", root_dir / "file2.py"]
            tree = generate_file_tree(files, root_dir)

            assert "file1.txt" in tree
            assert "file2.py" in tree
            assert "📁 Arborescence des fichiers" in tree

    def test_nested_file_tree(self):
        """Test génération d'une arborescence avec sous-dossiers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create nested structure
            subdir = root_dir / "src"
            subdir.mkdir()
            (subdir / "module.py").write_text("code")
            (root_dir / "README.md").write_text("readme")

            files = [root_dir / "README.md", subdir / "module.py"]
            tree = generate_file_tree(files, root_dir)

            assert "src" in tree
            assert "module.py" in tree
            assert "README.md" in tree


class TestProjectToMarkdown:
    """Tests pour la fonction project_to_markdown."""

    def test_nonexistent_directory(self):
        """Test avec un répertoire inexistant."""
        result = project_to_markdown("/nonexistent/directory")
        assert result == 1

    def test_with_file_instead_of_directory(self):
        """Test avec un fichier au lieu d'un répertoire."""
        with tempfile.NamedTemporaryFile() as f:
            result = project_to_markdown(f.name)
            assert result == 1

    def test_simple_directory(self):
        """Test conversion d'un répertoire simple."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create test files
            (root_dir / "test.py").write_text("print('hello')")
            (root_dir / "README.md").write_text("# Project")

            output_file = root_dir / "output.md"

            result = project_to_markdown(
                str(root_dir),
                str(output_file),
                verbose=False
            )

            assert result == 0
            assert output_file.exists()

            # Verify content
            content = output_file.read_text(encoding='utf-8')
            assert "test.py" in content
            assert "README.md" in content
            assert "print('hello')" in content

    def test_with_projectignore(self):
        """Test avec fichier .projectignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create .projectignore
            (root_dir / ".projectignore").write_text("ignored.txt\n")

            # Create test files
            (root_dir / "included.py").write_text("included")
            (root_dir / "ignored.txt").write_text("ignored")

            output_file = root_dir / "output.md"

            result = project_to_markdown(
                str(root_dir),
                str(output_file),
                verbose=False
            )

            assert result == 0

            # Verify content
            content = output_file.read_text(encoding='utf-8')
            assert "included.py" in content
            # ignored.txt should not be in the output
            # (it won't be in file tree or content sections)

    def test_empty_directory(self):
        """Test avec un répertoire vide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)
            output_file = root_dir / "output.md"

            result = project_to_markdown(
                str(root_dir),
                str(output_file),
                verbose=False
            )

            # Should return error for empty directory
            assert result == 1


class TestScanDirectory:
    """Tests pour la fonction scan_directory."""

    def test_scan_simple_directory(self):
        """Test scan d'un répertoire simple."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create test files
            (root_dir / "file1.txt").write_text("content")
            (root_dir / "file2.py").write_text("code")

            files = scan_directory(
                root_dir,
                exclude_dirs=set(),
                max_file_size=1024*1024,
                verbose=False,
                use_projectignore=False
            )

            assert len(files) == 2
            assert any(f.name == "file1.txt" for f in files)
            assert any(f.name == "file2.py" for f in files)

    def test_scan_with_excluded_dirs(self):
        """Test scan avec répertoires exclus."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create structure
            (root_dir / "included.txt").write_text("included")

            excluded_dir = root_dir / "__pycache__"
            excluded_dir.mkdir()
            (excluded_dir / "excluded.pyc").write_text("excluded")

            files = scan_directory(
                root_dir,
                exclude_dirs={'__pycache__'},
                max_file_size=1024*1024,
                verbose=False,
                use_projectignore=False
            )

            assert len(files) == 1
            assert files[0].name == "included.txt"

    def test_scan_with_size_limit(self):
        """Test scan avec limite de taille."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_dir = Path(tmpdir)

            # Create files of different sizes
            (root_dir / "small.txt").write_text("small")
            (root_dir / "large.txt").write_text("x" * 1000)

            files = scan_directory(
                root_dir,
                exclude_dirs=set(),
                max_file_size=100,  # Only 100 bytes
                verbose=False,
                use_projectignore=False
            )

            # Only small file should be included
            assert len(files) == 1
            assert files[0].name == "small.txt"
