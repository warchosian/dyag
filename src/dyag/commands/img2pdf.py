"""
Command to convert images in a directory to a PDF file.
"""

import os
import sys
from pathlib import Path
from typing import List

try:
    from PIL import Image
except ImportError:
    Image = None


# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}


def get_image_files(directory: Path) -> List[Path]:
    """
    Get all image files from a directory, sorted alphabetically.

    Args:
        directory: Path to the directory containing images

    Returns:
        List of Path objects for image files, sorted alphabetically
    """
    image_files = []

    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_files.append(file_path)

    # Sort alphabetically by name
    image_files.sort(key=lambda x: x.name)

    return image_files


def images_to_pdf(directory: str, output_path: str = None, verbose: bool = False, compress: bool = False, quality: int = 85) -> int:
    """
    Convert all images in a directory to a single PDF file.

    Args:
        directory: Path to the directory containing images
        output_path: Optional output PDF path. If None, uses directory name
        verbose: Print verbose output
        compress: Enable compression to reduce PDF size
        quality: JPEG quality for compression (1-100, default 85)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    if Image is None:
        print("Error: Pillow library is not installed.", file=sys.stderr)
        print("Install it with: pip install Pillow", file=sys.stderr)
        return 1

    dir_path = Path(directory).resolve()

    # Check if directory exists
    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        return 1

    if not dir_path.is_dir():
        print(f"Error: '{directory}' is not a directory.", file=sys.stderr)
        return 1

    # Get all image files
    image_files = get_image_files(dir_path)

    if not image_files:
        print(f"Error: No image files found in '{directory}'.", file=sys.stderr)
        print(f"Supported formats: {', '.join(sorted(IMAGE_EXTENSIONS))}", file=sys.stderr)
        return 1

    # Determine output path
    if output_path is None:
        # Create PDF inside the source directory with the directory name
        output_path = dir_path / (dir_path.name + ".pdf")
    else:
        output_path = Path(output_path)

    output_path = output_path.resolve()

    if verbose:
        print(f"Found {len(image_files)} image(s) in '{dir_path.name}':")
        for img_file in image_files:
            print(f"  - {img_file.name}")
        print(f"\nConverting to PDF: {output_path}")
        if compress:
            print(f"Compression enabled (quality: {quality})")

    try:
        # Open all images and convert to RGB
        images = []
        first_image = None

        for i, img_path in enumerate(image_files):
            try:
                img = Image.open(img_path)

                # Convert to RGB (PDF requires RGB mode)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Apply compression if requested
                if compress:
                    from io import BytesIO
                    # Compress by saving to BytesIO and reloading
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                    buffer.seek(0)
                    img = Image.open(buffer)

                if i == 0:
                    first_image = img
                else:
                    images.append(img)

                if verbose:
                    print(f"  Processed: {img_path.name}")

            except Exception as e:
                print(f"Warning: Could not process {img_path.name}: {e}", file=sys.stderr)
                continue

        if first_image is None:
            print("Error: No images could be processed.", file=sys.stderr)
            return 1

        # Save as PDF
        first_image.save(
            output_path,
            "PDF",
            save_all=True,
            append_images=images,
            resolution=100.0
        )

        print(f"\nSuccess! PDF created: {output_path}")
        print(f"Total pages: {len(image_files)}")

        return 0

    except Exception as e:
        print(f"Error: Failed to create PDF: {e}", file=sys.stderr)
        return 1


def register_img2pdf_command(subparsers):
    """
    Register the img2pdf command with the argument parser.

    Args:
        subparsers: The subparsers object from argparse
    """
    parser = subparsers.add_parser(
        'img2pdf',
        help='Convert images in a directory to a PDF file',
        description='Convert all image files in a directory to a single PDF file. '
                    'Images are ordered alphabetically by filename.'
    )

    parser.add_argument(
        'directory',
        type=str,
        help='Directory containing the images to convert'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output PDF file path (default: <directory>/<directory_name>.pdf)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed conversion progress'
    )

    parser.add_argument(
        '-c', '--compress',
        action='store_true',
        help='Enable compression to reduce PDF size'
    )

    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        choices=range(1, 101),
        metavar='QUALITY',
        help='JPEG quality for compression (1-100, default: 85). Lower values = smaller file size but lower quality'
    )

    parser.set_defaults(func=lambda args: images_to_pdf(
        args.directory,
        args.output,
        args.verbose,
        args.compress,
        args.quality
    ))
