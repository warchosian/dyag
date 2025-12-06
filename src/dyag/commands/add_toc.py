"""
Command to add a Table of Contents (TOC) to HTML files.

This module parses HTML files, extracts headings (h1-h6), and generates
a hierarchical table of contents with anchor links.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from html.parser import HTMLParser


class HeadingExtractor(HTMLParser):
    """HTML Parser to extract headings and their content."""

    def __init__(self):
        super().__init__()
        self.headings = []
        self.current_heading = None
        self.current_level = None
        self.capture_data = False

    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_level = int(tag[1])
            # Get existing id if present
            attrs_dict = dict(attrs)
            heading_id = attrs_dict.get('id', '')
            self.current_heading = {
                'level': self.current_level,
                'text': '',
                'id': heading_id,
                'tag': tag
            }
            self.capture_data = True

    def handle_endtag(self, tag):
        """Handle closing tags."""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] and self.current_heading:
            self.headings.append(self.current_heading)
            self.current_heading = None
            self.capture_data = False

    def handle_data(self, data):
        """Handle text data."""
        if self.capture_data and self.current_heading is not None:
            self.current_heading['text'] += data.strip()


def generate_id(text: str, existing_ids: set) -> str:
    """
    Generate a unique ID from heading text.

    Args:
        text: Heading text
        existing_ids: Set of already used IDs

    Returns:
        Unique ID string
    """
    # Convert to lowercase, replace spaces with hyphens, remove special chars
    base_id = re.sub(r'[^\w\s-]', '', text.lower())
    base_id = re.sub(r'[-\s]+', '-', base_id).strip('-')

    # Ensure uniqueness
    unique_id = base_id
    counter = 1
    while unique_id in existing_ids:
        unique_id = f"{base_id}-{counter}"
        counter += 1

    existing_ids.add(unique_id)
    return unique_id


def generate_toc_html(headings: List[dict]) -> str:
    """
    Generate HTML for table of contents.

    Args:
        headings: List of heading dictionaries

    Returns:
        HTML string for TOC
    """
    if not headings:
        return ""

    toc_html = ['<nav id="table-of-contents" class="table-of-contents">', '<h2>Table des matières</h2>']

    # Build hierarchical structure
    current_level = 0
    for heading in headings:
        level = heading['level']
        text = heading['text']
        heading_id = heading['id']

        # Skip if no text
        if not text:
            continue

        # Open/close lists as needed
        if level > current_level:
            for _ in range(level - current_level):
                toc_html.append('<ul>')
        elif level < current_level:
            for _ in range(current_level - level):
                toc_html.append('</ul>')
                toc_html.append('</li>')

        # Close previous item if at same level
        if level == current_level and current_level > 0:
            toc_html.append('</li>')

        # Add TOC item with anchor for back-navigation (works in both HTML and Markdown)
        toc_id = f'toc-{heading_id}'
        toc_html.append(f'<li><a id="{toc_id}"></a><a href="#{heading_id}">{text}</a>')

        current_level = level

    # Close remaining open lists
    for _ in range(current_level):
        toc_html.append('</li>')
        toc_html.append('</ul>')

    toc_html.append('</nav>')

    return '\n'.join(toc_html)


def add_ids_to_headings(html_content: str, headings: List[dict]) -> str:
    """
    Add IDs to headings in HTML content and add back-to-TOC links.

    Args:
        html_content: Original HTML content
        headings: List of headings with generated IDs

    Returns:
        Modified HTML content with IDs and back-links added
    """
    # Group headings that need IDs by tag type
    headings_by_tag = {}
    for heading in headings:
        if heading['id'] and not heading.get('had_id', False):  # Only process headings that got new IDs
            tag = heading['tag']
            if tag not in headings_by_tag:
                headings_by_tag[tag] = []
            headings_by_tag[tag].append(heading)

    result = html_content

    # For each tag type, replace opening tags and add back-links
    for tag, tag_headings in headings_by_tag.items():
        # Pattern to match complete heading: <tag>content</tag>
        pattern = f'<{tag}>(.*?)</{tag}>'

        # Replace each occurrence with ID and back-link
        heading_index = 0
        def replace_func(match):
            nonlocal heading_index
            if heading_index < len(tag_headings):
                content = match.group(1)
                heading_id = tag_headings[heading_index]['id']

                # Add ID to opening tag and back-link to TOC entry
                toc_id = f'toc-{heading_id}'
                back_link = f' <a href="#{toc_id}" class="back-to-toc" title="Retour à la table des matières">↩</a>'
                replacement = f'<{tag} id="{heading_id}">{content}{back_link}</{tag}>'

                heading_index += 1
                return replacement
            return match.group(0)

        result = re.sub(pattern, replace_func, result)

    return result


def get_toc_css() -> str:
    """
    Get CSS styles for table of contents with back-navigation.

    Returns:
        CSS string
    """
    return """
    /* Table of Contents Styles */
    .table-of-contents {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        margin: 30px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .table-of-contents h2 {
        margin-top: 0;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }

    .table-of-contents ul {
        list-style-type: none;
        padding-left: 0;
        margin: 10px 0;
    }

    .table-of-contents ul ul {
        padding-left: 20px;
        margin-top: 5px;
    }

    .table-of-contents li {
        margin: 8px 0;
        line-height: 1.6;
    }

    .table-of-contents a {
        color: #3498db;
        text-decoration: none;
        transition: color 0.2s;
    }

    .table-of-contents a:hover {
        color: #2980b9;
        text-decoration: underline;
    }

    /* Back-to-TOC links next to headings */
    .back-to-toc {
        font-size: 0.7em;
        color: #95a5a6;
        text-decoration: none;
        margin-left: 10px;
        opacity: 0.6;
        transition: opacity 0.2s, color 0.2s;
        vertical-align: super;
    }

    .back-to-toc:hover {
        opacity: 1;
        color: #3498db;
        text-decoration: none;
    }

    h1:hover .back-to-toc,
    h2:hover .back-to-toc,
    h3:hover .back-to-toc,
    h4:hover .back-to-toc,
    h5:hover .back-to-toc,
    h6:hover .back-to-toc {
        opacity: 1;
    }

    /* Floating TOC button */
    .floating-toc-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: #3498db;
        color: white;
        padding: 12px 18px;
        border-radius: 50px;
        text-decoration: none;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: background 0.3s, transform 0.2s;
        z-index: 1000;
    }

    .floating-toc-btn:hover {
        background: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        text-decoration: none;
    }

    /* Smooth scrolling for anchor links */
    html {
        scroll-behavior: smooth;
    }

    /* Highlight target when navigating */
    .table-of-contents li:target {
        background: #fff3cd;
        border-radius: 4px;
        transition: background 0.5s;
    }
    """


def add_toc_to_html(
    input_path: str,
    output_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Add a table of contents to an HTML file.

    Args:
        input_path: Path to input HTML file
        output_path: Optional path to output HTML file. If None, adds .toc before extension
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_file = Path(input_path).resolve()

    # Check if input file exists
    if not input_file.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        return 1

    if not input_file.is_file():
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_file = input_file.parent / f"{input_file.stem}.toc{input_file.suffix}"
    else:
        output_file = Path(output_path).resolve()

    if verbose:
        print(f"Processing: {input_file}")
        print(f"Output: {output_file}")

    try:
        # Read HTML content
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract headings
        parser = HeadingExtractor()
        parser.feed(html_content)
        headings = parser.headings

        if verbose:
            print(f"\nFound {len(headings)} headings")

        if not headings:
            print("Warning: No headings found in HTML file. No TOC will be added.", file=sys.stderr)
            # Still write the file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n[INFO] File copied without TOC: {output_file}")
            return 0

        # Generate IDs for headings that don't have them
        existing_ids = set(h['id'] for h in headings if h['id'])
        for heading in headings:
            if heading['id']:
                heading['had_id'] = True  # Mark that this heading already had an ID
            else:
                heading['id'] = generate_id(heading['text'], existing_ids)
                heading['had_id'] = False  # Mark that we generated this ID
            if verbose:
                try:
                    print(f"  {heading['tag'].upper()}: {heading['text']} (#{heading['id']})")
                except UnicodeEncodeError:
                    # Fallback for Windows console that can't handle certain Unicode characters
                    safe_text = heading['text'].encode('ascii', 'replace').decode('ascii')
                    print(f"  {heading['tag'].upper()}: {safe_text} (#{heading['id']})")

        # Add IDs to headings in HTML
        html_content = add_ids_to_headings(html_content, headings)

        # Generate TOC HTML
        toc_html = generate_toc_html(headings)

        # Add TOC CSS if not already present
        if '<style>' in html_content and '.table-of-contents' not in html_content:
            # Insert CSS before </style>
            toc_css = get_toc_css()
            html_content = html_content.replace('</style>', f'{toc_css}\n    </style>')
        elif '<head>' in html_content and '<style>' not in html_content:
            # Add style section in head
            toc_css = get_toc_css()
            style_section = f'<style>{toc_css}</style>\n</head>'
            html_content = html_content.replace('</head>', style_section)

        # Insert TOC after <body> tag or at the beginning of body content
        if '<body>' in html_content:
            html_content = html_content.replace('<body>', f'<body>\n{toc_html}\n', 1)
        elif '<body' in html_content:
            # Handle <body> with attributes
            body_pattern = r'(<body[^>]*>)'
            html_content = re.sub(body_pattern, f'\\g<1>\n{toc_html}\n', html_content, count=1)
        else:
            # No body tag, just prepend
            html_content = toc_html + '\n' + html_content

        # Add floating TOC button before </body>
        floating_btn = '<a href="#table-of-contents" class="floating-toc-btn" title="Retour à la table des matières">↑ TOC</a>'
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{floating_btn}\n</body>', 1)
        else:
            # No body tag, add at the end
            html_content = html_content + '\n' + floating_btn

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n[SUCCESS] HTML with TOC created: {output_file}")
        print(f"[INFO] Added table of contents with {len(headings)} entries")

        return 0

    except Exception as e:
        print(f"Error: Failed to add TOC: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def register_add_toc_command(subparsers):
    """
    Register the add-toc command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'add-toc',
        help='Add a table of contents to an HTML file',
        description='Parse HTML file, extract headings (h1-h6), and add a hierarchical table of contents with anchor links.'
    )

    parser.add_argument(
        'input',
        type=str,
        help='HTML file to process'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output HTML file path (default: <input>.toc.html)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: add_toc_to_html(
        args.input,
        args.output,
        args.verbose
    ))
