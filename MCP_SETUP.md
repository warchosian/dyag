# Configuration du serveur MCP pour dyag

Ce document explique comment configurer le serveur MCP (Model Context Protocol) pour que les assistants IA puissent utiliser dyag directement.

## Qu'est-ce que MCP ?

MCP (Model Context Protocol) permet aux assistants IA d'accéder à des outils externes pendant leurs conversations. Avec le serveur MCP de dyag, un assistant peut :

- Convertir des images en PDF
- Compresser des PDFs existants
- Tout cela directement depuis la conversation, sans que l'utilisateur doive taper des commandes

## Installation

### 1. Installer dyag avec Poetry

```bash
cd /home/firmin/codespace/dyag
poetry install
```

### 2. Configuration pour Claude Desktop

Ajoutez cette configuration à votre fichier de configuration Claude Desktop :

**Sur Linux/Mac :** `~/.config/Claude/claude_desktop_config.json`
**Sur Windows :** `%APPDATA%\Claude\claude_desktop_config.json`

```json
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
```

### 3. Configuration pour Claude Code CLI

Si vous utilisez Claude Code, ajoutez à votre configuration MCP :

```bash
# Fichier : ~/.config/claude-code/mcp_config.json
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
```

## Outils disponibles via MCP

### 1. `dyag_img2pdf`

Convertit des images d'un répertoire en PDF.

**Paramètres :**
- `directory` (requis) : Chemin vers le répertoire contenant les images
- `output` (optionnel) : Chemin du PDF de sortie
- `compress` (optionnel) : Active la compression (défaut: false)
- `quality` (optionnel) : Qualité JPEG 1-100 (défaut: 85)
- `verbose` (optionnel) : Afficher les détails (défaut: false)

**Exemple d'utilisation par l'assistant :**
```
Assistant : Je vais convertir vos images en PDF.
[Appelle dyag_img2pdf avec directory="/chemin/vers/images", compress=true, quality=70]
Assistant : PDF créé avec succès : /chemin/vers/images/images.pdf
```

### 2. `dyag_compresspdf`

Compresse un PDF existant.

**Paramètres :**
- `input` (requis) : Chemin du PDF à compresser
- `output` (optionnel) : Chemin du PDF compressé de sortie
- `quality` (optionnel) : Qualité JPEG 1-100 (défaut: 85)
- `verbose` (optionnel) : Afficher les détails (défaut: false)

**Exemple d'utilisation par l'assistant :**
```
Assistant : Je vais compresser votre PDF.
[Appelle dyag_compresspdf avec input="/chemin/vers/document.pdf", quality=60]
Assistant : PDF compressé avec succès : /chemin/vers/document_compressed.pdf
Taille originale : 24 MB
Taille compressée : 9.5 MB
Réduction : 60%
```

## Test du serveur MCP

Pour tester manuellement le serveur :

```bash
# Lancer le serveur
PYTHONPATH=/home/firmin/codespace/dyag/src python3 -m dyag.mcp_server

# Dans un autre terminal, envoyer une requête JSON :
echo '{"method": "tools/list", "params": {}}' | PYTHONPATH=/home/firmin/codespace/dyag/src python3 -m dyag.mcp_server
```

## Utilisation avec l'assistant

Une fois configuré, l'assistant peut automatiquement utiliser dyag quand vous demandez :

- "Convertis les images de ce dossier en PDF"
- "Compresse ce PDF pour réduire sa taille"
- "Crée un PDF à partir des captures d'écran dans /chemin/vers/images"

L'assistant appellera automatiquement les outils dyag appropriés sans que vous ayez à taper de commandes.

## Dépannage

### Le serveur ne démarre pas

Vérifiez que :
- Python 3.8+ est installé
- Les dépendances sont installées : `poetry install`
- Le PYTHONPATH pointe vers le bon répertoire

### Les outils ne sont pas disponibles

1. Redémarrez Claude Desktop/Code
2. Vérifiez les logs MCP
3. Testez le serveur manuellement avec la commande ci-dessus

### Permissions

Assurez-vous que le serveur a accès aux fichiers/répertoires que vous voulez traiter.

## Avantages

- **Automatique** : L'assistant sait quand utiliser dyag
- **Conversationnel** : Pas besoin de commandes, juste demander naturellement
- **Efficace** : Traitement direct sans copier-coller de commandes
- **Intégré** : Fonctionne dans le flux de conversation normal
