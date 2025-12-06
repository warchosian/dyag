"""
Tests unitaires pour le module html2md.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile

from dyag.commands.html2md import (
    HTMLToMarkdownConverter,
    convert_html_to_markdown,
    process_html_to_markdown
)


class TestHTMLToMarkdownConverter:
    """Tests pour la classe HTMLToMarkdownConverter."""

    def test_convert_heading_h1(self):
        """Test conversion d'un titre h1."""
        html = "<h1>Title</h1>"
        result = convert_html_to_markdown(html)
        assert result.strip() == "# Title"

    def test_convert_heading_h2(self):
        """Test conversion d'un titre h2."""
        html = "<h2>Subtitle</h2>"
        result = convert_html_to_markdown(html)
        assert result.strip() == "## Subtitle"

    def test_convert_heading_h3(self):
        """Test conversion d'un titre h3."""
        html = "<h3>Section</h3>"
        result = convert_html_to_markdown(html)
        assert result.strip() == "### Section"

    def test_convert_paragraph(self):
        """Test conversion d'un paragraphe."""
        html = "<p>This is a paragraph.</p>"
        result = convert_html_to_markdown(html)
        assert "This is a paragraph." in result

    def test_convert_bold(self):
        """Test conversion de texte gras."""
        html = "<p>This is <strong>bold</strong> text.</p>"
        result = convert_html_to_markdown(html)
        assert "**bold**" in result

    def test_convert_italic(self):
        """Test conversion de texte italique."""
        html = "<p>This is <em>italic</em> text.</p>"
        result = convert_html_to_markdown(html)
        assert "*italic*" in result

    def test_convert_link(self):
        """Test conversion d'un lien."""
        html = '<p>Check out <a href="https://example.com">this link</a>.</p>'
        result = convert_html_to_markdown(html)
        assert "[this link](https://example.com)" in result

    def test_convert_image(self):
        """Test conversion d'une image."""
        html = '<img src="image.png" alt="An image">'
        result = convert_html_to_markdown(html)
        assert "![An image](image.png)" in result

    def test_convert_unordered_list(self):
        """Test conversion d'une liste non ordonnée."""
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        """
        result = convert_html_to_markdown(html)
        assert "- Item 1" in result
        assert "- Item 2" in result
        assert "- Item 3" in result

    def test_convert_ordered_list(self):
        """Test conversion d'une liste ordonnée."""
        html = """
        <ol>
            <li>First</li>
            <li>Second</li>
            <li>Third</li>
        </ol>
        """
        result = convert_html_to_markdown(html)
        assert "1. First" in result
        assert "2. Second" in result
        assert "3. Third" in result

    def test_convert_nested_list(self):
        """Test conversion d'une liste imbriquée."""
        html = """
        <ul>
            <li>Item 1
                <ul>
                    <li>Nested 1</li>
                    <li>Nested 2</li>
                </ul>
            </li>
            <li>Item 2</li>
        </ul>
        """
        result = convert_html_to_markdown(html)
        assert "- Item 1" in result
        assert "  - Nested 1" in result
        assert "  - Nested 2" in result
        assert "- Item 2" in result

    def test_convert_code_inline(self):
        """Test conversion de code inline."""
        html = "<p>Use the <code>print()</code> function.</p>"
        result = convert_html_to_markdown(html)
        assert "`print()`" in result

    def test_convert_code_block(self):
        """Test conversion d'un bloc de code."""
        html = """
        <pre><code>def hello():
    print("Hello, World!")
</code></pre>
        """
        result = convert_html_to_markdown(html)
        assert "```" in result
        assert 'print("Hello, World!")' in result

    def test_convert_blockquote(self):
        """Test conversion d'une citation."""
        html = "<blockquote>This is a quote.</blockquote>"
        result = convert_html_to_markdown(html)
        assert "> This is a quote." in result

    def test_convert_horizontal_rule(self):
        """Test conversion d'une ligne horizontale."""
        html = "<p>Before</p><hr><p>After</p>"
        result = convert_html_to_markdown(html)
        assert "---" in result

    def test_convert_line_break(self):
        """Test conversion d'un saut de ligne."""
        html = "<p>Line 1<br>Line 2</p>"
        result = convert_html_to_markdown(html)
        assert "Line 1  \nLine 2" in result or "Line 1\nLine 2" in result

    def test_convert_table(self):
        """Test conversion d'un tableau."""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Cell 1</td>
                    <td>Cell 2</td>
                </tr>
                <tr>
                    <td>Cell 3</td>
                    <td>Cell 4</td>
                </tr>
            </tbody>
        </table>
        """
        result = convert_html_to_markdown(html)
        assert "Header 1" in result
        assert "Header 2" in result
        assert "Cell 1" in result
        assert "Cell 2" in result
        assert "---" in result  # Table separator

    def test_convert_complex_document(self):
        """Test conversion d'un document complexe."""
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Main Title</h1>
            <p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
            <h2>Section</h2>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <p>Check out <a href="https://example.com">this link</a>.</p>
        </body>
        </html>
        """
        result = convert_html_to_markdown(html)
        assert "# Main Title" in result
        assert "**bold**" in result
        assert "*italic*" in result
        assert "## Section" in result
        assert "- Item 1" in result
        assert "[this link](https://example.com)" in result

    def test_skip_script_tags(self):
        """Test que les balises script sont ignorées."""
        html = """
        <p>Visible text</p>
        <script>alert('This should be ignored');</script>
        <p>More visible text</p>
        """
        result = convert_html_to_markdown(html)
        assert "Visible text" in result
        assert "alert" not in result
        assert "More visible text" in result

    def test_skip_style_tags(self):
        """Test que les balises style sont ignorées."""
        html = """
        <p>Visible text</p>
        <style>body { color: red; }</style>
        <p>More visible text</p>
        """
        result = convert_html_to_markdown(html)
        assert "Visible text" in result
        assert "color: red" not in result
        assert "More visible text" in result

    def test_remove_html_comments(self):
        """Test que les commentaires HTML sont supprimés."""
        html = """
        <p>Visible text</p>
        <!-- This is a comment -->
        <p>More visible text</p>
        """
        result = convert_html_to_markdown(html)
        assert "Visible text" in result
        assert "This is a comment" not in result
        assert "More visible text" in result


class TestConvertHTMLToMarkdown:
    """Tests pour la fonction convert_html_to_markdown."""

    def test_simple_conversion(self):
        """Test conversion simple."""
        html = "<h1>Title</h1><p>Content</p>"
        result = convert_html_to_markdown(html)
        assert "# Title" in result
        assert "Content" in result

    def test_empty_html(self):
        """Test avec HTML vide."""
        result = convert_html_to_markdown("")
        assert result == "\n" or result == ""

    def test_verbose_mode(self):
        """Test mode verbeux."""
        html = "<p>Test</p>"
        result = convert_html_to_markdown(html, verbose=True)
        assert "Test" in result


class TestProcessHTMLToMarkdown:
    """Tests pour la fonction process_html_to_markdown."""

    def test_file_not_found(self):
        """Test avec un fichier inexistant."""
        result = process_html_to_markdown("/nonexistent/file.html")
        assert result == 1

    def test_path_is_not_file(self):
        """Test avec un chemin qui n'est pas un fichier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = process_html_to_markdown(tmpdir)
            assert result == 1

    def test_successful_conversion(self):
        """Test conversion réussie."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test HTML file
            input_file = Path(tmpdir) / "test.html"
            html_content = """
            <html>
            <body>
                <h1>Test Title</h1>
                <p>Test paragraph with <strong>bold</strong> text.</p>
            </body>
            </html>
            """
            input_file.write_text(html_content, encoding='utf-8')

            # Convert
            output_file = Path(tmpdir) / "test.md"
            result = process_html_to_markdown(str(input_file), str(output_file))

            assert result == 0
            assert output_file.exists()

            # Verify content
            md_content = output_file.read_text(encoding='utf-8')
            assert "# Test Title" in md_content
            assert "**bold**" in md_content

    def test_conversion_without_output_path(self):
        """Test conversion sans chemin de sortie spécifié."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test HTML file
            input_file = Path(tmpdir) / "test.html"
            html_content = "<h1>Title</h1>"
            input_file.write_text(html_content, encoding='utf-8')

            # Convert (output should be test.md)
            result = process_html_to_markdown(str(input_file))

            assert result == 0

            # Check that test.md was created
            expected_output = Path(tmpdir) / "test.md"
            assert expected_output.exists()

            md_content = expected_output.read_text(encoding='utf-8')
            assert "# Title" in md_content

    def test_verbose_mode(self):
        """Test mode verbeux."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "test.html"
            input_file.write_text("<p>Test</p>", encoding='utf-8')

            result = process_html_to_markdown(str(input_file), verbose=True)
            assert result == 0

    def test_conversion_with_complex_html(self):
        """Test conversion avec HTML complexe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "complex.html"
            html_content = """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <title>Test Document</title>
                <style>body { margin: 0; }</style>
            </head>
            <body>
                <h1>Main Title</h1>
                <p>Paragraph with <a href="https://example.com">link</a>.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <pre><code>print("Hello")</code></pre>
                <script>console.log("test");</script>
            </body>
            </html>
            """
            input_file.write_text(html_content, encoding='utf-8')

            output_file = Path(tmpdir) / "complex.md"
            result = process_html_to_markdown(str(input_file), str(output_file))

            assert result == 0

            md_content = output_file.read_text(encoding='utf-8')
            assert "# Main Title" in md_content
            assert "[link](https://example.com)" in md_content
            assert "- Item 1" in md_content
            assert "- Item 2" in md_content
            assert "print" in md_content
            # Script content should be excluded
            assert "console.log" not in md_content
