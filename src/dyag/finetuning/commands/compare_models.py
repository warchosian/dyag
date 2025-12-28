"""
Commande pour comparer les performances RAG vs Fine-Tuning.

Compare les résultats d'évaluation de evaluate-rag et evaluate-finetuned
pour identifier la meilleure approche pour un cas d'usage donné.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def register_compare_models_command(subparsers):
    """
    Enregistre la commande compare-models.

    Args:
        subparsers: Objet subparsers d'argparse
    """
    parser = subparsers.add_parser(
        'compare-models',
        help='Comparer RAG vs Fine-Tuning',
        description='Compare les performances de RAG et Fine-Tuning sur les mêmes questions'
    )

    parser.add_argument(
        '--rag-results',
        required=True,
        help='Fichier JSON de résultats evaluate-rag'
    )

    parser.add_argument(
        '--finetuned-results',
        required=True,
        help='Fichier JSON de résultats evaluate-finetuned'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Fichier de sortie pour le rapport de comparaison (JSON ou MD)'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'both'],
        default='both',
        help='Format de sortie (défaut: both)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Afficher les détails'
    )

    parser.set_defaults(func=compare_models)


def load_results(file_path: str) -> Dict[str, Any]:
    """
    Charge un fichier de résultats.

    Args:
        file_path: Chemin du fichier JSON

    Returns:
        Dict avec les résultats
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_winner(rag_metrics: Dict, ft_metrics: Dict) -> Dict[str, str]:
    """
    Détermine le gagnant pour chaque métrique.

    Args:
        rag_metrics: Métriques RAG
        ft_metrics: Métriques Fine-Tuning

    Returns:
        Dict indiquant le gagnant par métrique
    """
    winners = {}

    # Temps de réponse (plus bas = mieux)
    if 'avg_time_seconds' in rag_metrics and 'avg_time_seconds' in ft_metrics:
        winners['speed'] = 'Fine-Tuned' if ft_metrics['avg_time_seconds'] < rag_metrics['avg_time_seconds'] else 'RAG'

    # Tokens (RAG utilise plus de tokens avec le context)
    if 'avg_tokens' in rag_metrics and 'avg_tokens' in ft_metrics:
        winners['tokens'] = 'Fine-Tuned' if ft_metrics['avg_tokens'] < rag_metrics['avg_tokens'] else 'RAG'

    # Success rate (plus haut = mieux)
    if 'success_rate' in rag_metrics and 'success_rate' in ft_metrics:
        winners['success'] = 'Fine-Tuned' if ft_metrics['success_rate'] > rag_metrics['success_rate'] else 'RAG'

    # Exact match (plus haut = mieux)
    if 'exact_match_rate' in rag_metrics and 'exact_match_rate' in ft_metrics:
        winners['accuracy'] = 'Fine-Tuned' if ft_metrics.get('exact_match_rate', 0) > rag_metrics.get('exact_match_rate', 0) else 'RAG'

    return winners


def generate_json_report(rag_results: Dict, ft_results: Dict) -> Dict[str, Any]:
    """
    Génère un rapport JSON de comparaison.

    Args:
        rag_results: Résultats RAG
        ft_results: Résultats Fine-Tuning

    Returns:
        Dict avec le rapport de comparaison
    """
    rag_metrics = rag_results.get('metrics', {})
    ft_metrics = ft_results.get('metrics', {})

    winners = calculate_winner(rag_metrics, ft_metrics)

    comparison = {
        'comparison_date': Path(__file__).stat().st_mtime,
        'models': {
            'rag': {
                'collection': rag_results.get('metadata', {}).get('collection', 'unknown'),
                'provider': rag_results.get('metadata', {}).get('provider', 'unknown'),
                'model': rag_results.get('metadata', {}).get('model', 'unknown')
            },
            'finetuned': {
                'model_path': ft_results.get('metadata', {}).get('model', 'unknown'),
                'base_model': ft_results.get('metadata', {}).get('base_model', 'unknown')
            }
        },
        'metrics_comparison': {
            'success_rate': {
                'rag': rag_metrics.get('success_rate', 0),
                'finetuned': ft_metrics.get('success_rate', 0),
                'winner': winners.get('success', 'tie'),
                'difference': abs(ft_metrics.get('success_rate', 0) - rag_metrics.get('success_rate', 0))
            },
            'exact_match_rate': {
                'rag': rag_metrics.get('exact_match_rate', 0),
                'finetuned': ft_metrics.get('exact_match_rate', 0),
                'winner': winners.get('accuracy', 'tie'),
                'difference': abs(ft_metrics.get('exact_match_rate', 0) - rag_metrics.get('exact_match_rate', 0))
            },
            'avg_time_seconds': {
                'rag': rag_metrics.get('avg_time_seconds', 0),
                'finetuned': ft_metrics.get('avg_time_seconds', 0),
                'winner': winners.get('speed', 'tie'),
                'speedup': rag_metrics.get('avg_time_seconds', 1) / max(ft_metrics.get('avg_time_seconds', 1), 0.001)
            },
            'avg_tokens': {
                'rag': rag_metrics.get('avg_tokens', 0),
                'finetuned': ft_metrics.get('avg_tokens', 0),
                'winner': winners.get('tokens', 'tie'),
                'reduction': 1 - (ft_metrics.get('avg_tokens', 0) / max(rag_metrics.get('avg_tokens', 1), 1))
            }
        },
        'overall_winner': determine_overall_winner(winners),
        'recommendations': generate_recommendations(rag_metrics, ft_metrics, winners)
    }

    return comparison


def determine_overall_winner(winners: Dict[str, str]) -> str:
    """Détermine le gagnant global."""
    if not winners:
        return "tie"

    rag_wins = sum(1 for w in winners.values() if w == 'RAG')
    ft_wins = sum(1 for w in winners.values() if w == 'Fine-Tuned')

    if rag_wins > ft_wins:
        return "RAG"
    elif ft_wins > rag_wins:
        return "Fine-Tuned"
    else:
        return "tie"


def generate_recommendations(rag_metrics: Dict, ft_metrics: Dict, winners: Dict) -> List[str]:
    """Génère des recommandations basées sur les résultats."""
    recommendations = []

    # Recommandation vitesse
    if winners.get('speed') == 'Fine-Tuned':
        speedup = rag_metrics.get('avg_time_seconds', 1) / max(ft_metrics.get('avg_time_seconds', 1), 0.001)
        if speedup > 2:
            recommendations.append(f"Fine-Tuning est {speedup:.1f}x plus rapide - recommandé pour latence critique")
    elif winners.get('speed') == 'RAG':
        recommendations.append("RAG est plus rapide - avantage pour réponses temps réel")

    # Recommandation tokens/coût
    if winners.get('tokens') == 'Fine-Tuned':
        reduction = 1 - (ft_metrics.get('avg_tokens', 0) / max(rag_metrics.get('avg_tokens', 1), 1))
        if reduction > 0.3:
            recommendations.append(f"Fine-Tuning utilise {reduction*100:.0f}% moins de tokens - économies sur coûts API")

    # Recommandation précision
    if winners.get('accuracy') == 'RAG':
        recommendations.append("RAG offre une meilleure précision - recommandé si exactitude critique")
    elif winners.get('accuracy') == 'Fine-Tuned':
        recommendations.append("Fine-Tuning offre une meilleure précision - domaine bien appris")

    # Recommandations générales
    if ft_metrics.get('success_rate', 0) < 80:
        recommendations.append("Fine-Tuning: Envisager plus d'exemples ou epochs pour améliorer qualité")

    if rag_metrics.get('avg_tokens', 0) > 2000:
        recommendations.append("RAG: Context très large - considérer chunking ou Fine-Tuning pour réduire coûts")

    return recommendations


def generate_markdown_report(comparison: Dict[str, Any]) -> str:
    """Génère un rapport Markdown."""
    md = []

    md.append("# Rapport de Comparaison : RAG vs Fine-Tuning\n")
    md.append(f"**Gagnant Global**: {comparison['overall_winner']}\n")

    md.append("## Modèles Comparés\n")
    md.append("### RAG")
    md.append(f"- Collection: {comparison['models']['rag']['collection']}")
    md.append(f"- Provider: {comparison['models']['rag']['provider']}")
    md.append(f"- Model: {comparison['models']['rag']['model']}\n")

    md.append("### Fine-Tuned")
    md.append(f"- Model Path: {comparison['models']['finetuned']['model_path']}")
    md.append(f"- Base Model: {comparison['models']['finetuned']['base_model']}\n")

    md.append("## Comparaison des Métriques\n")
    md.append("| Métrique | RAG | Fine-Tuned | Gagnant | Différence |")
    md.append("|----------|-----|------------|---------|------------|")

    metrics = comparison['metrics_comparison']

    for metric_name, metric_data in metrics.items():
        rag_val = metric_data['rag']
        ft_val = metric_data['finetuned']
        winner = metric_data['winner']

        if 'difference' in metric_data:
            diff = f"{metric_data['difference']:.2f}"
        elif 'speedup' in metric_data:
            diff = f"{metric_data['speedup']:.2f}x"
        elif 'reduction' in metric_data:
            diff = f"{metric_data['reduction']*100:.1f}%"
        else:
            diff = "-"

        winner_icon = "🏆" if winner != "tie" else "🤝"
        md.append(f"| {metric_name} | {rag_val:.2f} | {ft_val:.2f} | {winner} {winner_icon} | {diff} |")

    md.append("\n## Recommandations\n")
    for i, rec in enumerate(comparison['recommendations'], 1):
        md.append(f"{i}. {rec}")

    md.append("\n## Analyse\n")

    # Avantages RAG
    md.append("### Avantages RAG")
    md.append("- ✅ Mise à jour instantanée des données (re-indexation)")
    md.append("- ✅ Transparence avec sources citées")
    md.append("- ✅ Pas de training nécessaire")

    # Avantages Fine-Tuning
    md.append("\n### Avantages Fine-Tuning")
    md.append("- ✅ Réponses plus naturelles et fluides")
    md.append("- ✅ Moins de tokens consommés (pas de context RAG)")
    md.append("- ✅ Meilleure compréhension du domaine après training")

    md.append("\n## Cas d'Usage Recommandés\n")

    md.append("### Utiliser RAG si:")
    md.append("- Les données changent fréquemment")
    md.append("- Besoin de traçabilité (sources)")
    md.append("- Pas de GPU disponible pour training")
    md.append("- Volume de données très large (> 10k documents)")

    md.append("\n### Utiliser Fine-Tuning si:")
    md.append("- Données stables dans le temps")
    md.append("- Budget GPU disponible pour training")
    md.append("- Réponses naturelles prioritaires")
    md.append("- Domaine spécialisé bien défini")

    md.append("\n### Approche Hybride (Recommandé)")
    md.append("- Utiliser RAG pour retrieval précis")
    md.append("- Utiliser Fine-Tuned pour génération naturelle")
    md.append("- Combiner les avantages des deux approches")

    return "\n".join(md)


def compare_models(args):
    """
    Compare RAG vs Fine-Tuning.

    Args:
        args: Arguments de la ligne de commande
    """
    print("="*70)
    print("DYAG - Comparaison RAG vs Fine-Tuning")
    print("="*70)

    # Charger les résultats
    print(f"\nChargement des résultats...")
    try:
        rag_results = load_results(args.rag_results)
        print(f"  [OK] RAG: {args.rag_results}")
    except Exception as e:
        print(f"\n[ERREUR] Impossible de charger RAG results: {e}")
        return 1

    try:
        ft_results = load_results(args.finetuned_results)
        print(f"  [OK] Fine-Tuned: {args.finetuned_results}")
    except Exception as e:
        print(f"\n[ERREUR] Impossible de charger Fine-Tuned results: {e}")
        return 1

    # Générer la comparaison
    print(f"\nGénération de la comparaison...")
    comparison = generate_json_report(rag_results, ft_results)

    # Afficher résumé
    print(f"\n" + "="*70)
    print("RÉSUMÉ")
    print("="*70)
    print(f"\nGagnant Global: {comparison['overall_winner']}")

    print(f"\nDétails par métrique:")
    for metric_name, metric_data in comparison['metrics_comparison'].items():
        winner = metric_data['winner']
        print(f"  {metric_name:20s}: {winner}")

    if args.verbose:
        print(f"\nRecommandations:")
        for i, rec in enumerate(comparison['recommendations'], 1):
            print(f"  {i}. {rec}")

    # Sauvegarder
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format in ['json', 'both']:
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] Rapport JSON: {json_path}")

    if args.format in ['markdown', 'both']:
        md_path = output_path.with_suffix('.md')
        markdown_report = generate_markdown_report(comparison)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        print(f"[OK] Rapport Markdown: {md_path}")

    return 0
