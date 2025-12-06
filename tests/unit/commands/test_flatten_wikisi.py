"""
Tests unitaires pour le module flatten_wikisi.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from dyag.commands.flatten_wikisi import (
    sanitize_filename,
    flatten_path,
    collect_index_files,
    check_duplicates,
    flatten_wikisi_directory
)


class TestSanitizeFilename:
    """Tests pour la fonction sanitize_filename."""

    def test_normal_name(self):
        """Test avec un nom normal."""
        assert sanitize_filename("agent") == "agent"
        assert sanitize_filename("api") == "api"
        assert sanitize_filename("donnee") == "donnee"

    def test_special_chars(self):
        """Test avec des caractères spéciaux."""
        assert sanitize_filename("api:v1") == "api_v1"
        assert sanitize_filename("data/test") == "data_test"
        assert sanitize_filename("file<>name") == "file__name"
        assert sanitize_filename("path\\to\\file") == "path_to_file"

    def test_multiple_invalid_chars(self):
        """Test avec plusieurs caractères invalides."""
        assert sanitize_filename('test"file"|name') == 'test_file__name'


class TestFlattenPath:
    """Tests pour la fonction flatten_path."""

    def test_single_level(self):
        """Test avec un niveau simple."""
        assert flatten_path(Path("agent/index.html")) == "agent.html"
        assert flatten_path(Path("api/index.html")) == "api.html"

    def test_nested_path(self):
        """Test avec un chemin imbriqué."""
        assert flatten_path(Path("api/application/index.html")) == "api-application.html"
        assert flatten_path(Path("donnee/1/historique/index.html")) == "donnee-1-historique.html"

    def test_deeply_nested(self):
        """Test avec une imbrication profonde."""
        assert flatten_path(Path("a/b/c/d/e/index.html")) == "a-b-c-d-e.html"

    def test_root_index_default(self):
        """Test avec index.html à la racine (nom par défaut)."""
        assert flatten_path(Path("index.html")) == "index.html"

    def test_root_index_custom_name(self):
        """Test avec index.html à la racine (nom personnalisé)."""
        assert flatten_path(Path("index.html"), root_name="home") == "home.html"
        assert flatten_path(Path("index.html"), root_name="main") == "main.html"

    def test_case_insensitive_index(self):
        """Test avec différentes casses pour index.html."""
        assert flatten_path(Path("agent/INDEX.HTML")) == "agent.html"
        assert flatten_path(Path("agent/Index.Html")) == "agent.html"


class TestCollectIndexFiles:
    """Tests pour la fonction collect_index_files."""

    def test_collect_simple(self):
        """Test collection avec structure simple."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Créer agent/index.html
            agent_dir = root / "agent"
            agent_dir.mkdir()
            (agent_dir / "index.html").write_text("<html>Agent</html>")

            # Collecter
            files = collect_index_files(root)

            assert len(files) == 1
            assert files[0][1] == "agent.html"

    def test_collect_nested(self):
        """Test avec structure imbriquée."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Créer api/application/index.html
            api_app = root / "api" / "application"
            api_app.mkdir(parents=True)
            (api_app / "index.html").write_text("<html>API App</html>")

            # Créer donnee/1/index.html
            donnee_1 = root / "donnee" / "1"
            donnee_1.mkdir(parents=True)
            (donnee_1 / "index.html").write_text("<html>Donnee 1</html>")

            files = collect_index_files(root)

            assert len(files) == 2
            names = {name for _, name in files}
            assert "api-application.html" in names
            assert "donnee-1.html" in names

    def test_collect_with_root_index(self):
        """Test avec index.html à la racine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Créer index.html à la racine
            (root / "index.html").write_text("<html>Root</html>")

            # Créer agent/index.html
            agent = root / "agent"
            agent.mkdir()
            (agent / "index.html").write_text("<html>Agent</html>")

            files = collect_index_files(root, root_name="main")

            assert len(files) == 2
            names = {name for _, name in files}
            assert "main.html" in names
            assert "agent.html" in names

    def test_collect_empty_directory(self):
        """Test avec répertoire vide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            files = collect_index_files(root)
            assert len(files) == 0


class TestCheckDuplicates:
    """Tests pour la fonction check_duplicates."""

    def test_no_duplicates(self):
        """Test sans doublons."""
        files = [
            (Path("/a/agent/index.html"), "agent.html"),
            (Path("/a/api/index.html"), "api.html"),
        ]
        assert check_duplicates(files) is None

    def test_with_duplicates(self):
        """Test avec doublons (cas théorique)."""
        # Note: En pratique, ceci ne devrait pas arriver avec une vraie structure wikisi
        files = [
            (Path("/a/test/index.html"), "test.html"),
            (Path("/b/test/index.html"), "test.html"),
        ]
        duplicates = check_duplicates(files)
        assert duplicates is not None
        assert "test.html" in duplicates
        assert len(duplicates["test.html"]) == 2


class TestFlattenWikisiDirectory:
    """Tests pour la fonction principale."""

    def test_flatten_basic(self):
        """Test flattening basique."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            # Créer agent/index.html
            agent = wikisi / "agent"
            agent.mkdir()
            (agent / "index.html").write_text("<html>Agent Page</html>")

            # Créer api/index.html
            api = wikisi / "api"
            api.mkdir()
            (api / "index.html").write_text("<html>API Page</html>")

            # Flatten
            output = root / "output"
            result = flatten_wikisi_directory(str(wikisi), str(output))

            # Vérifications
            assert result == 0
            assert output.exists()
            assert (output / "agent.html").exists()
            assert (output / "api.html").exists()
            assert (output / "agent.html").read_text() == "<html>Agent Page</html>"

    def test_flatten_nested(self):
        """Test avec chemins imbriqués."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            # Créer structure imbriquée
            path = wikisi / "api" / "application" / "v1"
            path.mkdir(parents=True)
            (path / "index.html").write_text("<html>API v1</html>")

            # Flatten
            output = root / "flat"
            result = flatten_wikisi_directory(str(wikisi), str(output))

            assert result == 0
            assert (output / "api-application-v1.html").exists()

    def test_flatten_default_output(self):
        """Test avec répertoire de sortie par défaut."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            agent = wikisi / "agent"
            agent.mkdir()
            (agent / "index.html").write_text("<html>Agent</html>")

            # Sans spécifier output, devrait créer wikisi-flat
            result = flatten_wikisi_directory(str(wikisi))

            assert result == 0
            expected_output = root / "wikisi-flat"
            assert expected_output.exists()
            assert (expected_output / "agent.html").exists()

    def test_flatten_with_root_name(self):
        """Test avec nom personnalisé pour la racine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            (wikisi / "index.html").write_text("<html>Home</html>")

            output = root / "flat"
            result = flatten_wikisi_directory(
                str(wikisi),
                str(output),
                root_name="home"
            )

            assert result == 0
            assert (output / "home.html").exists()

    def test_flatten_output_exists_no_update(self):
        """Test avec répertoire de sortie existant sans -u."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            agent = wikisi / "agent"
            agent.mkdir()
            (agent / "index.html").write_text("<html>Agent</html>")

            output = root / "flat"
            output.mkdir()

            # Sans update=True, devrait échouer
            result = flatten_wikisi_directory(str(wikisi), str(output), update=False)

            assert result == 1

    def test_flatten_output_exists_with_update(self):
        """Test avec répertoire de sortie existant avec -u."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            agent = wikisi / "agent"
            agent.mkdir()
            (agent / "index.html").write_text("<html>Agent New</html>")

            output = root / "flat"
            output.mkdir()
            # Créer un ancien fichier
            (output / "old.html").write_text("<html>Old</html>")

            # Avec update=True, devrait réussir
            result = flatten_wikisi_directory(str(wikisi), str(output), update=True)

            assert result == 0
            assert (output / "agent.html").exists()
            assert (output / "old.html").exists()  # L'ancien fichier reste

    def test_flatten_no_index_files(self):
        """Test avec répertoire sans index.html."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            # Créer d'autres fichiers mais pas index.html
            (wikisi / "readme.txt").write_text("README")

            output = root / "flat"
            result = flatten_wikisi_directory(str(wikisi), str(output))

            # Devrait retourner 1 (erreur)
            assert result == 1

    def test_flatten_nonexistent_directory(self):
        """Test avec répertoire inexistant."""
        result = flatten_wikisi_directory("/path/that/does/not/exist")
        assert result == 1

    def test_flatten_not_a_directory(self):
        """Test avec un fichier au lieu d'un répertoire."""
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile_path = tmpfile.name

        try:
            result = flatten_wikisi_directory(tmpfile_path)
            assert result == 1
        finally:
            try:
                Path(tmpfile_path).unlink()
            except (PermissionError, FileNotFoundError):
                pass  # Ignore cleanup errors on Windows

    def test_flatten_preserves_content(self):
        """Test que le contenu est préservé à l'identique."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            content = "<html><body><h1>Test Content</h1><p>Lorem ipsum</p></body></html>"

            agent = wikisi / "agent"
            agent.mkdir()
            (agent / "index.html").write_text(content, encoding="utf-8")

            output = root / "flat"
            result = flatten_wikisi_directory(str(wikisi), str(output))

            assert result == 0
            flattened_content = (output / "agent.html").read_text(encoding="utf-8")
            assert flattened_content == content

    def test_flatten_multiple_levels(self):
        """Test avec plusieurs niveaux de répertoires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            wikisi = root / "wikisi"
            wikisi.mkdir()

            # Créer plusieurs fichiers à différents niveaux
            (wikisi / "index.html").write_text("<html>Root</html>")

            agent = wikisi / "agent"
            agent.mkdir()
            (agent / "index.html").write_text("<html>Agent</html>")

            api_app = wikisi / "api" / "application"
            api_app.mkdir(parents=True)
            (api_app / "index.html").write_text("<html>API App</html>")

            donnee_hist = wikisi / "donnee" / "1" / "historique"
            donnee_hist.mkdir(parents=True)
            (donnee_hist / "index.html").write_text("<html>Donnee Hist</html>")

            output = root / "flat"
            result = flatten_wikisi_directory(str(wikisi), str(output), root_name="wikisi")

            assert result == 0
            assert (output / "wikisi.html").exists()
            assert (output / "agent.html").exists()
            assert (output / "api-application.html").exists()
            assert (output / "donnee-1-historique.html").exists()

            # Vérifier le nombre total de fichiers
            html_files = list(output.glob("*.html"))
            assert len(html_files) == 4
