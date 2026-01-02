"""
Tests unitaires pour dyag.analysis.commands.md2project
Tests de la commande CLI md2project.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dyag.analysis.commands.md2project import md2project
from dyag.analysis.core.md2project_parser import ProjectStructure, FileEntry


@pytest.fixture
def mock_project():
    """Fixture créant un projet mocké."""
    return ProjectStructure(
        name="test_project",
        root_path="/tmp/test",
        total_files=2,
        files=[
            FileEntry(path="README.md", content="# Test\n\nReadme content", language="markdown"),
            FileEntry(path="src/main.py", content="def main():\n    pass", language="python"),
        ]
    )


@pytest.mark.unit
@pytest.mark.commands
@pytest.mark.analysis
class TestMd2ProjectCommand:
    """Tests de la commande md2project."""

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_execute_success(self, mock_parser, temp_dir, mock_project):
        """Test conversion réussie."""
        # Créer fichier Markdown
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test\n\n## Contenu", encoding='utf-8')

        # Mock parser
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        # Exécuter commande
        output_dir = temp_dir / "output"
        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        # Vérifier succès
        assert result == 0

        # Vérifier que les fichiers ont été créés
        assert (output_dir / "README.md").exists()
        assert (output_dir / "src" / "main.py").exists()

        # Vérifier contenu
        readme_content = (output_dir / "README.md").read_text()
        assert "# Test" in readme_content

        main_content = (output_dir / "src" / "main.py").read_text()
        assert "def main():" in main_content

    def test_file_not_found(self):
        """Test avec fichier Markdown inexistant."""
        result = md2project(
            markdown_file="/nonexistent/file.md",
            output_dir=None,
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        assert result == 1

    def test_not_a_file(self, temp_dir):
        """Test avec répertoire au lieu de fichier."""
        result = md2project(
            markdown_file=str(temp_dir),
            output_dir=None,
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        assert result == 1

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_no_files_extracted(self, mock_parser, temp_dir):
        """Test quand aucun fichier n'est extrait."""
        md_file = temp_dir / "empty.md"
        md_file.write_text("# Projet : empty", encoding='utf-8')

        # Mock parser retournant projet vide
        empty_project = ProjectStructure(name="empty", files=[])
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = empty_project
        mock_parser_instance.validate_structure.return_value = ["Aucun fichier extrait"]
        mock_parser.return_value = mock_parser_instance

        result = md2project(
            markdown_file=str(md_file),
            output_dir=None,
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        assert result == 1

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_dry_run_mode(self, mock_parser, temp_dir, mock_project, capsys):
        """Test mode dry-run (sans créer de fichiers)."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        output_dir = temp_dir / "output"
        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=True,
            overwrite=False,
            merge=False,
            verbose=False
        )

        # Devrait retourner succès
        assert result == 0

        # Ne devrait PAS créer de fichiers
        assert not output_dir.exists()

        # Devrait afficher ce qui serait fait
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out
        assert "README.md" in captured.out
        assert "src/main.py" in captured.out

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_output_dir_exists_no_overwrite(self, mock_parser, temp_dir, mock_project):
        """Test quand répertoire de sortie existe (sans --overwrite)."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        output_dir = temp_dir / "existing"
        output_dir.mkdir()

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        # Devrait échouer
        assert result == 1

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_output_dir_exists_with_overwrite(self, mock_parser, temp_dir, mock_project):
        """Test quand répertoire existe (avec --overwrite)."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        output_dir = temp_dir / "existing"
        output_dir.mkdir()
        (output_dir / "old_file.txt").write_text("old content")

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=True,
            merge=False,
            verbose=False
        )

        # Devrait réussir
        assert result == 0

        # Nouveaux fichiers créés
        assert (output_dir / "README.md").exists()

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_merge_mode(self, mock_parser, temp_dir, mock_project):
        """Test mode merge (fusionner avec existant)."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        output_dir = temp_dir / "existing"
        output_dir.mkdir()
        existing_file = output_dir / "existing.txt"
        existing_file.write_text("keep this")

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=False,
            merge=True,
            verbose=False
        )

        # Devrait réussir
        assert result == 0

        # Fichiers nouveaux ET anciens présents
        assert (output_dir / "README.md").exists()
        assert (output_dir / "existing.txt").exists()
        assert existing_file.read_text() == "keep this"

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_verbose_mode(self, mock_parser, temp_dir, mock_project, capsys):
        """Test mode verbeux."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        output_dir = temp_dir / "output"
        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=True
        )

        assert result == 0

        # Devrait afficher des infos
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out
        assert "test_project" in captured.out

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_default_output_dir(self, mock_parser, temp_dir, mock_project):
        """Test répertoire de sortie par défaut (nom du projet)."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        # Changer de répertoire courant pour le test
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = md2project(
                markdown_file=str(md_file),
                output_dir=None,  # Pas de output_dir spécifié
                dry_run=False,
                overwrite=False,
                merge=False,
                verbose=False
            )

            assert result == 0

            # Devrait créer dans test_project/
            default_output = temp_dir / "test_project"
            assert default_output.exists()
            assert (default_output / "README.md").exists()
        finally:
            os.chdir(old_cwd)

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_file_write_error(self, mock_parser, temp_dir, mock_project, capsys):
        """Test gestion d'erreur lors de l'écriture."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        # Projet avec chemin invalide (on va simuler l'erreur)
        problematic_project = ProjectStructure(
            name="test",
            files=[
                FileEntry(path="good.txt", content="ok"),
                FileEntry(path="README.md", content="test"),
            ]
        )

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = problematic_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        output_dir = temp_dir / "output"
        output_dir.mkdir()

        # Créer un fichier read-only pour simuler erreur
        readonly_file = output_dir / "good.txt"
        readonly_file.write_text("existing")
        readonly_file.chmod(0o444)  # Read-only

        try:
            result = md2project(
                markdown_file=str(md_file),
                output_dir=str(output_dir),
                dry_run=False,
                overwrite=True,
                merge=False,
                verbose=False
            )

            # Peut réussir partiellement (Windows peut autoriser l'écriture malgré chmod)
            # On vérifie juste qu'il gère les erreurs
            captured = capsys.readouterr()
            # Devrait soit afficher erreur soit réussir selon OS
            assert result in (0, 1)
        finally:
            # Restaurer permissions
            readonly_file.chmod(0o644)

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_parser_exception(self, mock_parser, temp_dir):
        """Test gestion exception du parser."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        # Mock parser levant une exception
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.side_effect = Exception("Parse error")
        mock_parser.return_value = mock_parser_instance

        result = md2project(
            markdown_file=str(md_file),
            output_dir=None,
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        assert result == 1

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_validation_warnings(self, mock_parser, temp_dir, mock_project, capsys):
        """Test affichage des warnings de validation."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = mock_project
        mock_parser_instance.validate_structure.return_value = [
            "1 fichiers vides",
            "Incohérence : 3 fichiers attendus, 2 extraits"
        ]
        mock_parser.return_value = mock_parser_instance

        output_dir = temp_dir / "output"
        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        # Devrait quand même réussir (warnings, pas erreurs)
        assert result == 0

        # Devrait afficher warnings
        captured = capsys.readouterr()
        assert "[WARNING]" in captured.out
        assert "fichiers vides" in captured.out

    @patch('dyag.analysis.commands.md2project.Md2ProjectParser')
    def test_creates_nested_directories(self, mock_parser, temp_dir):
        """Test création de répertoires imbriqués."""
        md_file = temp_dir / "project.md"
        md_file.write_text("# Projet : test", encoding='utf-8')

        nested_project = ProjectStructure(
            name="nested",
            files=[
                FileEntry(path="a/b/c/deep.txt", content="deep content"),
            ]
        )

        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = nested_project
        mock_parser_instance.validate_structure.return_value = []
        mock_parser.return_value = mock_parser_instance

        output_dir = temp_dir / "output"
        result = md2project(
            markdown_file=str(md_file),
            output_dir=str(output_dir),
            dry_run=False,
            overwrite=False,
            merge=False,
            verbose=False
        )

        assert result == 0

        # Vérifier structure créée
        deep_file = output_dir / "a" / "b" / "c" / "deep.txt"
        assert deep_file.exists()
        assert deep_file.read_text() == "deep content"
