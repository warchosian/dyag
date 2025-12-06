"""
Command to convert HTML files to PDF while preserving hyperlinks and SVG vectors.

This module uses Playwright + Chromium to convert HTML to PDF with full support for:
- Internal anchor links (TOC navigation)
- External hyperlinks
- CSS styling
- SVG diagrams (preserved as vectors)
- Portrait and landscape orientations
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def convert_html_to_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    orientation: str = 'portrait',
    verbose: bool = False
) -> int:
    """
    Convert HTML file to PDF while preserving hyperlinks and SVG vectors.

    Args:
        input_path: Path to input HTML file
        output_path: Optional path to output PDF file. If None, uses <input>.pdf
        orientation: Page orientation - 'portrait' or 'landscape' (default: 'portrait')
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check if Playwright is available
    if not PLAYWRIGHT_AVAILABLE:
        print("Error: Playwright is not installed.", file=sys.stderr)
        print("Install it with:", file=sys.stderr)
        print("  pip install playwright", file=sys.stderr)
        print("  playwright install chromium", file=sys.stderr)
        return 1

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
        output_file = input_file.parent / f"{input_file.stem}.pdf"
    else:
        output_file = Path(output_path).resolve()

    # Validate orientation
    if orientation not in ['portrait', 'landscape']:
        print(f"Error: Invalid orientation '{orientation}'. Must be 'portrait' or 'landscape'.", file=sys.stderr)
        return 1

    if verbose:
        print(f"Processing: {input_file}")
        print(f"Output: {output_file}")
        print(f"Orientation: {orientation}")

    try:
        if verbose:
            print("\n[INFO] Starting Chromium for PDF conversion...")
            print("[INFO] SVG diagrams will be preserved as vectors")
            print("[INFO] All hyperlinks will be preserved")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Load HTML file
            if verbose:
                print(f"[INFO] Loading HTML file...")

            page.goto(f'file:///{input_file.as_posix()}')

            # Wait for page to fully load (including SVG rendering)
            page.wait_for_load_state('networkidle')

            # Configure PDF options
            pdf_options = {
                'path': str(output_file),
                'format': 'A4',
                'print_background': True,
                'prefer_css_page_size': False,
                'margin': {
                    'top': '20mm',
                    'right': '20mm',
                    'bottom': '20mm',
                    'left': '20mm'
                }
            }

            # Set orientation
            if orientation == 'landscape':
                pdf_options['landscape'] = True

            # Generate PDF
            if verbose:
                print("[INFO] Generating PDF with vector SVG...")

            page.pdf(**pdf_options)

            browser.close()

        # Get file sizes for reporting
        input_size = input_file.stat().st_size
        output_size = output_file.stat().st_size

        print(f"\n[SUCCESS] PDF created: {output_file}")
        print(f"[INFO] Input HTML: {input_size:,} bytes")
        print(f"[INFO] Output PDF: {output_size:,} bytes")
        print(f"[INFO] Orientation: {orientation}")
        print(f"[INFO] SVG diagrams preserved as vectors")
        print(f"[INFO] All hyperlinks preserved")

        return 0

    except Exception as e:
        error_msg = str(e)

        if "executable doesn't exist" in error_msg or "Executable doesn't exist" in error_msg:
            print("Error: Chromium browser is not installed.", file=sys.stderr)
            print("\nPlease install Chromium:", file=sys.stderr)
            print("  playwright install chromium", file=sys.stderr)
            print("\nThis will download Chromium (~100MB) once.", file=sys.stderr)
        else:
            print(f"Error: Failed to convert HTML to PDF: {e}", file=sys.stderr)

        import traceback
        if verbose:
            traceback.print_exc()
        return 1


def register_html2pdf_command(subparsers):
    """
    Register the html2pdf command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'html2pdf',
        help='Convert HTML file to PDF with vector SVG (via Chromium)',
        description='Convert HTML to PDF using Chromium browser. Preserves SVG diagrams as vectors '
                    'and maintains all internal/external hyperlinks. Supports portrait and landscape.'
    )

    parser.add_argument(
        'input',
        type=str,
        help='HTML file to convert'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output PDF file path (default: <input>.pdf)'
    )

    parser.add_argument(
        '-r', '--orientation',
        type=str,
        choices=['portrait', 'landscape'],
        default='portrait',
        help='Page orientation (default: portrait)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: convert_html_to_pdf(
        args.input,
        args.output,
        args.orientation,
        args.verbose
    ))
