"""
Command to concatenate HTML files from a directory into a single HTML file.

This module concatenates multiple HTML files in natural (numeric) order,
not alphabetic order. For example: file1.html, file2.html, file10.html
instead of file1.html, file10.html, file2.html.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Optional, Dict
from html.parser import HTMLParser


class FirstHeadingExtractor(HTMLParser):
    """Extract the first H1 heading ID and text from HTML content."""

    def __init__(self):
        super().__init__()
        self.first_h1_id = None
        self.first_h1_text = None
        self.found = False
        self.in_h1 = False
        self.h1_text_parts = []

    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        if not self.found and tag == 'h1':
            attrs_dict = dict(attrs)
            self.first_h1_id = attrs_dict.get('id', None)
            self.in_h1 = True
            self.h1_text_parts = []

    def handle_endtag(self, tag):
        """Handle closing tags."""
        if tag == 'h1' and self.in_h1:
            self.first_h1_text = ''.join(self.h1_text_parts).strip()
            self.in_h1 = False
            self.found = True

    def handle_data(self, data):
        """Handle text data."""
        if self.in_h1:
            self.h1_text_parts.append(data)


def generate_id_from_text(text: str) -> str:
    """
    Generate an ID from heading text (same algorithm as add_toc).

    Args:
        text: Heading text

    Returns:
        Generated ID string
    """
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    base_id = re.sub(r'[^\w\s-]', '', text.lower())
    base_id = re.sub(r'[-\s]+', '-', base_id).strip('-')
    return base_id


def extract_first_heading_id(html_content: str) -> Optional[str]:
    """
    Extract or generate the ID of the first H1 heading from HTML content.

    Args:
        html_content: HTML content as string

    Returns:
        ID of first H1 heading (existing or generated), or None if no H1 found
    """
    parser = FirstHeadingExtractor()
    try:
        parser.feed(html_content)

        # If we found an H1
        if parser.found:
            # Use existing ID if present, otherwise generate from text
            if parser.first_h1_id:
                return parser.first_h1_id
            elif parser.first_h1_text:
                return generate_id_from_text(parser.first_h1_text)

        return None
    except Exception:
        return None


def build_filename_to_id_map(html_files: List[Path]) -> Dict[str, str]:
    """
    Build a mapping of filename to first heading ID.

    Args:
        html_files: List of HTML file paths

    Returns:
        Dictionary mapping filename (with and without .html) to heading ID
    """
    filename_map = {}

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            heading_id = extract_first_heading_id(content)
            if heading_id:
                # Map both "page1.html" and "page1" to the heading ID
                filename_map[html_file.name] = heading_id
                filename_map[html_file.stem] = heading_id  # stem = filename without extension
        except Exception:
            continue

    return filename_map


def replace_internal_links(html_content: str, filename_map: Dict[str, str]) -> str:
    """
    Replace inter-page links with internal section links.

    Converts href="page2.html" to href="#big-data-pipelines" based on filename_map.

    Args:
        html_content: HTML content with inter-page links
        filename_map: Mapping of filenames to heading IDs

    Returns:
        HTML content with internal links
    """
    def replace_link(match):
        href = match.group(1)

        # Check if this is a link to one of the concatenated files
        for filename, heading_id in filename_map.items():
            if href == filename or href == f"./{filename}":
                # Replace with internal anchor link
                return f'href="#{heading_id}"'

        # Not a match, keep original
        return match.group(0)

    # Pattern to match href="..." or href='...'
    pattern = r'href=["\']([^"\']+)["\']'
    return re.sub(pattern, replace_link, html_content)


def natural_sort_key(filename: str) -> List:
    """
    Generate a sort key for natural (numeric) sorting.

    Converts 'file10.html' to ['file', 10, '.html'] for proper numeric comparison.

    Args:
        filename: Filename to generate key for

    Returns:
        List of strings and integers for sorting
    """
    def try_int(s):
        try:
            return int(s)
        except ValueError:
            return s.lower()

    return [try_int(part) for part in re.split(r'(\d+)', filename)]


def collect_html_files(directory: Path, output_file: Path, verbose: bool = False) -> List[Path]:
    """
    Collect HTML files from directory, excluding the output file.

    Args:
        directory: Directory to scan
        output_file: Output file to exclude
        verbose: Print progress

    Returns:
        List of HTML file paths sorted in natural order
    """
    html_files = []

    # Get all HTML files
    for file_path in directory.glob('*.html'):
        # Skip the output file if it exists in the same directory
        if file_path.resolve() == output_file.resolve():
            if verbose:
                print(f"[SKIP] Excluding output file: {file_path.name}")
            continue

        html_files.append(file_path)

    # Sort using natural sort
    html_files.sort(key=lambda f: natural_sort_key(f.name))

    if verbose:
        print(f"[INFO] Found {len(html_files)} HTML files to concatenate")
        for i, f in enumerate(html_files, 1):
            print(f"  {i}. {f.name}")

    return html_files


def extract_body_content(html_content: str) -> str:
    """
    Extract content from HTML body tag, or return full content if no body tag.

    Args:
        html_content: HTML content as string

    Returns:
        Body content or full content
    """
    # Try to extract body content
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)

    if body_match:
        return body_match.group(1)
    else:
        # No body tag, return content without html/head tags
        # Remove DOCTYPE
        content = re.sub(r'<!DOCTYPE[^>]*>', '', html_content, flags=re.IGNORECASE)
        # Remove html tags
        content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
        # Remove head section
        content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
        return content.strip()


def create_html_wrapper(title: str = "Concatenated HTML") -> tuple:
    """
    Create HTML document wrapper (header and footer).

    Args:
        title: Document title

    Returns:
        Tuple of (header, footer) strings
    """
    header = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }}

        .html-file-section {{
            background: white;
            margin: 2rem 0;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .html-file-header {{
            background: #2196F3;
            color: white;
            padding: 1rem 1.5rem;
            margin: -2rem -2rem 2rem -2rem;
            border-radius: 8px 8px 0 0;
            font-size: 1.2rem;
            font-weight: bold;
        }}

        .html-file-separator {{
            border: none;
            border-top: 3px solid #e0e0e0;
            margin: 3rem 0;
        }}
    </style>
</head>
<body>
"""

    footer = """
</body>
</html>
"""

    return header, footer


def concatenate_html_files(
    directory: str,
    output_file: str,
    include_headers: bool = True,
    title: str = "Concatenated HTML",
    verbose: bool = False
) -> int:
    """
    Concatenate HTML files from a directory into a single file.

    Args:
        directory: Directory containing HTML files
        output_file: Output file path
        include_headers: Add headers showing source file names
        title: Title for the concatenated document
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    dir_path = Path(directory)
    output_path = Path(output_file)

    # Validate directory
    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        return 1

    if not dir_path.is_dir():
        print(f"Error: '{directory}' is not a directory.", file=sys.stderr)
        return 1

    if verbose:
        print(f"[INFO] Scanning directory: {dir_path}")
        print(f"[INFO] Output file: {output_path}")

    try:
        # Collect HTML files
        html_files = collect_html_files(dir_path, output_path, verbose)

        if not html_files:
            print(f"[WARNING] No HTML files found in {directory}", file=sys.stderr)
            return 1

        # Build filename to heading ID mapping for internal link conversion
        if verbose:
            print(f"[INFO] Building internal link map...")
        filename_map = build_filename_to_id_map(html_files)
        if verbose and filename_map:
            print(f"[INFO] Found {len(filename_map) // 2} file-to-section mappings")
            for filename in sorted([k for k in filename_map.keys() if '.' in k]):
                print(f"  {filename} -> #{filename_map[filename]}")

        # Create output
        header, footer = create_html_wrapper(title)

        with open(output_path, 'w', encoding='utf-8') as out_file:
            # Write header
            out_file.write(header)

            # Concatenate files
            for i, html_file in enumerate(html_files, 1):
                if verbose:
                    print(f"[PROCESS] {i}/{len(html_files)}: {html_file.name}")

                try:
                    # Read file
                    with open(html_file, 'r', encoding='utf-8') as in_file:
                        content = in_file.read()

                    # Extract body content
                    body_content = extract_body_content(content)

                    # Replace inter-page links with internal section links
                    body_content = replace_internal_links(body_content, filename_map)

                    # Add section wrapper
                    out_file.write(f'\n<!-- Source: {html_file.name} -->\n')
                    out_file.write('<div class="html-file-section">\n')

                    if include_headers:
                        out_file.write(f'<div class="html-file-header">📄 {html_file.name}</div>\n')

                    out_file.write(body_content)
                    out_file.write('\n</div>\n')

                    # Add separator except for last file
                    if i < len(html_files):
                        out_file.write('<hr class="html-file-separator">\n')

                except Exception as e:
                    print(f"[WARNING] Failed to process {html_file.name}: {e}", file=sys.stderr)
                    continue

            # Write footer
            out_file.write(footer)

        print(f"\n[SUCCESS] Concatenated {len(html_files)} files into: {output_path}")

        # Show file size
        output_size = output_path.stat().st_size
        print(f"[INFO] Output file size: {output_size:,} bytes ({output_size / 1024:.1f} KB)")

        return 0

    except Exception as e:
        print(f"Error: Concatenation failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_concat_html_command(subparsers):
    """Register the concat-html command."""
    parser = subparsers.add_parser(
        'concat-html',
        help='Concatenate HTML files from a directory',
        description='Concatenate multiple HTML files into a single file with natural (numeric) sorting.'
    )

    parser.add_argument(
        'directory',
        type=str,
        help='Directory containing HTML files'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Output HTML file path'
    )

    parser.add_argument(
        '--no-headers',
        action='store_true',
        help='Do not add headers showing source file names'
    )

    parser.add_argument(
        '--title',
        type=str,
        default='Concatenated HTML',
        help='Title for the concatenated document'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: concatenate_html_files(
        args.directory,
        args.output,
        not args.no_headers,
        args.title,
        args.verbose
    ))
