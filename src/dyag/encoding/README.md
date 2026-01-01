# Module Encoding - DYAG

Module de gestion d'encodage pour fichiers Markdown.

## Fonctionnalités

### 1. Vérification d'encodage (`chk-utf8`)

Vérifie l'encodage de fichiers Markdown et détecte les problèmes potentiels.

**Utilisation CLI** :
```bash
# Vérifier tous les fichiers .md du répertoire courant
dyag chk-utf8 -P "*.md"

# Vérifier récursivement dans un dossier
dyag chk-utf8 -P "docs/**/*.md"

# Mode silencieux (afficher seulement les problèmes)
dyag chk-utf8 -P "src/**/*.md" --quiet

# Seuil de confiance personnalisé
dyag chk-utf8 -P "*.md" --min-confidence 0.9
```

**Utilisation programmatique** :
```python
from dyag.encoding import check_markdown_files

results = check_markdown_files(["docs/**/*.md"])
for result in results:
    print(f"{result['path']}: {result['encoding']} ({result['confidence']:.0%})")
```

### 2. Correction d'encodage (`fix-utf8`)

Corrige automatiquement l'encodage et le contenu des fichiers Markdown.

**Corrections appliquées** :
- ✅ Conversion vers UTF-8
- ✅ Décodage des entités HTML (`&nbsp;` → espace, etc.)
- ✅ Encodage des espaces dans les URLs Markdown
- ✅ Nettoyage des IDs HTML
- ✅ Remplissage des fichiers vides

**Utilisation CLI** :
```bash
# Simuler les corrections (dry-run)
dyag fix-utf8 -P "*.md" --dry-run

# Corriger avec backups
dyag fix-utf8 -P "docs/**/*.md" --backup

# Corriger silencieusement
dyag fix-utf8 -P "src/**/*.md" --quiet

# Corriger plusieurs patterns
dyag fix-utf8 -P "*.md" -P "docs/**/*.md"
```

**Utilisation programmatique** :
```python
from dyag.encoding import fix_markdown_files

results = fix_markdown_files(
    patterns=["docs/**/*.md"],
    dry_run=False,
    backup=True
)

for result in results:
    if result['success']:
        print(f"✅ {result['path']}: {result['message']}")
    else:
        print(f"❌ {result['path']}: {result['message']}")
```

## Dépendances

### Modules internes
- `dyag.core.pathglob`: Résolution de motifs de chemins (globs)

### Modules externes
- `chardet`: Détection d'encodage
- `pathlib`: Manipulation de chemins
- `html`: Décodage entités HTML
- `urllib.parse`: Encodage URLs

## Architecture

```
src/dyag/encoding/
├── __init__.py              # Exports publics
├── chk_utf8.py             # Logique vérification encodage
├── fix_utf8.py             # Logique correction encodage
├── commands/               # Intégration CLI
│   ├── __init__.py         # Exports commandes
│   ├── chk_utf8_cmd.py     # Commande chk-utf8
│   └── fix_utf8_cmd.py     # Commande fix-utf8
└── README.md               # Cette documentation
```

## API Publique

### Fonctions principales

#### `check_md(file_path: Path) -> dict`
Vérifie l'encodage d'un fichier Markdown individuel.

**Retourne** :
```python
{
    "path": Path,
    "encoding": str,           # Ex: "utf-8", "iso-8859-1"
    "confidence": float,       # 0.0 à 1.0
    "raw_data": bytes,
    "error": Optional[str]
}
```

#### `check_markdown_files(patterns: List[str]) -> List[dict]`
Vérifie l'encodage de plusieurs fichiers via patterns glob.

#### `fix_file_encoding_and_content(path: Path, dry_run: bool, backup: bool) -> Tuple[bool, str]`
Corrige un fichier Markdown (encodage + contenu).

**Retourne** : `(success: bool, message: str)`

#### `fix_markdown_files(patterns: List[str], dry_run: bool, backup: bool) -> List[dict]`
Corrige plusieurs fichiers via patterns glob.

### Fonctions utilitaires

- `decode_html_entities(text: str) -> str`: Décode entités HTML
- `fix_anchor_ids(text: str) -> str`: Nettoie IDs HTML
- `encode_spaces_in_links(text: str) -> str`: Encode espaces dans URLs
- `ensure_non_empty(content: str) -> str`: Remplit fichiers vides

## Exemples d'utilisation

### Workflow typique : Vérifier puis Corriger

```bash
# 1. Vérifier les fichiers
dyag chk-utf8 -P "docs/**/*.md" --quiet

# 2. Si problèmes détectés, simuler corrections
dyag fix-utf8 -P "docs/**/*.md" --dry-run

# 3. Appliquer corrections avec backup
dyag fix-utf8 -P "docs/**/*.md" --backup
```

### Script Python

```python
from dyag.encoding import check_markdown_files, fix_markdown_files

# Vérifier
patterns = ["docs/**/*.md", "*.md"]
results = check_markdown_files(patterns)

# Filtrer fichiers problématiques
problematic = [
    r for r in results
    if r['error'] or r['encoding'] not in ('utf-8', 'UTF-8')
]

if problematic:
    print(f"{len(problematic)} fichiers à corriger")

    # Corriger avec backup
    fix_results = fix_markdown_files(patterns, backup=True)
    print(f"{len(fix_results)} fichiers traités")
```

## Intégration dans projet

Le module est automatiquement intégré dans la CLI `dyag` via :
- `src/dyag/commands/__init__.py`: Imports register functions
- `src/dyag/main.py`: Enregistrement commandes

Les commandes `chk-utf8` et `fix-utf8` sont disponibles directement :
```bash
dyag --help                    # Liste toutes les commandes
dyag chk-utf8 --help          # Aide chk-utf8
dyag fix-utf8 --help          # Aide fix-utf8
```

## Tests

Tests unitaires à créer dans `tests/unit/encoding/`:
- `test_chk_utf8.py`: Tests vérification
- `test_fix_utf8.py`: Tests correction
- `test_pathglob.py`: Tests résolution patterns

## Notes

- Le module est **safe par défaut** : `fix-utf8` supporte `--dry-run` et `--backup`
- La détection d'encodage via `chardet` peut avoir des faux positifs (~70-90% confiance)
- Le module gère gracieusement les erreurs (pas de crash, retour codes d'erreur)
- Compatible Windows (gestion chemins, BOM UTF-8)

---

**Version** : 1.0.0
**Date** : 2026-01-01
**Auteur** : Intégration DYAG par Claude Sonnet 4.5
