"""Core logic for encoding detection and correction - DYAG"""

from .checker import check_md, check_markdown_files
from .fixer import (
    decode_html_entities,
    fix_anchor_ids,
    encode_spaces_in_links,
    ensure_non_empty,
    fix_file_encoding_and_content,
    fix_markdown_files
)

__all__ = [
    # Checker functions
    'check_md',
    'check_markdown_files',
    # Fixer functions
    'decode_html_entities',
    'fix_anchor_ids',
    'encode_spaces_in_links',
    'ensure_non_empty',
    'fix_file_encoding_and_content',
    'fix_markdown_files',
]
