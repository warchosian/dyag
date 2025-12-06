# Analyse détaillée de l'application dyag

## ?? Vue d'ensemble

`dyag` est une application CLI (Command Line Interface) Python conçue pour la manipulation de fichiers et la conversion entre différents formats. Le nom semble être un acronyme ou un jeu de mots basé sur les fonctionnalités principales de l'application.

**Version courante** : v0.2.0-rc.1 (Release Candidate 1)  
**Compatibilité** : Python 3.8+  
**Type** : Application de bureau avec intégration MCP (Model Context Protocol) pour assistants IA

Voici un diagramme donnant un aperçu global de l'architecture de l'application :

```plantuml
@startuml
!theme plain
skinparam componentStyle rectangle

title Architecture globale de dyag

package "dyag" {
  [CLI Interface] as cli
  [MCP Server] as mcp
  [Command Handler] as handler
  
  package "Commands" {
    [img2pdf] as cmd1
    [compresspdf] as cmd2
    [md2html] as cmd3
    [add_toc] as cmd4
    [html2pdf] as cmd5
    [project2md] as cmd6
  }
  
  package "Libraries" {
    [Pillow] as lib1
    [PyMuPDF] as lib2
    [Playwright] as lib3
    [Graphviz] as lib4
    [Kroki API] as lib5
  }
}

cli --> handler : "Appelle"
mcp --> handler : "Appelle via MCP"
handler --> cmd1
handler --> cmd2
handler --> cmd3
handler --> cmd4
handler --> cmd5
handler --> cmd6

cmd1 --> lib1 : "Utilise pour\nconversion images"
cmd2 --> lib2 : "Utilise pour\ncompression"
cmd3 --> lib4 : "Conversion\ndiagrammes locaux"
cmd3 --> lib5 : "Conversion\nPlantUML/Mermaid"
cmd5 --> lib3 : "Conversion\nHTML->PDF"
@enduml
```

## ??? Structure technique du projet

### Organisation des fichiers

Le projet est organisé selon une structure standard pour une application Python :

```
?? dyag03/
+-- ?? doc/                       # Documentation technique
+-- ?? src/dyag/                  # Code source principal
¦   +-- ?? commands/              # Commandes CLI
¦   ¦   +-- add_toc.py            # Ajout de table des matières
¦   ¦   +-- compresspdf.py        # Compression de PDF
¦   ¦   +-- html2pdf.py           # Conversion HTML en PDF
¦   ¦   +-- img2pdf.py            # Conversion d'images en PDF
¦   ¦   +-- md2html.py            # Conversion Markdown en HTML
¦   ¦   +-- project2md.py         # Conversion projet en Markdown
¦   +-- __init__.py               # Version du package
¦   +-- __main__.py               # Entrée principale
¦   +-- main.py                   # Logique CLI principale
¦   +-- mcp_server.py             # Serveur MCP pour assistants IA
+-- ?? pyproject.toml             # Configuration du projet (Poetry)
+-- ?? poetry.lock                # Dépendances verrouillées
+-- ?? README.md                  # Documentation utilisateur
+-- ?? ...                        # Scripts de build et tests
```

### Diagramme des dépendances

```plantuml
@startuml
!theme plain
skinparam classStyle rectangle

title Dépendances principales de dyag

class "dyag.main" {
  +main()
  +create_parser()
}

class "dyag.mcp_server" {
  +run()
  +handle_request()
  +list_tools()
  +call_tool()
}

class "dyag.commands.md2html" {
  +process_markdown_to_html()
  +convert_graphviz_to_svg()
  +convert_plantuml_to_svg()
  +convert_mermaid_to_svg()
  +clean_svg_content()
}

class "dyag.commands.add_toc" {
  +add_toc_to_html()
  +generate_toc_html()
}

class "dyag.commands.html2pdf" {
  +convert_html_to_pdf()
}

class "dyag.commands.img2pdf" {
  +images_to_pdf()
}

class "dyag.commands.compresspdf" {
  +compress_pdf()
}

class "dyag.commands.project2md" {
  +project_to_markdown()
  +generate_file_tree()
}

"dyag.main" --> "dyag.commands.*" : Utilise
"dyag.main" --> "dyag.mcp_server" : Délègue
"dyag.mcp_server" --> "dyag.commands.*" : Appelle directement
"dyag.commands.md2html" --> "dyag.commands.add_toc" : Peut utiliser
"dyag.commands.html2pdf" --> "dyag.commands.add_toc" : Peut utiliser

note right of "dyag.commands.md2html"
  Le module md2html dépend de commandes externes
  (dot, plantuml) ou d'API en ligne (Kroki)
end note

note right of "dyag.commands.html2pdf"
  Dépend de Playwright qui nécessite
  l'installation de Chromium
end note
@enduml
```

## ?? Fonctionnalités principales

### 1. Conversion d'images en PDF (`img2pdf`)

Cette fonctionnalité permet de convertir toutes les images d'un répertoire en un fichier PDF unique, avec l'option de compression pour réduire la taille du fichier final.

```plantuml
@startuml
!theme plain
start
:Utilisateur exécute "dyag img2pdf";
:Spécification du répertoire;
:Optionnels: sortie personnalisée,\ncompression, qualité;
:Scan des fichiers images\n(JPG, PNG, GIF, etc.);
if (Fichiers trouvés?) then (oui)
  :Tri alphabétique;
  :Conversion en mode RGB;
  if (Compression activée?) then (oui)
    :Application compression JPEG\n(qualité spécifiée);
  endif
  :Création du fichier PDF\n(réglage résolution=100 DPI);
  :Sauvegarde;
  :Affichage résultats\n(nom fichier, nombre de pages);
else (non)
  :Erreur: Aucun fichier image trouvé;
  stop
endif
stop
@enduml
```

### 2. Compression de PDF (`compresspdf`)

Cette commande retraite les images d'un PDF existant pour réduire sa taille avec une qualité configurable.

```plantuml
@startuml
!theme plain
title Processus de compression PDF

participant Utilisateur
participant CLI
participant "Module compresspdf"
participant PyMuPDF
participant Pillow

Utilisateur -> CLI: dyag compresspdf input.pdf -q 70
CLI -> "Module compresspdf": Appel fonction compress_pdf()
"Module compresspdf" -> PyMuPDF: Ouverture PDF (fitz.open)
loop Pour chaque page
  PyMuPDF --> "Module compresspdf": get_pixmap()
  "Module compresspdf" -> Pillow: Conversion en image
  if Qualité spécifiée? then (oui)
    Pillow --> "Module compresspdf": Sauvegarde avec qualité=70
  else (non)
    Pillow --> "Module compresspdf": Sauvegarde avec qualité=85
  endif
  "Module compresspdf" -> PyMuPDF: Insertion image compressée
end
"Module compresspdf" -> PyMuPDF: Sauvegarde PDF compressé
PyMuPDF --> "Module compresspdf": Fichier sauvegardé
"Module compresspdf" --> CLI: Statistiques (taille avant/après)
CLI --> Utilisateur: Affichage résultats
@enduml
```

### 3. Conversion Markdown en HTML avec diagrammes (`md2html`)

Cette fonctionnalité centrale permet de convertir des fichiers Markdown contenant des diagrammes en HTML avec des SVG intégrés. Voici le flux détaillé :

```plantuml
@startuml
!theme plain
title Processus de conversion Markdown vers HTML

start
:Chargement fichier Markdown;
:Détection des blocs de code;
note right
  Recherche de:
  ```dot / ```graphviz
  ```plantuml
  ```mermaid
end note

repeat
  switch (Type de diagramme?)
  case (dot/graphviz)
    :Appel commande "dot -Tsvg";
    if (Succès?) then (oui)
      :Nettoyage SVG\n(retirer XML declaration,\nDOCTYPE, commentaires);
    else (non)
      :Garder bloc de code original;
    endif
  case (plantuml)
    :Essayer conversion locale "plantuml -tsvg";
    if (Échec) then (oui)
      :Utiliser service Kroki online\n(https://kroki.io/plantuml/svg/...);
    endif
    :Nettoyage SVG;
  case (mermaid)
    :Utiliser service Kroki online\n(https://kroki.io/mermaid/svg/...);
    :Nettoyage SVG;
  case (autre)
    :Garder comme bloc de code;
  endswitch
repeat while (Plus de blocs?) is (oui)
->non;

:Conversion Markdown basique en HTML;
note right
  - Titres H1-H6
  - Listes
  - Tableaux
  - Mise en forme (bold/italic)
end note

if (Mode standalone?) then (oui)
  :Ajout structure HTML complète\n(en-tête, CSS, etc.);
endif

:Sauvegarde fichier HTML;
:Affichage statistiques\n(conversion réussie/échouée);
stop
@enduml
```

### 4. Intégration MCP (Model Context Protocol)

L'application dispose d'un serveur MCP pour permettre aux assistants IA (comme Claude) d'utiliser les fonctionnalités de `dyag` directement depuis leurs conversations.

```plantuml
@startuml
!theme plain
title Intégration MCP

actor Utilisateur
actor "Assistant IA" as AI
component "dyag-mcp" as MCP
database "Fichiers" as Files

Utilisateur -> AI: "Convertir mes images en PDF"
AI -> MCP: Appel tool "dyag_img2pdf"
note right of AI
  L'assistant détermine automatiquement
  le bon outil et les paramètres
  basés sur la demande de l'utilisateur
end note

MCP -> Files: Traitement des fichiers
MCP <-- Files: Résultats
MCP -> AI: Résultat de la conversion
AI -> Utilisateur: "PDF créé avec succès:\n/images/images.pdf\nTaille: 12 MB, 102 pages"

Utilisateur -> AI: "Compresser ce PDF"
AI -> MCP: Appel tool "dyag_compresspdf"
MCP -> Files: Compression
MCP <-- Files: PDF compressé
MCP -> AI: Statistiques de compression
AI -> Utilisateur: "PDF compressé avec succès:\nTaille originale: 24 MB\nTaille compressée: 9.5 MB\nRéduction: 60%"
@enduml
```

### Diagramme des outils MCP disponibles

```plantuml
@startuml
!theme plain
skinparam componentStyle rectangle

title Outils MCP disponibles

component "MCP Server" as server

component "dyag_img2pdf" as tool1
component "dyag_compresspdf" as tool2
component "dyag_md2html" as tool3

server --> tool1 : "Convertit images\nen PDF"
server --> tool2 : "Compresse PDF\nexistants"
server --> tool3 : "Convertit Markdown\navec diagrammes en HTML"
@enduml
```

## ?? Workflow de Build et Distribution

```plantuml
@startuml
!theme plain
title Processus de build et distribution

start
:Préparation release;
:1. Update version via commitizen\n(poetry run cz bump --yes);
note right
  Met à jour:
  - pyproject.toml
  - src/dyag/__init__.py
  - CHANGELOG.md
end note

:2. Build du package\n(poetry build);
note right
  Génère:
  - dyag-0.2.0rc1-py3-none-any.whl (15 KB)
  - dyag-0.2.0rc1.tar.gz (24 KB)
end note

:3. Tests de conversion;
note right
  Vérification:
  - Conversion images -> PDF
  - Compression PDF
  - Conversion Markdown -> HTML
  - Génération TOC
end note

if (Tests réussis?) then (oui)
  :Création documentation\n(RELEASE_NOTES, BUILD_SUMMARY);
  :Package prêt à la distribution;
  note right
    Distribution via:
    - Fichier .whl (recommandé)
    - Source tar.gz
    - Serveur local
    - Git
  end note
else (non)
  :Correction des bugs;
  :Retour aux tests;
endif

stop
@enduml
```

## ?? Statistiques et performances

### Couverture des fonctionnalités

```plantuml
@startuml
pie title Couverture des fonctionnalités
"Conversion Markdown->HTML" : 35
"Manipulation PDF" : 30
"Intégration IA (MCP)" : 20
"Génération de documentation" : 15
@enduml
```

### Support des types de diagrammes

```plantuml
@startuml
!theme plain
title Support des types de diagrammes dans md2html

class Diagramme {
  +type: string
  +méthode_conversion: string
  +support: string
}

class Graphviz_DOT {
  +méthode_conversion: "Local (commande 'dot')"
  +support: "? Complet"
}

class PlantUML {
  +méthode_conversion: "Local ou Kroki API"
  +support: "? Complet"
}

class Mermaid {
  +méthode_conversion: "Kroki API"
  +support: "? Complet"
}

class Tableaux {
  +méthode_conversion: "Conversion directe"
  +support: "? Complet"
}

Diagramme <|-- Graphviz_DOT
Diagramme <|-- PlantUML
Diagramme <|-- Mermaid
Diagramme <|-- Tableaux
@enduml
```

## ?? Perspectives d'amélioration

```plantuml
@startuml
!theme plain
title Feuille de route

package "v0.2.0 (Final)" {
  [Améliorer conversion locale Mermaid]
  [Ajout configuration fichier]
  [Gestion erreurs réseau]
  [Barre de progression]
}

package "v0.3.0" {
  [Support D2 et Nomnoml]
  [Édition WYSIWYG]
  [Prévisualisation en temps réel]
  [Export vers formats multiples]
}

package "v1.0.0" {
  [Interface graphique complète]
  [Intégration cloud]
  [Collaboration en temps réel]
  [Thèmes personnalisables]
}

[md2html] --> [Améliorer conversion locale Mermaid]
[MCP] --> [Ajout configuration fichier]
[md2html] --> [Support D2 et Nomnoml]
[global] --> [Interface graphique complète]
@enduml
```

## ?? Conclusion

`dyag` est une application polyvalente pour la manipulation de documents, avec un focus particulier sur la conversion entre formats et l'enrichissement des documents avec des diagrammes. Son architecture modulaire permet une maintenance facile et une évolution progressive.

Points forts notables :
- **Architecture modulaire** avec séparation claire des responsabilités
- **Intégration IA avancée** via le protocole MCP
- **Support étendu des diagrammes** (Graphviz, PlantUML, Mermaid)
- **Workflow de release professionnel** avec Commitizen et Poetry
- **Documentation complète** pour les utilisateurs et développeurs

Points d'amélioration :
- Dépendance à des services externes (Kroki API) pour certaines fonctionnalités
- Nécessite des commandes système supplémentaires (dot, plantuml) pour un fonctionnement complet
- Pas d'interface graphique pour le moment (CLI uniquement)

Cette application représente une excellente base pour un système de génération de documentation technique moderne, avec une intégration transparente avec les assistants IA qui devient de plus en plus importante dans les workflows de développement.