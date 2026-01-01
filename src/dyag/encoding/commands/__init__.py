"""Commandes d'encodage pour fichiers Markdown - DYAG"""

from .chk_utf8 import run_chk_utf8, main_cli as chk_utf8_cli
from .fix_utf8 import run_fix_utf8, main_cli as fix_utf8_cli


def register_chk_utf8_command(subparsers):
    """Register chk-utf8 command"""
    parser = subparsers.add_parser(
        "chk-utf8",
        help="Vérifier l'encodage de fichiers Markdown"
    )

    parser.add_argument(
        "--path-pattern", "-P",
        action="append",
        required=True,
        help="Motif(s) de fichiers Markdown (ex: '*.md', 'docs/**/*.md')"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Seuil minimal de confiance pour l'encodage (défaut: 0.7)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Mode silencieux: afficher seulement les problèmes"
    )

    def wrapper(args):
        exit_code = run_chk_utf8(
            patterns=args.path_pattern,
            min_confidence=args.min_confidence,
            quiet=args.quiet
        )
        return exit_code

    parser.set_defaults(func=wrapper)


def register_fix_utf8_command(subparsers):
    """Register fix-utf8 command"""
    parser = subparsers.add_parser(
        "fix-utf8",
        help="Corriger l'encodage et le contenu de fichiers Markdown"
    )

    parser.add_argument(
        "--path-pattern", "-P",
        action="append",
        required=True,
        help="Motif(s) de fichiers Markdown (ex: '*.md', 'docs/**/*.md')"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simuler sans modifier les fichiers"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Créer un fichier .bak avant modification"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Mode silencieux: afficher seulement les erreurs"
    )

    def wrapper(args):
        exit_code = run_fix_utf8(
            patterns=args.path_pattern,
            dry_run=args.dry_run,
            backup=args.backup,
            quiet=args.quiet
        )
        return exit_code

    parser.set_defaults(func=wrapper)


__all__ = [
    "run_chk_utf8",
    "run_fix_utf8",
    "chk_utf8_cli",
    "fix_utf8_cli",
    "register_chk_utf8_command",
    "register_fix_utf8_command",
]
