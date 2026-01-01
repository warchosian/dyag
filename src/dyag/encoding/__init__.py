"""
Module de gestion d'encodage pour fichiers Markdown - DYAG

Ce module fournit des outils pour :
- Vérifier l'encodage des fichiers Markdown (chk_utf8)
- Corriger l'encodage et le contenu des fichiers Markdown (fix_utf8)

Architecture :
- core/ : Logique métier (checker, fixer)
- commands/ : Wrappers CLI (chk_utf8, fix_utf8)

Fonctions principales :
- check_md: Vérifie l'encodage d'un fichier
- check_markdown_files: API pour vérifier plusieurs fichiers
- fix_file_encoding_and_content: Corrige un fichier
- fix_markdown_files: API pour corriger plusieurs fichiers
"""

# Export depuis core/
from .core.checker import (
    check_md,
    check_markdown_files,
)

from .core.fixer import (
    fix_file_encoding_and_content,
    fix_markdown_files,
    decode_html_entities,
    fix_anchor_ids,
    encode_spaces_in_links,
    ensure_non_empty,
)

# Export CLI depuis commands/
from .commands.chk_utf8 import main_cli as check_md_cli
from .commands.fix_utf8 import main_cli as fix_md_cli

__all__ = [
    # Checker functions
    'check_md',
    'check_markdown_files',
    'check_md_cli',
    # Fixer functions
    'fix_file_encoding_and_content',
    'fix_markdown_files',
    'fix_md_cli',
    # Utility functions
    'decode_html_entities',
    'fix_anchor_ids',
    'encode_spaces_in_links',
    'ensure_non_empty',
]
