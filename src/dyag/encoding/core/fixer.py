"""
Correction d'encodage et contenu de fichiers Markdown - DYAG

Fonctions pour convertir vers UTF-8 et corriger le contenu Markdown.
"""

import re
import urllib.parse
import html
from pathlib import Path
from typing import List, Tuple

from ...core.pathglob import resolve_path_patterns
from .checker import check_md


# === RÈGLES DE CORRECTION ===

def decode_html_entities(text: str) -> str:
    """Décode les entités HTML courantes (&nbsp; → ' ', etc.)"""
    # D'abord les numériques (&#160; → \xa0), puis nommées (&nbsp; → \xa0), puis html.unescape
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
    text = html.unescape(text)
    return text


def fix_anchor_ids(text: str) -> str:
    """Supprime les espaces à la fin des valeurs id dans les balises HTML.

    Corrige: id="section-1 " → id="section-1"
    """
    # Matcher id="..." et capturer le contenu sans espaces finaux
    return re.sub(r'id\s*=\s*"([^"]*?)\s*"', r'id="\1"', text)


def encode_spaces_in_links(text: str) -> str:
    """Encode les espaces dans les URLs de liens/images Markdown :
    [text](path/file name.md) → [text](path/file%20name.md)
    ![alt](uploads/xxx xxx.png) → ![alt](uploads/xxx%20xxx.png)
    """
    def repl_link(match):
        pre, url, post = match.groups()
        # Ne pas encoder les % déjà présents (éviter double encodage)
        if "%" not in url:
            url = urllib.parse.quote(url, safe="/:?#[]@!$&'()*+,;=-._~")
        return f"{pre}{url}{post}"

    # Markdown links & images
    text = re.sub(r"(!?\[[^\]]*\]\()([^)]+)(\))", repl_link, text)
    # HTML <a href="">, <img src="">
    text = re.sub(r"""(<(?:a|img)\s[^>]*?(?:href|src)\s*=\s*['"])([^'"]*)(['"][^>]*?>)""", repl_link, text, flags=re.IGNORECASE)
    return text


def ensure_non_empty(content: str) -> str:
    """Si vide (ou uniquement du blanc), ajoute un commentaire"""
    stripped = content.strip()
    if not stripped:
        return "<!-- À compléter -->\n"
    return content


def fix_file_encoding_and_content(path: Path, dry_run: bool = False, backup: bool = False) -> Tuple[bool, str]:
    """
    Corrige un fichier .md :
      1. Détecte et re-encode en UTF-8
      2. Applique les corrections de contenu
    Retourne (ok: bool, message: str)
    """
    try:
        # 🔍 Détection initiale via check_md
        check_result = check_md(path)
        raw = check_result.get("raw_data")
        encoding = check_result.get("encoding") or "utf-8"
        confidence = check_result.get("confidence") or 0.0

        if check_result.get("error") or raw is None:
            error_msg = check_result.get('error', 'could not read file')
            return False, f"❌ échec: {error_msg}"

        # chardet peut se tromper sur un fichier avec BOM ('utf-8' au lieu de 'utf-8-sig').
        # On force 'utf-8-sig' pour que le decode() supprime le BOM.
        if raw.startswith(b'\xef\xbb\xbf'):
            encoding = 'utf-8-sig'

        try:
            text = raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            # fallback hard
            text = raw.decode("utf-8", errors="replace")
            encoding = "utf-8 (fallback)"
            confidence = 0.0

        # 🛠️ CORRECTIONS
        original = text
        text = decode_html_entities(text)
        text = fix_anchor_ids(text)
        text = encode_spaces_in_links(text)
        text = ensure_non_empty(text)

        changed = (text != original) or (encoding.lower() not in ("utf-8", "utf8", "ascii"))

        if not changed:
            return True, "ok (déjà conforme)"

        # 💾 ÉCRITURE
        if not dry_run:
            if backup and path.exists():
                bak = path.with_suffix(path.suffix + ".bak")
                path.replace(bak)  # backup atomique

            # Toujours écrire en UTF-8 *sans BOM* (standard GitHub/GitLab)
            path.write_text(text, encoding="utf-8", newline="\n")

        status = "✅ corrigé" if not dry_run else "🔧 (dry-run)"
        details = []
        if encoding.lower() not in ("utf-8", "utf8", "ascii"):
            details.append(f"encoding:{encoding}({confidence:.0%})→UTF-8")
        if text != original:
            details.append("contenu modifié")
        return True, f"{status} [{', '.join(details)}]"

    except Exception as e:
        return False, f"❌ échec: {e}"


def fix_markdown_files(patterns: List[str], dry_run: bool = False, backup: bool = False) -> List[dict]:
    """API programmatique : retourne un rapport détaillé"""
    try:
        paths = resolve_path_patterns(patterns)
        md_files = [p for p in paths if p.suffix.lower() == ".md"]
    except Exception as e:
        return [{"error": f"resolve_path_patterns failed: {e}"}]

    results = []
    for p in md_files:
        ok, msg = fix_file_encoding_and_content(p, dry_run=dry_run, backup=backup)
        results.append({
            "path": str(p),
            "success": ok,
            "message": msg,
            "dry_run": dry_run
        })
    return results
