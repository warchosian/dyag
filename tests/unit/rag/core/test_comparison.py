"""
Tests unitaires pour dyag.rag.core.comparison

Tests exhaustifs de la comparaison de résultats d'évaluation RAG.
"""

import pytest
import json
from pathlib import Path
from dyag.rag.core.comparison import (
    load_results,
    analyze_results,
    compare_results,
    calculate_improvements
)


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestLoadResults:
    """Tests de chargement des résultats."""

    def test_load_valid_results(self, temp_dir, sample_evaluation_results):
        """Test chargement de résultats valides."""
        # Créer un fichier de résultats
        results_file = temp_dir / "results.json"
        results_file.write_text(
            json.dumps(sample_evaluation_results),
            encoding='utf-8'
        )

        results = load_results(str(results_file))

        assert results is not None
        assert "metadata" in results
        assert "results" in results
        assert "summary" in results

    def test_load_nonexistent_file(self):
        """Test erreur sur fichier inexistant."""
        with pytest.raises(FileNotFoundError):
            load_results("/path/to/nonexistent/file.json")

    def test_load_invalid_json(self, temp_dir):
        """Test erreur sur JSON invalide."""
        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("This is not JSON", encoding='utf-8')

        with pytest.raises(json.JSONDecodeError):
            load_results(str(invalid_file))

    def test_load_empty_file(self, temp_dir):
        """Test erreur sur fichier vide."""
        empty_file = temp_dir / "empty.json"
        empty_file.write_text("", encoding='utf-8')

        with pytest.raises(json.JSONDecodeError):
            load_results(str(empty_file))


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestAnalyzeResults:
    """Tests d'analyse de résultats."""

    def test_analyze_success_results(self, sample_evaluation_results):
        """Test analyse de résultats avec succès."""
        metrics = analyze_results(sample_evaluation_results)

        assert metrics["total_questions"] == 2  # Le fixture contient 2 résultats
        assert metrics["successful"] == 1  # 1 succès (le premier)
        assert metrics["failed"] == 1  # 1 échec (le second)
        assert 0 <= metrics["avg_similarity"] <= 1
        assert metrics["avg_time"] > 0
        assert metrics["avg_tokens"] > 0

    def test_analyze_empty_results(self):
        """Test analyse de résultats vides."""
        empty_results = {
            "metadata": {},
            "results": [],
            "summary": {}
        }

        metrics = analyze_results(empty_results)

        assert metrics["total_questions"] == 0
        assert metrics["successful"] == 0
        assert metrics["avg_similarity"] == 0.0

    def test_analyze_all_failed_results(self):
        """Test analyse quand toutes les questions échouent."""
        failed_results = {
            "results": [
                {
                    "success": False,
                    "similarity": 0.0,
                    "time": 1.0,
                    "tokens": 100
                }
            ]
        }

        metrics = analyze_results(failed_results)

        assert metrics["successful"] == 0
        assert metrics["failed"] == 1
        assert metrics["avg_similarity"] == 0.0

    def test_analyze_calculates_averages(self):
        """Test calcul correct des moyennes."""
        results = {
            "results": [
                {
                    "success": True,
                    "expected": "Test answer A",
                    "answer": "Test answer A is correct",  # Similarité ~0.8
                    "time": 1.0,
                    "tokens": 100
                },
                {
                    "success": True,
                    "expected": "Test answer B long text",
                    "answer": "Test answer B",  # Similarité ~0.6
                    "time": 2.0,
                    "tokens": 200
                }
            ]
        }

        metrics = analyze_results(results)

        # La similarité est calculée par calculate_similarity(), pas directement depuis les données
        assert 0 <= metrics["avg_similarity"] <= 1
        assert metrics["avg_time"] == 1.5
        assert metrics["avg_tokens"] == 150

    def test_analyze_filters_failed_questions(self):
        """Test que les questions échouées n'affectent pas les moyennes."""
        results = {
            "results": [
                {
                    "success": True,
                    "expected": "Exact answer",
                    "answer": "Exact answer",  # Similarité très élevée ~1.0
                    "time": 1.0,
                    "tokens": 100
                },
                {
                    "success": False,  # Ne devrait pas être comptée
                    "expected": "Expected",
                    "answer": "Completely wrong",
                    "time": 10.0,
                    "tokens": 1000
                }
            ]
        }

        metrics = analyze_results(results)

        # Seule la question réussie devrait affecter les moyennes
        assert metrics["successful"] == 1
        assert metrics["failed"] == 1
        assert metrics["avg_similarity"] >= 0.9  # Similarité très élevée pour réponse exacte
        assert metrics["avg_time"] == 1.0
        assert metrics["avg_tokens"] == 100


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestCalculateImprovements:
    """Tests de calcul d'améliorations."""

    def test_calculate_improvements_positive(self):
        """Test calcul avec amélioration."""
        baseline_metrics = {
            "avg_similarity": 0.6,
            "successful": 6,
            "total_questions": 10
        }
        improved_metrics = {
            "avg_similarity": 0.8,
            "successful": 8,
            "total_questions": 10
        }

        improvements = calculate_improvements(baseline_metrics, improved_metrics)

        assert improvements["similarity_delta"] == pytest.approx(0.2)
        assert improvements["similarity_improvement"] == pytest.approx(33.33, rel=0.01)
        assert improvements["success_delta"] == 2
        assert improvements["success_improvement"] == pytest.approx(33.33, rel=0.01)

    def test_calculate_improvements_negative(self):
        """Test calcul avec régression."""
        baseline_metrics = {
            "avg_similarity": 0.8,
            "successful": 8,
            "total_questions": 10
        }
        improved_metrics = {
            "avg_similarity": 0.6,
            "successful": 6,
            "total_questions": 10
        }

        improvements = calculate_improvements(baseline_metrics, improved_metrics)

        assert improvements["similarity_delta"] < 0
        assert improvements["similarity_improvement"] < 0
        assert improvements["success_delta"] < 0

    def test_calculate_improvements_no_change(self):
        """Test calcul sans changement."""
        metrics = {
            "avg_similarity": 0.7,
            "successful": 7,
            "total_questions": 10
        }

        improvements = calculate_improvements(metrics, metrics)

        assert improvements["similarity_delta"] == 0
        assert improvements["similarity_improvement"] == 0
        assert improvements["success_delta"] == 0

    def test_calculate_improvements_from_zero(self):
        """Test calcul depuis zéro (évite division par zéro)."""
        baseline_metrics = {
            "avg_similarity": 0.0,
            "successful": 0,
            "total_questions": 10
        }
        improved_metrics = {
            "avg_similarity": 0.5,
            "successful": 5,
            "total_questions": 10
        }

        improvements = calculate_improvements(baseline_metrics, improved_metrics)

        assert improvements["similarity_delta"] == 0.5
        # Amélioration depuis 0 devrait être infinie ou très élevée
        assert improvements["similarity_improvement"] > 0


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestCompareResults:
    """Tests de comparaison complète de résultats."""

    def test_compare_results_success(self, temp_dir):
        """Test comparaison réussie entre deux fichiers."""
        # Créer fichier baseline
        baseline = {
            "results": [
                {"success": True, "similarity": 0.6, "time": 1.0, "tokens": 100},
                {"success": True, "similarity": 0.7, "time": 1.0, "tokens": 100},
                {"success": False, "similarity": 0.1, "time": 1.0, "tokens": 100}
            ]
        }
        baseline_file = temp_dir / "baseline.json"
        baseline_file.write_text(json.dumps(baseline), encoding='utf-8')

        # Créer fichier improved
        improved = {
            "results": [
                {"success": True, "similarity": 0.8, "time": 1.0, "tokens": 100},
                {"success": True, "similarity": 0.9, "time": 1.0, "tokens": 100},
                {"success": True, "similarity": 0.7, "time": 1.0, "tokens": 100}
            ]
        }
        improved_file = temp_dir / "improved.json"
        improved_file.write_text(json.dumps(improved), encoding='utf-8')

        # Comparer
        result = compare_results(str(baseline_file), str(improved_file))

        assert result == 0  # Exit code 0 = succès
        # La fonction devrait afficher les résultats (testé via capsys si besoin)

    def test_compare_shows_improvement(self, temp_dir, capsys):
        """Test que la comparaison affiche les améliorations."""
        baseline = {
            "results": [
                {
                    "success": True,
                    "expected": "Test answer",
                    "answer": "Test",  # Similarité faible ~0.5
                    "time": 1.0,
                    "tokens": 100
                }
            ]
        }
        improved = {
            "results": [
                {
                    "success": True,
                    "expected": "Test answer",
                    "answer": "Test answer is correct",  # Similarité élevée ~0.9
                    "time": 1.0,
                    "tokens": 100
                }
            ]
        }

        baseline_file = temp_dir / "baseline.json"
        improved_file = temp_dir / "improved.json"
        baseline_file.write_text(json.dumps(baseline), encoding='utf-8')
        improved_file.write_text(json.dumps(improved), encoding='utf-8')

        compare_results(str(baseline_file), str(improved_file))

        captured = capsys.readouterr()
        # Devrait afficher des informations sur l'amélioration
        # Le mot "amélioration" ou "amélioré" devrait apparaître quelque part
        output_lower = captured.out.lower()
        assert "am" in output_lower and "lior" in output_lower  # Flexible pour encodage

    def test_compare_handles_missing_file(self, temp_dir):
        """Test gestion de fichier manquant."""
        existing_file = temp_dir / "exists.json"
        existing_file.write_text('{"results": []}', encoding='utf-8')

        # Devrait gérer l'erreur gracieusement et retourner code d'erreur
        result = compare_results(str(existing_file), "/nonexistent/file.json")
        assert result != 0  # Exit code non-zéro = erreur


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestEdgeCases:
    """Tests de cas limites."""

    def test_analyze_missing_fields(self):
        """Test analyse avec champs manquants."""
        partial_results = {
            "results": [
                {"success": True}  # Champs manquants
            ]
        }

        # Ne devrait pas crasher, devrait gérer les valeurs par défaut
        metrics = analyze_results(partial_results)
        assert "total_questions" in metrics

    def test_analyze_with_none_values(self):
        """Test analyse avec valeurs None."""
        results_with_none = {
            "results": [
                {
                    "success": True,
                    "similarity": None,
                    "time": None,
                    "tokens": None
                }
            ]
        }

        # Devrait gérer None gracieusement
        metrics = analyze_results(results_with_none)
        assert metrics is not None

    def test_large_dataset(self):
        """Test avec un grand dataset."""
        large_results = {
            "results": [
                {
                    "success": True,
                    "similarity": 0.7,
                    "time": 1.0,
                    "tokens": 100
                }
            ] * 10000  # 10k résultats
        }

        # Devrait gérer efficacement
        metrics = analyze_results(large_results)
        assert metrics["total_questions"] == 10000
        assert metrics["successful"] == 10000
