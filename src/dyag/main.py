#!/usr/bin/env python3
"""
Main entry point for dyag application.
"""

import argparse
import sys

from dyag import __version__
from dyag.commands import (
    register_img2pdf_command,
    register_compresspdf_command,
    register_md2html_command,
    register_html2md_command,
    register_concat_html_command,
    register_add_toc_command,
    register_html2pdf_command,
    register_project2md_command,
    register_make_interactive_command,
    register_flatten_wikisi_command
)


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="dyag",
        description="Dyag - Outil de manipulation de fichiers et conversion",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"dyag {__version__}"
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(
        title="Commandes disponibles",
        description="Utilisez 'dyag <commande> -h' pour plus d'informations",
        dest="command",
        help="Commande à exécuter"
    )

    # Register commands
    register_img2pdf_command(subparsers)
    register_compresspdf_command(subparsers)
    register_md2html_command(subparsers)
    register_html2md_command(subparsers)
    register_concat_html_command(subparsers)
    register_add_toc_command(subparsers)
    register_html2pdf_command(subparsers)
    register_project2md_command(subparsers)
    register_make_interactive_command(subparsers)
    register_flatten_wikisi_command(subparsers)

    return parser


def main():
    """Main function to handle command-line arguments and application logic."""
    parser = create_parser()
    args = parser.parse_args()

    # If no command is provided, show help
    if args.command is None:
        parser.print_help()
        return 0

    # Execute the command
    if hasattr(args, 'func'):
        return args.func(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
