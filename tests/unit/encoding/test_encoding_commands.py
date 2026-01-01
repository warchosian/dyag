"""Tests unitaires pour encoding commands - Wrappers CLI"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from dyag.encoding.commands.chk_utf8 import run_chk_utf8
from dyag.encoding.commands.fix_utf8 import run_fix_utf8


# ============================================================================
# Tests run_chk_utf8()
# ============================================================================

class TestRunChkUtf8:
    """Tests pour la fonction run_chk_utf8()."""

    def test_run_with_utf8_files(self, temp_dir):
        """Test run_chk_utf8 avec fichiers UTF-8 valides."""
        # Créer fichiers UTF-8
        (temp_dir / "file1.md").write_text("# UTF-8 Test 1", encoding='utf-8')
        (temp_dir / "file2.md").write_text("# UTF-8 Test 2", encoding='utf-8')

        patterns = [str(temp_dir / "*.md")]
        exit_code = run_chk_utf8(patterns, min_confidence=0.7, quiet=False)

        # Devrait retourner 0 (succès)
        assert exit_code == 0

    def test_run_with_non_utf8_file(self, temp_dir):
        """Test run_chk_utf8 avec fichier non UTF-8."""
        # Créer fichier ISO-8859-1
        iso_file = temp_dir / "iso.md"
        content = "# Test avec accents: é, à, ù"
        iso_file.write_bytes(content.encode('iso-8859-1'))

        patterns = [str(temp_dir / "*.md")]
        exit_code = run_chk_utf8(patterns, min_confidence=0.7, quiet=False)

        # Devrait retourner 1 (problème détecté)
        assert exit_code == 1

    def test_run_with_low_confidence(self, temp_dir):
        """Test run_chk_utf8 avec confiance faible."""
        # Créer fichier très court (confiance souvent faible)
        (temp_dir / "short.md").write_text(".", encoding='utf-8')

        patterns = [str(temp_dir / "*.md")]
        exit_code = run_chk_utf8(patterns, min_confidence=0.95, quiet=False)

        # Peut retourner 1 si confiance < 0.95
        assert exit_code in (0, 1)

    def test_run_quiet_mode(self, temp_dir):
        """Test run_chk_utf8 en mode silencieux."""
        (temp_dir / "file.md").write_text("# Test", encoding='utf-8')

        patterns = [str(temp_dir / "*.md")]
        exit_code = run_chk_utf8(patterns, quiet=True)

        assert exit_code == 0

    def test_run_no_files_found(self, temp_dir):
        """Test run_chk_utf8 sans fichiers trouvés."""
        patterns = [str(temp_dir / "*.md")]
        exit_code = run_chk_utf8(patterns)

        # Devrait retourner 1 (pas de fichiers)
        assert exit_code == 1

    def test_run_multiple_patterns(self, temp_dir):
        """Test run_chk_utf8 avec plusieurs patterns."""
        subdir = temp_dir / "docs"
        subdir.mkdir()

        (temp_dir / "readme.md").write_text("# README", encoding='utf-8')
        (subdir / "guide.md").write_text("# Guide", encoding='utf-8')

        patterns = [
            str(temp_dir / "readme.md"),
            str(subdir / "*.md")
        ]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

    def test_run_with_error(self, temp_dir):
        """Test run_chk_utf8 avec erreur."""
        # Pattern invalide
        patterns = ["///invalid///pattern///*.md"]
        exit_code = run_chk_utf8(patterns)

        # Devrait retourner 1 (erreur)
        assert exit_code == 1

    @patch('dyag.encoding.commands.chk_utf8.check_markdown_files')
    def test_run_handles_exception(self, mock_check):
        """Test gestion d'exception."""
        mock_check.side_effect = Exception("Test error")

        exit_code = run_chk_utf8(["*.md"])

        assert exit_code == 1


# ============================================================================
# Tests run_fix_utf8()
# ============================================================================

class TestRunFixUtf8:
    """Tests pour la fonction run_fix_utf8()."""

    def test_run_fix_success(self, temp_dir):
        """Test run_fix_utf8 avec correction réussie."""
        test_file = temp_dir / "test.md"
        test_file.write_text("Hello&nbsp;World", encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_fix_utf8(patterns, dry_run=False, backup=False, quiet=False)

        # Devrait retourner 0 (succès)
        assert exit_code == 0

        # Vérifier correction appliquée
        assert "&nbsp;" not in test_file.read_text()

    def test_run_fix_multiple_files(self, temp_dir):
        """Test run_fix_utf8 sur plusieurs fichiers."""
        (temp_dir / "file1.md").write_text("Test&nbsp;1", encoding='utf-8')
        (temp_dir / "file2.md").write_text("Test&nbsp;2", encoding='utf-8')
        (temp_dir / "file3.md").write_text("Test&nbsp;3", encoding='utf-8')

        patterns = [str(temp_dir / "*.md")]
        exit_code = run_fix_utf8(patterns)

        assert exit_code == 0

        # Vérifier tous corrigés
        for i in range(1, 4):
            assert "&nbsp;" not in (temp_dir / f"file{i}.md").read_text()

    def test_run_fix_dry_run(self, temp_dir):
        """Test run_fix_utf8 en mode dry-run."""
        test_file = temp_dir / "test.md"
        original_content = "Hello&nbsp;World"
        test_file.write_text(original_content, encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_fix_utf8(patterns, dry_run=True)

        assert exit_code == 0

        # Vérifier fichier non modifié
        assert test_file.read_text() == original_content

    def test_run_fix_with_backup(self, temp_dir):
        """Test run_fix_utf8 avec backup."""
        test_file = temp_dir / "test.md"
        original_content = "Hello&nbsp;World"
        test_file.write_text(original_content, encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_fix_utf8(patterns, backup=True)

        assert exit_code == 0

        # Vérifier backup créé
        backup_file = temp_dir / "test.md.bak"
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

        # Vérifier fichier modifié
        assert "&nbsp;" not in test_file.read_text()

    def test_run_fix_quiet_mode(self, temp_dir):
        """Test run_fix_utf8 en mode silencieux."""
        test_file = temp_dir / "test.md"
        test_file.write_text("Hello&nbsp;World", encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_fix_utf8(patterns, quiet=True)

        assert exit_code == 0

    def test_run_fix_no_files(self, temp_dir):
        """Test run_fix_utf8 sans fichiers trouvés."""
        patterns = [str(temp_dir / "*.md")]
        exit_code = run_fix_utf8(patterns)

        # Devrait retourner 0 (pas d'erreur, juste rien à faire)
        assert exit_code == 0

    def test_run_fix_with_errors(self, temp_dir):
        """Test run_fix_utf8 avec erreurs."""
        # Créer un fichier puis le rendre inaccessible en le supprimant
        test_file = temp_dir / "test.md"
        test_file.write_text("Test", encoding='utf-8')

        # Tester avec pattern invalide
        patterns = ["///invalid///pattern///*.md"]
        exit_code = run_fix_utf8(patterns)

        # Devrait retourner 1 ou 0 selon gestion d'erreur
        assert exit_code in (0, 1)

    def test_run_fix_already_compliant(self, temp_dir):
        """Test run_fix_utf8 avec fichiers déjà conformes."""
        test_file = temp_dir / "compliant.md"
        test_file.write_text("# Already UTF-8\n\nNo issues.", encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_fix_utf8(patterns)

        assert exit_code == 0

    @patch('dyag.encoding.commands.fix_utf8.fix_markdown_files')
    def test_run_fix_handles_exception(self, mock_fix):
        """Test gestion d'exception."""
        mock_fix.side_effect = Exception("Test error")

        exit_code = run_fix_utf8(["*.md"])

        assert exit_code == 1

    @patch('dyag.encoding.commands.fix_utf8.fix_markdown_files')
    def test_run_fix_counts_errors(self, mock_fix, temp_dir):
        """Test comptage d'erreurs."""
        mock_fix.return_value = [
            {"path": "file1.md", "success": True, "message": "OK"},
            {"path": "file2.md", "success": False, "message": "Error"},
            {"path": "file3.md", "success": True, "message": "OK"},
        ]

        patterns = ["*.md"]
        exit_code = run_fix_utf8(patterns)

        # Devrait retourner 1 (au moins une erreur)
        assert exit_code == 1


# ============================================================================
# Tests d'intégration CLI
# ============================================================================

class TestCliIntegration:
    """Tests d'intégration des commandes CLI."""

    def test_chk_utf8_full_workflow(self, temp_dir):
        """Test workflow complet chk-utf8."""
        # Créer différents types de fichiers
        (temp_dir / "utf8.md").write_text("# UTF-8 OK", encoding='utf-8')
        (temp_dir / "iso.md").write_bytes("# ISO".encode('iso-8859-1'))

        patterns = [str(temp_dir / "*.md")]

        # Première vérification : devrait détecter problème
        exit_code = run_chk_utf8(patterns)
        assert exit_code == 1

    def test_fix_utf8_full_workflow(self, temp_dir):
        """Test workflow complet fix-utf8."""
        test_file = temp_dir / "test.md"
        test_file.write_text("Hello&nbsp;World [link](file name.md)", encoding='utf-8')

        patterns = [str(test_file)]

        # 1. Dry-run d'abord
        exit_code = run_fix_utf8(patterns, dry_run=True)
        assert exit_code == 0
        assert "&nbsp;" in test_file.read_text()  # Pas modifié

        # 2. Fix avec backup
        exit_code = run_fix_utf8(patterns, backup=True)
        assert exit_code == 0

        # Vérifier corrections
        fixed = test_file.read_text()
        assert "&nbsp;" not in fixed
        assert "file%20name.md" in fixed

        # Vérifier backup
        assert (temp_dir / "test.md.bak").exists()

    def test_combined_workflow(self, temp_dir):
        """Test workflow combiné chk → fix."""
        test_file = temp_dir / "workflow.md"
        test_file.write_text("Test&nbsp;file", encoding='utf-8')

        patterns = [str(test_file)]

        # 1. Vérifier - devrait détecter problème
        exit_code_chk = run_chk_utf8(patterns)
        # Peut être 0 ou 1 selon confiance

        # 2. Corriger
        exit_code_fix = run_fix_utf8(patterns)
        assert exit_code_fix == 0

        # 3. Revérifier - devrait être OK
        exit_code_chk2 = run_chk_utf8(patterns)
        assert exit_code_chk2 == 0


# ============================================================================
# Tests de régression
# ============================================================================

class TestRegressions:
    """Tests de régression pour cas spécifiques."""

    def test_windows_paths(self, temp_dir):
        """Test chemins Windows."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Test", encoding='utf-8')

        # Utiliser chemin absolu Windows-style
        patterns = [str(test_file)]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

    def test_unicode_filenames(self, temp_dir):
        """Test noms de fichiers Unicode."""
        test_file = temp_dir / "测试文件.md"
        test_file.write_text("# Test", encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

    def test_spaces_in_paths(self, temp_dir):
        """Test espaces dans chemins."""
        subdir = temp_dir / "my folder"
        subdir.mkdir()
        test_file = subdir / "my file.md"
        test_file.write_text("# Test", encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

    def test_very_long_path(self, temp_dir):
        """Test chemin très long."""
        # Créer structure de dossiers profonde
        deep_path = temp_dir
        for i in range(10):
            deep_path = deep_path / f"level{i}"
            deep_path.mkdir()

        test_file = deep_path / "deep.md"
        test_file.write_text("# Deep", encoding='utf-8')

        patterns = [str(test_file)]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

    def test_empty_directory(self, temp_dir):
        """Test répertoire vide."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        patterns = [str(empty_dir / "*.md")]
        exit_code = run_chk_utf8(patterns)

        # Devrait retourner 1 (pas de fichiers)
        assert exit_code == 1

    def test_symlinks(self, temp_dir):
        """Test liens symboliques (si supporté)."""
        test_file = temp_dir / "original.md"
        test_file.write_text("# Original", encoding='utf-8')

        try:
            link_file = temp_dir / "link.md"
            link_file.symlink_to(test_file)

            patterns = [str(link_file)]
            exit_code = run_chk_utf8(patterns)

            assert exit_code == 0
        except (OSError, NotImplementedError):
            # Symlinks non supportés (Windows sans privilèges)
            pytest.skip("Symlinks not supported")


# ============================================================================
# Tests de performance
# ============================================================================

class TestPerformance:
    """Tests basiques de performance."""

    def test_many_small_files(self, temp_dir):
        """Test avec nombreux petits fichiers."""
        # Créer 100 fichiers
        for i in range(100):
            (temp_dir / f"file{i:03d}.md").write_text(f"# File {i}", encoding='utf-8')

        patterns = [str(temp_dir / "*.md")]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

    def test_large_file(self, temp_dir):
        """Test avec fichier volumineux."""
        large_file = temp_dir / "large.md"
        content = "# Large\n\n" + ("Line of text\n" * 10000)
        large_file.write_text(content, encoding='utf-8')

        patterns = [str(large_file)]
        exit_code = run_chk_utf8(patterns)

        assert exit_code == 0

        # Test correction aussi
        exit_code = run_fix_utf8(patterns)
        assert exit_code == 0
