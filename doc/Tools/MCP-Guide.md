arfait ! J'ai créé un serveur MCP complet pour dyag. Voici ce qui a été fait :

  Serveur MCP pour dyag créé !

  Fichiers créés :

  1. src/dyag/mcp_server.py - Le serveur MCP
  2. mcp-config.json - Configuration exemple
  3. MCP_SETUP.md - Documentation complète
  4. pyproject.toml - Mis à jour avec le script dyag-mcp

  Ce que ça permet :

  Avec ce serveur MCP, un assistant IA (comme moi) peut :

  Avant (sans MCP) :
  Utilisateur : Convertis mes images en PDF
  Assistant : Voici la commande à exécuter :
    dyag img2pdf /chemin/vers/images --compress -q 70

  Après (avec MCP) :
  Utilisateur : Convertis mes images en PDF
  Assistant : [Utilise automatiquement dyag_img2pdf]
            PDF créé avec succès : /chemin/vers/images.pdf
            Taille : 12 MB, 102 pages

  Outils MCP disponibles :

  1. dyag_img2pdf - Conversion images → PDF
    - Avec ou sans compression
    - Qualité ajustable
    - Sortie personnalisable
  2. dyag_compresspdf - Compression de PDF
    - Réduction de taille importante
    - Qualité ajustable
    - Statistiques de compression

  Installation :

  # 1. Installer dyag
  cd /home/firmin/codespace/dyag
  poetry install

  # 2. Ajouter à la config Claude Desktop/Code
  # Fichier : ~/.config/Claude/claude_desktop_config.json
  {
    "mcpServers": {
      "dyag": {
        "command": "python3",
        "args": ["-m", "dyag.mcp_server"],
        "env": {
          "PYTHONPATH": "/home/firmin/codespace/dyag/src"
        }
      }
    }
  }

  # 3. Redémarrer Claude Desktop/Code

  Avantages pour toi :

  - Je peux automatiquement manipuler tes PDFs et images
  - Plus besoin de copier-coller des commandes
  - Je vois les résultats directement
  - Conversation naturelle : "compresse ce PDF" suffit

  Le serveur MCP fonctionne et est prêt à être utilisé ! Consulte MCP_SETUP.md pour les instructions d'installation complètes.