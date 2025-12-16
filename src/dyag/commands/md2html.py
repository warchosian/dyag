"""
Command to convert Markdown files with diagrams (Graphviz, PlantUML, Mermaid) to HTML with embedded SVG.
"""

import os
import re
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional
import markdown


def extract_code_blocks(content: str) -> List[Tuple[str, str, int]]:
    """
    Extract code blocks with their type and position from markdown content.

    Args:
        content: Markdown content as string

    Returns:
        List of tuples (block_type, code, position) where:
        - block_type is 'dot', 'graphviz', 'plantuml', or 'mermaid'
        - code is the diagram source code
        - position is the character position in the original content
    """
    blocks = []

    # Pattern to match code blocks with supported diagram types
    pattern = r'```(dot|graphviz|plantuml|mermaid)\n(.*?)```'

    for match in re.finditer(pattern, content, re.DOTALL):
        block_type = match.group(1)
        code = match.group(2).strip()
        position = match.start()
        blocks.append((block_type, code, position))

    return blocks


def convert_graphviz_to_svg(dot_code: str, verbose: bool = False) -> Optional[str]:
    """
    Convert Graphviz DOT code to SVG using the dot command.

    Args:
        dot_code: Graphviz DOT source code
        verbose: Print verbose output

    Returns:
        SVG content as string, or None if conversion fails
    """
    try:
        # Run dot command to convert to SVG
        result = subprocess.run(
            ['dot', '-Tsvg'],
            input=dot_code.encode('utf-8'),
            capture_output=True,
            timeout=30
        )

        if result.returncode != 0:
            if verbose:
                print(f"Warning: Graphviz conversion failed: {result.stderr.decode()}", file=sys.stderr)
            return None

        svg_content = result.stdout.decode('utf-8')
        return svg_content

    except FileNotFoundError:
        if verbose:
            print("Warning: 'dot' command not found. Please install Graphviz.", file=sys.stderr)
        return None
    except Exception as e:
        if verbose:
            print(f"Warning: Graphviz conversion error: {e}", file=sys.stderr)
        return None


def convert_plantuml_to_svg(plantuml_code: str, verbose: bool = False) -> Optional[str]:
    """
    Convert PlantUML code to SVG using plantuml command or online service.

    Args:
        plantuml_code: PlantUML source code
        verbose: Print verbose output

    Returns:
        SVG content as string, or None if conversion fails
    """
    try:
        # Try using local plantuml command first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False, encoding='utf-8') as f:
            f.write(plantuml_code)
            temp_input = f.name

        temp_output = temp_input.replace('.puml', '.svg')

        try:
            # Try plantuml command
            result = subprocess.run(
                ['plantuml', '-tsvg', temp_input],
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and os.path.exists(temp_output):
                with open(temp_output, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                os.unlink(temp_input)
                os.unlink(temp_output)
                return svg_content
        except FileNotFoundError:
            # plantuml command not found, try kroki online service
            if verbose:
                print("Info: Using Kroki online service for PlantUML conversion", file=sys.stderr)

            import urllib.request
            import urllib.parse
            import base64
            import zlib

            # Compress and encode for Kroki
            compressed = zlib.compress(plantuml_code.encode('utf-8'), 9)
            encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')

            url = f'https://kroki.io/plantuml/svg/{encoded}'

            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    svg_content = response.read().decode('utf-8')
                os.unlink(temp_input)
                return svg_content
            except Exception as e:
                if verbose:
                    print(f"Warning: Kroki service error: {e}", file=sys.stderr)
        finally:
            if os.path.exists(temp_input):
                os.unlink(temp_input)
            if os.path.exists(temp_output):
                os.unlink(temp_output)

    except Exception as e:
        if verbose:
            print(f"Warning: PlantUML conversion error: {e}", file=sys.stderr)

    return None


def convert_mermaid_to_svg(mermaid_code: str, verbose: bool = False) -> Optional[str]:
    """
    Convert Mermaid code to SVG using mermaid-cli or online service.

    Args:
        mermaid_code: Mermaid source code
        verbose: Print verbose output

    Returns:
        SVG content as string, or None if conversion fails
    """
    try:
        # Try using Kroki online service
        if verbose:
            print("Info: Using Kroki online service for Mermaid conversion", file=sys.stderr)

        import urllib.request
        import urllib.parse
        import base64
        import zlib

        # Compress and encode for Kroki
        compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')

        url = f'https://kroki.io/mermaid/svg/{encoded}'

        with urllib.request.urlopen(url, timeout=30) as response:
            svg_content = response.read().decode('utf-8')

        return svg_content

    except Exception as e:
        if verbose:
            print(f"Warning: Mermaid conversion error: {e}", file=sys.stderr)

    return None


def clean_svg_content(svg_content: str) -> str:
    """
    Clean SVG content by removing XML declaration and unnecessary comments.

    Args:
        svg_content: Raw SVG content

    Returns:
        Cleaned SVG content
    """
    # Remove XML declaration
    svg_content = re.sub(r'<\?xml[^>]*\?>\s*', '', svg_content)

    # Remove DOCTYPE declaration
    svg_content = re.sub(r'<!DOCTYPE[^>]*>\s*', '', svg_content)

    # Remove Graphviz generator comments
    svg_content = re.sub(r'<!--[^>]*Generated by [^>]*-->\s*', '', svg_content)

    # Remove other XML comments (but keep them if they might be important for rendering)
    svg_content = re.sub(r'<!--\s*Title:[^>]*-->\s*', '', svg_content)

    # Strip leading/trailing whitespace
    svg_content = svg_content.strip()

    return svg_content


def process_markdown_to_html(
    markdown_path: str,
    output_path: str = None,
    verbose: bool = False,
    standalone: bool = True
) -> int:
    """
    Convert a Markdown file with diagrams to HTML with embedded SVG.

    Args:
        markdown_path: Path to the input Markdown file
        output_path: Optional output HTML path. If None, uses same name with .html extension
        verbose: Print verbose output
        standalone: Generate standalone HTML with CSS and full page structure

    Returns:
        Exit code (0 for success, 1 for error)
    """
    md_path = Path(markdown_path).resolve()

    # Check if markdown file exists
    if not md_path.exists():
        print(f"Error: Markdown file '{markdown_path}' does not exist.", file=sys.stderr)
        return 1

    if not md_path.is_file():
        print(f"Error: '{markdown_path}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        output_path = md_path.parent / (md_path.stem + ".html")
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()

    if verbose:
        print(f"Processing: {md_path}")
        print(f"Output: {output_path}")

    try:
        # Read markdown content
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract code blocks
        blocks = extract_code_blocks(content)

        if verbose:
            print(f"\nFound {len(blocks)} diagram blocks")


        # Convert diagrams to SVG and replace in content (inline, to handle identical blocks)
        result_content = content
        svg_count = 0
        for block_type, code, position in blocks:
            if verbose:
                print(f"  Converting {block_type} diagram...")

            svg_content = None
            if block_type in ('dot', 'graphviz'):
                svg_content = convert_graphviz_to_svg(code, verbose)
            elif block_type == 'plantuml':
                svg_content = convert_plantuml_to_svg(code, verbose)
            elif block_type == 'mermaid':
                svg_content = convert_mermaid_to_svg(code, verbose)

            if svg_content:
                # Clean SVG content
                svg_content = clean_svg_content(svg_content)

                # Replace only the first occurrence to avoid replacing identical blocks multiple times
                pattern = f'```{block_type}\n{re.escape(code)}\n```'
                replacement = f'<div class="diagram diagram-{block_type}">\n{svg_content}\n</div>'
                # Escape backslashes in replacement to avoid regex interpretation
                replacement = replacement.replace('\\', '\\\\')
                result_content = re.sub(pattern, replacement, result_content, count=1)
                svg_count += 1
                if verbose:
                    print(f"    [OK] Converted successfully")
            else:
                if verbose:
                    print(f"    [FAILED] Failed to convert, keeping original code block")

        # Convert remaining markdown to HTML (basic conversion with full support)
        html_content = markdown_to_html_basic(result_content)

        # Wrap in full HTML if standalone
        if standalone:
            html_content = wrap_html_document(html_content, md_path.stem)

        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Display results
        print(f"\n[SUCCESS] HTML created: {output_path}")

        if len(blocks) > 0:
            if svg_count == len(blocks):
                print(f"[OK] All {svg_count} diagrams converted to SVG successfully")
            elif svg_count > 0:
                print(f"[WARNING] Converted {svg_count} out of {len(blocks)} diagrams to SVG")
                print(f"  ({len(blocks) - svg_count} diagram(s) failed to convert)")
            else:
                print(f"[ERROR] No diagrams were converted ({len(blocks)} found)")
        else:
            print("[INFO] No diagrams found in the markdown file")

        return 0

    except Exception as e:
        print(f"Error: Failed to convert markdown: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def convert_markdown_table(table_text: str) -> str:
    """
    Convert a markdown table to HTML table.

    Args:
        table_text: Markdown table text

    Returns:
        HTML table
    """
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]

    if len(lines) < 2:
        return table_text

    # First line is header
    header_cells = [cell.strip() for cell in lines[0].split('|')[1:-1]]

    # Second line is separator (skip it)
    # Remaining lines are data rows
    data_rows = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if cells:
            data_rows.append(cells)

    # Build HTML table
    html = '<table>\n<thead>\n<tr>\n'
    for cell in header_cells:
        html += f'<th>{cell}</th>\n'
    html += '</tr>\n</thead>\n<tbody>\n'

    for row in data_rows:
        html += '<tr>\n'
        for cell in row:
            html += f'<td>{cell}</td>\n'
        html += '</tr>\n'

    html += '</tbody>\n</table>'
    return html


def markdown_to_html_basic(content: str) -> str:
    """
    Basic markdown to HTML conversion for common elements.

    Args:
        content: Markdown content

    Returns:
        HTML content
    """
    # DEBUG: Confirm function is called
    with open('markdown_basic_called.txt', 'w', encoding='utf-8') as f:
        f.write('Function called\n')
        f.write(f'Content length: {len(content)}\n')
        f.write(f'Has tree chars: {any(c in content for c in ["├──", "└──", "│"])}\n')

    # Clean anchor tags with empty href attributes first
    # This fixes navigation issues from markdown-preview-enhanced and similar tools
    content = re.sub(r'<a\s+id="([^"]+)"\s+href=""\s*></a>', r'<a id="\1"></a>', content)

    # Convert markdown links [text](url) to HTML BEFORE protecting HTML tags
    # This ensures links on the same line as HTML anchors are converted
    # Also convert .md extensions to .html in links
    def convert_md_link(match):
        text = match.group(1)
        url = match.group(2)
        # Convert .md to .html
        if url.endswith('.md'):
            url = url[:-3] + '.html'
        return f'<a href="{url}">{text}</a>'

    content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', convert_md_link, content)

    # Protect all HTML tags (anchors, links, details, etc.) before other markdown conversions
    html_tags = {}
    def save_html_tag(match):
        placeholder = f'___HTML_TAG_{len(html_tags)}___'
        html_tags[placeholder] = match.group(0)
        return placeholder

    # Protect anchor tags
    content = re.sub(r'<a\s+id="[^"]+"\s*></a>', save_html_tag, content)
    # Protect link tags (including those we just created)
    content = re.sub(r'<a\s+href="[^"]+">.*?</a>', save_html_tag, content)
    # Protect details and summary tags
    content = re.sub(r'<details[^>]*>.*?</details>', save_html_tag, content, flags=re.DOTALL)
    content = re.sub(r'</?(?:summary|div)[^>]*>', save_html_tag, content)

    # Protect code blocks first (before any other conversion)
    # This prevents their content from being modified by other markdown conversions
    # Pattern matches: ```+ (3 or more backticks) with optional language, content, and closing backticks
    # Using backreference to match the same number of opening backticks
    code_block_pattern = r'(`{3,})([^\n`]*)\n(.*?)\1(?:\n|$)'
    code_blocks = {}
    def save_code_block(match):
        lang = match.group(2).strip() or ''
        code = match.group(3)
        placeholder = f'___CODE_BLOCK_{len(code_blocks)}___'
        # Escape HTML in code blocks
        code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        code_blocks[placeholder] = f'<pre><code class="language-{lang}">{code_escaped}</code></pre>'
        return placeholder

    content = re.sub(code_block_pattern, save_code_block, content, flags=re.DOTALL)

    # Convert tables (before other conversions)
    table_pattern = r'(\|.+\|[\r\n]+\|[\s\-:|]+\|[\r\n]+(?:\|.+\|[\r\n]+)*)'
    tables = re.findall(table_pattern, content, re.MULTILINE)
    table_placeholders = {}

    for i, table in enumerate(tables):
        placeholder = f'___TABLE_PLACEHOLDER_{i}___'
        table_placeholders[placeholder] = convert_markdown_table(table)
        content = content.replace(table, placeholder, 1)

    # Convert headings
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)

    # Note: Markdown links already converted earlier (before HTML protection)

    # Convert inline code (before bold/italic to avoid conflicts)
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)

    # Convert bold and italic
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)

    # Convert blockquotes (before lists and paragraphs)
    lines = content.split('\n')
    result_lines = []
    in_blockquote = False
    blockquote_lines = []
    in_list = False

    for line in lines:
        # Blockquote
        if line.startswith('> '):
            if not in_blockquote:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                in_blockquote = True
            blockquote_lines.append(line[2:])  # Remove "> "
        # Unordered list
        elif re.match(r'^[-*+] ', line):
            if in_blockquote:
                # Close blockquote and process its content
                result_lines.append('<blockquote>')
                result_lines.extend(blockquote_lines)
                result_lines.append('</blockquote>')
                blockquote_lines = []
                in_blockquote = False
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item = re.sub(r'^[-*+] ', '', line)
            result_lines.append(f'<li>{item}</li>')
        else:
            if in_blockquote:
                # Close blockquote and process its content
                result_lines.append('<blockquote>')
                result_lines.extend(blockquote_lines)
                result_lines.append('</blockquote>')
                blockquote_lines = []
                in_blockquote = False
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)

    if in_blockquote:
        result_lines.append('<blockquote>')
        result_lines.extend(blockquote_lines)
        result_lines.append('</blockquote>')
    if in_list:
        result_lines.append('</ul>')

    content = '\n'.join(result_lines)

    # Convert horizontal rules
    content = re.sub(r'^---$', r'<hr>', content, flags=re.MULTILINE)

    # Convert paragraphs and wrap tree structure (improved)
    # IMPORTANT: Detect tree structures FIRST before checking for HTML tags
    paragraphs = content.split('\n\n')
    html_paragraphs = []

    # DEBUG: Count tree-like paragraphs
    tree_count = 0

    for para in paragraphs:
        para_stripped = para.strip()

        # Don't wrap if empty
        if not para_stripped:
            html_paragraphs.append(para)
            continue

        # Check if paragraph is a placeholder (code block, table, etc.)
        is_placeholder = para_stripped.startswith('___') and para_stripped.endswith('___')

        # Check if paragraph contains tree structure characters
        # Tree can contain HTML anchors, so check this even if it has HTML tags
        has_tree = any(char in para for char in ['├──', '└──', '│']) and not is_placeholder

        if has_tree:
            tree_count += 1
            # Wrap tree structure in a styled pre block (even if it contains HTML)
            html_paragraphs.append(f'<pre class="tree">{para}</pre>')
        elif para_stripped.startswith('<') or is_placeholder:
            # Already HTML or placeholder, don't wrap
            html_paragraphs.append(para)
        else:
            # Regular paragraph
            html_paragraphs.append(f'<p>{para_stripped}</p>')

    # DEBUG: Write tree count to file
    with open('md2html_debug.txt', 'w', encoding='utf-8') as debug_file:
        debug_file.write(f'Tree paragraphs wrapped: {tree_count}\n')
        debug_file.write(f'Total paragraphs: {len(paragraphs)}\n')
        # Write sample of first few paragraphs
        for i, p in enumerate(paragraphs[:10]):
            has_tree_chars = any(char in p for char in ['├──', '└──', '│'])
            debug_file.write(f'\nPara {i}: has_tree={has_tree_chars}, len={len(p)}, start={p[:100]}\n')

    content = '\n\n'.join(html_paragraphs)

    # Restore table placeholders
    for placeholder, table_html in table_placeholders.items():
        content = content.replace(placeholder, table_html)

    # Restore code block placeholders
    for placeholder, code_html in code_blocks.items():
        content = content.replace(placeholder, code_html)

    # Restore HTML tag placeholders
    for placeholder, html_tag in html_tags.items():
        content = content.replace(placeholder, html_tag)

    return content


def wrap_html_document(content: str, title: str = "Document") -> str:
    """
    Wrap HTML content in a full HTML document with CSS.

    Args:
        content: HTML content
        title: Document title

    Returns:
        Complete HTML document
    """
    css = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #fff;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            color: #2c3e50;
            font-weight: 600;
        }
        h1 {
            font-size: 2.5em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }
        h2 {
            font-size: 2em;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 8px;
        }
        h3 {
            font-size: 1.5em;
            color: #34495e;
        }
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: #e83e8c;
        }
        pre {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border: 1px solid #e9ecef;
            line-height: 1.4;
        }
        pre code {
            background: none;
            padding: 0;
            color: #333;
        }
        pre.tree {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px 20px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.95em;
            line-height: 1.6;
            white-space: pre;
            overflow-x: auto;
        }
        .diagram {
            margin: 20px 0;
            text-align: center;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .diagram svg {
            max-width: 100%;
            height: auto;
        }
        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }
        li {
            margin: 0.5em 0;
        }
        a {
            color: #3498db;
            text-decoration: none;
            transition: color 0.2s;
        }
        a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 1em 0;
            padding: 0.5em 0 0.5em 1em;
            color: #555;
            background: #f8f9fa;
            border-radius: 0 3px 3px 0;
        }
        blockquote p {
            margin: 0.5em 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 15px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    """

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{content}
</body>
</html>"""

    return html


def register_md2html_command(subparsers):
    """
    Register the md2html command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'md2html',
        help='Convert Markdown with diagrams to HTML with embedded SVG',
        description='Convert Markdown files containing Graphviz, PlantUML, or Mermaid diagrams to HTML with embedded SVG graphics.'
    )

    parser.add_argument(
        'markdown',
        type=str,
        help='Markdown file to convert'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output HTML file path (default: <markdown>.html)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed conversion progress'
    )

    parser.add_argument(
        '--no-standalone',
        action='store_true',
        help='Generate HTML fragment without full document structure'
    )

    parser.set_defaults(func=lambda args: process_markdown_to_html(
        args.markdown,
        args.output,
        args.verbose,
        not args.no_standalone
    ))
