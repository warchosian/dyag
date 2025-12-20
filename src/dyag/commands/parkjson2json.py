"""
parkjson2json - Extraction et filtrage d'applications du parc applicatif JSON.

Extrait un sous-ensemble d'applications d'un fichier JSON en appliquant des filtres
(plage, nom, ID) et génère un nouveau fichier JSON contenant uniquement les applications
sélectionnées.

Exemple:
    dyag parkjson2json applicationsIA.json -r 1-10 -o subset.json
    dyag parkjson2json applicationsIA.json -n "ADEME" -o ademe_apps.json
    dyag parkjson2json applicationsIA.json -i "AFF1234" -o app_specific.json
"""

import json
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Import version from dyag package
try:
    from dyag import __version__
except ImportError:
    __version__ = "0.7.0"


def normalize_key(key: str) -> str:
    """Normalize a key to lowercase for comparison."""
    return str(key).lower().strip().replace('_', ' ').replace('-', ' ')


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: The string to sanitize
        max_length: Maximum length of the resulting filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Replace multiple spaces/underscores with single underscore
    safe_name = re.sub(r'[_\s]+', '_', safe_name)
    # Remove leading/trailing underscores and spaces
    safe_name = safe_name.strip('_ ')
    # Limit length
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    return safe_name


def parse_range_spec(spec: str, total: int) -> List[int]:
    """
    Parse range specification and return list of indices.

    Examples:
        "1-3" -> [0, 1, 2]
        "-5" -> last 5 elements
        "10-" -> from 10 to end
        "1,3,5-7" -> [0, 2, 4, 5, 6]

    Args:
        spec: Range specification string
        total: Total number of elements

    Returns:
        List of indices (0-based)
    """
    if not spec.strip():
        return list(range(total))

    indices = set()
    parts = spec.replace(" ", "").split(",")

    for part in parts:
        if not part:
            continue

        if "-" in part:
            if part.startswith("-"):
                # Last N elements: "-5" means last 5
                n = int(part[1:])
                start = max(0, total - n)
                indices.update(range(start, total))
            elif part.endswith("-"):
                # From N to end: "10-" means from 10 to end
                start = int(part[:-1]) - 1
                if 0 <= start < total:
                    indices.update(range(start, total))
            else:
                # Range: "5-10" means from 5 to 10
                a, b = part.split("-")
                a_i = max(0, int(a) - 1)
                b_i = min(total, int(b))
                indices.update(range(a_i, b_i))
        else:
            # Single index: "5" means element 5 (0-based: index 4)
            i = int(part) - 1
            if 0 <= i < total:
                indices.add(i)

    return sorted(indices)


def sanitize_tag(tag: str) -> str:
    """
    Sanitize a tag for use in filenames.

    Args:
        tag: Tag string to sanitize

    Returns:
        Sanitized tag
    """
    import re
    tag = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", tag.strip())
    return re.sub(r'_+', "_", tag)[:50]


def get_field(data: Dict, *key_variants) -> Any:
    """
    Get a field from a dictionary, trying multiple key variants (case-insensitive).

    Args:
        data: Dictionary to search
        *key_variants: One or more key variants to try

    Returns:
        Value if found, None otherwise
    """
    if not isinstance(data, dict):
        return None

    # Create normalized lookup
    normalized = {normalize_key(k): v for k, v in data.items()}

    # Try each variant
    for variant in key_variants:
        norm_variant = normalize_key(variant)
        if norm_variant in normalized:
            return normalized[norm_variant]

    return None


def find_by_name(data_list: List[Dict], name_query: str) -> List[Dict]:
    """
    Filter applications by name (case-insensitive substring match).

    Args:
        data_list: List of application dictionaries
        name_query: Name to search for

    Returns:
        List of matching applications
    """
    results = []
    query = name_query.strip().lower()

    for item in data_list:
        # Try different name field variants
        name = get_field(item, "nom", "name", "title", "label")
        if name and query in str(name).lower():
            results.append(item)

    return results


def find_by_id(data_list: List[Dict], id_query: str) -> List[Dict]:
    """
    Filter applications by ID (case-insensitive substring match).

    Args:
        data_list: List of application dictionaries
        id_query: ID to search for

    Returns:
        List of matching applications
    """
    results = []
    target = id_query.strip().upper()

    for item in data_list:
        # Try to find ID field
        item_id = get_field(item, "id")
        if item_id and target in str(item_id).upper():
            results.append(item)

    return results


def generate_metadata(
    source_file: str,
    original_count: int,
    filtered_count: int,
    filter_type: Optional[str] = None,
    filter_value: Optional[str] = None
) -> Dict:
    """
    Generate metadata for the filtered JSON output.

    Args:
        source_file: Source filename
        original_count: Total number of applications in source
        filtered_count: Number of applications after filtering
        filter_type: Type of filter applied ('range', 'name', 'id', or None)
        filter_value: Value of the filter

    Returns:
        Dictionary containing metadata
    """
    # Determine filter description
    if filter_type == "range":
        if filter_value.startswith("-"):
            description = f"{filter_value[1:]} dernières applications"
        elif filter_value.endswith("-"):
            description = f"À partir de l'application {filter_value[:-1]}"
        else:
            description = f"Applications {filter_value}"
    elif filter_type == "name":
        description = f"Applications contenant '{filter_value}' dans le nom (insensible à la casse)"
    elif filter_type == "id":
        description = f"Applications avec ID contenant '{filter_value}' (insensible à la casse)"
    else:
        description = "Toutes les applications (aucun filtre appliqué)"

    # Calculate percentage
    if original_count > 0:
        percentage = f"{(filtered_count / original_count * 100):.1f}%"
    else:
        percentage = "0.0%"

    metadata = {
        "tool": "dyag parkjson2json",
        "version": __version__,
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source": {
            "file": source_file,
            "total_count": original_count
        },
        "filter": {
            "type": filter_type if filter_type else "none",
            "value": filter_value,
            "description": description
        },
        "output": {
            "count": filtered_count,
            "percentage": percentage
        }
    }

    return metadata


def process_parkjson2json(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False,
    range_spec: Optional[str] = None,
    name_filter: Optional[str] = None,
    id_filter: Optional[str] = None,
    preserve_structure: bool = True,
    include_metadata: bool = True,
    split_dir: Optional[str] = None
) -> int:
    """
    Extract filtered applications from JSON and save to new JSON file.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (optional)
        verbose: Show detailed progress
        range_spec: Range specification (e.g., "1-3", "-5", "10-")
        name_filter: Filter by application name
        id_filter: Filter by application ID
        preserve_structure: Keep original JSON structure (default: True)
        include_metadata: Include metadata in output JSON (default: True)
        split_dir: Directory to generate separate files for each application

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: '{input_file}' does not exist.", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"Error: '{input_file}' is not a file.", file=sys.stderr)
        return 1

    try:
        # Read JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            json_content = f.read()

        if verbose:
            print(f"[INFO] Read {len(json_content)} characters from {input_path}")

        # Parse JSON
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}", file=sys.stderr)
            return 1

        # Find applications list and track structure
        apps = None
        apps_key = None
        root_is_list = False

        if isinstance(data, dict):
            for key in data:
                key_lower = normalize_key(key)
                if 'application' in key_lower:
                    apps = data[key]
                    apps_key = key
                    if verbose:
                        print(f"[INFO] Found applications under key: {key}")
                    break

            if apps is None:
                if verbose:
                    print(f"[INFO] No applications key found, treating as generic JSON")
                apps = [data]
                preserve_structure = False

        elif isinstance(data, list):
            apps = data
            root_is_list = True
            if verbose:
                print(f"[INFO] JSON root is a list with {len(apps)} items")

        if not apps:
            print("[ERROR] No data found in JSON", file=sys.stderr)
            return 1

        original_count = len(apps)
        tag_parts = []
        used_filter = False
        filter_type = None
        filter_value = None

        # Apply filters
        if id_filter:
            apps = find_by_id(apps, id_filter)
            clean_id = sanitize_tag(id_filter.upper())
            tag_parts.append(f"ID{clean_id}")
            print(f"[FILTER] ID '{id_filter}' -> {len(apps)} resultat(s)")
            used_filter = True
            filter_type = "id"
            filter_value = id_filter

        elif name_filter:
            apps = find_by_name(apps, name_filter)
            if apps and get_field(apps[0], "nom", "name"):
                tag_name = sanitize_tag(str(get_field(apps[0], "nom", "name")))
            else:
                tag_name = sanitize_tag(name_filter)
            tag_parts.append(tag_name)
            print(f"[FILTER] Nom '{name_filter}' -> {len(apps)} resultat(s)")
            used_filter = True
            filter_type = "name"
            filter_value = name_filter

        elif range_spec:
            indices = parse_range_spec(range_spec, original_count)
            apps = [apps[i] for i in indices] if indices else []
            tag_parts.append(sanitize_tag(range_spec))
            print(f"[FILTER] Plage '{range_spec}' -> {len(apps)} element(s)")
            used_filter = True
            filter_type = "range"
            filter_value = range_spec

        if not apps:
            print("[WARNING] No applications match the filters", file=sys.stderr)
            return 1

        # SPLIT MODE: Generate separate file for each application
        if split_dir:
            split_path = Path(split_dir)
            split_path.mkdir(parents=True, exist_ok=True)

            if verbose:
                print(f"[INFO] Extracting {len(apps)} application(s) to separate JSON files...")
                print(f"[INFO] Input:  {input_path}")
                print(f"[INFO] Output directory: {split_path}")

            files_created = 0
            for i, app in enumerate(apps):
                if verbose and (i + 1) % 100 == 0:
                    print(f"[INFO] Processed {i + 1}/{len(apps)} applications...")

                # Get application name
                app_name = get_field(app, "nom", "name", "title", "label") or f"app_{i+1}"
                safe_app_name = sanitize_filename(app_name)

                # Create filename: inputname_appname.json
                filename = f"{input_path.stem}_{safe_app_name}.json"
                file_path = split_path / filename

                # Write application to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(app, f, ensure_ascii=False, indent=2)

                files_created += 1

            # Calculate percentage for summary
            percentage = f"{(len(apps) / original_count * 100):.1f}%" if original_count > 0 else "0.0%"

            print(f"[SUCCESS] {files_created} JSON files created in {split_path}")
            print(f"          Contains {len(apps)} application(s) ({percentage} of original)")
            return 0

        # NORMAL MODE: Single file output
        # Determine output path
        if output_file is None:
            if used_filter and tag_parts:
                tag_suffix = "_".join(tag_parts)
                output_path = input_path.with_name(f"{input_path.stem}_{tag_suffix}.json")
            else:
                # No filter: just change extension to .json
                output_path = input_path.with_suffix(".json")
        else:
            output_path = Path(output_file)

        if verbose:
            print(f"[INFO] Extracting {len(apps)} application(s) to JSON...")
            print(f"[INFO] Input:  {input_path}")
            print(f"[INFO] Output: {output_path}")

        # Build output JSON structure
        if preserve_structure and apps_key:
            # Preserve original structure with wrapper key
            output_data = {apps_key: apps}
        elif root_is_list:
            # Root was already a list
            output_data = apps
        else:
            # Default: wrap in applications key
            output_data = {"applications": apps}

        # Add metadata if requested
        if include_metadata:
            if verbose:
                print(f"[INFO] Adding metadata to output...")

            metadata = generate_metadata(
                source_file=input_path.name,
                original_count=original_count,
                filtered_count=len(apps),
                filter_type=filter_type,
                filter_value=filter_value
            )

            # Insert metadata at the beginning
            if isinstance(output_data, dict):
                # Create new dict with metadata first
                output_data = {"_metadata": metadata, **output_data}
            else:
                # If output_data is a list, wrap it with metadata
                output_data = {
                    "_metadata": metadata,
                    "applications": output_data
                }

        # Write JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        if verbose:
            output_size = output_path.stat().st_size
            print(f"[INFO] Wrote {output_size} bytes to {output_path}")
            print(f"[INFO] Metadata included: {'Yes' if include_metadata else 'No'}")

        # Calculate percentage for summary
        percentage = f"{(len(apps) / original_count * 100):.1f}%" if original_count > 0 else "0.0%"

        print(f"[SUCCESS] JSON file created: {output_path}")
        print(f"          Contains {len(apps)} application(s) ({percentage} of original)")
        if include_metadata:
            print(f"          Metadata: Included")
        return 0

    except Exception as e:
        print(f"Error: Extraction failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_parkjson2json_command(subparsers):
    """Register the parkjson2json command."""
    parser = subparsers.add_parser(
        'parkjson2json',
        help='Extract filtered applications to new JSON file',
        description='Extract and filter applications from a JSON file, creating a new JSON file with only the selected applications.'
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Input JSON file path'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output JSON file path (default: input_FILTER.json with filter, or input.json without filter)'
    )

    parser.add_argument(
        '-r', '--range',
        type=str,
        metavar='RANGE',
        default=None,
        help='Select range of applications (e.g., "1-3", "-5" for last 5, "10-" from 10 to end)'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        metavar='NAME',
        default=None,
        help='Filter applications by name (case-insensitive substring match)'
    )

    parser.add_argument(
        '-i', '--id',
        type=str,
        metavar='ID',
        default=None,
        help='Filter applications by ID (case-insensitive substring match)'
    )

    parser.add_argument(
        '--no-preserve-structure',
        action='store_true',
        help='Do not preserve original JSON structure (use default "applications" key)'
    )

    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Do not include metadata in output JSON (metadata included by default)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.add_argument(
        '--split-dir',
        type=str,
        metavar='DIR',
        default=None,
        help='Generate each application in a separate file in the specified directory (filename: inputname_appname.json)'
    )

    parser.set_defaults(func=lambda args: process_parkjson2json(
        args.input_file,
        args.output,
        args.verbose,
        args.range,
        args.name,
        args.id,
        not args.no_preserve_structure,
        not args.no_metadata,
        args.split_dir
    ))
