"""
Utilitaires pour détecter et corriger les problèmes d'encodage, notamment les emojis.
"""

import re
from pathlib import Path
from typing import Tuple, Optional

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


class EncodingFixer:
    """Détecte et corrige les problèmes d'encodage dans les fichiers Markdown"""

    # Mapping des emojis corrompus latin-1 → emoji UTF-8 correct
    EMOJI_FIXES = {
        # 📄 (U+1F4C4) corrompu en latin-1
        '\xf0\x9f\x93\x84': '📄',  # File emoji
        'ðŸ"„': '📄',

        # 📁 (U+1F4C1) corrompu en latin-1
        '\xf0\x9f\x93\x81': '📁',  # Folder emoji
        'ðŸ"': '📁',

        # 🔍 (U+1F50D) corrompu
        '\xf0\x9f\x94\x8d': '🔍',
        'ðŸ"': '🔍',

        # Variantes avec ?? (quand complètement perdu)
        '??': '',  # Supprimer les ?? orphelins
    }

    @staticmethod
    def detect_encoding(file_path: str) -> Tuple[str, float]:
        """
        Détecte l'encodage d'un fichier avec chardet (si disponible).

        Args:
            file_path: Chemin du fichier

        Returns:
            Tuple (encoding, confidence)
        """
        if not HAS_CHARDET:
            # Fallback : essayer de détecter le BOM
            with open(file_path, 'rb') as f:
                start = f.read(4)
                if start.startswith(b'\xef\xbb\xbf'):
                    return 'utf-8-sig', 1.0
                elif start.startswith(b'\xff\xfe') or start.startswith(b'\xfe\xff'):
                    return 'utf-16', 0.9
                else:
                    return 'utf-8', 0.5  # Guess par défaut

        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']

    @staticmethod
    def read_with_fallback(file_path: str, verbose: bool = False) -> Tuple[str, str]:
        """
        Lit un fichier en essayant plusieurs encodages.

        Args:
            file_path: Chemin du fichier
            verbose: Afficher les tentatives

        Returns:
            Tuple (content, encoding_used)
        """
        # D'abord essayer chardet
        try:
            detected_encoding, confidence = EncodingFixer.detect_encoding(file_path)
            if verbose:
                print(f"[DETECT] {detected_encoding} (confiance: {confidence:.2%})")

            if confidence > 0.7:
                try:
                    content = Path(file_path).read_text(encoding=detected_encoding)
                    return content, detected_encoding
                except (UnicodeDecodeError, LookupError):
                    pass
        except Exception as e:
            if verbose:
                print(f"[WARNING] Détection chardet échouée: {e}")

        # Fallback sur liste d'encodages
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        last_error = None

        for encoding in encodings:
            try:
                content = Path(file_path).read_text(encoding=encoding)
                if verbose:
                    print(f"[INFO] Fichier lu avec encodage: {encoding}")
                return content, encoding
            except (UnicodeDecodeError, LookupError) as e:
                last_error = e
                continue

        raise last_error or Exception(f"Impossible de lire {file_path}")

    @staticmethod
    def fix_mojibake(text: str) -> str:
        """
        Corrige les mojibake (emojis corrompus).

        Détecte si le texte contient des emojis UTF-8 mal décodés en latin-1,
        et tente de les reconstruire.

        Args:
            text: Texte potentiellement corrompu

        Returns:
            Texte corrigé
        """
        # Essayer de détecter et corriger les emojis UTF-8 lus comme latin-1
        # Pattern: séquences de bytes UTF-8 décodés en latin-1
        try:
            # Si le texte contient des caractères comme "ðŸ"„"
            # C'est probablement UTF-8 mal décodé en latin-1
            # On réencode en latin-1 puis décode en UTF-8
            if any(ord(c) > 127 for c in text):
                # Détecter si c'est du mojibake
                test_bytes = text.encode('latin-1', errors='ignore')
                try:
                    fixed = test_bytes.decode('utf-8')
                    # Vérifier si ça a amélioré (présence d'emojis)
                    if any(ord(c) > 0x1F000 for c in fixed):
                        return fixed
                except UnicodeDecodeError:
                    pass
        except Exception:
            pass

        return text

    @staticmethod
    def replace_corrupted_emojis(text: str) -> str:
        """
        Remplace les emojis corrompus connus par leurs versions correctes.

        Args:
            text: Texte avec emojis corrompus

        Returns:
            Texte avec emojis corrigés
        """
        for corrupted, correct in EncodingFixer.EMOJI_FIXES.items():
            text = text.replace(corrupted, correct)
        return text

    @staticmethod
    def normalize_content(text: str, aggressive: bool = False) -> str:
        """
        Normalise le contenu en corrigeant les problèmes d'encodage.

        Args:
            text: Texte à normaliser
            aggressive: Si True, applique des corrections plus agressives

        Returns:
            Texte normalisé
        """
        # 1. Essayer de corriger les mojibake
        text = EncodingFixer.fix_mojibake(text)

        # 2. Remplacer les emojis corrompus connus
        text = EncodingFixer.replace_corrupted_emojis(text)

        if aggressive:
            # 3. Supprimer les caractères de contrôle (sauf \n, \r, \t)
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

            # 4. Normaliser les ?? orphelins (plus de 2 consécutifs)
            text = re.sub(r'\?{3,}', '???', text)

        return text

    @staticmethod
    def convert_file(
        input_path: str,
        output_path: str,
        target_encoding: str = 'utf-8',
        fix_emojis: bool = True,
        verbose: bool = False
    ) -> bool:
        """
        Convertit un fichier d'un encodage à un autre en corrigeant les emojis.

        Args:
            input_path: Fichier source
            output_path: Fichier destination
            target_encoding: Encodage cible (défaut: utf-8)
            fix_emojis: Corriger les emojis corrompus
            verbose: Mode verbeux

        Returns:
            True si succès
        """
        try:
            # Lire avec détection automatique
            content, source_encoding = EncodingFixer.read_with_fallback(
                input_path, verbose=verbose
            )

            if verbose:
                print(f"[INFO] Lu depuis {source_encoding}")

            # Corriger les emojis si demandé
            if fix_emojis:
                original_len = len(content)
                content = EncodingFixer.normalize_content(content, aggressive=False)
                if verbose and len(content) != original_len:
                    print(f"[FIX] Contenu normalisé ({original_len} → {len(content)} chars)")

            # Écrire dans l'encodage cible
            Path(output_path).write_text(content, encoding=target_encoding)

            if verbose:
                print(f"[SUCCESS] Converti vers {target_encoding}: {output_path}")

            return True

        except Exception as e:
            if verbose:
                print(f"[ERROR] Échec conversion: {e}")
            return False


def detect_file_encoding(file_path: str) -> dict:
    """
    Fonction helper pour détecter l'encodage d'un fichier.

    Returns:
        Dict avec encoding, confidence, et BOM info
    """
    fixer = EncodingFixer()
    encoding, confidence = fixer.detect_encoding(file_path)

    # Vérifier BOM
    with open(file_path, 'rb') as f:
        start = f.read(4)
        bom = None
        if start.startswith(b'\xef\xbb\xbf'):
            bom = 'UTF-8'
        elif start.startswith(b'\xff\xfe') or start.startswith(b'\xfe\xff'):
            bom = 'UTF-16'

    return {
        'encoding': encoding,
        'confidence': confidence,
        'bom': bom
    }
