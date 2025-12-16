"""
Commande d'interrogation du système RAG.

Ce module permet de poser des questions au système RAG via la ligne de commande.
"""

import sys
import io
from pathlib import Path
from typing import Optional

# Fixer l'encodage UTF-8 pour Windows (seulement si exécuté comme script principal)
if sys.platform == 'win32' and __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dyag.rag_query import RAGQuerySystem


def execute(args):
    """Exécute la commande query-rag."""
    print("Initialisation du système RAG...")

    try:
        rag = RAGQuerySystem(
            chroma_path=args.chroma_path,
            collection_name=args.collection,
            embedding_model=args.embedding_model,
            timeout=args.timeout
        )
    except Exception as e:
        print(f"❌ Erreur d'initialisation du RAG: {e}")
        return 1

    # Afficher les statistiques
    if args.verbose:
        stats = rag.get_stats()
        print(f"\n📊 Statistiques:")
        print(f"  - Chunks indexés: {stats['total_chunks']}")
        print(f"  - Collection: {stats['collection_name']}")
        print(f"  - Modèle LLM: {stats['llm_model']}")
        print()

    # Mode question directe
    if args.query:
        print(f"\n❓ Question: {args.query}")
        print("\n🔍 Recherche en cours...")

        try:
            result = rag.ask(args.query, n_chunks=args.n_chunks)

            print(f"\n💬 Réponse:")
            print(result['answer'])

            if args.verbose:
                print(f"\n📊 Métadonnées:")
                print(f"  - Sources: {len(result['sources'])} chunks")
                print(f"  - Tokens: {result['tokens_used']}")
                print(f"  - IDs: {', '.join(result['sources'][:3])}...")

            return 0

        except Exception as e:
            print(f"\n❌ Erreur lors de la requête: {e}")
            return 1

    # Mode interactif
    print("\n" + "=" * 60)
    print("Mode interactif - Posez vos questions (Ctrl+C pour quitter)")
    print("=" * 60)

    while True:
        try:
            question = input("\n❓ Question: ")

            if not question.strip():
                continue

            print("\n🔍 Recherche en cours...")
            result = rag.ask(question, n_chunks=args.n_chunks)

            print(f"\n💬 Réponse:")
            print(result['answer'])

            if args.verbose:
                print(f"\n📊 Métadonnées:")
                print(f"  - Sources: {len(result['sources'])} chunks")
                print(f"  - Tokens: {result['tokens_used']}")
                print(f"  - IDs: {', '.join(result['sources'][:3])}...")

        except KeyboardInterrupt:
            print("\n\nAu revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

    return 0


def register_query_rag_command(subparsers):
    """Enregistre la commande query-rag."""
    parser = subparsers.add_parser(
        'query-rag',
        help='Interroge le système RAG avec une question'
    )

    parser.add_argument(
        'query',
        type=str,
        nargs='?',
        help='Question à poser (mode non-interactif). Si omis, lance le mode interactif'
    )
    parser.add_argument(
        '--n-chunks',
        type=int,
        default=5,
        help='Nombre de chunks de contexte (défaut: 5)'
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
        '--embedding-model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Modèle d\'embedding (défaut: all-MiniLM-L6-v2)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        help='Timeout en secondes pour Ollama'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Afficher des informations détaillées'
    )

    parser.set_defaults(func=execute)
