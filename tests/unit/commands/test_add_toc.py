"""
Tests unitaires pour le module add_toc.
"""

import pytest
from pathlib import Path

from dyag.commands.add_toc import (
    HeadingExtractor,
    generate_id,
    generate_toc_html,
    add_ids_to_headings,
    get_toc_css,
    add_toc_to_html
)


class TestHeadingExtractor:
    """Tests pour la classe HeadingExtractor."""

    def test_extract_single_heading(self):
        """Test extraction d'un seul titre."""
        html = "<h1>Title</h1>"
        parser = HeadingExtractor()
        parser.feed(html)

        assert len(parser.headings) == 1
        assert parser.headings[0]['level'] == 1
        assert parser.headings[0]['text'] == 'Title'
        assert parser.headings[0]['tag'] == 'h1'

    def test_extract_multiple_headings(self):
        """Test extraction de plusieurs titres."""
        html = """
        <h1>Title 1</h1>
        <h2>Title 2</h2>
        <h3>Title 3</h3>
        """
        parser = HeadingExtractor()
        parser.feed(html)

        assert len(parser.headings) == 3
        assert parser.headings[0]['level'] == 1
        assert parser.headings[1]['level'] == 2
        assert parser.headings[2]['level'] == 3

    def test_extract_heading_with_existing_id(self):
        """Test extraction d'un titre avec ID existant."""
        html = '<h1 id="existing-id">Title</h1>'
        parser = HeadingExtractor()
        parser.feed(html)

        assert len(parser.headings) == 1
        assert parser.headings[0]['id'] == 'existing-id'

    def test_extract_heading_without_id(self):
        """Test extraction d'un titre sans ID."""
        html = '<h1>Title</h1>'
        parser = HeadingExtractor()
        parser.feed(html)

        assert len(parser.headings) == 1
        assert parser.headings[0]['id'] == ''

    def test_extract_all_heading_levels(self):
        """Test extraction de tous les niveaux de titres (h1-h6)."""
        html = """
        <h1>H1</h1>
        <h2>H2</h2>
        <h3>H3</h3>
        <h4>H4</h4>
        <h5>H5</h5>
        <h6>H6</h6>
        """
        parser = HeadingExtractor()
        parser.feed(html)

        assert len(parser.headings) == 6
        for i in range(6):
            assert parser.headings[i]['level'] == i + 1

    def test_extract_heading_with_nested_tags(self):
        """Test extraction avec des balises imbriquées dans les titres."""
        html = '<h1>Title with <strong>bold</strong> text</h1>'
        parser = HeadingExtractor()
        parser.feed(html)

        assert len(parser.headings) == 1
        assert 'bold' in parser.headings[0]['text']


class TestGenerateId:
    """Tests pour la fonction generate_id."""

    def test_generate_simple_id(self):
        """Test génération d'un ID simple."""
        existing_ids = set()
        result = generate_id("Simple Title", existing_ids)

        assert result == "simple-title"
        assert "simple-title" in existing_ids

    def test_generate_id_with_special_chars(self):
        """Test génération avec caractères spéciaux."""
        existing_ids = set()
        result = generate_id("Title with @#$ special chars!", existing_ids)

        assert result == "title-with-special-chars"

    def test_generate_unique_id_when_duplicate(self):
        """Test génération d'ID unique en cas de doublon."""
        existing_ids = {"simple-title"}
        result = generate_id("Simple Title", existing_ids)

        assert result == "simple-title-1"
        assert "simple-title-1" in existing_ids

    def test_generate_multiple_duplicates(self):
        """Test génération avec plusieurs doublons."""
        existing_ids = {"title", "title-1", "title-2"}
        result = generate_id("Title", existing_ids)

        assert result == "title-3"

    def test_generate_id_with_spaces(self):
        """Test génération avec plusieurs espaces."""
        existing_ids = set()
        result = generate_id("Title   with    spaces", existing_ids)

        assert result == "title-with-spaces"

    def test_generate_id_with_accents(self):
        """Test génération avec accents."""
        existing_ids = set()
        result = generate_id("Titre avec accents éàù", existing_ids)

        # Les accents sont conservés car \w inclut les lettres accentuées
        assert "titre" in result.lower()


class TestGenerateTocHtml:
    """Tests pour la fonction generate_toc_html."""

    def test_generate_empty_toc(self):
        """Test génération avec liste vide."""
        result = generate_toc_html([])
        assert result == ""

    def test_generate_simple_toc(self):
        """Test génération d'une TOC simple."""
        headings = [
            {'level': 1, 'text': 'Title 1', 'id': 'title-1', 'tag': 'h1'},
            {'level': 2, 'text': 'Title 2', 'id': 'title-2', 'tag': 'h2'}
        ]

        result = generate_toc_html(headings)

        assert '<nav id="table-of-contents"' in result
        assert '<a href="#title-1">Title 1</a>' in result
        assert '<a href="#title-2">Title 2</a>' in result
        assert '<ul>' in result
        assert '</ul>' in result

    def test_generate_hierarchical_toc(self):
        """Test génération d'une TOC hiérarchique."""
        headings = [
            {'level': 1, 'text': 'H1', 'id': 'h1', 'tag': 'h1'},
            {'level': 2, 'text': 'H2-1', 'id': 'h2-1', 'tag': 'h2'},
            {'level': 2, 'text': 'H2-2', 'id': 'h2-2', 'tag': 'h2'},
            {'level': 3, 'text': 'H3', 'id': 'h3', 'tag': 'h3'}
        ]

        result = generate_toc_html(headings)

        # Vérifie la structure hiérarchique
        assert result.count('<ul>') > 1
        assert '<a href="#h1">H1</a>' in result
        assert '<a href="#h3">H3</a>' in result

    def test_skip_empty_headings(self):
        """Test qu'on ignore les titres vides."""
        headings = [
            {'level': 1, 'text': '', 'id': 'empty', 'tag': 'h1'},
            {'level': 2, 'text': 'Valid', 'id': 'valid', 'tag': 'h2'}
        ]

        result = generate_toc_html(headings)

        assert 'href="#empty"' not in result
        assert '<a href="#valid">Valid</a>' in result


class TestAddIdsToHeadings:
    """Tests pour la fonction add_ids_to_headings."""

    def test_add_id_to_heading_without_id(self):
        """Test ajout d'ID à un titre sans ID."""
        html = "<h1>Title</h1>"
        headings = [
            {'level': 1, 'text': 'Title', 'id': 'title', 'tag': 'h1', 'had_id': False}
        ]

        result = add_ids_to_headings(html, headings)

        assert '<h1 id="title">' in result
        assert 'back-to-toc' in result

    def test_preserve_heading_with_existing_id(self):
        """Test préservation d'un titre avec ID existant."""
        html = '<h1 id="existing">Title</h1>'
        headings = [
            {'level': 1, 'text': 'Title', 'id': 'existing', 'tag': 'h1', 'had_id': True}
        ]

        result = add_ids_to_headings(html, headings)

        # Ne devrait pas modifier les titres qui avaient déjà un ID
        assert result == html or 'id="existing"' in result

    def test_add_back_to_toc_links(self):
        """Test ajout des liens retour à la TOC."""
        html = "<h2>Section</h2>"
        headings = [
            {'level': 2, 'text': 'Section', 'id': 'section', 'tag': 'h2', 'had_id': False}
        ]

        result = add_ids_to_headings(html, headings)

        assert '<a href="#toc-section"' in result
        assert 'back-to-toc' in result


class TestGetTocCss:
    """Tests pour la fonction get_toc_css."""

    def test_returns_valid_css(self):
        """Test que le CSS retourné est valide."""
        css = get_toc_css()

        assert '.table-of-contents' in css
        assert '.back-to-toc' in css
        assert 'float' in css or 'fixed' in css  # Pour le bouton flottant
        assert 'scroll-behavior' in css  # Pour le défilement fluide


class TestAddTocToHtml:
    """Tests pour la fonction add_toc_to_html."""

    def test_file_not_found(self, temp_dir):
        """Test avec un fichier inexistant."""
        non_existent = temp_dir / "non_existent.html"
        result = add_toc_to_html(str(non_existent))

        assert result == 1

    def test_successful_toc_addition(self, temp_dir, sample_html):
        """Test ajout réussi d'une TOC."""
        html_file = temp_dir / "test.html"
        output_file = temp_dir / "test.toc.html"

        html_file.write_text(sample_html, encoding='utf-8')

        result = add_toc_to_html(str(html_file), str(output_file))

        assert result == 0
        assert output_file.exists()

        html_content = output_file.read_text(encoding='utf-8')
        assert 'table-of-contents' in html_content
        assert '<a href="#' in html_content  # Liens dans la TOC

    def test_toc_without_output_path(self, temp_dir, sample_html):
        """Test sans spécifier le chemin de sortie."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        result = add_toc_to_html(str(html_file))

        assert result == 0
        expected_output = temp_dir / "test.toc.html"
        assert expected_output.exists()

    def test_html_without_headings(self, temp_dir):
        """Test avec HTML sans titres."""
        html = "<html><body><p>No headings here</p></body></html>"
        html_file = temp_dir / "test.html"
        output_file = temp_dir / "test.toc.html"

        html_file.write_text(html, encoding='utf-8')

        result = add_toc_to_html(str(html_file), str(output_file))

        assert result == 0  # Réussit mais n'ajoute pas de TOC
        assert output_file.exists()

    def test_css_injection(self, temp_dir, sample_html):
        """Test que le CSS est injecté correctement."""
        html_file = temp_dir / "test.html"
        output_file = temp_dir / "test.toc.html"

        html_file.write_text(sample_html, encoding='utf-8')

        result = add_toc_to_html(str(html_file), str(output_file))

        assert result == 0

        html_content = output_file.read_text(encoding='utf-8')
        assert '.table-of-contents' in html_content
        assert '.back-to-toc' in html_content

    def test_floating_button_added(self, temp_dir, sample_html):
        """Test que le bouton flottant est ajouté."""
        html_file = temp_dir / "test.html"
        output_file = temp_dir / "test.toc.html"

        html_file.write_text(sample_html, encoding='utf-8')

        result = add_toc_to_html(str(html_file), str(output_file))

        assert result == 0

        html_content = output_file.read_text(encoding='utf-8')
        assert 'floating-toc-btn' in html_content
        assert '↑ TOC' in html_content or 'TOC' in html_content

    def test_verbose_mode(self, temp_dir, sample_html):
        """Test mode verbeux."""
        html_file = temp_dir / "test.html"
        output_file = temp_dir / "test.toc.html"

        html_file.write_text(sample_html, encoding='utf-8')

        result = add_toc_to_html(str(html_file), str(output_file), verbose=True)

        assert result == 0
