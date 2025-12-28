"""
Commande pour générer des datasets d'entraînement pour fine-tuning.

Support:
- Génération rule-based (patterns)
- Génération LLM-based
- Génération augmentée (data augmentation)
"""

import argparse
import json
import random
from pathlib import Path
from collections import defaultdict


def register_generate_training_command(subparsers):
    """
    Enregistre la commande generate-training.

    Args:
        subparsers: Objet subparsers d'argparse
    """
    parser = subparsers.add_parser(
        'generate-training',
        help='Générer des datasets d\'entraînement',
        description='Génère des datasets d\'entraînement pour fine-tuning'
    )

    parser.add_argument(
        'input',
        help='Fichier source (JSONL de chunks)'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Fichier de sortie (JSONL)'
    )

    parser.add_argument(
        '--method',
        choices=['rule-based', 'llm-based', 'augmented'],
        default='rule-based',
        help='Méthode de génération (défaut: rule-based)'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='Nombre d\'exemples à générer (défaut: 100)'
    )

    parser.add_argument(
        '--split',
        action='store_true',
        help='Séparer en train/val/test (80/10/10)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Valider le format JSONL'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Seed pour reproductibilité (défaut: 42)'
    )

    # Options spécifiques LLM-based
    parser.add_argument(
        '--llm-provider',
        choices=['openai', 'anthropic', 'ollama'],
        default='openai',
        help='Provider LLM pour méthode llm-based (défaut: openai)'
    )

    parser.add_argument(
        '--llm-model',
        help='Modèle LLM à utiliser (défaut: dépend du provider)'
    )

    parser.set_defaults(func=generate_training)


def validate_dataset(dataset):
    """
    Valide le format du dataset.

    Args:
        dataset: Liste d'exemples

    Returns:
        tuple: (is_valid, errors)
    """
    errors = []

    for i, example in enumerate(dataset):
        # Vérifier structure messages
        if 'messages' not in example:
            errors.append(f"Exemple {i}: clé 'messages' manquante")
            continue

        messages = example['messages']
        if not isinstance(messages, list):
            errors.append(f"Exemple {i}: 'messages' doit être une liste")
            continue

        # Vérifier qu'on a au moins system + user + assistant
        if len(messages) < 3:
            errors.append(f"Exemple {i}: au moins 3 messages requis (system, user, assistant)")
            continue

        # Vérifier le format de chaque message
        for j, msg in enumerate(messages):
            if 'role' not in msg:
                errors.append(f"Exemple {i}, message {j}: clé 'role' manquante")
            if 'content' not in msg:
                errors.append(f"Exemple {i}, message {j}: clé 'content' manquante")

            # Vérifier les rôles
            if msg.get('role') not in ['system', 'user', 'assistant']:
                errors.append(f"Exemple {i}, message {j}: rôle invalide '{msg.get('role')}'")

    return len(errors) == 0, errors


def split_dataset(dataset, train_ratio=0.8, val_ratio=0.1):
    """
    Sépare le dataset en train/val/test.

    Args:
        dataset: Liste d'exemples
        train_ratio: Ratio pour training
        val_ratio: Ratio pour validation

    Returns:
        dict: {'train': [...], 'val': [...], 'test': [...]}
    """
    random.shuffle(dataset)

    train_size = int(len(dataset) * train_ratio)
    val_size = int(len(dataset) * val_ratio)

    return {
        'train': dataset[:train_size],
        'val': dataset[train_size:train_size + val_size],
        'test': dataset[train_size + val_size:]
    }


def save_dataset(dataset, output_file):
    """
    Sauvegarde le dataset au format JSONL.

    Args:
        dataset: Liste d'exemples
        output_file: Chemin du fichier de sortie
    """
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in dataset:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')


def compute_stats(dataset):
    """
    Calcule des statistiques sur le dataset.

    Args:
        dataset: Liste d'exemples

    Returns:
        dict: Statistiques
    """
    stats = {
        'total_examples': len(dataset),
        'total_tokens': 0,
        'avg_tokens_per_example': 0,
        'question_types': defaultdict(int)
    }

    total_chars = 0
    for example in dataset:
        messages = example.get('messages', [])
        for msg in messages:
            content = msg.get('content', '')
            total_chars += len(content)

    # Approximation tokens (1 token ≈ 4 chars)
    stats['total_tokens'] = total_chars // 4
    stats['avg_tokens_per_example'] = stats['total_tokens'] // len(dataset) if dataset else 0

    return stats


def generate_training(args):
    """
    Génère des datasets d'entraînement.

    Args:
        args: Arguments de la ligne de commande
    """
    print("="*70)
    print("DYAG - Génération Dataset de Training")
    print("="*70)
    print(f"Input:   {args.input}")
    print(f"Output:  {args.output}")
    print(f"Méthode: {args.method}")
    print(f"Count:   {args.count}")
    print(f"Split:   {args.split}")
    print(f"Seed:    {args.seed}")
    print("="*70)

    # Vérifier que le fichier source existe
    if not Path(args.input).exists():
        print(f"\n[ERREUR] Fichier source non trouvé: {args.input}")
        return 1

    # Importer les générateurs
    from dyag.finetuning.core.dataset_generators import (
        RuleBasedGenerator,
        LLMBasedGenerator,
        AugmentedGenerator
    )

    # Sélectionner le générateur
    generator_kwargs = {'seed': args.seed}

    if args.method == 'rule-based':
        print("\nGénérateur: Rule-Based (patterns regex)")
        generator = RuleBasedGenerator()

    elif args.method == 'llm-based':
        print(f"\nGénérateur: LLM-Based (provider: {args.llm_provider})")
        print("Initialisation du LLM provider...")

        try:
            from dyag.rag.core.llm_providers import LLMProviderFactory

            llm_provider = LLMProviderFactory.create_provider(
                provider=args.llm_provider,
                model=args.llm_model
            )
            print(f"[OK] Provider: {llm_provider.get_model_name()}")

            generator_kwargs['llm_provider'] = llm_provider
            generator = LLMBasedGenerator()

        except Exception as e:
            print(f"\n[ERREUR] Impossible d'initialiser le LLM provider: {e}")
            print("\nAssurez-vous d'avoir configuré les clés API dans .env")
            return 1

    elif args.method == 'augmented':
        print("\nGénérateur: Augmented (data augmentation)")
        generator = AugmentedGenerator()

    else:
        print(f"\n[ERREUR] Méthode inconnue: {args.method}")
        return 1

    # Générer le dataset
    print(f"\nGénération de {args.count} exemples...")
    try:
        dataset = generator.generate(
            input_file=args.input,
            count=args.count,
            **generator_kwargs
        )
        print(f"[OK] {len(dataset)} exemples générés")
    except Exception as e:
        print(f"\n[ERREUR] Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Validation si demandée
    if args.validate:
        print("\nValidation du dataset...")
        is_valid, errors = validate_dataset(dataset)

        if is_valid:
            print("[OK] Dataset valide")
        else:
            print(f"[ERREUR] Dataset invalide ({len(errors)} erreurs)")
            for error in errors[:10]:  # Afficher max 10 erreurs
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... et {len(errors) - 10} autres erreurs")
            return 1

    # Statistiques
    print("\nStatistiques:")
    stats = compute_stats(dataset)
    print(f"  - Exemples:        {stats['total_examples']}")
    print(f"  - Tokens (approx): {stats['total_tokens']:,}")
    print(f"  - Tokens/exemple:  {stats['avg_tokens_per_example']}")

    # Split si demandé
    if args.split:
        print("\nSplit train/val/test (80/10/10)...")
        splits = split_dataset(dataset)

        output_path = Path(args.output)
        base_name = output_path.stem
        ext = output_path.suffix

        # Sauvegarder chaque split
        for split_name, split_data in splits.items():
            if split_data:
                split_file = output_path.parent / f"{base_name}_{split_name}{ext}"
                save_dataset(split_data, split_file)
                print(f"  [OK] {split_name:10s}: {len(split_data):4d} exemples -> {split_file}")

    else:
        # Sauvegarder tout dans un seul fichier
        print(f"\nSauvegarde du dataset...")
        save_dataset(dataset, args.output)
        print(f"[OK] {args.output}")

    # Résumé final
    print("\n" + "="*70)
    print("DATASET CRÉÉ AVEC SUCCÈS")
    print("="*70)

    if args.split:
        print(f"\nFichiers générés:")
        output_path = Path(args.output)
        base_name = output_path.stem
        ext = output_path.suffix
        for split_name in ['train', 'val', 'test']:
            split_file = output_path.parent / f"{base_name}_{split_name}{ext}"
            if split_file.exists():
                print(f"  - {split_file}")
    else:
        print(f"\nFichier: {args.output}")

    print(f"\nProchaine étape:")
    if args.split:
        output_path = Path(args.output)
        base_name = output_path.stem
        ext = output_path.suffix
        train_file = output_path.parent / f"{base_name}_train{ext}"
        print(f"  dyag finetune --dataset {train_file} --output models/my-model")
    else:
        print(f"  dyag finetune --dataset {args.output} --output models/my-model")

    return 0
