"""
Commande pour détecter et corriger les problèmes d'encodage dans les fichiers Markdown.
"""

import click
from pathlib import Path
from dyag.analysis.core.encoding_fixer import EncodingFixer, detect_file_encoding


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='Fichier de sortie (défaut: overwrite input)')
@click.option('-e', '--encoding', default='utf-8', help='Encodage cible (défaut: utf-8)')
@click.option('--detect-only', is_flag=True, help='Seulement détecter l\'encodage, sans conversion')
@click.option('--no-fix-emojis', is_flag=True, help='Ne pas corriger les emojis')
@click.option('-v', '--verbose', is_flag=True, help='Mode verbeux')
def fix_encoding(input_file, output, encoding, detect_only, no_fix_emojis, verbose):
    """
    Détecte et corrige les problèmes d'encodage dans les fichiers Markdown.

    Exemples:

    \b
    # Détecter l'encodage d'un fichier
    dyag fix-encoding fichier.md --detect-only

    \b
    # Convertir en UTF-8 et corriger les emojis
    dyag fix-encoding fichier.md -o fichier_fixed.md

    \b
    # Convertir en place (overwrite)
    dyag fix-encoding fichier.md
    """
    try:
        if detect_only:
            # Mode détection seulement
            info = detect_file_encoding(input_file)
            click.echo(f"\n[INFO] Analyse de: {input_file}")
            click.echo(f"  Encodage détecté: {info['encoding']}")
            click.echo(f"  Confiance: {info['confidence']:.2%}")
            if info['bom']:
                click.echo(f"  BOM: {info['bom']}")

            # Afficher un aperçu
            fixer = EncodingFixer()
            content, used_encoding = fixer.read_with_fallback(input_file, verbose=verbose)
            click.echo(f"  Encodage utilisé: {used_encoding}")
            click.echo(f"  Taille: {len(content)} caractères")

            # Détecter les emojis corrompus
            corrupted_count = sum(1 for emoji in fixer.EMOJI_FIXES.keys() if emoji in content)
            if corrupted_count > 0:
                click.echo(f"  ⚠ {corrupted_count} type(s) d'emojis corrompus détectés")

            return

        # Mode conversion
        output_file = output or input_file

        click.echo(f"[INFO] Conversion: {input_file} → {output_file}")

        success = EncodingFixer.convert_file(
            input_path=input_file,
            output_path=output_file,
            target_encoding=encoding,
            fix_emojis=not no_fix_emojis,
            verbose=verbose
        )

        if success:
            click.echo(f"[SUCCESS] Fichier converti avec succès")
            if input_file == output_file:
                click.echo(f"[WARNING] Fichier original écrasé")
        else:
            click.echo(f"[ERROR] Échec de la conversion", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"[ERROR] {str(e)}", err=True)
        raise click.Abort()
