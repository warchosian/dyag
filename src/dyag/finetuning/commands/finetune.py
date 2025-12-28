"""
Commande pour fine-tuner un modèle avec LoRA.

Support:
- Fine-tuning local avec LoRA/PEFT
- Support multi-modèles (TinyLlama, llama3.2:1b, llama3.1:8b)
- Auto-détection GPU/CPU
- Checkpoint management
"""

import argparse
import sys
import torch
from pathlib import Path


def register_finetune_command(subparsers):
    """
    Enregistre la commande finetune.

    Args:
        subparsers: Objet subparsers d'argparse
    """
    parser = subparsers.add_parser(
        'finetune',
        help='Fine-tuner un modèle avec LoRA',
        description='Fine-tune un modèle de base avec LoRA/PEFT'
    )

    parser.add_argument(
        '--dataset',
        required=True,
        help='Fichier JSONL de training'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Répertoire de sortie pour le modèle fine-tuné'
    )

    parser.add_argument(
        '--base-model',
        default='llama3.2:1b',
        help='Modèle de base (tinyllama, llama3.2:1b, llama3.1:8b, ou chemin HF)'
    )

    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Nombre d\'epochs (défaut: 3)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=4,
        help='Taille du batch (défaut: 4)'
    )

    parser.add_argument(
        '--lora-rank',
        type=int,
        default=16,
        help='Rank LoRA (défaut: 16)'
    )

    parser.add_argument(
        '--lora-alpha',
        type=int,
        default=32,
        help='Alpha LoRA (défaut: 32)'
    )

    parser.add_argument(
        '--max-seq-length',
        type=int,
        default=512,
        help='Longueur max de séquence (défaut: 512)'
    )

    parser.add_argument(
        '--device',
        choices=['auto', 'cuda', 'cpu'],
        default='auto',
        help='Device à utiliser (défaut: auto)'
    )

    parser.add_argument(
        '--resume',
        help='Reprendre depuis un checkpoint'
    )

    parser.add_argument(
        '--force-cpu',
        action='store_true',
        help='Forcer l\'utilisation du CPU (très lent)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Afficher les informations détaillées'
    )

    parser.set_defaults(func=finetune)


def check_system_requirements(args):
    """
    Vérifie la configuration système.

    Args:
        args: Arguments CLI

    Returns:
        dict: Informations système
    """
    info = {
        'has_cuda': torch.cuda.is_available(),
        'device': None,
        'gpu_name': None,
        'vram_gb': 0,
        'warnings': []
    }

    # Déterminer le device
    if args.force_cpu:
        info['device'] = 'cpu'
        info['warnings'].append("Mode CPU forcé - le training sera TRÈS lent (plusieurs jours possibles)")
    elif args.device == 'cpu':
        info['device'] = 'cpu'
        info['warnings'].append("CPU sélectionné - le training sera très lent")
    elif args.device == 'cuda':
        if info['has_cuda']:
            info['device'] = 'cuda'
        else:
            info['warnings'].append("CUDA demandé mais non disponible - utilisation du CPU")
            info['device'] = 'cpu'
    else:  # auto
        info['device'] = 'cuda' if info['has_cuda'] else 'cpu'
        if not info['has_cuda']:
            info['warnings'].append("Pas de GPU détecté - utilisation du CPU (très lent)")

    # Infos GPU si disponible
    if info['device'] == 'cuda':
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['vram_gb'] = torch.cuda.get_device_properties(0).total_memory / 1e9

        # Warnings VRAM
        if info['vram_gb'] < 4:
            info['warnings'].append(f"VRAM faible ({info['vram_gb']:.1f} GB) - réduisez batch-size à 1")
        elif info['vram_gb'] < 8:
            info['warnings'].append(f"VRAM limitée ({info['vram_gb']:.1f} GB) - batch-size de 2-4 recommandé")

    return info


def estimate_training_time(dataset_size, batch_size, epochs, device):
    """
    Estime la durée du training.

    Args:
        dataset_size: Nombre d'exemples
        batch_size: Taille du batch
        epochs: Nombre d'epochs
        device: Device utilisé

    Returns:
        str: Estimation lisible
    """
    steps_per_epoch = dataset_size // batch_size
    total_steps = steps_per_epoch * epochs

    # Temps par step (très approximatif)
    if device == 'cuda':
        seconds_per_step = 2  # GPU moyen
    else:
        seconds_per_step = 30  # CPU

    total_seconds = total_steps * seconds_per_step
    hours = total_seconds / 3600

    if hours < 1:
        return f"{int(total_seconds / 60)} minutes"
    elif hours < 24:
        return f"{hours:.1f} heures"
    else:
        return f"{hours / 24:.1f} jours"


def count_dataset_examples(dataset_path):
    """
    Compte le nombre d'exemples dans le dataset.

    Args:
        dataset_path: Chemin du fichier JSONL

    Returns:
        int: Nombre d'exemples
    """
    count = 0
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def finetune(args):
    """
    Fine-tune un modèle.

    Args:
        args: Arguments de la ligne de commande
    """
    print("="*70)
    print("DYAG - Fine-Tuning avec LoRA")
    print("="*70)

    # Vérifier que le dataset existe
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"\n[ERREUR] Dataset non trouvé: {args.dataset}")
        return 1

    # Compter les exemples
    print(f"\nDataset: {args.dataset}")
    try:
        num_examples = count_dataset_examples(args.dataset)
        print(f"  Exemples: {num_examples}")
    except Exception as e:
        print(f"\n[ERREUR] Impossible de lire le dataset: {e}")
        return 1

    # Configuration
    print(f"\nConfiguration:")
    print(f"  Base model:    {args.base_model}")
    print(f"  Output:        {args.output}")
    print(f"  Epochs:        {args.epochs}")
    print(f"  Batch size:    {args.batch_size}")
    print(f"  LoRA rank:     {args.lora_rank}")
    print(f"  LoRA alpha:    {args.lora_alpha}")
    print(f"  Max seq len:   {args.max_seq_length}")

    # Vérifier la configuration système
    print(f"\nVérification système...")
    sys_info = check_system_requirements(args)

    print(f"  Device:        {sys_info['device']}")
    if sys_info['device'] == 'cuda':
        print(f"  GPU:           {sys_info['gpu_name']}")
        print(f"  VRAM:          {sys_info['vram_gb']:.1f} GB")

    # Warnings
    if sys_info['warnings']:
        print(f"\n[AVERTISSEMENTS]")
        for warning in sys_info['warnings']:
            print(f"  - {warning}")

    # Estimation durée
    estimated_time = estimate_training_time(
        num_examples,
        args.batch_size,
        args.epochs,
        sys_info['device']
    )
    print(f"\nDurée estimée: {estimated_time}")

    # Confirmation si CPU
    if sys_info['device'] == 'cpu' and not args.force_cpu:
        print("\n" + "="*70)
        print("[AVERTISSEMENT] Training sur CPU détecté")
        print("="*70)
        print("Le training sur CPU est EXTRÊMEMENT lent.")
        print(f"Durée estimée: {estimated_time}")
        print("\nRecommandations:")
        print("  1. Utilisez Google Colab avec GPU gratuit")
        print("  2. Ou ajoutez --force-cpu pour confirmer")
        print("="*70)
        return 1

    # Résoudre le nom du modèle
    from dyag.finetuning.core.model_registry import resolve_base_model, get_model_info

    resolved_model = resolve_base_model(args.base_model)
    print(f"\nModèle de base résolu: {resolved_model}")

    # Infos sur le modèle
    model_info = get_model_info(args.base_model)
    if model_info:
        print(f"  Paramètres:    {model_info['params']}")
        print(f"  VRAM min:      {model_info['vram_min_gb']} GB")
        print(f"  Description:   {model_info['description']}")

    # Créer le trainer
    print(f"\n" + "="*70)
    print("INITIALISATION DU TRAINER")
    print("="*70)

    try:
        from dyag.finetuning.core.trainer import LoRATrainer

        trainer = LoRATrainer(
            base_model=resolved_model,
            dataset_path=args.dataset,
            output_dir=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lora_rank=args.lora_rank,
            lora_alpha=args.lora_alpha,
            device=sys_info['device'],
            max_seq_length=args.max_seq_length
        )

        print(f"[OK] Trainer initialisé")
        print(f"  Device:        {trainer.device}")
        print(f"  Model family:  {trainer.detect_model_family()}")

    except Exception as e:
        print(f"\n[ERREUR] Impossible de créer le trainer: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    # Lancer le training
    print(f"\n" + "="*70)
    print("LANCEMENT DU TRAINING")
    print("="*70)

    if args.resume:
        print(f"Reprise depuis: {args.resume}")
        try:
            results = trainer.resume(args.resume)
        except NotImplementedError:
            print("\n[INFO] La fonctionnalité resume n'est pas encore implémentée")
            print("      Pour l'instant, seul le training from scratch est supporté")
            return 1
        except Exception as e:
            print(f"\n[ERREUR] Erreur lors de la reprise: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    else:
        try:
            results = trainer.train()
        except NotImplementedError:
            print("\n[INFO] L'implémentation du training est en cours...")
            print("      La commande CLI est prête mais la logique de training")
            print("      sera implémentée dans la prochaine étape.")
            print(f"\n[OK] Configuration validée:")
            print(f"  - Dataset:     {num_examples} exemples")
            print(f"  - Device:      {trainer.device}")
            print(f"  - Model:       {resolved_model}")
            print(f"  - Output:      {args.output}")
            print(f"  - Durée:       ~{estimated_time}")
            return 0
        except Exception as e:
            print(f"\n[ERREUR] Erreur lors du training: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1

    # Résultats
    print(f"\n" + "="*70)
    print("TRAINING TERMINÉ")
    print("="*70)
    print(f"Modèle sauvegardé: {args.output}")

    if results and args.verbose:
        print(f"\nRésultats:")
        for key, value in results.items():
            print(f"  {key}: {value}")

    print(f"\nProchaine étape:")
    print(f"  dyag query-finetuned --model {args.output}/final --base-model {args.base_model}")

    return 0
