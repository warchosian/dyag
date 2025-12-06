"""
Tests unitaires pour le module make_interactive.
"""

import pytest
from pathlib import Path

from dyag.commands.make_interactive import (
    make_html_interactive,
    INTERACTIVE_CSS,
    INTERACTIVE_JS
)


class TestMakeHtmlInteractive:
    """Tests pour la fonction make_html_interactive."""

    def test_file_not_found(self, temp_dir):
        """Test avec un fichier inexistant."""
        non_existent = temp_dir / "non_existent.html"
        result = make_html_interactive(str(non_existent))

        assert result == 1

    def test_path_is_not_file(self, temp_dir):
        """Test avec un chemin qui n'est pas un fichier."""
        result = make_html_interactive(str(temp_dir))

        assert result == 1

    def test_successful_conversion(self, temp_dir, sample_html):
        """Test conversion réussie d'un HTML simple."""
        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(sample_html, encoding='utf-8')

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0
        assert output_file.exists()

        # Vérifier le contenu
        output_content = output_file.read_text(encoding='utf-8')
        assert 'zoom-indicator' in output_content
        assert 'interaction-help' in output_content
        assert 'addEventListener' in output_content

    def test_conversion_without_output_path(self, temp_dir, sample_html):
        """Test conversion sans spécifier le chemin de sortie."""
        input_file = temp_dir / "test.html"
        input_file.write_text(sample_html, encoding='utf-8')

        result = make_html_interactive(str(input_file))

        assert result == 0
        expected_output = temp_dir / "test.interactive.html"
        assert expected_output.exists()

    def test_css_injection(self, temp_dir, sample_html):
        """Test que le CSS est correctement injecté."""
        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(sample_html, encoding='utf-8')

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0

        output_content = output_file.read_text(encoding='utf-8')

        # Vérifier que le CSS est présent
        assert '.zoom-indicator' in output_content
        assert '.interaction-help' in output_content
        assert '.diagram-image' in output_content
        assert 'cursor: grab' in output_content

    def test_js_injection(self, temp_dir, sample_html):
        """Test que le JavaScript est correctement injecté."""
        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(sample_html, encoding='utf-8')

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0

        output_content = output_file.read_text(encoding='utf-8')

        # Vérifier que le JavaScript est présent
        assert 'document.addEventListener' in output_content
        assert 'enabledFeatures' in output_content
        assert 'querySelectorAll' in output_content
        assert "addEventListener('wheel'" in output_content
        assert "addEventListener('mousedown'" in output_content

    def test_with_svg_diagrams(self, temp_dir):
        """Test avec un HTML contenant des SVG."""
        html_with_svg = """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>Test</h1>
    <div class="diagram">
        <svg width="100" height="100">
            <circle cx="50" cy="50" r="40" fill="blue"/>
        </svg>
    </div>
</body>
</html>"""

        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(html_with_svg, encoding='utf-8')

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0

        output_content = output_file.read_text(encoding='utf-8')

        # Vérifier que le SVG est toujours présent
        assert '<svg' in output_content
        assert '<circle' in output_content

        # Vérifier que les fonctionnalités interactives sont ajoutées
        assert 'diagram-image' in output_content

    def test_without_head_tag(self, temp_dir):
        """Test avec un HTML sans balise </head>."""
        html_no_head = """<html>
<body>
    <h1>Test</h1>
    <p>No head tag</p>
</body>
</html>"""

        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(html_no_head, encoding='utf-8')

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0

        output_content = output_file.read_text(encoding='utf-8')

        # Le CSS devrait quand même être ajouté
        assert '.zoom-indicator' in output_content

    def test_without_body_tag(self, temp_dir):
        """Test avec un HTML sans balise </body>."""
        html_no_body = """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<h1>Test</h1>
<p>No body tag</p>
</html>"""

        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(html_no_body, encoding='utf-8')

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0

        output_content = output_file.read_text(encoding='utf-8')

        # Le JavaScript devrait quand même être ajouté
        assert 'enabledFeatures' in output_content

    def test_verbose_mode(self, temp_dir, sample_html):
        """Test mode verbeux."""
        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(sample_html, encoding='utf-8')

        result = make_html_interactive(
            str(input_file),
            str(output_file),
            verbose=True
        )

        assert result == 0

    def test_output_is_larger_than_input(self, temp_dir, sample_html):
        """Test que le fichier de sortie est plus grand que l'entrée."""
        input_file = temp_dir / "test.html"
        output_file = temp_dir / "test.interactive.html"

        input_file.write_text(sample_html, encoding='utf-8')

        input_size = len(sample_html)

        result = make_html_interactive(str(input_file), str(output_file))

        assert result == 0

        output_size = len(output_file.read_text(encoding='utf-8'))

        # Le fichier de sortie devrait être plus grand
        # (CSS + JS ajoutés)
        assert output_size > input_size


class TestInteractiveConstants:
    """Tests pour les constantes CSS et JS."""

    def test_css_contains_required_classes(self):
        """Test que le CSS contient les classes nécessaires."""
        assert '.zoom-indicator' in INTERACTIVE_CSS
        assert '.interaction-help' in INTERACTIVE_CSS
        assert '.diagram-image' in INTERACTIVE_CSS
        assert '.zoom-controls' in INTERACTIVE_CSS

    def test_js_contains_required_features(self):
        """Test que le JS contient les fonctionnalités nécessaires."""
        assert 'enabledFeatures' in INTERACTIVE_JS
        assert 'zoom: true' in INTERACTIVE_JS
        assert 'drag: true' in INTERACTIVE_JS
        assert 'addEventListener' in INTERACTIVE_JS
        assert 'querySelectorAll' in INTERACTIVE_JS

    def test_css_is_valid_style_tag(self):
        """Test que le CSS est dans une balise <style> valide."""
        assert INTERACTIVE_CSS.startswith('<style>')
        assert INTERACTIVE_CSS.endswith('</style>')

    def test_js_is_valid_script_tag(self):
        """Test que le JS est dans une balise <script> valide."""
        assert INTERACTIVE_JS.startswith('<script>')
        assert INTERACTIVE_JS.endswith('</script>')
