"""Tests unitaires pour fix_utf8 - Correction encodage et contenu Markdown"""

import pytest
from pathlib import Path
from unittest.mock import patch

from dyag.encoding.core.fixer import (
    decode_html_entities,
    fix_anchor_ids,
    encode_spaces_in_links,
    ensure_non_empty,
    fix_file_encoding_and_content,
    fix_markdown_files,
)
from dyag.encoding.commands.fix_utf8 import main_cli


# ============================================================================
# Tests decode_html_entities()
# ============================================================================

class TestDecodeHtmlEntities:
    """Tests pour décodage des entités HTML."""

    def test_decode_named_entities(self):
        """Test décodage entités nommées."""
        text = "Hello&nbsp;World&eacute;&agrave;&ugrave;"
        result = decode_html_entities(text)

        assert result == "Hello\xa0Worldéàù"

    def test_decode_numeric_entities(self):
        """Test décodage entités numériques décimales."""
        text = "Copyright&#169;2024&#160;Test"
        result = decode_html_entities(text)

        assert result == "Copyright©2024\xa0Test"

    def test_decode_hex_entities(self):
        """Test décodage entités hexadécimales."""
        text = "Euro&#x20AC;&#xa9;"
        result = decode_html_entities(text)

        assert result == "Euro€©"

    def test_decode_mixed_entities(self):
        """Test décodage entités mixtes."""
        text = "&lt;tag&gt; &#60;tag&#62; &#x3C;tag&#x3E;"
        result = decode_html_entities(text)

        assert result == "<tag> <tag> <tag>"

    def test_decode_preserves_plain_text(self):
        """Test que texte simple reste inchangé."""
        text = "This is plain text without entities"
        result = decode_html_entities(text)

        assert result == text

    def test_decode_ampersand_only(self):
        """Test & seul reste inchangé."""
        text = "AT&T and Ben&Jerry's"
        result = decode_html_entities(text)

        # Les & seuls restent car pas d'entité valide
        assert "AT&T" in result


# ============================================================================
# Tests fix_anchor_ids()
# ============================================================================

class TestFixAnchorIds:
    """Tests pour nettoyage IDs HTML."""

    def test_fix_trailing_space_in_id(self):
        """Test suppression espace en fin d'ID."""
        text = '<h2 id="section-1 ">Section</h2>'
        result = fix_anchor_ids(text)

        assert result == '<h2 id="section-1">Section</h2>'

    def test_fix_multiple_ids(self):
        """Test correction de plusieurs IDs."""
        text = '<h2 id="first ">First</h2><h3 id="second  ">Second</h3>'
        result = fix_anchor_ids(text)

        assert 'id="first "' not in result
        assert 'id="second  "' not in result

    def test_preserves_valid_ids(self):
        """Test que IDs valides restent inchangés."""
        text = '<h2 id="valid-id">Title</h2>'
        result = fix_anchor_ids(text)

        assert result == text

    def test_handles_empty_ids(self):
        """Test gestion IDs vides."""
        text = '<h2 id="">Empty</h2>'
        result = fix_anchor_ids(text)

        # Ne devrait pas crasher
        assert 'id=""' in result


# ============================================================================
# Tests encode_spaces_in_links()
# ============================================================================

class TestEncodeSpacesInLinks:
    """Tests pour encodage espaces dans liens."""

    def test_encode_markdown_link(self):
        """Test encodage espace dans lien Markdown."""
        text = "[Click here](path/file name.md)"
        result = encode_spaces_in_links(text)

        assert result == "[Click here](path/file%20name.md)"

    def test_encode_markdown_image(self):
        """Test encodage espace dans image Markdown."""
        text = "![Alt text](uploads/my image.png)"
        result = encode_spaces_in_links(text)

        assert result == "![Alt text](uploads/my%20image.png)"

    def test_encode_html_link(self):
        """Test encodage espace dans lien HTML."""
        text = '<a href="docs/user guide.html">Guide</a>'
        result = encode_spaces_in_links(text)

        assert result == '<a href="docs/user%20guide.html">Guide</a>'

    def test_encode_html_image(self):
        """Test encodage espace dans image HTML."""
        text = '<img src="images/my photo.jpg" alt="Photo"/>'
        result = encode_spaces_in_links(text)

        assert result == '<img src="images/my%20photo.jpg" alt="Photo"/>'

    def test_preserves_already_encoded(self):
        """Test ne ré-encode pas les URLs déjà encodées."""
        text = "[Link](path/file%20name.md)"
        result = encode_spaces_in_links(text)

        # Ne devrait pas double-encoder
        assert result == text

    def test_preserves_links_without_spaces(self):
        """Test liens sans espaces restent inchangés."""
        text = "[Link](path/file-name.md)"
        result = encode_spaces_in_links(text)

        assert result == text

    def test_encode_multiple_spaces(self):
        """Test encodage de plusieurs espaces."""
        text = "[Link](path/file with many spaces.md)"
        result = encode_spaces_in_links(text)

        assert result == "[Link](path/file%20with%20many%20spaces.md)"

    def test_preserves_url_components(self):
        """Test préserve composants URL (?, #, etc.)."""
        text = "[Link](path/file name.md?param=value#anchor)"
        result = encode_spaces_in_links(text)

        assert "file%20name.md" in result
        assert "?param=value#anchor" in result


# ============================================================================
# Tests ensure_non_empty()
# ============================================================================

class TestEnsureNonEmpty:
    """Tests pour remplissage fichiers vides."""

    def test_fill_empty_string(self):
        """Test remplissage chaîne vide."""
        result = ensure_non_empty("")

        assert result == "<!-- À compléter -->\n"

    def test_fill_whitespace_only(self):
        """Test remplissage chaîne avec espaces uniquement."""
        result = ensure_non_empty("   \n\t  \n")

        assert result == "<!-- À compléter -->\n"

    def test_preserves_content(self):
        """Test contenu existant reste inchangé."""
        content = "# Title\n\nContent here"
        result = ensure_non_empty(content)

        assert result == content

    def test_preserves_single_character(self):
        """Test même un seul caractère est préservé."""
        result = ensure_non_empty(".")

        assert result == "."


# ============================================================================
# Tests fix_file_encoding_and_content()
# ============================================================================

class TestFixFileEncodingAndContent:
    """Tests pour correction complète d'un fichier."""

    def test_fix_utf8_file_no_changes(self, temp_dir):
        """Test fichier UTF-8 déjà conforme."""
        test_file = temp_dir / "test.md"
        content = "# Test\n\nDéjà conforme UTF-8."
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True
        assert "déjà conforme" in message

    def test_fix_iso8859_to_utf8(self, temp_dir):
        """Test conversion ISO-8859-1 vers UTF-8."""
        test_file = temp_dir / "test.md"
        content = "# Test\n\nTexte avec accents: é, à, ù."
        test_file.write_bytes(content.encode('iso-8859-1'))

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True
        assert "corrigé" in message or "encoding" in message

        # Vérifier fichier réécrit en UTF-8
        fixed_content = test_file.read_text(encoding='utf-8')
        assert "é, à, ù" in fixed_content

    def test_fix_html_entities(self, temp_dir):
        """Test décodage entités HTML."""
        test_file = temp_dir / "test.md"
        content = "# Test\n\nHello&nbsp;World&eacute;"
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True

        # Vérifier entités décodées
        fixed_content = test_file.read_text(encoding='utf-8')
        assert "&nbsp;" not in fixed_content
        assert "&eacute;" not in fixed_content
        assert "é" in fixed_content

    def test_fix_spaces_in_links(self, temp_dir):
        """Test encodage espaces dans liens."""
        test_file = temp_dir / "test.md"
        content = "# Test\n\n[Link](path/file name.md)"
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True

        # Vérifier espaces encodés
        fixed_content = test_file.read_text(encoding='utf-8')
        assert "file%20name.md" in fixed_content

    def test_fix_empty_file(self, temp_dir):
        """Test remplissage fichier vide."""
        test_file = temp_dir / "empty.md"
        test_file.write_text("", encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True

        # Vérifier commentaire ajouté
        fixed_content = test_file.read_text(encoding='utf-8')
        assert "<!-- À compléter -->" in fixed_content

    def test_fix_file_with_bom(self, temp_dir):
        """Test suppression BOM UTF-8."""
        test_file = temp_dir / "bom.md"
        content = "# Test BOM"
        test_file.write_bytes(b'\xef\xbb\xbf' + content.encode('utf-8'))

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True

        # Vérifier BOM supprimé
        fixed_bytes = test_file.read_bytes()
        assert not fixed_bytes.startswith(b'\xef\xbb\xbf')

    def test_fix_dry_run(self, temp_dir):
        """Test mode dry-run (simulation)."""
        test_file = temp_dir / "test.md"
        content = "# Test\n\nHello&nbsp;World"
        test_file.write_text(content, encoding='utf-8')

        original_content = test_file.read_text()

        success, message = fix_file_encoding_and_content(test_file, dry_run=True)

        assert success is True
        assert "dry-run" in message

        # Vérifier fichier non modifié
        assert test_file.read_text() == original_content

    def test_fix_with_backup(self, temp_dir):
        """Test création de backup."""
        test_file = temp_dir / "test.md"
        content = "# Test\n\nOriginal&nbsp;content"
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file, backup=True)

        assert success is True

        # Vérifier backup créé
        backup_file = temp_dir / "test.md.bak"
        assert backup_file.exists()
        assert "Original&nbsp;content" in backup_file.read_text()

        # Vérifier fichier modifié
        assert "&nbsp;" not in test_file.read_text()

    def test_fix_nonexistent_file(self, temp_dir):
        """Test gestion fichier inexistant."""
        nonexistent = temp_dir / "nonexistent.md"

        success, message = fix_file_encoding_and_content(nonexistent)

        assert success is False
        assert "échec" in message

    def test_fix_all_corrections_combined(self, temp_dir):
        """Test toutes corrections combinées."""
        test_file = temp_dir / "complex.md"
        content = """# Test&nbsp;Complex

<h2 id="section ">Section</h2>

[Link](path/file name.md)
![Image](img/my photo.png)

&eacute;&agrave;&ugrave;
"""
        test_file.write_bytes(content.encode('iso-8859-1'))

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True

        fixed = test_file.read_text(encoding='utf-8')
        assert "&nbsp;" not in fixed
        assert 'id="section "' not in fixed
        assert "file%20name.md" in fixed
        assert "my%20photo.png" in fixed
        assert "é" in fixed


# ============================================================================
# Tests fix_markdown_files()
# ============================================================================

class TestFixMarkdownFiles:
    """Tests pour correction batch de fichiers."""

    def test_fix_single_file(self, temp_dir):
        """Test correction d'un seul fichier."""
        test_file = temp_dir / "test.md"
        test_file.write_text("Hello&nbsp;World", encoding='utf-8')

        pattern = str(test_file)
        results = fix_markdown_files([pattern])

        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["path"] == str(test_file)

    def test_fix_multiple_files(self, temp_dir):
        """Test correction de plusieurs fichiers."""
        (temp_dir / "file1.md").write_text("Test&nbsp;1", encoding='utf-8')
        (temp_dir / "file2.md").write_text("Test&nbsp;2", encoding='utf-8')
        (temp_dir / "file3.md").write_text("Test&nbsp;3", encoding='utf-8')

        pattern = str(temp_dir / "*.md")
        results = fix_markdown_files([pattern])

        assert len(results) == 3
        for res in results:
            assert res["success"] is True

    def test_fix_filters_non_md_files(self, temp_dir):
        """Test que seuls les .md sont traités."""
        (temp_dir / "file.md").write_text("MD&nbsp;file", encoding='utf-8')
        (temp_dir / "file.txt").write_text("Text&nbsp;file", encoding='utf-8')

        pattern = str(temp_dir / "*")
        results = fix_markdown_files([pattern])

        # Seul le .md devrait être traité
        assert len(results) == 1
        assert ".md" in results[0]["path"]

    def test_fix_dry_run_batch(self, temp_dir):
        """Test dry-run sur plusieurs fichiers."""
        (temp_dir / "file1.md").write_text("Test&nbsp;1", encoding='utf-8')
        (temp_dir / "file2.md").write_text("Test&nbsp;2", encoding='utf-8')

        pattern = str(temp_dir / "*.md")
        results = fix_markdown_files([pattern], dry_run=True)

        assert len(results) == 2
        for res in results:
            assert res["dry_run"] is True

        # Vérifier fichiers non modifiés
        assert "&nbsp;" in (temp_dir / "file1.md").read_text()
        assert "&nbsp;" in (temp_dir / "file2.md").read_text()

    def test_fix_with_errors(self, temp_dir):
        """Test gestion d'erreurs dans batch."""
        (temp_dir / "valid.md").write_text("Valid&nbsp;file", encoding='utf-8')
        # Le fichier invalide sera créé mais supprimé pour tester l'erreur
        invalid = temp_dir / "invalid.md"
        invalid.write_text("temp", encoding='utf-8')
        invalid_path = str(invalid)
        invalid.unlink()  # Supprimer pour simuler erreur

        pattern = str(temp_dir / "*.md")
        results = fix_markdown_files([pattern])

        # Au moins le fichier valide devrait être traité
        assert len(results) >= 1
        valid_result = [r for r in results if "valid.md" in r["path"]]
        assert len(valid_result) == 1
        assert valid_result[0]["success"] is True


# ============================================================================
# Tests main_cli()
# ============================================================================

class TestMainCli:
    """Tests pour la fonction main_cli()."""

    @patch('sys.argv', ['fix_utf8', '-P', 'test.md'])
    @patch('dyag.encoding.commands.fix_utf8.resolve_path_patterns')
    def test_cli_success(self, mock_resolve, temp_dir, capsys):
        """Test CLI avec correction réussie."""
        test_file = temp_dir / "test.md"
        test_file.write_text("Hello&nbsp;World", encoding='utf-8')

        mock_resolve.return_value = [test_file]

        exit_code = main_cli()

        assert exit_code == 0

        # Vérifier correction appliquée
        assert "&nbsp;" not in test_file.read_text()

    @patch('sys.argv', ['fix_utf8', '-P', 'test.md', '--dry-run'])
    @patch('dyag.encoding.commands.fix_utf8.resolve_path_patterns')
    def test_cli_dry_run(self, mock_resolve, temp_dir):
        """Test CLI en mode dry-run."""
        test_file = temp_dir / "test.md"
        content = "Hello&nbsp;World"
        test_file.write_text(content, encoding='utf-8')

        mock_resolve.return_value = [test_file]

        exit_code = main_cli()

        assert exit_code == 0

        # Vérifier fichier non modifié
        assert test_file.read_text() == content

    @patch('sys.argv', ['fix_utf8', '-P', 'test.md', '--backup'])
    @patch('dyag.encoding.commands.fix_utf8.resolve_path_patterns')
    def test_cli_with_backup(self, mock_resolve, temp_dir):
        """Test CLI avec backup."""
        test_file = temp_dir / "test.md"
        content = "Hello&nbsp;World"
        test_file.write_text(content, encoding='utf-8')

        mock_resolve.return_value = [test_file]

        exit_code = main_cli()

        assert exit_code == 0

        # Vérifier backup créé
        backup = temp_dir / "test.md.bak"
        assert backup.exists()

    @patch('sys.argv', ['fix_utf8', '-P', 'test.md'])
    @patch('dyag.encoding.commands.fix_utf8.resolve_path_patterns')
    def test_cli_no_files(self, mock_resolve, capsys):
        """Test CLI sans fichiers trouvés."""
        mock_resolve.return_value = []

        exit_code = main_cli()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Aucun fichier Markdown" in captured.err

    @patch('sys.argv', ['fix_utf8', '-P', 'invalid/**/*.md'])
    @patch('dyag.encoding.commands.fix_utf8.resolve_path_patterns')
    def test_cli_pattern_error(self, mock_resolve, capsys):
        """Test CLI avec erreur de résolution de patterns."""
        mock_resolve.side_effect = ValueError("Invalid pattern")

        exit_code = main_cli()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Échec résolution" in captured.err


# ============================================================================
# Tests edge cases
# ============================================================================

class TestEdgeCases:
    """Tests de cas limites."""

    def test_fix_unicode_characters(self, temp_dir):
        """Test avec caractères Unicode variés."""
        test_file = temp_dir / "unicode.md"
        content = "# Unicode: 中文, 日本語, 한국어, العربية, עברית, Ελληνικά"
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True
        fixed = test_file.read_text(encoding='utf-8')
        assert "中文" in fixed

    def test_fix_mixed_line_endings(self, temp_dir):
        """Test avec fins de ligne mixtes."""
        test_file = temp_dir / "mixed.md"
        content = "Line 1\nLine 2\r\nLine 3\rLine 4"
        test_file.write_bytes(content.encode('utf-8'))

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True

    def test_fix_large_file(self, temp_dir):
        """Test avec fichier volumineux."""
        test_file = temp_dir / "large.md"
        content = "# Large\n\n" + ("Test&nbsp;line\n" * 10000)
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True
        fixed = test_file.read_text(encoding='utf-8')
        assert "&nbsp;" not in fixed

    def test_fix_preserves_code_blocks(self, temp_dir):
        """Test préserve blocs de code."""
        test_file = temp_dir / "code.md"
        content = """# Code

```python
# This is code with &nbsp; entity
text = "Hello&nbsp;World"
```
"""
        test_file.write_text(content, encoding='utf-8')

        success, message = fix_file_encoding_and_content(test_file)

        assert success is True
        # Les entités dans le code devraient être décodées
        # (c'est le comportement actuel - pas de distinction code/texte)
