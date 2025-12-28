"""
Commande pour évaluer un modèle fine-tuné.

Évalue les performances d'un modèle fine-tuné sur un dataset de questions.
Fournit des métriques comparables à evaluate-rag pour permettre la comparaison.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def register_evaluate_finetuned_command(subparsers):
    """
    Enregistre la commande evaluate-finetuned.

    Args:
        subparsers: Objet subparsers d'argparse
    """
    parser = subparsers.add_parser(
        'evaluate-finetuned',
        help='Évaluer un modèle fine-tuné',
        description='Évalue les performances d\'un modèle fine-tuné sur un dataset de questions'
    )

    parser.add_argument(
        'dataset',
        help='Fichier JSONL de questions pour l\'évaluation'
    )

    parser.add_argument(
        '--model',
        required=True,
        help='Chemin vers le modèle fine-tuné (adapter LoRA)'
    )

    parser.add_argument(
        '--base-model',
        required=True,
        help='Nom ou chemin du modèle de base (ex: qwen2.5:1.5b, tinyllama)'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Fichier JSON de sortie pour les résultats'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Température de génération (défaut: 0.7)'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=500,
        help='Nombre maximum de tokens générés (défaut: 500)'
    )

    parser.add_argument(
        '--device',
        choices=['auto', 'cuda', 'cpu'],
        default='auto',
        help='Device à utiliser (défaut: auto)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        help='Limiter le nombre de questions évaluées (pour tests rapides)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Afficher les détails pendant l\'évaluation'
    )

    parser.set_defaults(func=evaluate_finetuned)


def load_questions(dataset_path: str, limit: int = None) -> List[Dict]:
    """
    Charge les questions depuis le dataset.

    Args:
        dataset_path: Chemin du fichier JSONL
        limit: Nombre max de questions à charger

    Returns:
        Liste de questions
    """
    questions = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            if line.strip():
                questions.append(json.loads(line))
    return questions


def evaluate_finetuned(args):
    """
    Évalue un modèle fine-tuné.

    Args:
        args: Arguments de la ligne de commande
    """
    print("="*70)
    print("DYAG - Évaluation Modèle Fine-Tuné")
    print("="*70)

    # Vérifier que le dataset existe
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"\n[ERREUR] Dataset non trouvé: {args.dataset}")
        return 1

    # Vérifier que le modèle existe
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"\n[ERREUR] Modèle non trouvé: {args.model}")
        return 1

    # Charger les questions
    print(f"\nChargement du dataset: {args.dataset}")
    try:
        questions = load_questions(args.dataset, args.limit)
        print(f"  Questions chargées: {len(questions)}")
    except Exception as e:
        print(f"\n[ERREUR] Impossible de charger le dataset: {e}")
        return 1

    # Charger le modèle
    print(f"\nChargement du modèle fine-tuné...")
    print(f"  Modèle: {args.model}")
    print(f"  Base model: {args.base_model}")
    print(f"  Device: {args.device}")

    try:
        from dyag.rag.core.llm_providers import LocalFineTunedProvider

        provider = LocalFineTunedProvider(
            model_path=args.model,
            base_model=args.base_model,
            device=args.device
        )
        print(f"[OK] Modèle chargé: {provider.model_name}")
    except Exception as e:
        print(f"\n[ERREUR] Impossible de charger le modèle: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Évaluation
    print(f"\n" + "="*70)
    print("ÉVALUATION EN COURS")
    print("="*70)

    results = []
    total_time = 0
    total_tokens = 0
    errors = 0

    start_time = datetime.now()

    for i, question_data in enumerate(questions):
        question = question_data.get('question', question_data.get('query', ''))
        expected = question_data.get('expected_answer', question_data.get('answer', ''))

        if args.verbose:
            print(f"\n[{i+1}/{len(questions)}] {question[:60]}...")

        try:
            # Générer la réponse
            q_start = time.time()

            response = provider.chat_completion(
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui répond aux questions sur les applications MYGUSI."},
                    {"role": "user", "content": question}
                ],
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )

            q_time = time.time() - q_start
            total_time += q_time

            answer = response.get('content', '')
            tokens = response.get('usage', {}).get('total_tokens', 0)
            total_tokens += tokens

            # Calculer des métriques simples
            # Note: Pour des métriques avancées (BLEU, ROUGE), il faudrait ajouter les librairies appropriées
            exact_match = answer.strip().lower() == expected.strip().lower() if expected else False

            result = {
                'question': question,
                'expected_answer': expected,
                'generated_answer': answer,
                'exact_match': exact_match,
                'time_seconds': q_time,
                'tokens': tokens,
                'model': provider.model_name
            }

            results.append(result)

            if args.verbose:
                print(f"  Réponse: {answer[:100]}...")
                print(f"  Temps: {q_time:.2f}s | Tokens: {tokens}")

        except Exception as e:
            errors += 1
            print(f"\n[ERREUR] Question {i+1}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

            results.append({
                'question': question,
                'expected_answer': expected,
                'generated_answer': None,
                'error': str(e),
                'exact_match': False,
                'time_seconds': 0,
                'tokens': 0,
                'model': provider.model_name
            })

    end_time = datetime.now()
    duration = end_time - start_time

    # Calculer les métriques globales
    print(f"\n" + "="*70)
    print("RÉSULTATS")
    print("="*70)

    total_questions = len(questions)
    successful = total_questions - errors
    success_rate = (successful / total_questions * 100) if total_questions > 0 else 0

    exact_matches = sum(1 for r in results if r.get('exact_match', False))
    exact_match_rate = (exact_matches / successful * 100) if successful > 0 else 0

    avg_time = total_time / successful if successful > 0 else 0
    avg_tokens = total_tokens / successful if successful > 0 else 0

    print(f"\nQuestions évaluées: {total_questions}")
    print(f"  Succès:           {successful} ({success_rate:.1f}%)")
    print(f"  Erreurs:          {errors}")
    print(f"  Exact matches:    {exact_matches} ({exact_match_rate:.1f}%)")
    print(f"\nPerformance:")
    print(f"  Temps total:      {duration}")
    print(f"  Temps moyen:      {avg_time:.2f}s/question")
    print(f"  Tokens moyens:    {avg_tokens:.0f} tokens/question")
    print(f"  Tokens total:     {total_tokens}")

    # Sauvegarder les résultats
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    evaluation_results = {
        'metadata': {
            'model': args.model,
            'base_model': args.base_model,
            'dataset': args.dataset,
            'total_questions': total_questions,
            'evaluated_at': start_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'parameters': {
                'temperature': args.temperature,
                'max_tokens': args.max_tokens,
                'device': args.device
            }
        },
        'metrics': {
            'success_rate': success_rate,
            'exact_match_rate': exact_match_rate,
            'avg_time_seconds': avg_time,
            'avg_tokens': avg_tokens,
            'total_tokens': total_tokens,
            'errors': errors
        },
        'results': results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_results, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Résultats sauvegardés: {args.output}")

    # Afficher quelques exemples si verbose
    if args.verbose and results:
        print(f"\n" + "="*70)
        print("EXEMPLES DE RÉPONSES (3 premiers)")
        print("="*70)
        for i, result in enumerate(results[:3]):
            print(f"\n[Question {i+1}]")
            print(f"Q: {result['question']}")
            if result.get('expected_answer'):
                print(f"Attendu: {result['expected_answer'][:150]}...")
            if result.get('generated_answer'):
                print(f"Généré:  {result['generated_answer'][:150]}...")
            else:
                print(f"Erreur: {result.get('error')}")

    return 0
