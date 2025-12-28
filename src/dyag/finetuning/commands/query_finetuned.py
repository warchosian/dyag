"""
Commande pour interroger un modèle fine-tuné.

Support:
- Mode direct: dyag query-finetuned "Question ?" --model path/to/model
- Mode interactif: dyag query-finetuned --model path/to/model
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from dyag.rag.core.llm_providers import LLMProviderFactory


def register_query_finetuned_command(subparsers):
    """
    Enregistre la commande query-finetuned.

    Args:
        subparsers: Objet subparsers d'argparse
    """
    parser = subparsers.add_parser(
        'query-finetuned',
        help='Interroger un modèle fine-tuné',
        description='Interroge un modèle fine-tuné avec LoRA (mode direct ou interactif)'
    )

    parser.add_argument(
        'query',
        nargs='?',
        help='Question à poser (si absent: mode interactif)'
    )

    parser.add_argument(
        '--model',
        default='models/tinyllama-mygusi-1000/final',
        help='Chemin vers l\'adapter LoRA (défaut: models/tinyllama-mygusi-1000/final)'
    )

    parser.add_argument(
        '--base-model',
        default='llama3.2:1b',
        help='Modèle de base (tinyllama, llama3.2:1b, llama3.1:8b, ou chemin HF)'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Créativité du modèle 0-1 (défaut: 0.7)'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=500,
        help='Longueur maximale de la réponse (défaut: 500)'
    )

    parser.add_argument(
        '--device',
        choices=['auto', 'cuda', 'cpu'],
        default='auto',
        help='Device à utiliser (défaut: auto)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Afficher les informations détaillées (tokens, etc.)'
    )

    parser.set_defaults(func=query_finetuned)


def query_finetuned(args):
    """
    Interroge un modèle fine-tuné.

    Args:
        args: Arguments de la ligne de commande
    """
    import os

    # Vérifier que le modèle existe
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"[ERREUR] Le modele '{args.model}' n'existe pas")
        sys.exit(1)

    # Vérifier que c'est bien un adapter LoRA
    adapter_config = model_path / 'adapter_config.json'
    if not adapter_config.exists():
        print(f"[ERREUR] '{args.model}' ne semble pas etre un adapter LoRA")
        print(f"   (adapter_config.json non trouve)")
        sys.exit(1)

    # Configurer les variables d'environnement
    os.environ['FINETUNED_MODEL_PATH'] = args.model
    os.environ['FINETUNED_BASE_MODEL'] = args.base_model
    os.environ['FINETUNED_DEVICE'] = args.device

    print("="*60)
    print("DYAG - Query Fine-Tuned Model")
    print("="*60)
    print(f"Modèle: {args.model}")
    print(f"Base model: {args.base_model}")
    print(f"Device: {args.device}")
    print("="*60)

    # Charger le modèle
    print("\nChargement du modèle...")
    try:
        provider = LLMProviderFactory.create_provider(provider='finetuned')
        print(f"\n[OK] Modele charge: {provider.get_model_name()}")
    except Exception as e:
        print(f"\n[ERREUR] Erreur lors du chargement: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Mode direct vs interactif
    if args.query:
        # Mode direct: une seule question
        run_direct_mode(provider, args)
    else:
        # Mode interactif: shell
        run_interactive_mode(provider, args)


def run_direct_mode(provider, args):
    """
    Mode direct: pose une seule question et quitte.

    Args:
        provider: Instance du provider
        args: Arguments CLI
    """
    print("\n" + "="*60)
    print(f"Question: {args.query}")
    print("="*60)

    try:
        # Générer la réponse
        result = provider.chat_completion(
            messages=[
                {"role": "system", "content": "Tu es un assistant expert qui répond de manière précise et concise aux questions sur les applications métier."},
                {"role": "user", "content": args.query}
            ],
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        # Afficher la réponse
        print(f"\nReponse:")
        print("="*60)
        print(result['content'])
        print("="*60)

        # Afficher les métadonnées si verbose
        if args.verbose:
            print(f"\nMetadonnees:")
            print(f"  Tokens: {result['usage']['total_tokens']}")
            print(f"    - Prompt: {result['usage']['prompt_tokens']}")
            print(f"    - Completion: {result['usage']['completion_tokens']}")

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_interactive_mode(provider, args):
    """
    Mode interactif: shell de conversation.

    Args:
        provider: Instance du provider
        args: Arguments CLI
    """
    print("\n" + "="*60)
    print("MODE INTERACTIF")
    print("="*60)
    print("Posez vos questions (Ctrl+C, 'exit', 'quit', ou 'q' pour quitter)")
    print("="*60)

    # Historique de conversation
    conversation_history = [
        {"role": "system", "content": "Tu es un assistant expert qui répond de manière précise et concise aux questions sur les applications métier."}
    ]

    while True:
        try:
            # Prompt utilisateur
            question = input("\nQuestion: ").strip()

            # Commandes de sortie
            if question.lower() in ['exit', 'quit', 'q', '']:
                print("\nAu revoir!")
                break

            # Ajouter à l'historique
            conversation_history.append({"role": "user", "content": question})

            # Générer la réponse
            print("\nGeneration en cours...")
            result = provider.chat_completion(
                messages=conversation_history,
                temperature=args.temperature,
                max_tokens=args.max_tokens
            )

            # Afficher la réponse
            print(f"\nReponse:")
            print("-"*60)
            print(result['content'])
            print("-"*60)

            # Ajouter la réponse à l'historique
            conversation_history.append({"role": "assistant", "content": result['content']})

            # Afficher les métadonnées si verbose
            if args.verbose:
                print(f"\nTokens: {result['usage']['total_tokens']} "
                      f"(prompt: {result['usage']['prompt_tokens']}, "
                      f"completion: {result['usage']['completion_tokens']})")

        except KeyboardInterrupt:
            print("\n\nAu revoir!")
            break

        except EOFError:
            print("\n\nAu revoir!")
            break

        except Exception as e:
            print(f"\n[ERREUR] {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            # Continuer la boucle même en cas d'erreur


if __name__ == '__main__':
    """Test en ligne de commande directe."""
    parser = argparse.ArgumentParser(description='Interroger un modèle fine-tuné')
    subparsers = parser.add_subparsers()
    register_query_finetuned_command(subparsers)

    # Parse avec 'query-finetuned' ajouté automatiquement
    import sys
    sys.argv.insert(1, 'query-finetuned')
    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
