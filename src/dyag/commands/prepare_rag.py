"""
Command to prepare a merged Markdown file for RAG (Retrieval-Augmented Generation).

This module cleans up merged Markdown files by:
- Removing the table of contents
- Removing HTML anchors
- Cleaning internal and relative links
- Optionally handling external links
- Removing navigation noise and repeated menus
- Optionally chunking the content
- Optionally extracting metadata to JSON

Example:
    dyag prepare-rag merged-tocced.md -o rag-ready.md --extract-json
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional


def remove_toc(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Remove the table of contents from the beginning of the document.

    The TOC ends when we find the first content anchor that is not
    'table-des-matières'.

    Args:
        content: Full document content
        verbose: Print progress

    Returns:
        Tuple of (content without TOC, number of lines removed)
    """
    lines = content.split('\n')

    # Find the first anchor that is not the TOC itself
    toc_anchor_pattern = re.compile(r'^<a id="table-des-mati[èe]res"></a>$')
    content_anchor_pattern = re.compile(r'^<a id="[^"]+"></a>$')

    toc_end_idx = 0
    found_toc_anchor = False

    for idx, line in enumerate(lines):
        # Check if this is the TOC anchor
        if toc_anchor_pattern.match(line):
            found_toc_anchor = True
            continue

        # After finding TOC anchor, look for the first content anchor
        if found_toc_anchor and content_anchor_pattern.match(line):
            toc_end_idx = idx
            break

    if toc_end_idx > 0:
        removed_lines = toc_end_idx
        if verbose:
            print(f"[INFO] Removed TOC: {removed_lines} lines")
        return '\n'.join(lines[toc_end_idx:]), removed_lines

    if verbose:
        print("[WARNING] No TOC found to remove")
    return content, 0


def remove_html_anchors(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Remove HTML anchors like <a id="..."></a>.

    Args:
        content: Document content
        verbose: Print progress

    Returns:
        Tuple of (cleaned content, number of anchors removed)
    """
    anchor_pattern = r'<a id="[^"]+"></a>\n?'
    matches = re.findall(anchor_pattern, content)
    count = len(matches)

    cleaned = re.sub(anchor_pattern, '', content)

    if verbose and count > 0:
        print(f"[INFO] Removed {count} HTML anchors")

    return cleaned, count


def clean_internal_links(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Clean internal markdown links [text](#anchor) → text.

    Args:
        content: Document content
        verbose: Print progress

    Returns:
        Tuple of (cleaned content, number of links cleaned)
    """
    pattern = r'\[([^\]]+)\]\(#[^\)]+\)'
    matches = re.findall(pattern, content)
    count = len(matches)

    cleaned = re.sub(pattern, r'\1', content)

    if verbose and count > 0:
        print(f"[INFO] Cleaned {count} internal links")

    return cleaned, count


def clean_relative_links(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Clean relative links to .md files [text](file.md) → text.

    Args:
        content: Document content
        verbose: Print progress

    Returns:
        Tuple of (cleaned content, number of links cleaned)
    """
    pattern = r'\[([^\]]+)\]\([^\)]*\.md[^\)]*\)'
    matches = re.findall(pattern, content)
    count = len(matches)

    cleaned = re.sub(pattern, r'\1', content)

    if verbose and count > 0:
        print(f"[INFO] Cleaned {count} relative links")

    return cleaned, count


def clean_external_links(content: str, keep_urls: bool = False, verbose: bool = False) -> Tuple[str, int]:
    """
    Clean external links.

    Args:
        content: Document content
        keep_urls: If True, keep URLs in parentheses; if False, remove them
        verbose: Print progress

    Returns:
        Tuple of (cleaned content, number of links processed)
    """
    pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    matches = re.findall(pattern, content)
    count = len(matches)

    if keep_urls:
        # [text](https://url) → text (https://url)
        cleaned = re.sub(pattern, r'\1 (\2)', content)
    else:
        # [text](https://url) → text
        cleaned = re.sub(pattern, r'\1', content)

    if verbose and count > 0:
        action = "kept" if keep_urls else "removed"
        print(f"[INFO] Processed {count} external links (URLs {action})")

    return cleaned, count


def remove_navigation_noise(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Remove navigation noise and repeated menu items.

    Args:
        content: Document content
        verbose: Print progress

    Returns:
        Tuple of (cleaned content, number of lines removed)
    """
    lines = content.split('\n')

    # Patterns to identify noise lines
    noise_patterns = [
        r'^\s*Fermer\s*$',
        r'^\s*Aller au\s*$',
        r'^\s*Wiki SI - v\d+\.\d+.*$',
        r'^\s*Menu\s+Réduire\s+Non connecté\s*$',
        r'^\s*Afficher le moteur de recherche.*$',
        r'^\s*Je recherche.*$',
        r'^\s*Publié le.*Mis à jour le.*$',
        r'^\s*\*\*Source :\*\*`[^`]+`.*$',
        # Repeated "Ajouter un outil" sections (keep only title, remove empty content)
        r'^\s*##\s*Ajouter un outil\s*$',
        r'^\s*##\s*Ajouter un intranet\s*$',
    ]

    # Compile patterns
    compiled_patterns = [re.compile(p) for p in noise_patterns]

    cleaned_lines = []
    removed_count = 0

    for line in lines:
        # Check if line matches any noise pattern
        is_noise = any(pattern.match(line) for pattern in compiled_patterns)

        if not is_noise:
            cleaned_lines.append(line)
        else:
            removed_count += 1

    if verbose and removed_count > 0:
        print(f"[INFO] Removed {removed_count} noise lines")

    return '\n'.join(cleaned_lines), removed_count


def remove_repeated_menus(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Remove repeated navigation menus that appear in each page.

    Args:
        content: Document content
        verbose: Print progress

    Returns:
        Tuple of (cleaned content, number of menu blocks removed)
    """
    # Pattern to match the repeated menu block
    # This is the menu that appears after each page source
    menu_pattern = r'- \[Menu\]\(#site-navigation\)\n- \[Contenu\]\(#main\)\n- \[Recherche\]\(#searchbox\)'

    matches = re.findall(menu_pattern, content)
    count = len(matches)

    cleaned = re.sub(menu_pattern, '', content)

    # Also remove the expanded menu items
    expanded_menu_pattern = r'-\s+\[\s*Le Portail\s*\].*?\n-\s+Mes intranets.*?\n\n-\s+Mes outils.*?\n\n.*?Fermer'
    cleaned = re.sub(expanded_menu_pattern, '', cleaned, flags=re.DOTALL)

    if verbose and count > 0:
        print(f"[INFO] Removed {count} repeated menu blocks")

    return cleaned, count


def normalize_whitespace(content: str, verbose: bool = False) -> Tuple[str, int]:
    """
    Normalize excessive whitespace.

    - Remove multiple consecutive blank lines (keep max 2)
    - Remove trailing whitespace on lines

    Args:
        content: Document content
        verbose: Print progress

    Returns:
        Tuple of (normalized content, number of blank lines removed)
    """
    # Remove trailing whitespace
    content = '\n'.join(line.rstrip() for line in content.split('\n'))

    # Count blank lines before normalization
    blank_before = content.count('\n\n\n')

    # Replace 3+ consecutive newlines with 2
    while '\n\n\n' in content:
        content = content.replace('\n\n\n', '\n\n')

    blank_after = content.count('\n\n\n')
    removed = blank_before - blank_after

    if verbose and removed > 0:
        print(f"[INFO] Normalized whitespace ({removed} excess blank lines removed)")

    return content, removed


def extract_sections(content: str, verbose: bool = False) -> List[Dict[str, str]]:
    """
    Extract distinct sections from the content.

    A section is identified by ## 📄 marker followed by the source filename.

    Args:
        content: Cleaned document content
        verbose: Print progress

    Returns:
        List of section dictionaries with 'id', 'title', 'source', 'content'
    """
    sections = []

    # Pattern to match section markers: ## 📄 path › to › file
    section_pattern = r'^## 📄 (.+)$'

    lines = content.split('\n')
    current_section = None
    current_lines = []
    section_id = 0

    for line in lines:
        match = re.match(section_pattern, line)

        if match:
            # Save previous section
            if current_section:
                sections.append({
                    'id': f'chunk_{section_id}',
                    'title': current_section,
                    'source': current_section,
                    'content': '\n'.join(current_lines).strip()
                })
                section_id += 1

            # Start new section
            current_section = match.group(1)
            current_lines = []
        else:
            if current_section:
                current_lines.append(line)

    # Save last section
    if current_section:
        sections.append({
            'id': f'chunk_{section_id}',
            'title': current_section,
            'source': current_section,
            'content': '\n'.join(current_lines).strip()
        })

    if verbose:
        print(f"[INFO] Extracted {len(sections)} sections")

    return sections


def extract_markdown_sections(content: str, verbose: bool = False) -> List[Dict[str, str]]:
    """
    Extract sections based on standard Markdown ## headers (level 2).

    This mode is designed for standard Markdown files where:
    - # is the main title (level 1)
    - ## are section headers (level 2) that define chunk boundaries

    Args:
        content: Cleaned document content
        verbose: Print progress

    Returns:
        List of section dictionaries with 'id', 'title', 'source', 'content'
    """
    sections = []

    # Pattern to match level 2 headers: ## Title
    # Matches: "## " followed by any text, but NOT "### " (level 3+)
    section_pattern = r'^## ([^#].*)$'

    lines = content.split('\n')
    current_section = None
    current_lines = []
    section_id = 0

    for line in lines:
        match = re.match(section_pattern, line)

        if match:
            # Save previous section
            if current_section:
                sections.append({
                    'id': f'chunk_{section_id}',
                    'title': current_section,
                    'source': current_section,
                    'content': '\n'.join(current_lines).strip()
                })
                section_id += 1

            # Start new section
            current_section = match.group(1).strip()
            current_lines = []
        else:
            # Only collect content if we're inside a section
            if current_section:
                current_lines.append(line)

    # Save last section
    if current_section:
        sections.append({
            'id': f'chunk_{section_id}',
            'title': current_section,
            'source': current_section,
            'content': '\n'.join(current_lines).strip()
        })

    if verbose:
        print(f"[INFO] Extracted {len(sections)} markdown sections (## headers)")

    return sections


def validate_chunks(data: Dict, verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate the structure of chunks JSON data.

    Checks:
    - Required top-level keys (metadata, chunks)
    - Each chunk has required fields (title, source, content)
    - IDs are strings if present
    - No empty chunks
    - Content is not too large

    Args:
        data: The JSON data structure to validate
        verbose: Print detailed validation messages

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check top-level structure
    if not isinstance(data, dict):
        errors.append("Root structure must be a dictionary")
        return False, errors

    if 'metadata' not in data:
        errors.append("Missing required key: 'metadata'")

    if 'chunks' not in data:
        errors.append("Missing required key: 'chunks'")
        return False, errors

    chunks = data.get('chunks', [])
    if not isinstance(chunks, list):
        errors.append("'chunks' must be a list")
        return False, errors

    if len(chunks) == 0:
        errors.append("No chunks found in data")
        return False, errors

    # Validate each chunk
    for i, chunk in enumerate(chunks):
        chunk_num = i + 1

        if not isinstance(chunk, dict):
            errors.append(f"Chunk {chunk_num}: must be a dictionary")
            continue

        # Check required fields
        required_fields = ['title', 'source', 'content']
        for field in required_fields:
            if field not in chunk:
                errors.append(f"Chunk {chunk_num}: missing required field '{field}'")

        # Validate ID type if present
        if 'id' in chunk:
            chunk_id = chunk['id']
            if not isinstance(chunk_id, str):
                errors.append(f"Chunk {chunk_num}: 'id' must be a string, got {type(chunk_id).__name__} (value: {chunk_id})")

        # Check for empty content
        if 'content' in chunk:
            content = chunk['content']
            if not isinstance(content, str):
                errors.append(f"Chunk {chunk_num}: 'content' must be a string")
            elif len(content.strip()) == 0:
                errors.append(f"Chunk {chunk_num}: empty content")
            elif len(content) > 50000:
                errors.append(f"Chunk {chunk_num}: content too large ({len(content)} chars)")

    if verbose:
        print(f"\n{'='*70}")
        print(f"CHUNK VALIDATION")
        print(f"{'='*70}")
        print(f"Total chunks:        {len(chunks)}")
        print(f"Errors found:        {len(errors)}")
        if errors:
            print(f"\nErrors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"Status:              OK - All checks passed")
        print(f"{'='*70}\n")

    return len(errors) == 0, errors


def chunk_by_size(content: str, chunk_size: int = 2000, overlap: int = 200, verbose: bool = False) -> List[Dict[str, any]]:
    """
    Split content into chunks of approximately chunk_size characters.

    Args:
        content: Content to chunk
        chunk_size: Target size for each chunk in characters
        overlap: Number of characters to overlap between chunks
        verbose: Print progress

    Returns:
        List of chunk dictionaries
    """
    chunks = []

    # Split by paragraphs (double newline)
    paragraphs = content.split('\n\n')

    current_chunk = []
    current_size = 0
    chunk_id = 0

    for para in paragraphs:
        para_size = len(para)

        if current_size + para_size > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                'id': f'chunk_{chunk_id}',
                'content': '\n\n'.join(current_chunk),
                'size': current_size
            })
            chunk_id += 1

            # Start new chunk with overlap (keep last paragraph)
            if overlap > 0 and current_chunk:
                current_chunk = [current_chunk[-1]]
                current_size = len(current_chunk[-1])
            else:
                current_chunk = []
                current_size = 0

        current_chunk.append(para)
        current_size += para_size

    # Save last chunk
    if current_chunk:
        chunks.append({
            'id': f'chunk_{chunk_id}',
            'content': '\n\n'.join(current_chunk),
            'size': current_size
        })

    if verbose:
        print(f"[INFO] Created {len(chunks)} chunks (avg size: {sum(c['size'] for c in chunks) // len(chunks)} chars)")

    return chunks


def prepare_for_rag(
    input_path: str,
    output_path: Optional[str] = None,
    keep_external_urls: bool = False,
    chunk_mode: str = 'none',
    chunk_size: int = 2000,
    chunk_overlap: int = 200,
    extract_json: bool = False,
    check: bool = False,
    verbose: bool = False
) -> int:
    """
    Prepare a merged Markdown file for RAG ingestion.

    Args:
        input_path: Path to input Markdown file
        output_path: Optional path to output file. Default: <input>-rag.md
        keep_external_urls: Keep external URLs in output
        chunk_mode: Chunking mode - 'none', 'section', or 'size'
        chunk_size: Target chunk size in characters (for 'size' mode)
        chunk_overlap: Overlap between chunks in characters (for 'size' mode)
        extract_json: Also output metadata as JSON
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_file = Path(input_path).resolve()

    # Check if input file exists
    if not input_file.exists():
        print(f"[ERROR] Input file '{input_path}' does not exist.", file=sys.stderr)
        return 1

    if not input_file.is_file():
        print(f"[ERROR] '{input_path}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_file = input_file.parent / f"{input_file.stem}-rag.md"
    else:
        output_file = Path(output_path).resolve()

    if verbose:
        print(f"[INFO] Processing: {input_file}")
        print(f"[INFO] Output: {output_file}")

    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_size = len(content)
        original_lines = len(content.split('\n'))

        if verbose:
            print(f"\n[INFO] Original file: {original_lines} lines, {original_size:,} characters")
            print("\n" + "="*70)
            print("CLEANING PROCESS")
            print("="*70)

        # Step 1: Remove TOC
        content, toc_removed = remove_toc(content, verbose)

        # Step 2: Remove HTML anchors
        content, anchors_removed = remove_html_anchors(content, verbose)

        # Step 3: Clean internal links
        content, internal_links = clean_internal_links(content, verbose)

        # Step 4: Clean relative links
        content, relative_links = clean_relative_links(content, verbose)

        # Step 5: Clean external links
        content, external_links = clean_external_links(content, keep_external_urls, verbose)

        # Step 6: Remove navigation noise
        content, noise_removed = remove_navigation_noise(content, verbose)

        # Step 7: Remove repeated menus
        content, menus_removed = remove_repeated_menus(content, verbose)

        # Step 8: Normalize whitespace
        content, whitespace_normalized = normalize_whitespace(content, verbose)

        cleaned_size = len(content)
        cleaned_lines = len(content.split('\n'))

        if verbose:
            print("\n" + "="*70)
            print("CHUNKING" if chunk_mode != 'none' else "SAVING")
            print("="*70)

        # Chunking
        output_data = None
        metadata = {
            'source_file': str(input_file),
            'original_size': original_size,
            'original_lines': original_lines,
            'cleaned_size': cleaned_size,
            'cleaned_lines': cleaned_lines,
            'stats': {
                'toc_lines_removed': toc_removed,
                'html_anchors_removed': anchors_removed,
                'internal_links_cleaned': internal_links,
                'relative_links_cleaned': relative_links,
                'external_links_processed': external_links,
                'noise_lines_removed': noise_removed,
                'menu_blocks_removed': menus_removed,
                'whitespace_normalized': whitespace_normalized
            }
        }

        if chunk_mode == 'section':
            sections = extract_sections(content, verbose)
            output_data = {
                'metadata': metadata,
                'chunks': sections
            }

            # Write sections as markdown
            sections_md = []
            for i, section in enumerate(sections, 1):
                sections_md.append(f"## Section {i}: {section['title']}\n\n{section['content']}")
            content = '\n\n---\n\n'.join(sections_md)

        elif chunk_mode == 'markdown-headers':
            sections = extract_markdown_sections(content, verbose)
            output_data = {
                'metadata': metadata,
                'chunks': sections
            }

            # Write sections as markdown
            sections_md = []
            for i, section in enumerate(sections, 1):
                sections_md.append(f"## Section {i}: {section['title']}\n\n{section['content']}")
            content = '\n\n---\n\n'.join(sections_md)

        elif chunk_mode == 'size':
            chunks = chunk_by_size(content, chunk_size, chunk_overlap, verbose)
            output_data = {
                'metadata': metadata,
                'chunks': chunks
            }

            # Write chunks as markdown
            chunks_md = []
            for chunk in chunks:
                chunks_md.append(f"## Chunk {chunk['id']} ({chunk['size']} chars)\n\n{chunk['content']}")
            content = '\n\n---\n\n'.join(chunks_md)
        else:
            # No chunking
            output_data = {
                'metadata': metadata,
                'content': content
            }

        # Write output markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Write JSON metadata if requested
        if extract_json:
            json_file = output_file.with_suffix('.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            if verbose:
                print(f"[INFO] JSON metadata written to: {json_file}")

            # Validate chunks if requested
            if check:
                if chunk_mode == 'none':
                    print(f"[WARNING] --check requires chunking mode (section, markdown-headers, or size)")
                else:
                    is_valid, errors = validate_chunks(output_data, verbose)
                    if not is_valid:
                        print(f"[ERROR] Chunk validation failed with {len(errors)} error(s):", file=sys.stderr)
                        for error in errors:
                            print(f"  - {error}", file=sys.stderr)
                        return 1

        # Summary
        reduction_pct = ((original_size - cleaned_size) / original_size * 100) if original_size > 0 else 0

        print(f"\n{'='*70}")
        print(f"PREPARATION COMPLETE")
        print(f"{'='*70}")
        print(f"Input file:          {input_file.name}")
        print(f"Output file:         {output_file}")
        print(f"Original size:       {original_lines:,} lines, {original_size:,} chars")
        print(f"Cleaned size:        {cleaned_lines:,} lines, {cleaned_size:,} chars")
        print(f"Reduction:           {reduction_pct:.1f}%")
        print(f"Chunk mode:          {chunk_mode}")
        if chunk_mode == 'section':
            print(f"Sections extracted:  {len(output_data['chunks'])}")
        elif chunk_mode == 'markdown-headers':
            print(f"Markdown sections:   {len(output_data['chunks'])}")
        elif chunk_mode == 'size':
            print(f"Chunks created:      {len(output_data['chunks'])}")
        print(f"{'='*70}\n")

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to prepare file: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def register_prepare_rag_command(subparsers):
    """
    Register the prepare-rag command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'prepare-rag',
        help='Prepare a merged Markdown file for RAG ingestion',
        description='Clean and prepare a merged Markdown file for use with RAG systems by removing TOC, links, navigation noise, and optionally chunking the content.'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Input Markdown file (typically merged-tocced.md)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path (default: <input>-rag.md)'
    )

    parser.add_argument(
        '--keep-urls',
        action='store_true',
        help='Keep external URLs in output (default: remove them)'
    )

    parser.add_argument(
        '--chunk',
        type=str,
        choices=['none', 'section', 'markdown-headers', 'size'],
        default='none',
        help='Chunking mode: none (default), section (merged docs with ## 📄), markdown-headers (standard ## headers), size (by character count)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=2000,
        help='Target chunk size in characters for size-based chunking (default: 2000)'
    )

    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=200,
        help='Overlap between chunks in characters (default: 200)'
    )

    parser.add_argument(
        '--extract-json',
        action='store_true',
        help='Also export metadata and chunks to JSON file'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Validate chunk structure after generation (requires --extract-json)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: prepare_for_rag(
        args.input,
        args.output,
        args.keep_urls,
        args.chunk,
        args.chunk_size,
        args.chunk_overlap,
        args.extract_json,
        args.check,
        args.verbose
    ))


if __name__ == '__main__':
    # Allow running as standalone script
    import argparse
    parser = argparse.ArgumentParser(
        description="Prepare a merged Markdown file for RAG ingestion"
    )
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--keep-urls', action='store_true')
    parser.add_argument('--chunk', choices=['none', 'section', 'markdown-headers', 'size'], default='none')
    parser.add_argument('--chunk-size', type=int, default=2000)
    parser.add_argument('--chunk-overlap', type=int, default=200)
    parser.add_argument('--extract-json', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    sys.exit(prepare_for_rag(
        args.input,
        args.output,
        args.keep_urls,
        args.chunk,
        args.chunk_size,
        args.chunk_overlap,
        args.extract_json,
        args.check,
        args.verbose
    ))
