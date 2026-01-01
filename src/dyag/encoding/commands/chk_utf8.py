"""Commande chk-utf8 - Vérification d'encodage de fichiers Markdown"""

import sys
from pathlib import Path
from typing import List

from ..core.checker import check_markdown_files
from ...core.pathglob import resolve_path_patterns


def run_chk_utf8(patterns: List[str], min_confidence: float = 0.7, quiet: bool = False) -> int:
    """
    API programmatique pour chk-utf8.

    Args:
        patterns: Liste de motifs de fichiers
        min_confidence: Seuil de confiance minimal
        quiet: Mode silencieux

    Returns:
        Code de sortie (0 = succès, 1 = erreur)
    """
    try:
        results = check_markdown_files(patterns)

        has_issue = False
        for res in results:
            encoding = res.get('encoding') or 'inconnu'
            confidence = res.get('confidence', 0.0)
            error = res.get('error')

            # Afficher résultat si pas quiet ou si problème
            if not quiet:
                status = "❌" if error else ("⚠️ " if confidence < min_confidence else "✅")
                print(f"{status} {res['path']}")
                if error:
                    print(f"    → Erreur: {error}")
                else:
                    print(f"    → Encodage: {encoding} (confiance: {confidence:.2%})")

            # Détecter problèmes
            if error or (encoding and encoding.upper() not in ("UTF-8", "UTF8", "ASCII")) or confidence < min_confidence:
                has_issue = True
                if quiet:
                    print(f"⚠️  {res['path']}: {encoding} ({confidence:.0%})", file=sys.stderr)

        return 1 if has_issue else 0

    except Exception:
        return 1


def main_cli() -> int:
    """CLI entry point — retourne le code de sortie (0 = OK, 1 = erreur)."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Vérifie l'encodage de fichiers Markdown (supporte les globs)."
    )
    parser.add_argument(
        "--path-pattern", "-P",
        action="append",
        required=True,
        metavar="PATTERN",
        help="Motif(s) de chemin(s) Markdown (ex: '*.md', 'docs/**/*.md')"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Seuil minimal de confiance (défaut: 0.7)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Mode silencieux : n'affiche que les erreurs"
    )

    args = parser.parse_args()

    # Résolution des motifs → chemins concrets
    try:
        all_paths = resolve_path_patterns(args.path_pattern, recursive=True)
    except (ValueError, OSError) as e:
        print(f"❌ Échec de la résolution des motifs : {e}", file=sys.stderr)
        return 1

    # Filtrer *seulement* les fichiers .md
    md_paths = [
        p for p in all_paths
        if p.is_file() and p.suffix.lower() == ".md"
    ]

    if not md_paths:
        print("⚠️  Aucun fichier Markdown (.md) trouvé.", file=sys.stderr)
        return 1

    # Utiliser run_chk_utf8
    patterns = [str(p) for p in md_paths]
    return run_chk_utf8(patterns, min_confidence=args.min_confidence, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main_cli())
