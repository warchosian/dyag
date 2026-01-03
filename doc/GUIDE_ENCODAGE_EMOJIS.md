# Guide : Gérer les emojis créés en latin-1 et convertis en UTF-8

## Le problème

Quand un fichier UTF-8 contenant des emojis (📄, 📁, etc.) est ouvert/sauvegardé avec le mauvais encodage, les emojis sont corrompus.

### Exemple concret

```
Fichier original (UTF-8) :  ### 📄 `fichier.py`
Lu en latin-1 :             ### ðŸ"„ `fichier.py`
Sauvegardé en UTF-8 :       ### ðŸ"„ `fichier.py` (corrompu définitivement)
```

## Solutions disponibles

### 1. Commandes DYAG existantes

#### a) Détecter l'encodage

```bash
# Vérifier l'encodage d'un fichier
dyag chk-utf8 --path-pattern "mon_fichier.md"

# Vérifier plusieurs fichiers
dyag chk-utf8 --path-pattern "docs/**/*.md"
```

#### b) Corriger automatiquement

```bash
# Corriger l'encodage en UTF-8
dyag fix-utf8 --path-pattern "mon_fichier.md"

# Avec backup avant modification
dyag fix-utf8 --path-pattern "mon_fichier.md" --backup

# Mode dry-run (simulation)
dyag fix-utf8 --path-pattern "mon_fichier.md" --dry-run
```

### 2. Module Python `encoding_fixer` (nouveau)

Pour des cas plus complexes (mojibake, emojis multiples corrompus).

#### a) Détecter l'encodage avec chardet

```python
from dyag.analysis.core.encoding_fixer import EncodingFixer, detect_file_encoding

# Détection automatique
info = detect_file_encoding("fichier.md")
print(f"Encodage: {info['encoding']}")
print(f"Confiance: {info['confidence']:.2%}")
print(f"BOM: {info['bom']}")
```

#### b) Lire avec fallback automatique

```python
from dyag.analysis.core.encoding_fixer import EncodingFixer

fixer = EncodingFixer()

# Lecture avec détection automatique d'encodage
content, encoding = fixer.read_with_fallback("fichier.md", verbose=True)
print(f"Lu avec {encoding}")
```

#### c) Corriger les mojibake (emojis UTF-8 mal décodés)

```python
from dyag.analysis.core.encoding_fixer import EncodingFixer

# Texte corrompu : "ðŸ"„" au lieu de "📄"
corrupted_text = "### ðŸ"„ `fichier.py`"

# Méthode 1 : Correction automatique des mojibake
fixed = EncodingFixer.fix_mojibake(corrupted_text)
print(fixed)  # "### 📄 `fichier.py`"

# Méthode 2 : Remplacement par mapping connu
fixed = EncodingFixer.replace_corrupted_emojis(corrupted_text)
print(fixed)

# Méthode 3 : Normalisation complète
fixed = EncodingFixer.normalize_content(corrupted_text, aggressive=False)
print(fixed)
```

#### d) Convertir un fichier complet

```python
from dyag.analysis.core.encoding_fixer import EncodingFixer

# Conversion avec correction d'emojis
success = EncodingFixer.convert_file(
    input_path="fichier_corrompu.md",
    output_path="fichier_fixe.md",
    target_encoding="utf-8",
    fix_emojis=True,
    verbose=True
)
```

### 3. Script batch pour corriger plusieurs fichiers

```python
#!/usr/bin/env python3
"""Correctif batch pour emojis corrompus"""

from pathlib import Path
from dyag.analysis.core.encoding_fixer import EncodingFixer

def fix_directory(directory: str, pattern: str = "*.md"):
    """Corrige tous les fichiers MD d'un répertoire"""

    fixer = EncodingFixer()
    directory_path = Path(directory)

    for md_file in directory_path.rglob(pattern):
        print(f"\n[PROCESS] {md_file}")

        try:
            # Détecter l'encodage
            content, encoding = fixer.read_with_fallback(str(md_file))
            print(f"  Encodage: {encoding}")

            # Vérifier si emojis corrompus
            corrupted = any(
                emoji in content
                for emoji in fixer.EMOJI_FIXES.keys()
            )

            if corrupted:
                # Corriger et sauvegarder
                fixed = fixer.normalize_content(content)
                md_file.write_text(fixed, encoding='utf-8')
                print(f"  ✓ Emojis corrigés")
            else:
                print(f"  ✓ Pas de corruption détectée")

        except Exception as e:
            print(f"  ✗ Erreur: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fix_emojis.py <directory>")
        sys.exit(1)

    fix_directory(sys.argv[1])
```

## Cas d'usage courants

### Cas 1 : Fichier project2md avec emojis corrompus

```bash
# Le fichier formation-ecologie.md a des "??" au lieu de 📄

# Solution 1 : Utiliser dyag fix-utf8
dyag fix-utf8 --path-pattern "formation-ecologie.md" --backup

# Solution 2 : Utiliser encoding_fixer en Python
python -c "
from dyag.analysis.core.encoding_fixer import EncodingFixer
EncodingFixer.convert_file(
    'formation-ecologie.md',
    'formation-ecologie-fixed.md',
    fix_emojis=True,
    verbose=True
)
"
```

### Cas 2 : Détecter le vrai encodage d'un fichier suspect

```python
from dyag.analysis.core.encoding_fixer import detect_file_encoding

info = detect_file_encoding("fichier_suspect.md")

if info['confidence'] < 0.7:
    print("⚠ Confiance faible, vérification manuelle recommandée")
else:
    print(f"✓ {info['encoding']} (confiance: {info['confidence']:.0%})")
```

### Cas 3 : md2project ignore les emojis corrompus

Le parser `md2project` est déjà configuré pour tolérer les emojis corrompus :

```bash
# Ces patterns sont automatiquement gérés :
# - ### 📄 `fichier.py`   (UTF-8 correct)
# - ### ?? `fichier.py`   (Emojis corrompus)
# - ## Fichier 1: `fichier.py`  (Format manuel)

dyag md2project fichier.md -o output_dir
```

## Emojis supportés (mapping de corruption)

Le module `encoding_fixer` reconnaît ces corruptions courantes :

| Emoji | UTF-8 bytes | Corrompu latin-1 | Corrompu "??" |
|-------|-------------|------------------|---------------|
| 📄    | `\xf0\x9f\x93\x84` | `ðŸ"„` | `??` |
| 📁    | `\xf0\x9f\x93\x81` | `ðŸ"` | `??` |
| 🔍    | `\xf0\x9f\x94\x8d` | `ðŸ"` | `??` |

## Prévenir les problèmes

### 1. Toujours utiliser UTF-8

Dans votre éditeur (VS Code, Notepad++, etc.) :
- Définir UTF-8 comme encodage par défaut
- Sauvegarder avec BOM si nécessaire (`UTF-8-BOM`)

### 2. Vérifier avant commit

```bash
# Hook pre-commit
#!/bin/bash
dyag chk-utf8 --path-pattern "**/*.md" || exit 1
```

### 3. Utiliser project2md avec --encoding

```bash
# Forcer UTF-8 en sortie
dyag project2md mon_projet -o projet.md --encoding utf-8
```

## Outils externes complémentaires

### iconv (Linux/Mac)

```bash
# Convertir latin-1 vers UTF-8
iconv -f latin1 -t utf-8 fichier.md > fichier_utf8.md
```

### recode (Linux)

```bash
# Détection et conversion automatique
recode ..UTF-8 fichier.md
```

### chardet (Python)

```bash
# Détecter l'encodage
chardetect fichier.md
```

## Dépannage

### Problème : "UnicodeDecodeError" malgré fix-utf8

**Cause** : Le fichier contient des séquences de bytes invalides

**Solution** :
```python
# Lecture forcée avec remplacement
with open('fichier.md', 'rb') as f:
    raw = f.read()
    text = raw.decode('utf-8', errors='replace')  # Remplace les invalides par �

# Ou ignorance
text = raw.decode('utf-8', errors='ignore')  # Ignore les invalides
```

### Problème : Les emojis restent "??" après correction

**Cause** : L'emoji original est perdu définitivement (remplacé par '?' dans l'encoding)

**Solution** : Remplacement manuel ou regex
```python
import re
text = re.sub(r'##\s*\?\?\s*`', r'## 📄 `', text)
```

### Problème : chardet détecte le mauvais encodage

**Cause** : Confiance trop faible ou fichier trop court

**Solution** : Spécifier manuellement
```python
from pathlib import Path

# Forcer latin-1
content = Path('fichier.md').read_text(encoding='latin-1')

# Ou essayer plusieurs encodages
for enc in ['utf-8', 'latin-1', 'cp1252']:
    try:
        content = Path('fichier.md').read_text(encoding=enc)
        break
    except UnicodeDecodeError:
        continue
```

## Ressources

- [Documentation Unicode Python](https://docs.python.org/3/howto/unicode.html)
- [chardet sur PyPI](https://pypi.org/project/chardet/)
- [UTF-8 Everywhere](http://utf8everywhere.org/)
- [Mojibake expliqué](https://fr.wikipedia.org/wiki/Mojibake)
