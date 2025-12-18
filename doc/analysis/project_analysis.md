# Analyse du projet Dyag

## Informations générales
- **Nom du projet** : dyag
- **Version** : 0.1.0
- **Description** : Dyag application package
- **Auteurs** : Your Name <your.email@example.com>
- **Python requis** : >=3.9

## Dépendances principales
- Pillow >= 10.0.0
- PyMuPDF >= 1.23.0

## Dépendances de développement
- pytest
- black
- flake8
- commitizen

## Structure du projet
- `src/dyag/` : Code source principal
  - `main.py` : Point d'entrée CLI, gestion des sous-commandes
  - `mcp_server.py` : Serveur MCP (détail non analysé ici)
  - `commands/` : Commandes CLI
    - `img2pdf.py` : Conversion d'images en PDF
    - `compresspdf.py` : Compression de PDF
    - `md2html.py` : Conversion Markdown+diagrammes en HTML+SVG
- `tests/` : (non trouvé ou vide)
- `README.md` : Documentation d'utilisation et d'installation
- `pyproject.toml` : Configuration du projet (Poetry)

## Commandes CLI disponibles
- `dyag img2pdf` : Convertir des images en PDF
- `dyag compresspdf` : Compresser un PDF
- `dyag md2html` : Convertir Markdown avec diagrammes en HTML

## Installation
- Utiliser Poetry : `poetry install`

## Utilisation
- Lancer une commande : `dyag <commande> -h`

## Remarques
- Le projet est structuré pour être utilisé en ligne de commande.
- Les dépendances sont gérées par Poetry.
- Les commandes principales sont bien séparées dans des modules dédiés.
- Les tests ne sont pas présents ou non détectés dans le dossier `tests/`.

*Analyse générée automatiquement le 30/11/2025.*
