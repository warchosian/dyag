# Dyag

Dyag - Outil de manipulation de fichiers et conversion

## Commandes disponibles

- `dyag img2pdf` - Convertir des images en PDF
- `dyag compresspdf` - Compresser un fichier PDF
- `dyag md2html` - Convertir Markdown avec diagrammes vers HTML avec SVG

## Installation

```bash
poetry install
```

### Installation des dépendances RAG (optionnel)

Si vous souhaitez utiliser les fonctionnalités RAG (Retrieval-Augmented Generation) pour l'indexation et la recherche de documents, vous avez deux options :

#### Option 1 : Via Poetry (recommandé)

```bash
poetry install -E rag
```

Cette commande installe dyag avec toutes les dépendances RAG définies dans `pyproject.toml`.

#### Option 2 : Via pip (alternative)

```bash
pip install -r requirements-rag.txt
```

Cette méthode est utile si :
- Vous utilisez conda ou un autre gestionnaire d'environnement
- Vous rencontrez des conflits de dépendances avec Poetry
- Vous préférez une installation directe sans Poetry

**Note**: En raison d'incompatibilités temporaires entre Poetry 2.2+ et certaines dépendances RAG (notamment `packaging`), l'option 2 peut être plus fiable dans certains environnements.

## Utilisation

```bash
dyag <commande> -h
```
