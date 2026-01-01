"""Commande fix-utf8 - Correction d'encodage et contenu de fichiers Markdown"""

import sys
from pathlib import Path
from typing import List

from ..core.fixer import fix_markdown_files
from ...core.pathglob import resolve_path_patterns


def run_fix_utf8(patterns: List[str], dry_run: bool = False, backup: bool = False, quiet: bool = False) -> int:
    """
    API programmatique pour fix-utf8.

    Args:
        patterns: Liste de motifs de fichiers
        dry_run: Simuler sans modifier
        backup: Créer backups
        quiet: Mode silencieux

    Returns:
        Code de sortie (0 = succès, 1 = erreur)
    """
    try:
        results = fix_markdown_files(patterns, dry_run=dry_run, backup=backup)
        errors = sum(1 for r in results if not r.get('success', False))
        return 1 if errors else 0
    except Exception:
        return 1


def main_cli() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Corrige l'encodage et le contenu des fichiers Markdown."
    )
    parser.add_argument(
        "--path-pattern", "-P",
        action="append",
        required=True,
        metavar="PATTERN",
        help="Motif(s) de fichiers Markdown (ex: 'si/**/*.md')"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simuler sans modifier les fichiers"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Créer un .bak avant modification"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="N'afficher que les erreurs"
    )

    args = parser.parse_args()

    try:
        all_paths = resolve_path_patterns(args.path_pattern, recursive=True)
    except Exception as e:
        print(f"❌ Échec résolution des motifs : {e}", file=sys.stderr)
        return 1

    md_paths = [
        p for p in all_paths
        if p.is_file() and p.suffix.lower() == ".md"
    ]

    if not md_paths:
        print("⚠️ Aucun fichier Markdown trouvé.", file=sys.stderr)
        return 1

    errors = 0
    for p in md_paths:
        from ..core.fixer import fix_file_encoding_and_content
        ok, msg = fix_file_encoding_and_content(p, dry_run=args.dry_run, backup=args.backup)
        if not ok:
            errors += 1
        if not args.quiet or not ok:
            icon = "  " if ok and args.quiet else ("✅" if ok else "❌")
            try:
                rel_path = p.relative_to(Path.cwd())
            except ValueError:
                rel_path = p
            print(f"{icon} {rel_path} → {msg}")

    if errors:
        print(f"\n❌ {errors} erreur(s)", file=sys.stderr)
        return 1
    else:
        print(f"\n✅ {len(md_paths)} fichier(s) traité(s)", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main_cli())
