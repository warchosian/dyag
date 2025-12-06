"""
Command to compress an existing PDF file.
"""

import sys
from pathlib import Path
from io import BytesIO

try:
    from PIL import Image
    import fitz  # PyMuPDF
except ImportError:
    Image = None
    fitz = None


def compress_pdf(input_path: str, output_path: str = None, quality: int = 85, verbose: bool = False) -> int:
    """
    Compress an existing PDF file by reprocessing its images.

    Args:
        input_path: Path to the input PDF file
        output_path: Optional output PDF path. If None, adds '_compressed' suffix
        quality: JPEG quality for compression (1-100, default 85)
        verbose: Print verbose output

    Returns:
        Exit code (0 for success, 1 for error)
    """
    if Image is None or fitz is None:
        print("Error: Required libraries are not installed.", file=sys.stderr)
        print("Install them with: pip install Pillow PyMuPDF", file=sys.stderr)
        return 1

    pdf_path = Path(input_path).resolve()

    # Check if PDF exists
    if not pdf_path.exists():
        print(f"Error: PDF file '{input_path}' does not exist.", file=sys.stderr)
        return 1

    if not pdf_path.is_file():
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        return 1

    if pdf_path.suffix.lower() != '.pdf':
        print(f"Error: '{input_path}' is not a PDF file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        # Add '_compressed' before the extension
        output_path = pdf_path.parent / f"{pdf_path.stem}_compressed{pdf_path.suffix}"
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()

    if verbose:
        print(f"Input PDF: {pdf_path}")
        print(f"Output PDF: {output_path}")
        print(f"Compression quality: {quality}")

    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        if verbose:
            print(f"\nProcessing {total_pages} pages...")

        # Create a new PDF
        new_doc = fitz.open()

        for page_num in range(total_pages):
            page = doc[page_num]

            # Render page to image at 72 DPI (standard PDF resolution)
            # Use 1.0 zoom to keep original size
            mat = fitz.Matrix(1.0, 1.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert to PIL Image
            img_data = pix.tobytes("jpeg")
            img = Image.open(BytesIO(img_data))

            # Ensure RGB mode
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Compress the image with optimization
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
            buffer.seek(0)

            # Create a new page with compressed image
            rect = page.rect
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(rect, stream=buffer.getvalue())

            if verbose:
                print(f"  Compressed page {page_num + 1}/{total_pages}")

        # Save the compressed PDF
        new_doc.save(output_path, garbage=4, deflate=True, clean=True)
        new_doc.close()
        doc.close()

        # Get file sizes
        original_size = pdf_path.stat().st_size
        compressed_size = output_path.stat().st_size
        reduction = ((original_size - compressed_size) / original_size) * 100

        print(f"\nSuccess! Compressed PDF created: {output_path}")
        print(f"Original size: {original_size / (1024*1024):.2f} MB")
        print(f"Compressed size: {compressed_size / (1024*1024):.2f} MB")
        print(f"Size reduction: {reduction:.1f}%")

        return 0

    except Exception as e:
        print(f"Error: Failed to compress PDF: {e}", file=sys.stderr)
        return 1


def register_compresspdf_command(subparsers):
    """
    Register the compresspdf command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'compresspdf',
        help='Compress an existing PDF file',
        description='Compress an existing PDF file by reprocessing its images with JPEG compression.'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Input PDF file to compress'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output PDF file path (default: <input>_compressed.pdf)'
    )

    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        choices=range(1, 101),
        metavar='QUALITY',
        help='JPEG quality for compression (1-100, default: 85). Lower values = smaller file size but lower quality'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed compression progress'
    )

    parser.set_defaults(func=lambda args: compress_pdf(
        args.input,
        args.output,
        args.quality,
        args.verbose
    ))
