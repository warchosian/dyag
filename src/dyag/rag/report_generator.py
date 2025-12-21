"""
RAG Evaluation Report Generator

Generates detailed analysis reports from RAG evaluation results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from difflib import SequenceMatcher


def calculate_similarity(expected: str, obtained: str) -> float:
    """
    Calculate similarity ratio between expected and obtained answers.

    Args:
        expected: Expected answer
        obtained: Obtained answer

    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if not expected or not obtained:
        return 0.0

    # Normalize strings
    exp_lower = expected.lower().strip()
    obt_lower = obtained.lower().strip()

    # Calculate sequence similarity
    similarity = SequenceMatcher(None, exp_lower, obt_lower).ratio()

    # Bonus if expected is contained in obtained
    if exp_lower in obt_lower:
        similarity = max(similarity, 0.7)

    return similarity


def categorize_answer_quality(similarity: float, obtained: str) -> tuple[str, str]:
    """
    Categorize answer quality based on similarity and content.

    Returns:
        (status_emoji, status_text)
    """
    # Check for common failure patterns
    if any(phrase in obtained.lower() for phrase in [
        "je n'ai pas trouvé",
        "je n'ai pas d'information",
        "je ne trouve aucune",
        "je ne peux pas",
        "désolé",
        "aucune information"
    ]):
        return "❌", "Aucune information trouvée"

    if similarity >= 0.8:
        return "✅", "Réponse correcte"
    elif similarity >= 0.5:
        return "⚠️", "Réponse partielle"
    elif similarity >= 0.2:
        return "❌", "Réponse incorrecte"
    else:
        return "❌", "Réponse totalement erronée"


def analyze_chunks(results: List[Dict]) -> Dict[str, int]:
    """
    Analyze chunk distribution across questions.

    Returns:
        Dictionary of chunk_id -> frequency
    """
    chunk_freq = {}
    for result in results:
        for chunk_id in result.get("sources", []):
            chunk_freq[chunk_id] = chunk_freq.get(chunk_id, 0) + 1

    # Sort by frequency
    return dict(sorted(chunk_freq.items(), key=lambda x: x[1], reverse=True))


def generate_markdown_report(
    results_data: Dict[str, Any],
    output_path: str = None,
    verbose: bool = False
) -> str:
    """
    Generate a detailed markdown evaluation report.

    Args:
        results_data: Evaluation results from JSON
        output_path: Optional output file path
        verbose: Show detailed progress

    Returns:
        Generated markdown content
    """
    metadata = results_data.get("metadata", {})
    results = results_data.get("results", [])

    if not results:
        raise ValueError("No results found in data")

    # Calculate similarities and stats
    similarities = []
    correct_count = 0
    partial_count = 0
    incorrect_count = 0

    for result in results:
        sim = calculate_similarity(
            result.get("expected", ""),
            result.get("answer", "")
        )
        similarities.append(sim)

        if sim >= 0.8:
            correct_count += 1
        elif sim >= 0.5:
            partial_count += 1
        else:
            incorrect_count += 1

    avg_similarity = sum(similarities) / len(similarities) if similarities else 0

    # Analyze chunks
    chunk_freq = analyze_chunks(results)

    # Build report
    report = []

    # Header
    report.append("# Rapport d'Évaluation RAG\n")
    report.append(f"**Date de génération**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**Date d'évaluation**: {metadata.get('timestamp', 'N/A')}\n")
    report.append(f"**Modèle LLM**: {metadata.get('model', 'N/A')}\n")
    report.append(f"**Chunks par question**: {metadata.get('n_chunks', 'N/A')}\n")
    report.append("\n---\n\n")

    # Executive Summary
    report.append("## 📊 Résumé Exécutif\n\n")
    report.append("### Métriques Techniques\n\n")
    report.append("| Métrique | Valeur |\n")
    report.append("|----------|--------|\n")
    report.append(f"| **Questions testées** | {metadata.get('total_questions', 0)} |\n")
    report.append(f"| **Succès technique** | {metadata.get('successful', 0)}/{metadata.get('total_questions', 0)} ({metadata.get('successful', 0)/metadata.get('total_questions', 1)*100:.1f}%) |\n")
    report.append(f"| **Temps moyen** | {metadata.get('total_time', 0)/metadata.get('total_questions', 1):.1f}s |\n")
    report.append(f"| **Tokens moyens** | {metadata.get('total_tokens', 0)//metadata.get('total_questions', 1)} tokens |\n")
    report.append(f"| **Temps total** | {metadata.get('total_time', 0)/60:.1f} minutes |\n\n")

    report.append("### Métriques Qualitatives\n\n")
    report.append("| Métrique | Valeur | Commentaire |\n")
    report.append("|----------|--------|-------------|\n")
    report.append(f"| **Score moyen de similarité** | **{avg_similarity*100:.1f}%** | Correspondance attendu/obtenu |\n")
    report.append(f"| **Réponses correctes** | {correct_count}/{len(results)} ({correct_count/len(results)*100:.1f}%) | Similarité ≥ 80% |\n")
    report.append(f"| **Réponses partielles** | {partial_count}/{len(results)} ({partial_count/len(results)*100:.1f}%) | Similarité 50-80% |\n")
    report.append(f"| **Réponses incorrectes** | {incorrect_count}/{len(results)} ({incorrect_count/len(results)*100:.1f}%) | Similarité < 50% |\n\n")

    # Detailed Analysis
    report.append("---\n\n")
    report.append("## 🔍 Analyse Détaillée par Question\n\n")

    for i, result in enumerate(results, 1):
        question = result.get("question", "N/A")
        expected = result.get("expected", "")
        obtained = result.get("answer", "")
        sources = result.get("sources", [])
        tokens = result.get("tokens", 0)
        time = result.get("time", 0)

        sim = calculate_similarity(expected, obtained)
        emoji, status = categorize_answer_quality(sim, obtained)

        report.append(f"### Question {i}: {question}\n\n")
        report.append("| Métrique | Valeur |\n")
        report.append("|----------|--------|\n")
        report.append(f"| **Statut** | {emoji} {status} |\n")
        report.append(f"| **Similarité** | {sim*100:.1f}% |\n")
        report.append(f"| **Temps** | {time:.1f}s |\n")
        report.append(f"| **Tokens** | {tokens} |\n")
        report.append(f"| **Chunks** | {', '.join(sources[:5])} |\n\n")

        # Expected vs Obtained
        report.append("**Réponse attendue:**\n")
        exp_preview = expected[:200] + "..." if len(expected) > 200 else expected
        report.append(f"> {exp_preview}\n\n")

        report.append("**Réponse obtenue:**\n")
        obt_preview = obtained[:200] + "..." if len(obtained) > 200 else obtained
        report.append(f"> {obt_preview}\n\n")

        # Analysis
        if sim < 0.5:
            report.append("**Analyse:**\n")
            if "je n'ai pas trouvé" in obtained.lower() or "je n'ai pas d'information" in obtained.lower():
                report.append("- ❌ Le système n'a trouvé aucune information pertinente\n")
            elif sim < 0.1:
                report.append("- ❌ Réponse totalement hors sujet ou hallucination\n")
            else:
                report.append("- ⚠️ Réponse incorrecte mais contient des éléments pertinents\n")

        report.append("\n---\n\n")

    # Chunk Analysis
    report.append("## 📦 Analyse des Chunks Retournés\n\n")
    report.append("### Chunks les Plus Fréquents\n\n")
    report.append("| Chunk ID | Fréquence | Pourcentage |\n")
    report.append("|----------|-----------|-------------|\n")

    total_questions = len(results)
    for chunk_id, freq in list(chunk_freq.items())[:10]:
        percentage = freq / total_questions * 100
        report.append(f"| {chunk_id} | {freq}/{total_questions} | {percentage:.1f}% |\n")

    report.append("\n")

    # Recommendations
    report.append("---\n\n")
    report.append("## 💡 Recommandations\n\n")

    if avg_similarity < 0.3:
        report.append("### 🔴 Critique - Action Immédiate Requise\n\n")
        report.append("Le score de similarité moyen est très faible ({:.1f}%). Les problèmes majeurs identifiés:\n\n".format(avg_similarity * 100))
        report.append("1. **Revoir la stratégie de chunking**\n")
        report.append("   - Utiliser `size-based` au lieu de `markdown-headers`\n")
        report.append("   - Augmenter la taille des chunks (1500-2000 tokens)\n")
        report.append("   - Ajouter overlap (300-500 tokens)\n\n")
        report.append("2. **Enrichir les métadonnées**\n")
        report.append("   - Ajouter identifiants d'entités dans chaque chunk\n")
        report.append("   - Tagger les chunks par catégorie\n\n")
        report.append("3. **Tester d'autres modèles d'embedding**\n")
        report.append("   - `all-mpnet-base-v2` (meilleure qualité)\n")
        report.append("   - `multilingual-e5-large` (multilingue)\n\n")
    elif avg_similarity < 0.6:
        report.append("### 🟡 Moyen - Améliorations Recommandées\n\n")
        report.append("Le score de similarité moyen est moyen ({:.1f}%). Améliorations suggérées:\n\n".format(avg_similarity * 100))
        report.append("1. **Optimiser le prompt système**\n")
        report.append("   - Réduire la verbosité\n")
        report.append("   - Améliorer les instructions de formatage\n\n")
        report.append("2. **Augmenter le nombre de chunks récupérés**\n")
        report.append("   - Tester avec n_chunks=10 au lieu de 5\n\n")
        report.append("3. **Implémenter le reranking**\n")
        report.append("   - Reclasser les chunks après récupération\n\n")
    else:
        report.append("### 🟢 Bon - Optimisations Mineures\n\n")
        report.append("Le score de similarité moyen est bon ({:.1f}%). Optimisations possibles:\n\n".format(avg_similarity * 100))
        report.append("1. **Fine-tuner le modèle LLM**\n")
        report.append("   - Utiliser les données d'évaluation pour le fine-tuning\n\n")
        report.append("2. **Monitorer les performances**\n")
        report.append("   - Mettre en place des alertes sur les métriques\n\n")

    # Footer
    report.append("\n---\n\n")
    report.append("**Rapport généré automatiquement par DYAG**\n")
    report.append(f"**Outil**: `dyag generate-evaluation-report`\n")
    report.append(f"**Version**: 0.8.0+\n")

    markdown_content = "".join(report)

    # Save if output path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        if verbose:
            print(f"[OK] Rapport généré: {output_path}")

    return markdown_content


def generate_report_from_file(
    results_file: str,
    output_path: str = None,
    verbose: bool = False
) -> str:
    """
    Generate report from evaluation results JSON file.

    Args:
        results_file: Path to evaluation results JSON
        output_path: Optional output markdown file
        verbose: Show progress

    Returns:
        Generated markdown content
    """
    if verbose:
        print(f"Chargement des résultats: {results_file}")

    with open(results_file, 'r', encoding='utf-8') as f:
        results_data = json.load(f)

    if verbose:
        total = results_data.get("metadata", {}).get("total_questions", 0)
        print(f"[OK] {total} questions chargées\n")

    return generate_markdown_report(results_data, output_path, verbose)
