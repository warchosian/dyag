"""
Commande d'évaluation du système RAG.

Teste le système RAG avec des questions de référence et compare
les réponses avec les réponses attendues.
"""

import json
import sys
import io
from pathlib import Path
from typing import List, Dict
import time
from datetime import datetime

# Fixer l'encodage UTF-8 pour Windows (seulement si exécuté comme script principal)
if sys.platform == 'win32' and __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dyag.rag_query import RAGQuerySystem


def load_dataset(dataset_path: str) -> List[Dict]:
    """
    Charge un dataset JSONL de questions/réponses.

    Args:
        dataset_path: Chemin vers le fichier JSONL

    Returns:
        Liste de {question, expected_answer, system_prompt}
    """
    print(f"Chargement du dataset: {dataset_path}")

    questions = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                messages = data.get('messages', [])

                # Extraire question et réponse
                user_msg = next((m for m in messages if m['role'] == 'user'), None)
                assistant_msg = next((m for m in messages if m['role'] == 'assistant'), None)
                system_msg = next((m for m in messages if m['role'] == 'system'), None)

                if user_msg and assistant_msg:
                    questions.append({
                        'question': user_msg['content'],
                        'expected_answer': assistant_msg['content'],
                        'system_prompt': system_msg['content'] if system_msg else None,
                        'line_num': line_num
                    })
            except Exception as e:
                print(f"Erreur ligne {line_num}: {e}")
                continue

    print(f"✓ {len(questions)} questions chargées\n")
    return questions


def evaluate_rag(
    rag: RAGQuerySystem,
    questions: List[Dict],
    n_chunks: int = 5,
    max_questions: int = None,
    output_file: str = None
) -> Dict:
    """
    Évalue le système RAG sur un ensemble de questions.

    Args:
        rag: Système RAG initialisé
        questions: Liste de questions avec réponses attendues
        n_chunks: Nombre de chunks de contexte
        max_questions: Nombre max de questions à tester (None = toutes)
        output_file: Fichier JSON pour sauvegarder les résultats détaillés

    Returns:
        Statistiques d'évaluation
    """
    if max_questions:
        questions = questions[:max_questions]

    print("=" * 80)
    print(f"ÉVALUATION RAG - {len(questions)} questions")
    print("=" * 80)
    print(f"Modèle LLM: {rag.llm_provider.get_model_name()}")
    print(f"Chunks par question: {n_chunks}")
    print(f"Collection: {rag.collection.name}")
    print("=" * 80)
    print()

    results = []
    total_time = 0
    total_tokens = 0

    for i, q in enumerate(questions, 1):
        question = q['question']
        expected = q['expected_answer']

        print(f"\n[{i}/{len(questions)}] {question}")
        print("-" * 80)

        try:
            start_time = time.time()
            result = rag.ask(question, n_chunks=n_chunks)
            elapsed = time.time() - start_time

            answer = result['answer']
            tokens = result.get('tokens_used', 0)
            sources = result.get('sources', [])

            # Afficher réponse
            print(f"\n✓ Réponse ({elapsed:.1f}s, {tokens} tokens):")
            print(answer[:300] + "..." if len(answer) > 300 else answer)

            print(f"\n📌 Attendu:")
            print(expected[:300] + "..." if len(expected) > 300 else expected)

            print(f"\n📊 Sources: {', '.join(sources[:3])}...")

            # Enregistrer résultat
            results.append({
                'question': question,
                'answer': answer,
                'expected': expected,
                'sources': sources,
                'tokens': tokens,
                'time': elapsed,
                'success': True,
                'error': None
            })

            total_time += elapsed
            total_tokens += tokens

        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            results.append({
                'question': question,
                'answer': None,
                'expected': expected,
                'sources': [],
                'tokens': 0,
                'time': 0,
                'success': False,
                'error': str(e)
            })

    # Statistiques
    print("\n" + "=" * 80)
    print("RÉSULTATS")
    print("=" * 80)

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\nQuestions traitées: {len(results)}")
    print(f"  ✓ Succès: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"  ✗ Échecs: {failed} ({failed/len(results)*100:.1f}%)")

    if successful > 0:
        avg_time = total_time / successful
        avg_tokens = total_tokens / successful
        print(f"\nPerformance moyenne:")
        print(f"  Temps: {avg_time:.1f}s")
        print(f"  Tokens: {avg_tokens:.0f}")

    print(f"\nTemps total: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Tokens total: {total_tokens}")

    # Sauvegarder résultats détaillés
    if output_file:
        output_path = Path(output_file)
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'model': rag.llm_provider.get_model_name(),
                'n_chunks': n_chunks,
                'total_questions': len(results),
                'successful': successful,
                'failed': failed,
                'total_time': total_time,
                'total_tokens': total_tokens
            },
            'results': results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Résultats sauvegardés: {output_file}")

    print("=" * 80)

    return {
        'total': len(results),
        'successful': successful,
        'failed': failed,
        'total_time': total_time,
        'total_tokens': total_tokens,
        'results': results
    }


def execute(args):
    """Exécute la commande evaluate-rag."""
    # Vérifier dataset
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Dataset introuvable: {args.dataset}")
        return 1

    # Charger questions
    questions = load_dataset(args.dataset)
    if not questions:
        print("❌ Aucune question trouvée dans le dataset")
        return 1

    # Initialiser RAG
    print("Initialisation du système RAG...")
    try:
        rag = RAGQuerySystem(
            chroma_path=args.chroma_path,
            collection_name=args.collection,
            timeout=args.timeout
        )
    except Exception as e:
        print(f"❌ Erreur d'initialisation du RAG: {e}")
        return 1

    # Évaluer
    stats = evaluate_rag(
        rag=rag,
        questions=questions,
        n_chunks=args.n_chunks,
        max_questions=args.max_questions,
        output_file=args.output
    )

    # Code de sortie selon résultats
    return 0 if stats['failed'] == 0 else 1


def register_evaluate_rag_command(subparsers):
    """Enregistre la commande evaluate-rag."""
    parser = subparsers.add_parser(
        'evaluate-rag',
        help='Évalue le système RAG avec un dataset de questions/réponses'
    )

    parser.add_argument(
        'dataset',
        type=str,
        help='Chemin vers le dataset JSONL (ex: data/finetuning/dataset_mygusi_train-100.jsonl)'
    )
    parser.add_argument(
        '--n-chunks',
        type=int,
        default=5,
        help='Nombre de chunks de contexte (défaut: 5)'
    )
    parser.add_argument(
        '--max-questions',
        type=int,
        help='Nombre max de questions à tester (défaut: toutes)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Fichier JSON pour sauvegarder les résultats détaillés'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default='applications',
        help='Nom de la collection ChromaDB (défaut: applications)'
    )
    parser.add_argument(
        '--chroma-path',
        type=str,
        default='./chroma_db',
        help='Chemin vers ChromaDB (défaut: ./chroma_db)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        help='Timeout en secondes pour Ollama'
    )

    parser.set_defaults(func=execute)
