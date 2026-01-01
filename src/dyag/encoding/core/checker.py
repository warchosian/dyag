"""
Vérification d'encodage de fichiers Markdown - DYAG

Fonctions pour détecter l'encodage de fichiers Markdown via chardet.
"""

from pathlib import Path
from typing import List

import chardet

from ...core.pathglob import resolve_path_patterns


def check_md(file_path: Path) -> dict:
    """Vérifie l'encodage d'un fichier Markdown.

    Args:
        file_path (Path): Chemin vers le fichier (doit exister).

    Returns:
        dict: Résultat avec 'path', 'encoding', 'confidence', 'raw_data', 'error'.
    """
    result = {
        "path": file_path,
        "encoding": None,
        "confidence": 0.0,
        "raw_data": None,
        "error": None
    }

    try:
        if not file_path.is_file():
            result["error"] = "Not a file or does not exist"
            return result

        raw_data = file_path.read_bytes()
        result["raw_data"] = raw_data

        detected = chardet.detect(raw_data)
        result["encoding"] = detected["encoding"]
        result["confidence"] = detected["confidence"]

    except Exception as e:
        result["error"] = str(e)

    return result


def check_markdown_files(patterns: List[str]) -> List[dict]:
    """API publique : analyse les .md correspondant aux motifs.

    Args:
        patterns: Liste de motifs (ex: ["docs/**/*.md"])

    Returns:
        Liste de résultats (dict), un par fichier Markdown trouvé.
    """
    paths = resolve_path_patterns(patterns)
    md_files = [p for p in paths if p.suffix.lower() == ".md"]
    return [check_md(p) for p in md_files]
