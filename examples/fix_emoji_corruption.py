#!/usr/bin/env python3
"""
Exemple : Corriger les emojis corrompus dans des fichiers Markdown

Usage:
    python fix_emoji_corruption.py fichier.md
    python fix_emoji_corruption.py directory/
    python fix_emoji_corruption.py "*.md"
"""

import sys
from pathlib import Path
from dyag.analysis.core.encoding_fixer import EncodingFixer


def fix_single_file(file_path: Path, backup: bool = True, verbose: bool = True):
    """Corrige un seul fichier"""

    if verbose:
        print(f"\n{'='*60}")
        print(f"Fichier: {file_path}")
        print(f"{'='*60}")

    fixer = EncodingFixer()

    try:
        # 1. Détecter l'encodage
        encoding_info = EncodingFixer.detect_encoding(str(file_path))
        if verbose:
            print(f"[DETECT] Encodage: {encoding_info[0]} (confiance: {encoding_info[1]:.2%})")

        # 2. Lire le contenu
        content, used_encoding = fixer.read_with_fallback(str(file_path), verbose=verbose)

        # 3. Détecter les emojis corrompus
        corrupted_emojis = []
        for corrupted, correct in fixer.EMOJI_FIXES.items():
            if corrupted in content and corrupted != correct:
                count = content.count(corrupted)
                corrupted_emojis.append((corrupted, correct, count))

        if not corrupted_emojis:
            if verbose:
                print("[OK] Aucun emoji corrompu détecté")
            return True

        # 4. Afficher les corruptions trouvées
        if verbose:
            print(f"\n[FOUND] {len(corrupted_emojis)} type(s) d'emojis corrompus:")
            for corr, fix, count in corrupted_emojis:
                print(f"  - {repr(corr)} -> {repr(fix)} ({count} occurrence(s))")

        # 5. Créer un backup si demandé
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            backup_path.write_text(content, encoding='utf-8')
            if verbose:
                print(f"[BACKUP] Sauvegardé: {backup_path}")

        # 6. Corriger le contenu
        fixed_content = fixer.normalize_content(content, aggressive=False)

        # 7. Vérifier si des changements ont été faits
        if fixed_content == content:
            if verbose:
                print("[WARNING] Aucun changement après normalisation")
            return True

        # 8. Sauvegarder
        file_path.write_text(fixed_content, encoding='utf-8')

        if verbose:
            print(f"[SUCCESS] Fichier corrigé et sauvegardé en UTF-8")

        # 9. Afficher un diff rapide
        if verbose:
            changes = sum(1 for old, new in zip(content, fixed_content) if old != new)
            print(f"[STATS] {changes} caractère(s) modifié(s)")

        return True

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def fix_directory(directory: Path, pattern: str = "*.md", backup: bool = True):
    """Corrige tous les fichiers MD d'un répertoire"""

    print(f"\n[SCAN] Recherche de {pattern} dans {directory}")

    files = list(directory.rglob(pattern)) if '**' not in pattern else list(directory.glob(pattern))

    if not files:
        print("[WARNING] Aucun fichier trouvé")
        return

    print(f"[INFO] {len(files)} fichier(s) trouvé(s)\n")

    success_count = 0
    error_count = 0

    for file_path in files:
        if file_path.suffix == '.bak':
            continue  # Ignorer les backups

        success = fix_single_file(file_path, backup=backup, verbose=True)
        if success:
            success_count += 1
        else:
            error_count += 1

    # Résumé
    print(f"\n{'='*60}")
    print(f"RÉSUMÉ")
    print(f"{'='*60}")
    print(f"✓ Succès: {success_count}")
    if error_count:
        print(f"✗ Erreurs: {error_count}")
    print()


def main():
    """Point d'entrée principal"""

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    backup = '--no-backup' not in sys.argv

    path = Path(target)

    if path.is_file():
        # Fichier unique
        success = fix_single_file(path, backup=backup, verbose=True)
        sys.exit(0 if success else 1)

    elif path.is_dir():
        # Répertoire
        fix_directory(path, pattern="**/*.md", backup=backup)
        sys.exit(0)

    else:
        # Pattern glob
        base_dir = Path('.')
        pattern = target

        matching_files = list(base_dir.glob(pattern))
        if not matching_files:
            print(f"[ERROR] Aucun fichier trouvé pour le pattern: {pattern}")
            sys.exit(1)

        for file_path in matching_files:
            if file_path.is_file():
                fix_single_file(file_path, backup=backup, verbose=True)

        sys.exit(0)


if __name__ == "__main__":
    main()
