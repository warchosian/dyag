"""
Command to convert HTML files to Markdown.

This module converts HTML documents to Markdown format, handling:
- Headings (h1-h6)
- Paragraphs
- Lists (ordered and unordered)
- Links and images
- Code blocks and inline code
- Tables
- Bold and italic text
- Blockquotes
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional
from html.parser import HTMLParser


class HTMLToMarkdownConverter(HTMLParser):
    """
    HTML parser that converts HTML to Markdown.
    """

    def __init__(self):
        super().__init__()
        self.markdown = []
        self.current_tag = []
        self.list_stack = []  # Stack to track nested lists
        self.table_data = []  # Current table data
        self.in_table = False
        self.in_table_row = False
        self.in_table_header = False
        self.in_table_cell = False
        self.current_row = []
        self.current_cell_content = []  # Buffer for cell content
        self.table_caption = None
        self.skip_content = False  # For script, style tags
        self.link_url = None
        self.is_anchor_only = False  # Track if current <a> is just an anchor (no link)
        self.img_alt = None
        self.preserve_whitespace = False
        self.current_section_id = None  # Track section IDs for headings
        self.pending_heading_id = None  # ID to add to next heading

    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        attrs_dict = dict(attrs)
        self.current_tag.append(tag)

        # Skip script and style content
        if tag in ['script', 'style']:
            self.skip_content = True
            return

        # Headings
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            self.markdown.append('\n' + '#' * level + ' ')
            # Check if heading has an ID
            if 'id' in attrs_dict:
                self.pending_heading_id = attrs_dict['id']

        # Paragraphs
        elif tag == 'p':
            self.markdown.append('\n\n')

        # Line break
        elif tag == 'br':
            self.markdown.append('  \n')

        # Horizontal rule
        elif tag == 'hr':
            self.markdown.append('\n\n---\n\n')

        # Bold
        elif tag in ['strong', 'b']:
            if self.in_table_cell:
                self.current_cell_content.append('**')
            else:
                self.markdown.append('**')

        # Italic
        elif tag in ['em', 'i']:
            if self.in_table_cell:
                self.current_cell_content.append('*')
            else:
                self.markdown.append('*')

        # Code (inline)
        elif tag == 'code' and 'pre' not in self.current_tag:
            if self.in_table_cell:
                self.current_cell_content.append('`')
            else:
                self.markdown.append('`')

        # Code block
        elif tag == 'pre':
            self.markdown.append('\n```\n')
            self.preserve_whitespace = True

        # Links and anchors
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            anchor_id = attrs_dict.get('id', '')

            # If it's just an anchor (no href), preserve it as HTML
            if anchor_id and not href:
                self.markdown.append(f'<a id="{anchor_id}">')
                self.is_anchor_only = True
                self.link_url = None
            else:
                # It's a link
                self.link_url = href
                self.is_anchor_only = False
                self.markdown.append('[')

        # Images
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            self.markdown.append(f'![{alt}]({src})')

        # Lists
        elif tag == 'ul':
            self.list_stack.append('ul')
            if len(self.list_stack) > 1:
                self.markdown.append('\n')

        elif tag == 'ol':
            self.list_stack.append(('ol', 1))
            if len(self.list_stack) > 1:
                self.markdown.append('\n')

        elif tag == 'li':
            indent = '  ' * (len(self.list_stack) - 1)
            if self.list_stack:
                list_type = self.list_stack[-1]
                if isinstance(list_type, tuple):  # Ordered list
                    _, num = list_type
                    self.markdown.append(f'\n{indent}{num}. ')
                    self.list_stack[-1] = (list_type[0], num + 1)
                else:  # Unordered list
                    self.markdown.append(f'\n{indent}- ')

        # Blockquote
        elif tag == 'blockquote':
            self.markdown.append('\n> ')

        # Table
        elif tag == 'table':
            self.in_table = True
            self.table_data = []
            self.table_caption = None

        elif tag == 'caption':
            if self.in_table:
                self.current_cell_content = []  # Use cell buffer for caption

        elif tag in ['thead', 'tbody', 'tfoot']:
            if tag == 'thead':
                self.in_table_header = True
            # tbody and tfoot just pass through

        elif tag == 'tr':
            self.in_table_row = True
            self.current_row = []

        elif tag in ['th', 'td']:
            self.in_table_cell = True
            self.current_cell_content = []

        # Sections - capture ID for next heading
        elif tag == 'section':
            if 'id' in attrs_dict and not self.pending_heading_id:
                self.current_section_id = attrs_dict['id']

        # Divs and spans (just pass through)
        elif tag in ['div', 'span', 'article', 'header', 'footer', 'nav', 'main']:
            pass

    def handle_endtag(self, tag):
        """Handle closing HTML tags."""
        # Reset section ID when closing section
        if tag == 'section':
            self.current_section_id = None

        if self.current_tag and self.current_tag[-1] == tag:
            self.current_tag.pop()

        # Skip script and style content
        if tag in ['script', 'style']:
            self.skip_content = False
            return

        # Headings
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Add ID if present (heading ID or section ID)
            heading_id = self.pending_heading_id or self.current_section_id
            if heading_id:
                self.markdown.append(f' {{#{heading_id}}}')
                self.pending_heading_id = None
                self.current_section_id = None
            self.markdown.append('\n')

        # Paragraphs
        elif tag == 'p':
            pass  # Already handled in starttag

        # Bold
        elif tag in ['strong', 'b']:
            if self.in_table_cell:
                self.current_cell_content.append('**')
            else:
                self.markdown.append('**')

        # Italic
        elif tag in ['em', 'i']:
            if self.in_table_cell:
                self.current_cell_content.append('*')
            else:
                self.markdown.append('*')

        # Code (inline)
        elif tag == 'code' and 'pre' not in self.current_tag:
            if self.in_table_cell:
                self.current_cell_content.append('`')
            else:
                self.markdown.append('`')

        # Code block
        elif tag == 'pre':
            self.markdown.append('\n```\n')
            self.preserve_whitespace = False

        # Links and anchors
        elif tag == 'a':
            if self.is_anchor_only:
                # Close the anchor tag
                self.markdown.append('</a>')
                self.is_anchor_only = False
            elif self.link_url:
                # Convert .html extensions to .md in links
                link_url = self.link_url
                if link_url.endswith('.html'):
                    link_url = link_url[:-5] + '.md'
                self.markdown.append(f']({link_url})')
                self.link_url = None

        # Lists
        elif tag == 'ul':
            if self.list_stack and self.list_stack[-1] == 'ul':
                self.list_stack.pop()
                if not self.list_stack:
                    self.markdown.append('\n')

        elif tag == 'ol':
            if self.list_stack and isinstance(self.list_stack[-1], tuple):
                self.list_stack.pop()
                if not self.list_stack:
                    self.markdown.append('\n')

        elif tag == 'li':
            pass  # Already handled in starttag

        # Blockquote
        elif tag == 'blockquote':
            self.markdown.append('\n\n')

        # Table
        elif tag == 'caption':
            if self.in_table:
                self.table_caption = ''.join(self.current_cell_content).strip()
                self.current_cell_content = []

        elif tag in ['th', 'td']:
            if self.in_table_cell:
                # Get cell content from buffer
                cell_text = ''.join(self.current_cell_content).strip()
                self.current_row.append(cell_text)
                self.current_cell_content = []
                self.in_table_cell = False

        elif tag == 'tr':
            if self.in_table_row:
                self.table_data.append(self.current_row[:])
                self.current_row = []
                self.in_table_row = False

        elif tag == 'thead':
            if self.in_table_header:
                # Add separator row after header
                if self.table_data:
                    num_cols = len(self.table_data[-1])
                    separator = ['---'] * num_cols
                    self.table_data.append(separator)
                self.in_table_header = False

        elif tag == 'table':
            if self.in_table:
                self._render_table()
                self.in_table = False
                self.table_data = []
                self.table_caption = None

    def handle_data(self, data):
        """Handle text content."""
        if self.skip_content:
            return

        # Clean up whitespace unless in code block
        if not self.preserve_whitespace:
            # Preserve single spaces, collapse multiple spaces
            data = re.sub(r'\s+', ' ', data)
            # Don't add empty strings
            if not data.strip():
                return

        # If in table cell or caption, add to buffer
        if self.in_table_cell or (self.in_table and 'caption' in self.current_tag):
            self.current_cell_content.append(data)
        else:
            self.markdown.append(data)

    def _render_table(self):
        """Render accumulated table data as Markdown table."""
        if not self.table_data:
            return

        # Add caption if present
        if self.table_caption:
            self.markdown.append(f'\n\n**{self.table_caption}**\n\n')
        else:
            self.markdown.append('\n\n')

        # Calculate column widths
        num_cols = max(len(row) for row in self.table_data) if self.table_data else 0
        if num_cols == 0:
            return

        col_widths = [0] * num_cols

        for row in self.table_data:
            for i, cell in enumerate(row):
                if i < num_cols:
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Render table
        for row in self.table_data:
            cells = []
            for i in range(num_cols):
                if i < len(row):
                    cell = str(row[i])
                else:
                    cell = ''
                # Pad cell to column width
                padded = cell.ljust(col_widths[i])
                cells.append(padded)

            self.markdown.append('| ' + ' | '.join(cells) + ' |\n')

        self.markdown.append('\n')

    def get_markdown(self) -> str:
        """Get the converted Markdown content."""
        result = ''.join(self.markdown)

        # Clean up excessive newlines
        result = re.sub(r'\n{3,}', '\n\n', result)

        # Clean up spaces before newlines
        result = re.sub(r' +\n', '\n', result)

        return result.strip() + '\n'


def convert_html_to_markdown(html_content: str, verbose: bool = False) -> str:
    """
    Convert HTML content to Markdown.

    Args:
        html_content: HTML content as string
        verbose: Print verbose output

    Returns:
        Markdown content as string
    """
    # Remove HTML comments
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

    # Create converter and parse
    converter = HTMLToMarkdownConverter()

    try:
        converter.feed(html_content)
        markdown_content = converter.get_markdown()

        if verbose:
            print(f"[INFO] Converted HTML to Markdown ({len(markdown_content)} characters)")

        return markdown_content

    except Exception as e:
        if verbose:
            print(f"[ERROR] HTML conversion failed: {e}", file=sys.stderr)
        return ""


def process_html_to_markdown(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Convert HTML file to Markdown file.

    Args:
        input_file: Path to input HTML file
        output_file: Path to output Markdown file (default: input with .md extension)
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_path = Path(input_file)

    # Validate input
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"Error: '{input_file}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_file is None:
        output_path = input_path.with_suffix('.md')
    else:
        output_path = Path(output_file)

    if verbose:
        print(f"[INFO] Converting HTML to Markdown...")
        print(f"[INFO] Input:  {input_path}")
        print(f"[INFO] Output: {output_path}")

    try:
        # Read HTML file
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        if verbose:
            print(f"[INFO] Read {len(html_content)} characters from {input_path}")

        # Convert to Markdown
        markdown_content = convert_html_to_markdown(html_content, verbose)

        if not markdown_content:
            print("[WARNING] Conversion produced empty result", file=sys.stderr)
            return 1

        # Write Markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        if verbose:
            print(f"[INFO] Wrote {len(markdown_content)} characters to {output_path}")

        print(f"[SUCCESS] Markdown file created: {output_path}")
        return 0

    except Exception as e:
        print(f"Error: Conversion failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_html2md_command(subparsers):
    """Register the html2md command."""
    parser = subparsers.add_parser(
        'html2md',
        help='Convert HTML file to Markdown',
        description='Convert an HTML file to Markdown format, preserving structure and formatting.'
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Input HTML file path'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output Markdown file path (default: input file with .md extension)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: process_html_to_markdown(
        args.input_file,
        args.output,
        args.verbose
    ))
