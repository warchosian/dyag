"""
Tests unitaires pour le module html2pdf.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from dyag.commands.html2pdf import convert_html_to_pdf


class TestConvertHtmlToPdf:
    """Tests pour la fonction convert_html_to_pdf."""

    def test_file_not_found(self, temp_dir):
        """Test avec un fichier inexistant."""
        non_existent = temp_dir / "non_existent.html"
        result = convert_html_to_pdf(str(non_existent))

        assert result == 1

    def test_path_is_not_file(self, temp_dir):
        """Test avec un chemin qui n'est pas un fichier."""
        result = convert_html_to_pdf(str(temp_dir))

        assert result == 1

    def test_invalid_orientation(self, temp_dir, sample_html):
        """Test avec une orientation invalide."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        result = convert_html_to_pdf(
            str(html_file),
            orientation='invalid'
        )

        assert result == 1

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', False)
    def test_playwright_not_available(self, temp_dir, sample_html):
        """Test quand Playwright n'est pas disponible."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        result = convert_html_to_pdf(str(html_file))

        assert result == 1

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_successful_conversion_portrait(self, mock_playwright, temp_dir, sample_html):
        """Test conversion réussie en mode portrait."""
        html_file = temp_dir / "test.html"
        pdf_file = temp_dir / "test.pdf"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(return_value=mock_playwright_ctx)
        mock_playwright_ctx.__exit__ = MagicMock(return_value=None)
        mock_playwright_ctx.chromium.launch.return_value = mock_browser

        mock_playwright.return_value = mock_playwright_ctx

        # Simulate PDF creation
        def create_pdf(**kwargs):
            pdf_path = Path(kwargs['path'])
            pdf_path.write_bytes(b'%PDF-1.4 fake pdf content')

        mock_page.pdf = create_pdf

        result = convert_html_to_pdf(
            str(html_file),
            str(pdf_file),
            orientation='portrait'
        )

        assert result == 0
        assert pdf_file.exists()
        mock_page.goto.assert_called_once()
        mock_page.wait_for_load_state.assert_called_once_with('networkidle')

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_successful_conversion_landscape(self, mock_playwright, temp_dir, sample_html):
        """Test conversion réussie en mode paysage."""
        html_file = temp_dir / "test.html"
        pdf_file = temp_dir / "test.pdf"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(return_value=mock_playwright_ctx)
        mock_playwright_ctx.__exit__ = MagicMock(return_value=None)
        mock_playwright_ctx.chromium.launch.return_value = mock_browser

        mock_playwright.return_value = mock_playwright_ctx

        # Simulate PDF creation
        def create_pdf(**kwargs):
            pdf_path = Path(kwargs['path'])
            pdf_path.write_bytes(b'%PDF-1.4 fake pdf content')
            # Verify landscape option is set
            assert 'landscape' in kwargs
            assert kwargs['landscape'] is True

        mock_page.pdf = create_pdf

        result = convert_html_to_pdf(
            str(html_file),
            str(pdf_file),
            orientation='landscape'
        )

        assert result == 0
        assert pdf_file.exists()

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_conversion_without_output_path(self, mock_playwright, temp_dir, sample_html):
        """Test conversion sans spécifier le chemin de sortie."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(return_value=mock_playwright_ctx)
        mock_playwright_ctx.__exit__ = MagicMock(return_value=None)
        mock_playwright_ctx.chromium.launch.return_value = mock_browser

        mock_playwright.return_value = mock_playwright_ctx

        # Simulate PDF creation
        def create_pdf(**kwargs):
            pdf_path = Path(kwargs['path'])
            pdf_path.write_bytes(b'%PDF-1.4 fake pdf content')

        mock_page.pdf = create_pdf

        result = convert_html_to_pdf(str(html_file))

        assert result == 0
        expected_pdf = temp_dir / "test.pdf"
        assert expected_pdf.exists()

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_chromium_not_installed(self, mock_playwright, temp_dir, sample_html):
        """Test quand Chromium n'est pas installé."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright pour simuler l'erreur
        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(
            side_effect=Exception("Executable doesn't exist")
        )

        mock_playwright.return_value = mock_playwright_ctx

        result = convert_html_to_pdf(str(html_file))

        assert result == 1

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_conversion_error(self, mock_playwright, temp_dir, sample_html):
        """Test gestion d'une erreur lors de la conversion."""
        html_file = temp_dir / "test.html"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright pour simuler une erreur
        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(
            side_effect=Exception("Conversion error")
        )

        mock_playwright.return_value = mock_playwright_ctx

        result = convert_html_to_pdf(str(html_file))

        assert result == 1

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_verbose_mode(self, mock_playwright, temp_dir, sample_html):
        """Test mode verbeux."""
        html_file = temp_dir / "test.html"
        pdf_file = temp_dir / "test.pdf"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(return_value=mock_playwright_ctx)
        mock_playwright_ctx.__exit__ = MagicMock(return_value=None)
        mock_playwright_ctx.chromium.launch.return_value = mock_browser

        mock_playwright.return_value = mock_playwright_ctx

        # Simulate PDF creation
        def create_pdf(**kwargs):
            pdf_path = Path(kwargs['path'])
            pdf_path.write_bytes(b'%PDF-1.4 fake pdf content')

        mock_page.pdf = create_pdf

        result = convert_html_to_pdf(
            str(html_file),
            str(pdf_file),
            verbose=True
        )

        assert result == 0

    @patch('dyag.commands.html2pdf.PLAYWRIGHT_AVAILABLE', True)
    @patch('dyag.commands.html2pdf.sync_playwright')
    def test_pdf_options_configuration(self, mock_playwright, temp_dir, sample_html):
        """Test que les options PDF sont correctement configurées."""
        html_file = temp_dir / "test.html"
        pdf_file = temp_dir / "test.pdf"
        html_file.write_text(sample_html, encoding='utf-8')

        # Mock Playwright
        mock_page = MagicMock()
        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_playwright_ctx = MagicMock()
        mock_playwright_ctx.__enter__ = MagicMock(return_value=mock_playwright_ctx)
        mock_playwright_ctx.__exit__ = MagicMock(return_value=None)
        mock_playwright_ctx.chromium.launch.return_value = mock_browser

        mock_playwright.return_value = mock_playwright_ctx

        # Capture PDF options
        captured_options = {}

        def create_pdf(**kwargs):
            captured_options.update(kwargs)
            pdf_path = Path(kwargs['path'])
            pdf_path.write_bytes(b'%PDF-1.4 fake pdf content')

        mock_page.pdf = create_pdf

        result = convert_html_to_pdf(
            str(html_file),
            str(pdf_file)
        )

        assert result == 0
        assert captured_options['format'] == 'A4'
        assert captured_options['print_background'] is True
        assert 'margin' in captured_options
        assert captured_options['margin']['top'] == '20mm'
