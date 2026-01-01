"""Tests unitaires pour chk_utf8 - Vérification encodage Markdown"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from dyag.encoding.core.checker import (
    check_md,
    check_markdown_files,
)
from dyag.encoding.commands.chk_utf8 import main_cli


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def utf8_md_file(temp_dir):
    """Crée un fichier .md UTF-8 valide."""
    file_path = temp_dir / "test_utf8.md"
    content = "# Test UTF-8\n\nCeci est un test avec des caractères accentués: é, à, ù."
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def iso8859_md_file(temp_dir):
    """Crée un fichier .md encodé en ISO-8859-1."""
    file_path = temp_dir / "test_iso.md"
    content = "# Test ISO-8859-1\n\nCeci est un test avec des caractères: é, à, ù."
    file_path.write_bytes(content.encode('iso-8859-1'))
    return file_path


@pytest.fixture
def empty_md_file(temp_dir):
    """Crée un fichier .md vide."""
    file_path = temp_dir / "empty.md"
    file_path.write_text("", encoding='utf-8')
    return file_path


@pytest.fixture
def ascii_md_file(temp_dir):
    """Crée un fichier .md ASCII pur (sans accents)."""
    file_path = temp_dir / "test_ascii.md"
    content = "# Test ASCII\n\nThis is a test without special characters."
    file_path.write_text(content, encoding='ascii')
    return file_path


@pytest.fixture
def md_with_bom(temp_dir):
    """Crée un fichier .md UTF-8 avec BOM."""
    file_path = temp_dir / "test_bom.md"
    content = "# Test UTF-8 BOM\n\nFichier avec BOM."
    # BOM UTF-8: 0xEF, 0xBB, 0xBF
    file_path.write_bytes(b'\xef\xbb\xbf' + content.encode('utf-8'))
    return file_path


# ============================================================================
# Tests check_md()
# ============================================================================

class TestCheckMd:
    """Tests pour la fonction check_md()."""

    def test_check_utf8_file(self, utf8_md_file):
        """Test détection fichier UTF-8 valide."""
        result = check_md(utf8_md_file)

        assert result["path"] == utf8_md_file
        assert result["encoding"] in ("utf-8", "UTF-8", "ascii")
        assert result["confidence"] > 0.7
        assert result["raw_data"] is not None
        assert result["error"] is None

    def test_check_iso8859_file(self, iso8859_md_file):
        """Test détection fichier ISO-8859-1."""
        result = check_md(iso8859_md_file)

        assert result["path"] == iso8859_md_file
        # chardet peut détecter ISO-8859-1 ou Windows-1252
        assert result["encoding"] is not None
        assert result["encoding"].lower() not in ("utf-8", "utf8", "ascii")
        assert result["confidence"] > 0.0
        assert result["error"] is None

    def test_check_empty_file(self, empty_md_file):
        """Test détection fichier vide."""
        result = check_md(empty_md_file)

        assert result["path"] == empty_md_file
        # chardet peut retourner None pour fichiers vides
        assert result["raw_data"] == b""
        assert result["error"] is None

    def test_check_ascii_file(self, ascii_md_file):
        """Test détection fichier ASCII pur."""
        result = check_md(ascii_md_file)

        assert result["path"] == ascii_md_file
        assert result["encoding"] in ("ascii", "utf-8", "UTF-8")
        assert result["confidence"] > 0.5
        assert result["error"] is None

    def test_check_file_with_bom(self, md_with_bom):
        """Test détection fichier UTF-8 avec BOM."""
        result = check_md(md_with_bom)

        assert result["path"] == md_with_bom
        # chardet peut détecter UTF-8 ou UTF-8-SIG
        assert result["encoding"] in ("utf-8", "UTF-8", "UTF-8-SIG", "utf-8-sig")
        assert result["raw_data"].startswith(b'\xef\xbb\xbf')
        assert result["error"] is None

    def test_check_nonexistent_file(self, temp_dir):
        """Test gestion fichier inexistant."""
        nonexistent = temp_dir / "nonexistent.md"
        result = check_md(nonexistent)

        assert result["path"] == nonexistent
        assert result["encoding"] is None
        assert result["confidence"] == 0.0
        assert result["raw_data"] is None
        assert result["error"] == "Not a file or does not exist"

    def test_check_directory(self, temp_dir):
        """Test gestion d'un répertoire au lieu d'un fichier."""
        result = check_md(temp_dir)

        assert result["path"] == temp_dir
        assert result["encoding"] is None
        assert result["error"] == "Not a file or does not exist"


# ============================================================================
# Tests check_markdown_files()
# ============================================================================

class TestCheckMarkdownFiles:
    """Tests pour la fonction check_markdown_files()."""

    def test_check_single_pattern(self, temp_dir, utf8_md_file):
        """Test vérification avec pattern simple."""
        pattern = str(temp_dir / "*.md")
        results = check_markdown_files([pattern])

        assert len(results) == 1
        assert results[0]["path"] == utf8_md_file
        assert results[0]["error"] is None

    def test_check_multiple_files(self, temp_dir):
        """Test vérification de plusieurs fichiers."""
        # Créer plusieurs fichiers
        (temp_dir / "file1.md").write_text("# File 1", encoding='utf-8')
        (temp_dir / "file2.md").write_text("# File 2", encoding='utf-8')
        (temp_dir / "file3.md").write_text("# File 3", encoding='utf-8')

        pattern = str(temp_dir / "*.md")
        results = check_markdown_files([pattern])

        assert len(results) == 3
        for res in results:
            assert res["encoding"] in ("utf-8", "UTF-8", "ascii")
            assert res["error"] is None

    def test_check_recursive_pattern(self, temp_dir):
        """Test vérification récursive avec **."""
        # Créer structure de dossiers
        subdir1 = temp_dir / "docs"
        subdir2 = temp_dir / "docs" / "api"
        subdir1.mkdir()
        subdir2.mkdir()

        (temp_dir / "root.md").write_text("# Root", encoding='utf-8')
        (subdir1 / "doc1.md").write_text("# Doc 1", encoding='utf-8')
        (subdir2 / "api.md").write_text("# API", encoding='utf-8')

        pattern = str(temp_dir / "**" / "*.md")
        results = check_markdown_files([pattern])

        assert len(results) == 3

    def test_check_multiple_patterns(self, temp_dir):
        """Test vérification avec plusieurs patterns."""
        subdir = temp_dir / "docs"
        subdir.mkdir()

        (temp_dir / "readme.md").write_text("# README", encoding='utf-8')
        (subdir / "guide.md").write_text("# Guide", encoding='utf-8')

        patterns = [
            str(temp_dir / "readme.md"),
            str(subdir / "*.md")
        ]
        results = check_markdown_files(patterns)

        assert len(results) == 2

    def test_check_no_matching_files(self, temp_dir):
        """Test avec pattern ne trouvant aucun fichier."""
        pattern = str(temp_dir / "*.md")
        results = check_markdown_files([pattern])

        assert len(results) == 0

    def test_check_filters_non_md_files(self, temp_dir):
        """Test que seuls les .md sont traités."""
        (temp_dir / "file.md").write_text("# MD", encoding='utf-8')
        (temp_dir / "file.txt").write_text("Text file", encoding='utf-8')
        (temp_dir / "file.rst").write_text("RST file", encoding='utf-8')

        pattern = str(temp_dir / "*")
        results = check_markdown_files([pattern])

        assert len(results) == 1
        assert results[0]["path"].suffix == ".md"


# ============================================================================
# Tests main_cli()
# ============================================================================

class TestMainCli:
    """Tests pour la fonction main_cli()."""

    @patch('sys.argv', ['chk_utf8', '-P', 'test.md'])
    @patch('dyag.encoding.commands.chk_utf8.resolve_path_patterns')
    @patch('dyag.encoding.core.checker.check_md')
    def test_cli_success(self, mock_check, mock_resolve, temp_dir):
        """Test CLI avec fichier UTF-8 valide."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')

        mock_resolve.return_value = [test_file]
        mock_check.return_value = {
            "path": test_file,
            "encoding": "utf-8",
            "confidence": 0.99,
            "raw_data": b"# Test",
            "error": None
        }

        exit_code = main_cli()

        assert exit_code == 0
        mock_resolve.assert_called_once()
        mock_check.assert_called_once()

    @patch('sys.argv', ['chk_utf8', '-P', 'test.md'])
    @patch('dyag.encoding.commands.chk_utf8.resolve_path_patterns')
    @patch('dyag.encoding.core.checker.check_md')
    def test_cli_non_utf8_file(self, mock_check, mock_resolve, temp_dir):
        """Test CLI avec fichier non UTF-8."""
        test_file = temp_dir / "test.md"

        mock_resolve.return_value = [test_file]
        mock_check.return_value = {
            "path": test_file,
            "encoding": "iso-8859-1",
            "confidence": 0.85,
            "raw_data": b"test",
            "error": None
        }

        exit_code = main_cli()

        # Devrait retourner 1 (problème détecté)
        assert exit_code == 1

    @patch('sys.argv', ['chk_utf8', '-P', 'test.md', '--min-confidence', '0.9'])
    @patch('dyag.encoding.commands.chk_utf8.resolve_path_patterns')
    @patch('dyag.encoding.core.checker.check_md')
    def test_cli_low_confidence(self, mock_check, mock_resolve, temp_dir):
        """Test CLI avec confiance inférieure au seuil."""
        test_file = temp_dir / "test.md"

        mock_resolve.return_value = [test_file]
        mock_check.return_value = {
            "path": test_file,
            "encoding": "utf-8",
            "confidence": 0.6,  # < 0.9
            "raw_data": b"test",
            "error": None
        }

        exit_code = main_cli()

        # Devrait retourner 1 (confiance trop faible)
        assert exit_code == 1

    @patch('sys.argv', ['chk_utf8', '-P', 'test.md', '--quiet'])
    @patch('dyag.encoding.commands.chk_utf8.resolve_path_patterns')
    @patch('dyag.encoding.core.checker.check_md')
    def test_cli_quiet_mode(self, mock_check, mock_resolve, temp_dir, capsys):
        """Test CLI en mode silencieux."""
        test_file = temp_dir / "test.md"

        mock_resolve.return_value = [test_file]
        mock_check.return_value = {
            "path": test_file,
            "encoding": "utf-8",
            "confidence": 0.99,
            "raw_data": b"test",
            "error": None
        }

        exit_code = main_cli()

        assert exit_code == 0

        # En mode quiet, pas de sortie si tout va bien
        captured = capsys.readouterr()
        assert captured.out == ""

    @patch('sys.argv', ['chk_utf8', '-P', 'test.md'])
    @patch('dyag.encoding.chk_utf8.resolve_path_patterns')
    def test_cli_no_markdown_files(self, mock_resolve, capsys):
        """Test CLI sans fichiers Markdown trouvés."""
        mock_resolve.return_value = []

        exit_code = main_cli()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Aucun fichier Markdown" in captured.err

    @patch('sys.argv', ['chk_utf8', '-P', 'invalid/**/*.md'])
    @patch('dyag.encoding.chk_utf8.resolve_path_patterns')
    def test_cli_pattern_resolution_error(self, mock_resolve, capsys):
        """Test CLI avec erreur de résolution de patterns."""
        mock_resolve.side_effect = ValueError("Invalid pattern")

        exit_code = main_cli()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Échec de la résolution" in captured.err

    @patch('sys.argv', ['chk_utf8', '-P', 'test.md'])
    @patch('dyag.encoding.commands.chk_utf8.resolve_path_patterns')
    @patch('dyag.encoding.core.checker.check_md')
    def test_cli_file_error(self, mock_check, mock_resolve, temp_dir):
        """Test CLI avec erreur de lecture de fichier."""
        test_file = temp_dir / "test.md"

        mock_resolve.return_value = [test_file]
        mock_check.return_value = {
            "path": test_file,
            "encoding": None,
            "confidence": 0.0,
            "raw_data": None,
            "error": "Permission denied"
        }

        exit_code = main_cli()

        # Devrait retourner 1 (erreur détectée)
        assert exit_code == 1


# ============================================================================
# Tests edge cases
# ============================================================================

class TestEdgeCases:
    """Tests de cas limites."""

    def test_check_large_file(self, temp_dir):
        """Test vérification d'un fichier volumineux."""
        large_file = temp_dir / "large.md"
        content = "# Large File\n\n" + ("Lorem ipsum dolor sit amet. " * 10000)
        large_file.write_text(content, encoding='utf-8')

        result = check_md(large_file)

        assert result["error"] is None
        assert result["encoding"] in ("utf-8", "UTF-8", "ascii")

    def test_check_special_characters(self, temp_dir):
        """Test avec caractères spéciaux divers."""
        special_file = temp_dir / "special.md"
        content = "# Special: €, ©, ®, ™, ±, °, µ, π, Σ, √"
        special_file.write_text(content, encoding='utf-8')

        result = check_md(special_file)

        assert result["error"] is None
        assert result["encoding"] in ("utf-8", "UTF-8")

    def test_check_mixed_encodings_in_batch(self, temp_dir):
        """Test batch avec encodages mixtes."""
        (temp_dir / "utf8.md").write_text("# UTF-8: é", encoding='utf-8')
        (temp_dir / "iso.md").write_bytes("# ISO: é".encode('iso-8859-1'))
        (temp_dir / "ascii.md").write_text("# ASCII", encoding='ascii')

        pattern = str(temp_dir / "*.md")
        results = check_markdown_files([pattern])

        assert len(results) == 3
        # Tous devraient être traités sans erreur
        for res in results:
            assert res["error"] is None
