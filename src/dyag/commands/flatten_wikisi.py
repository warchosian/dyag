


"""
Command to flatten a wikisi directory structure.

This module copies all index.html files from a nested wikisi directory structure
to a flat directory with filenames based on their paths.

Examples:
    agent/index.html → agent.html
    api/application/index.html → api-application.html
    donnee/1/historique/index.html → donnee-1-historique.html
"""

import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from collections import defaultdict


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use in filenames.

    Replaces invalid filename characters with underscores.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string safe for filenames
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name


def flatten_path(relative_path: Path, root_name: str = "index") -> str:
    """
    Convert a relative path to a flattened filename.

    Examples:
        agent/index.html → agent.html
        api/application/index.html → api-application.html
        index.html → index.html (or {root_name}.html)

    Args:
        relative_path: Path relative to wikisi root
        root_name: Name to use for root index.html (without extension)

    Returns:
        Flattened filename with .html extension
    """
    parts = list(relative_path.parts)

    # Remove 'index.html' from end
    if parts and parts[-1].lower() == 'index.html':
        parts = parts[:-1]

    # Handle root index.html
    if not parts:
        return f"{root_name}.html"

    # Sanitize each part
    sanitized_parts = [sanitize_filename(part) for part in parts]

    # Join with hyphen and add extension
    flattened = '-'.join(sanitized_parts) + '.html'

    return flattened


def collect_index_files(
    wikisi_dir: Path,
    root_name: str = "index",
    verbose: bool = False
) -> List[Tuple[Path, str]]:
    """
    Collect all index.html files and their flattened names.

    Args:
        wikisi_dir: Root wikisi directory
        root_name: Name for root index.html
        verbose: Print progress

    Returns:
        List of (source_path, flattened_name) tuples
    """
    files = []

    # Find all index.html files
    index_files = list(wikisi_dir.rglob('index.html'))

    if verbose:
        print(f"[INFO] Found {len(index_files)} index.html files")

    for file_path in index_files:
        # Get relative path
        rel_path = file_path.relative_to(wikisi_dir)

        # Generate flattened name
        flattened_name = flatten_path(rel_path, root_name)

        files.append((file_path, flattened_name))

        if verbose:
            print(f"  {rel_path} -> {flattened_name}")

    return files


def check_duplicates(files: List[Tuple[Path, str]]) -> Optional[Dict[str, List[Path]]]:
    """
    Check for duplicate flattened filenames.

    Args:
        files: List of (source_path, flattened_name) tuples

    Returns:
        None if no duplicates, otherwise dict mapping duplicate names to source paths
    """
    name_to_sources = defaultdict(list)

    for source_path, flattened_name in files:
        name_to_sources[flattened_name].append(source_path)

    duplicates = {name: sources for name, sources in name_to_sources.items()
                  if len(sources) > 1}

    return duplicates if duplicates else None


def flatten_wikisi_directory(
    wikisi_dir: str,
    output_dir: Optional[str] = None,
    root_name: str = "index",
    update: bool = False,
    verbose: bool = False
) -> int:
    """
    Flatten a wikisi directory by copying all index.html files to a flat structure.

    Args:
        wikisi_dir: Path to wikisi directory (e.g., .../wikisi)
        output_dir: Output directory path (default: wikisi-flat next to input)
        root_name: Name for root index.html file (default: "index")
        update: Overwrite output directory if exists (default: False)
        verbose: Print detailed progress (default: False)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    wikisi_path = Path(wikisi_dir).resolve()

    # Validation
    if not wikisi_path.exists():
        print(f"Error: Directory '{wikisi_dir}' does not exist.", file=sys.stderr)
        return 1

    if not wikisi_path.is_dir():
        print(f"Error: '{wikisi_dir}' is not a directory.", file=sys.stderr)
        return 1

    # Determine output directory
    if output_dir is None:
        output_path = wikisi_path.parent / "wikisi-flat"
    else:
        output_path = Path(output_dir).resolve()

    # Check if output exists
    if output_path.exists():
        if not update:
            print(f"Error: Output directory '{output_path}' already exists.", file=sys.stderr)
            print(f"Use -u/--update to overwrite.", file=sys.stderr)
            return 1

        if verbose:
            print(f"[INFO] Updating existing directory: {output_path}")

    if verbose:
        print(f"[INFO] Source: {wikisi_path}")
        print(f"[INFO] Output: {output_path}")

    try:
        # Collect index.html files
        files = collect_index_files(wikisi_path, root_name, verbose)

        if not files:
            print(f"[WARNING] No index.html files found in {wikisi_dir}", file=sys.stderr)
            return 1

        # Check for duplicates
        duplicates = check_duplicates(files)
        if duplicates:
            print(f"Error: Duplicate flattened names detected:", file=sys.stderr)
            for name, sources in duplicates.items():
                print(f"  {name}:", file=sys.stderr)
                for source in sources:
                    rel = source.relative_to(wikisi_path)
                    print(f"    - {rel}", file=sys.stderr)
            return 1

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Copy files
        copied_count = 0
        for source_path, flattened_name in files:
            target_path = output_path / flattened_name

            if verbose:
                rel_source = source_path.relative_to(wikisi_path)
                print(f"[COPY] {rel_source} -> {flattened_name}")

            shutil.copy2(source_path, target_path)
            copied_count += 1

        print(f"\n[SUCCESS] Flattened {copied_count} files to: {output_path}")

        # Show size info
        total_size = sum(f.stat().st_size for f, _ in files)
        print(f"[INFO] Total size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")

        return 0

    except Exception as e:
        print(f"Error: Failed to flatten wikisi directory: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_flatten_wikisi_command(subparsers):
    """Register the flatten-wikisi command."""
    parser = subparsers.add_parser(
        'flatten-wikisi',
        help='Flatten wikisi directory structure to flat HTML files',
        description='Copy all index.html files from nested wikisi structure to a flat directory '
                    'with filenames based on their path (e.g., agent/index.html -> agent.html).'
    )

    parser.add_argument(
        'wikisi_dir',
        type=str,
        help='Wikisi directory containing nested index.html files'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory (default: wikisi-flat next to input directory)'
    )

    parser.add_argument(
        '--root-name',
        type=str,
        default='index',
        help='Name for root index.html file (default: index)'
    )

    parser.add_argument(
        '-u', '--update',
        action='store_true',
        help='Overwrite output directory if it exists'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: flatten_wikisi_directory(
        args.wikisi_dir,
        args.output,
        args.root_name,
        args.update,
        args.verbose
    ))
