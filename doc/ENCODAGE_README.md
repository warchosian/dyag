# Outils de gestion d'encodage - DYAG

## Vue d'ensemble

DYAG fournit plusieurs outils pour gérer les problèmes d'encodage dans les fichiers Markdown, notamment les emojis corrompus.

## Outils disponibles

### 1. Commandes CLI

#### `chk-utf8` - Vérifier l'encodage

```bash
# Vérifier un fichier
dyag chk-utf8 --path-pattern "fichier.md"

# Vérifier un répertoire entier
dyag chk-utf8 --path-pattern "docs/**/*.md"
```

#### `fix-utf8` - Corriger l'encodage

```bash
# Corriger et convertir en UTF-8
dyag fix-utf8 --path-pattern "fichier.md"

# Avec backup
dyag fix-utf8 --path-pattern "fichier.md" --backup

# Simulation (dry-run)
dyag fix-utf8 --path-pattern "fichier.md" --dry-run
```

#### `md2project` - Parser tolérant aux emojis corrompus

```bash
# Le parser md2project tolère automatiquement :
# - Emojis UTF-8 corrects (📄)
# - Emojis corrompus (??)
# - Headers variés (##, ###, ####)

dyag md2project fichier.md -o output_dir
```

### 2. Module Python `encoding_fixer`

Pour des cas avancés (mojibake, détection fine, conversion par lot).

```python
from dyag.analysis.core.encoding_fixer import EncodingFixer

# Détecter l'encodage
fixer = EncodingFixer()
content, encoding = fixer.read_with_fallback("fichier.md")

# Corriger les emojis corrompus
fixed = fixer.normalize_content(content)

# Convertir un fichier
EncodingFixer.convert_file(
    "source.md",
    "destination.md",
    fix_emojis=True
)
```

### 3. Script exemple

```bash
# Utiliser le script de correction d'emojis
python examples/fix_emoji_corruption.py fichier.md
python examples/fix_emoji_corruption.py directory/
python examples/fix_emoji_corruption.py "*.md"
```

## Problèmes courants

### Emojis affichés comme "??"

**Cause** : Fichier UTF-8 lu en latin-1 ou inversement

**Solutions** :
1. `dyag fix-utf8 --path-pattern "fichier.md"`
2. `python examples/fix_emoji_corruption.py fichier.md`
3. Utiliser `encoding_fixer.normalize_content()` en Python

### "UnicodeDecodeError" à la lecture

**Cause** : Mauvais encodage ou bytes invalides

**Solution** :
```python
from dyag.analysis.core.encoding_fixer import EncodingFixer

# Lecture avec fallback automatique
fixer = EncodingFixer()
content, encoding = fixer.read_with_fallback("fichier.md", verbose=True)
```

### Mojibake (ðŸ"„ au lieu de 📄)

**Cause** : UTF-8 mal décodé en latin-1 puis réencodé

**Solution** :
```python
from dyag.analysis.core.encoding_fixer import EncodingFixer

text = "### ðŸ"„ `fichier.py`"
fixed = EncodingFixer.fix_mojibake(text)
# Résultat : "### 📄 `fichier.py`"
```

## Documentation

- [Guide complet : GUIDE_ENCODAGE_EMOJIS.md](./GUIDE_ENCODAGE_EMOJIS.md)
- [Script exemple : examples/fix_emoji_corruption.py](../examples/fix_emoji_corruption.py)

## Corrections appliquées par `fix-utf8`

- Décodage des entités HTML (`&nbsp;`, `&#160;`)
- Suppression espaces dans `id="..."`
- Encodage espaces dans URLs (`%20`)
- Détection BOM UTF-8
- Conversion vers UTF-8

## Corrections appliquées par `encoding_fixer`

- Correction mojibake (UTF-8 → latin-1 → UTF-8)
- Remplacement emojis corrompus connus
- Détection automatique d'encodage (chardet)
- Fallback multi-encodages
- Normalisation de contenu

## Mapping des emojis supportés

| Emoji | Corruption latin-1 | Corruption "??" |
|-------|-------------------|-----------------|
| 📄    | ðŸ"„               | ??              |
| 📁    | ðŸ"               | ??              |
| 🔍    | ðŸ"               | ??              |

*Note : `encoding_fixer` peut détecter et corriger automatiquement ces corruptions.*

## Workflow recommandé

1. **Détecter** : `dyag chk-utf8 --path-pattern "**/*.md"`
2. **Corriger** : `dyag fix-utf8 --path-pattern "**/*.md" --backup`
3. **Vérifier** : `dyag chk-utf8 --path-pattern "**/*.md"`
4. **Parser** : `dyag md2project fichier.md -o output`

## Dépendances

- `chardet` : Détection automatique d'encodage (optionnel mais recommandé)

```bash
pip install chardet
```

## Exemples d'utilisation

### Corriger un projet entier

```bash
# Backup + correction de tous les MD
dyag fix-utf8 --path-pattern "**/*.md" --backup

# Vérification
dyag chk-utf8 --path-pattern "**/*.md"
```

### Utiliser en Python

```python
from dyag.analysis.core.encoding_fixer import EncodingFixer, detect_file_encoding

# Analyse
info = detect_file_encoding("fichier.md")
print(f"Encodage: {info['encoding']} ({info['confidence']:.0%})")

# Correction
EncodingFixer.convert_file(
    "fichier.md",
    "fichier_fixed.md",
    target_encoding="utf-8",
    fix_emojis=True,
    verbose=True
)
```

### Script batch

```python
from pathlib import Path
from dyag.analysis.core.encoding_fixer import EncodingFixer

for md_file in Path("docs").rglob("*.md"):
    EncodingFixer.convert_file(
        str(md_file),
        str(md_file),  # Overwrite
        fix_emojis=True
    )
```
