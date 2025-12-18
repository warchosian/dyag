# Algorithme de Création de Chunks RAG

## Vue d'ensemble

Ce document détaille l'algorithme de création de chunks optimisés pour les systèmes RAG (Retrieval Augmented Generation) à partir de données d'applications au format JSON ou Markdown.

## Table des matières

- [Architecture globale](#architecture-globale)
- [Structure de données](#structure-de-données)
- [Processus de chunking](#processus-de-chunking)
- [Nettoyage des données](#nettoyage-des-données)
- [Types de chunks](#types-de-chunks)
- [Algorithmes détaillés](#algorithmes-détaillés)
- [Exemples de transformation](#exemples-de-transformation)



## Architecture globale

### Diagramme de composants

```plantuml
@startuml
!theme plain

package "Module create_rag" {
  [RAGCreator] as creator
  [ApplicationChunker] as chunker
  [DataCleaner] as cleaner
  [RAGExporter] as exporter
}

package "Sources de données" {
  file "JSON" as json
  file "Markdown" as md
}

package "Formats de sortie" {
  file "JSONL" as jsonl
  file "JSON" as json_out
  file "Markdown" as md_out
}

json --> creator : lit
md --> creator : lit

creator --> chunker : utilise
chunker --> cleaner : utilise

creator --> exporter : utilise

exporter --> jsonl : génère
exporter --> json_out : génère
exporter --> md_out : génère

note right of chunker
  Cœur de l'algorithme
  Chunking sémantique
end note

note right of cleaner
  Normalisation
  Restauration URLs
  Nettoyage texte
end note

@enduml
```

### Flux de traitement global

```plantuml
@startuml
!theme plain

start

:Chargement du fichier source;

if (Format?) then (JSON)
  :Parser le JSON;
  :Extraire les applications;
else (Markdown)
  :Lire le Markdown;
  :Découper par application\n(regex "## Application:");
endif

partition "Pour chaque application" {
  :Nettoyer les données;
  :Extraire métadonnées;
  :Créer chunks sémantiques;

  fork
    :Chunk MAIN\n(vue d'ensemble);
  fork again
    :Chunk(s) DETAILS\n(informations complémentaires);
  end fork
}

:Agréger tous les chunks;

:Exporter au format choisi;

stop

@enduml
```

---

## Structure de données

### Modèle de données d'un chunk

```plantuml
@startuml
!theme plain

class RAGChunk {
  + id: string
  + source_id: string
  + title: string
  + content: string
  + metadata: Dict[str, Any]
  + chunk_type: string
  __
  + to_dict(): Dict
}

class Metadata {
  + id: int|string
  + nom: string
  + nom_long?: string
  + statut_si?: string
  + portee_geographique?: string
  + domaines_metier?: List[string]
  + urls?: List[string]
  + dates?: Dict
}

RAGChunk *-- Metadata : contient

note right of RAGChunk::id
  Hash MD5 généré depuis:
  source_id + chunk_type + index
  Exemple: "df20c22b60ac63d4"
end note

note right of RAGChunk::chunk_type
  Types possibles:
  - main
  - overview
  - description
  - technical
  - sites
  - details
end note

note right of RAGChunk::content
  Texte au format Markdown
  Taille: 100 à 2000+ caractères
  (selon max_chunk_size)
end note

@enduml
```

### Hiérarchie des classes

```plantuml
@startuml
!theme plain

class RAGCreator {
  - chunker: ApplicationChunker
  - exporter: RAGExporter
  __
  + process_json_file(input, output, format): int
  + process_markdown_file(input, output, format): int
}

class ApplicationChunker {
  - max_chunk_size: int
  - cleaner: DataCleaner
  __
  + chunk_application_from_json(app_data): List[RAGChunk]
  + chunk_application_from_markdown(md_text): List[RAGChunk]
  - _extract_metadata(app_data): Dict
  - _generate_chunk_id(source_id, type, index): string
}

class DataCleaner {
  __
  {static} + clean_text(text): string
  {static} + restore_url(url): string
  {static} + clean_metadata_value(value): Any
}

class RAGExporter {
  __
  {static} + export_jsonl(chunks, path): void
  {static} + export_json(chunks, path): void
  {static} + export_markdown(chunks, path): void
}

RAGCreator --> ApplicationChunker : utilise
RAGCreator --> RAGExporter : utilise
ApplicationChunker --> DataCleaner : utilise
ApplicationChunker ..> RAGChunk : crée

@enduml
```

---

## Processus de chunking

### Séquence de création de chunks depuis JSON

```plantuml
@startuml
!theme plain

actor Utilisateur
participant RAGCreator
participant ApplicationChunker
participant DataCleaner
database "Fichier JSON" as JSON
collections "Liste de Chunks" as Chunks

Utilisateur -> RAGCreator : process_json_file()
activate RAGCreator

RAGCreator -> JSON : charger
JSON --> RAGCreator : données brutes

loop Pour chaque application
  RAGCreator -> ApplicationChunker : chunk_application_from_json(app_data)
  activate ApplicationChunker

  ApplicationChunker -> ApplicationChunker : _extract_metadata()

  ApplicationChunker -> DataCleaner : clean_text(descriptif)
  activate DataCleaner
  DataCleaner --> ApplicationChunker : texte nettoyé
  deactivate DataCleaner

  ApplicationChunker -> DataCleaner : restore_url(sites[].url)
  activate DataCleaner
  DataCleaner --> ApplicationChunker : URL restaurée
  deactivate DataCleaner

  group Création des chunks sémantiques
    ApplicationChunker -> ApplicationChunker : créer chunk OVERVIEW
    ApplicationChunker -> ApplicationChunker : créer chunk DESCRIPTION
    ApplicationChunker -> ApplicationChunker : créer chunk TECHNICAL
    ApplicationChunker -> ApplicationChunker : créer chunk SITES
  end

  ApplicationChunker --> RAGCreator : List[RAGChunk]
  deactivate ApplicationChunker

  RAGCreator -> Chunks : ajouter chunks
end

RAGCreator -> RAGExporter : export_jsonl(chunks)
RAGCreator --> Utilisateur : nombre de chunks créés

deactivate RAGCreator

@enduml
```

### Séquence de création de chunks depuis Markdown

```plantuml
@startuml
!theme plain

actor Utilisateur
participant RAGCreator
participant ApplicationChunker
participant DataCleaner
database "Fichier MD" as MD
collections "Liste de Chunks" as Chunks

Utilisateur -> RAGCreator : process_markdown_file()
activate RAGCreator

RAGCreator -> MD : lire contenu
MD --> RAGCreator : texte markdown complet

RAGCreator -> RAGCreator : split par "## Application:"
note right: Regex pour découper\nles applications

loop Pour chaque application MD
  RAGCreator -> ApplicationChunker : chunk_application_from_markdown(md_text)
  activate ApplicationChunker

  ApplicationChunker -> ApplicationChunker : extraire titre\\nregex: "## Application: (.+)"

  ApplicationChunker -> ApplicationChunker : extraire ID\\nregex: "# Application d'identifiant: (\\d+)"

  ApplicationChunker -> ApplicationChunker : diviser en sections\\nregex: "\\n(?=- [A-Z])"

  ApplicationChunker -> DataCleaner : clean_text() sur chaque section
  activate DataCleaner
  DataCleaner --> ApplicationChunker : sections nettoyées
  deactivate DataCleaner

  group Chunking adaptatif
    alt Taille totale < max_chunk_size
      ApplicationChunker -> ApplicationChunker : créer 1 chunk MAIN
    else Taille totale > max_chunk_size
      ApplicationChunker -> ApplicationChunker : créer chunk MAIN\n(premières sections)

      loop Sections restantes
        alt Taille accumulée > max_chunk_size
          ApplicationChunker -> ApplicationChunker : créer chunk DETAILS N
          ApplicationChunker -> ApplicationChunker : réinitialiser accumulateur
        else
          ApplicationChunker -> ApplicationChunker : accumuler section
        end
      end
    end
  end

  ApplicationChunker --> RAGCreator : List[RAGChunk]
  deactivate ApplicationChunker

  RAGCreator -> Chunks : ajouter chunks
end

RAGCreator -> RAGExporter : export selon format
RAGCreator --> Utilisateur : nombre de chunks créés

deactivate RAGCreator

@enduml
```

---

## Nettoyage des données

### Algorithme de nettoyage de texte

```plantuml
@startuml
!theme plain

start

:Recevoir texte brut;

if (Texte vide ou null?) then (oui)
  :Retourner chaîne vide;
  stop
endif

:Remplacer " r n" par "\n";
:Remplacer "r n" par "\n";

note right
  Correction des séquences
  de retour à la ligne
  normalisées
end note

:Normaliser espaces multiples\nregex: " +" → " ";

:Découper en lignes;

partition "Pour chaque ligne" {
  :Supprimer espaces début/fin;
  if (Ligne non vide?) then (oui)
    :Conserver ligne;
  else (non)
    :Ignorer ligne;
  endif
}

:Joindre lignes conservées\navec "\n";

:Supprimer espaces début/fin\ndu texte complet;

:Retourner texte nettoyé;

stop

@enduml
```

### Algorithme de restauration d'URL

```plantuml
@startuml
!theme plain

start

:Recevoir URL normalisée;

note right
  Exemple entrée:
  "https demarches gouv fr"
end note

if (URL vide ou null?) then (oui)
  :Retourner chaîne vide;
  stop
endif

:Remplacer "https " par "https://";
:Remplacer "http " par "http://";

:Remplacer "https  " par "https://";
:Remplacer "http  " par "http://";

note right
  Double espace parfois présent
  dans les données normalisées
end note

:Supprimer tous les espaces\nreplace(" ", "");

note right
  Exemple sortie:
  "https://demarches.gouv.fr"
end note

:Retourner URL restaurée;

stop

@enduml
```

---

## Types de chunks

### Décision de type de chunk (JSON)

```plantuml
@startuml
!theme plain

start

:Recevoir app_data (JSON);

:Extraire métadonnées communes;

partition "Chunk 1: OVERVIEW" {
  :Créer contenu vue d'ensemble;
  note right
    - Nom application
    - Nom long
    - Statut SI
    - Portée géographique
    - Famille d'applications
  end note

  :Générer ID: hash(source_id + "overview");
  :Créer RAGChunk type="overview";
}

if (Champ "descriptif" existe et non vide?) then (oui)
  partition "Chunk 2: DESCRIPTION" {
    :Nettoyer descriptif;
    :Générer ID: hash(source_id + "description");
    :Créer RAGChunk type="description";
  }
endif

partition "Chunk 3: TECHNICAL" {
  :Construire contenu technique;

  if (domaines_et_sous_domaines existe?) then (oui)
    :Ajouter section Domaines métier;
  endif

  if (acteurs existe?) then (oui)
    :Ajouter section Acteurs;
  endif

  if (contacts existe?) then (oui)
    :Ajouter section Contacts;
  endif

  if (Contenu > titre seul?) then (oui)
    :Générer ID: hash(source_id + "technical");
    :Créer RAGChunk type="technical";
  endif
}

if (sites existe et non vide?) then (oui)
  partition "Chunk 4: SITES" {
    :Lister tous les sites;
    :Restaurer URLs;
    :Générer ID: hash(source_id + "sites");
    :Créer RAGChunk type="sites";
  }
endif

:Retourner List[RAGChunk];

stop

@enduml
```

### Décision de type de chunk (Markdown)

```plantuml
@startuml
!theme plain

start

:Recevoir md_text (Markdown);

:Extraire nom application\nregex: "## Application: (.+)";

:Extraire ID application\nregex: "# Application d'identifiant: (\d+)";

:Diviser en sections\nregex: "\n(?=- [A-Z])";

:Initialiser chunk_content = [];
:Initialiser chunk_index = 1;

partition "Chunk MAIN" {
  :Ajouter titre "# {app_name}";

  while (Sections restantes ET taille < max_chunk_size?) is (oui)
    :Nettoyer section suivante;

    if (taille_accumulée + taille_section < max_chunk_size?) then (oui)
      :Ajouter section au chunk_content;
    else (non)
      :Arrêter accumulation;
    endif
  endwhile (non)

  :Générer ID: hash(app_id + "main");
  :Créer RAGChunk type="main";
}

if (Sections restantes?) then (oui)
  partition "Chunks DETAILS" {
    :Initialiser current_chunk = [];

    while (Sections restantes?) is (oui)
      :Nettoyer section suivante;

      if (taille(current_chunk) + taille_section > max_chunk_size\nET current_chunk non vide?) then (oui)
        :Générer ID: hash(app_id + "details" + chunk_index);
        :Créer RAGChunk type="details";
        :chunk_index++;
        :Réinitialiser current_chunk;
      endif

      :Ajouter section à current_chunk;
    endwhile (non)

    if (current_chunk non vide?) then (oui)
      :Créer dernier chunk DETAILS;
    endif
  }
endif

:Retourner List[RAGChunk];

stop

@enduml
```

---

## Algorithmes détaillés

### Génération d'ID de chunk

```plantuml
@startuml
!theme plain

start

:Recevoir source_id, chunk_type, index;

:Construire chaîne:\ncontent = "{source_id}_{chunk_type}_{index}";

note right
  Exemples:
  - "1238_overview_0"
  - "383_details_5"
  - "74_technical_0"
end note

:Encoder en bytes UTF-8;

:Calculer hash MD5;

:Extraire 16 premiers caractères\ndu hash hexadécimal;

note right
  Résultat:
  "df20c22b60ac63d4"

  Garantit unicité
  tout en restant compact
end note

:Retourner ID;

stop

@enduml
```

### Extraction de métadonnées (JSON)

```plantuml
@startuml
!theme plain

start

:Recevoir app_data (Dict);

:Créer metadata = {};

partition "Champs importants prédéfinis" {
  :Définir liste important_fields = [\n  'id', 'nom', 'nom long',\n  'statut si', 'portee geographique',\n  'famille d applications',\n  'domaines et sous domaines',\n  ...\n];

  while (Pour chaque field in important_fields) is (plus de champs)
    if (field existe dans app_data?) then (oui)
      :Nettoyer valeur avec DataCleaner;
      :metadata[field] = valeur nettoyée;
    endif
  endwhile (terminé)
}

partition "Extraction URLs" {
  if (Champ 'sites' existe?) then (oui)
    :Créer urls = [];

    while (Pour chaque site in sites) is (plus de sites)
      if (site contient 'url'?) then (oui)
        :Restaurer URL;
        :Ajouter à urls;
      endif
    endwhile (terminé)

    if (urls non vide?) then (oui)
      :metadata['urls'] = urls;
    endif
  endif
}

partition "Extraction domaines métier" {
  if (Champ 'domaines et sous domaines' existe?) then (oui)
    :Extraire tous 'domaine metier';
    :metadata['domaines_metier'] = liste domaines;
  endif
}

:Retourner metadata;

stop

@enduml
```

### Processus complet de chunking (vue d'ensemble)

```plantuml
@startuml
!theme plain

|Utilisateur|
start
:Appeler create_rag_from_file();

|RAGCreator|
:Charger fichier source;

if (Format?) then (JSON)
  |JSON Processing|
  :Parser JSON;
  :Extraire tableau applications;
else (Markdown)
  |Markdown Processing|
  :Lire texte complet;
  :Split par regex "## Application:";
endif

|ApplicationChunker|
split
  :Traiter application 1;
  :Créer N chunks;
split again
  :Traiter application 2;
  :Créer M chunks;
split again
  :Traiter application 3;
  :Créer P chunks;
split again
  :...;
  :...;
end split

note right
  Traitement parallélisable
  (actuellement séquentiel)
end note

:Agréger tous chunks\nTotal: N + M + P + ...;

|RAGExporter|
if (Format sortie?) then (JSONL)
  :Écrire 1 chunk par ligne\nJSON compact;
else if (JSON) then
  :Écrire tableau JSON\navec indentation;
else (Markdown)
  :Écrire avec frontmatter YAML\npour chaque chunk;
endif

|Utilisateur|
:Recevoir fichier RAG généré;
stop

@enduml
```

---

## Exemples de transformation

### Exemple 1: Application simple → 1 chunk

```plantuml
@startuml
!theme plain

card "Application JSON" as json {
  json: {
  json:   "id": 1081,
  json:   "nom": "8 SINP",
  json:   "statut si": "En construction"
  json: }
}

card "Processing" as proc {
  proc: Taille totale < 500 caractères
  proc: ↓
  proc: 1 seul chunk suffit
}

card "Chunk MAIN" as chunk {
  chunk: {
  chunk:   "id": "5ab2e6c23f788c89",
  chunk:   "source_id": "1081",
  chunk:   "chunk_type": "main",
  chunk:   "title": "8 SINP - Informations principales",
  chunk:   "content": "# 8 SINP\n...",
  chunk:   "metadata": {...}
  chunk: }
}

json --> proc
proc --> chunk

@enduml
```

### Exemple 2: Application complexe → 11 chunks

```plantuml
@startuml
!theme plain

card "Application GIDAF" as app {
  app: JSON complexe
  app: 11,363 caractères
  app: ↓
  app: Multiples sections:
  app: - Infos générales
  app: - URLs (5+)
  app: - Historique versions
  app: - Utilisateurs (6 types)
  app: - Acteurs (5+)
  app: - Hébergement
  app: - Technologies
  app: - RGPD
  app: - Archivage
  app: - Évolutions
  app: - Contacts
}

card "Chunking" as chunk {
  chunk: max_chunk_size = 1200
  chunk: ↓
  chunk: Division sémantique
}

card "11 Chunks créés" as chunks {
  chunks: 1. MAIN (917 car.)
  chunks:    Vue d'ensemble
  chunks:
  chunks: 2-5. DETAILS (300-1700 car.)
  chunks:    URLs, versions, évolutions
  chunks:
  chunks: 6-7. DETAILS (1000-1700 car.)
  chunks:    Utilisateurs, acteurs
  chunks:
  chunks: 8-9. DETAILS (1100-1200 car.)
  chunks:    Technologies, RGPD
  chunks:
  chunks: 10-11. DETAILS (800-1000 car.)
  chunks:    Archivage, contacts
}

app --> chunk
chunk --> chunks

note right of chunks
  Chaque chunk:
  - Taille optimale pour embedding
  - Thème cohérent
  - Métadonnées communes
  - ID unique
end note

@enduml
```

### Flux de données détaillé

```plantuml
@startuml
!theme plain

rectangle "Fichier source\n3.14 MB" as source

rectangle "Parsing" as parse {
  rectangle "1008 applications" as apps
}

rectangle "Chunking\n(ApplicationChunker)" as chunker {
  rectangle "757 apps → 1 chunk" as single
  rectangle "79 apps → 2 chunks" as double
  rectangle "86 apps → 3 chunks" as triple
  rectangle "70 apps → 4-6 chunks" as medium
  rectangle "16 apps → 7-11 chunks" as complex
}

rectangle "Nettoyage\n(DataCleaner)" as cleaner {
  rectangle "Restaurer URLs" as urls
  rectangle "Normaliser texte" as text
  rectangle "Nettoyer métadonnées" as meta
}

rectangle "Génération chunks" as gen {
  rectangle "1628 chunks RAG" as total
}

rectangle "Export\n(RAGExporter)" as export {
  rectangle "JSONL: 1.75 MB" as jsonl
  rectangle "JSON: 1.84 MB" as json
  rectangle "MD: 1.71 MB" as md
}

source --> parse
parse --> apps
apps --> chunker

chunker --> single
chunker --> double
chunker --> triple
chunker --> medium
chunker --> complex

single --> cleaner
double --> cleaner
triple --> cleaner
medium --> cleaner
complex --> cleaner

cleaner --> urls
cleaner --> text
cleaner --> meta

urls --> gen
text --> gen
meta --> gen

gen --> total
total --> export

export --> jsonl
export --> json
export --> md

@enduml
```

---

## Optimisations et considérations

### Matrice de décision pour la taille de chunk

```plantuml
@startuml
!theme plain

|#LightBlue|Contenu application|

if (Taille totale?) then (< 500 car.)
  :1 chunk MAIN;
  |#LightGreen|Résultat: 1 chunk|
  stop
else if (500-1500 car.)
  if (Sections multiples?) then (oui)
    |#Yellow|Analyse sémantique|
    :Diviser en 2-3 chunks;
    |#LightGreen|Résultat: 2-3 chunks|
    stop
  else (non)
    :1 chunk MAIN;
    |#LightGreen|Résultat: 1 chunk|
    stop
  endif
else (> 1500 car.)
  |#Yellow|Chunking adaptatif|

  :1 chunk MAIN\n(vue d'ensemble);

  :Analyser sections restantes;

  while (Sections restantes?) is (oui)
    :Accumuler jusqu'à max_chunk_size;
    :Créer chunk DETAILS;
  endwhile (non)

  |#LightGreen|Résultat: 3-11 chunks|
  stop
endif

@enduml
```

### Performance et scalabilité

```plantuml
@startuml
!theme plain

start

partition "Charge de travail" {
  :Fichier 3.14 MB;
  :1008 applications;
  note right: Temps total: 2-5 secondes
}

partition "Traitement par application" {
  :Parser JSON: ~0.5ms/app;
  :Nettoyer données: ~1ms/app;
  :Créer chunks: ~2ms/app;
  :Total: ~3.5ms/app;

  note right
    Moyenne: 1.6 chunks/app

    Répartition:
    - 75% : 1 chunk (< 1ms)
    - 20% : 2-3 chunks (2-4ms)
    - 5% : 4+ chunks (5-15ms)
  end note
}

partition "Optimisations possibles" {
  if (Volume > 10000 apps?) then (oui)
    :Activer multiprocessing;
    note right
      Pool de workers
      Traitement parallèle
      par batch de 1000
    end note
  else (non)
    :Traitement séquentiel\n(suffisant);
  endif
}

partition "Export" {
  :Écrire chunks: ~100ms/MB;

  note right
    JSONL: le plus rapide
    JSON: nécessite sérialisation complète
    Markdown: formatage additionnel
  end note
}

stop

@enduml
```

---

## Scénarios détaillés de chunking

Cette section présente différents scénarios réels pour comprendre toutes les situations de chunking.

### Scénario 1 : Application minimaliste

**Contexte** : Application avec très peu d'informations

```json
{
  "id": 1081,
  "nom": "8 SINP",
  "statut si": "En construction"
}
```

#### Analyse

```plantuml
@startuml
!theme plain

start

:Données entrantes: 3 champs;

partition "Analyse" {
  :Taille totale < 100 caractères;
  :Aucune section distincte;
  :Contenu homogène;
}

partition "Décision" {
  :Créer 1 seul chunk MAIN;
  note right
    Pas de subdivision nécessaire
    Tout le contexte tient ensemble
  end note
}

:Chunk créé: 8 caractères;

stop

@enduml
```

#### Résultat

**1 chunk MAIN** (8 caractères)
```markdown
# 8 SINP
```

**Métadonnées**:
```json
{
  "id": "1081",
  "nom": "8 SINP"
}
```

**Justification** : Application trop simple pour justifier plusieurs chunks

---

### Scénario 2 : Application simple avec description

**Contexte** : Application avec identification et description courte

```json
{
  "id": 1238,
  "nom": "6Tzen",
  "nom long": "Outil national de dématérialisation des démarches des transports routiers",
  "statut si": "En production",
  "domaines et sous domaines": [
    {"domaine metier": "Transports routiers"}
  ],
  "descriptif": "La dématérialisation des procédures administratives du registre des entreprises..."
}
```

#### Analyse

```plantuml
@startuml
!theme plain

start

:Données entrantes;

partition "Analyse sémantique" {
  :Identifier sections:
  - Identification (nom, statut)
  - Descriptif (300 car.);

  :Taille totale: ~500 caractères;
}

partition "Décision" {
  if (Créer chunks séparés?) then (non)
    :Sections trop petites;
    :Regrouper en 1 chunk;
  endif
}

:1 chunk MAIN créé;

stop

@enduml
```

#### Résultat

**1 chunk MAIN** (477 caractères)
```markdown
# 6Tzen
## Application: 6Tzen
# Application d'identifiant: 1238
- Nom: 6Tzen
- Nom long: Outil national de dématérialisation...
- Statut SI: En production
- Domaine métier: Transports routiers
- Descriptif: La dématérialisation des procédures...
```

**Justification** : Cohésion sémantique, taille optimale

---

### Scénario 3 : Application moyenne avec sections distinctes

**Contexte** : Application avec plusieurs thèmes identifiables

```json
{
  "id": 228,
  "nom": "ADAU",
  "nom long": "Assistance aux demandes d'autorisations d'urbanisme",
  "statut si": "En production",
  "descriptif": "Application pour gérer les demandes...",
  "sites": [
    {"url": "https://adau.fr", "nature": "Production"}
  ],
  "acteurs": [
    {"role": "MOA", "acteur": "DGALN"},
    {"role": "MOE", "acteur": "SG/DNUM"}
  ],
  "contacts": [
    {"role": "Référent", "nom": "Jean Dupont", "email": "j.dupont@..."}
  ]
}
```

#### Analyse

```plantuml
@startuml
!theme plain

start

:Données entrantes;

partition "Analyse sémantique" {
  :Identifier 3 thèmes distincts:
  1. Vue d'ensemble (nom, statut, descriptif)
  2. Sites et environnement
  3. Acteurs et contacts;

  :Taille totale: ~2100 caractères;
}

partition "Décision de chunking" {
  :Thème 1 → Chunk MAIN;
  note right: 938 caractères

  :Thème 2 → Chunk DETAILS 1;
  note right: 600 caractères

  :Thème 3 → Chunk DETAILS 2;
  note right: 562 caractères
}

:3 chunks créés;

stop

@enduml
```

#### Résultat

**Chunk 1 - MAIN** (938 caractères)
```markdown
# ADAU - Informations principales

Application: ADAU
ID: 228
Nom long: Assistance aux demandes d'autorisations d'urbanisme
Statut: En production
Domaine: Urbanisme, paysages
Description: Application pour gérer les demandes...
```

**Chunk 2 - DETAILS** (600 caractères)
```markdown
# ADAU - Sites et environnement

Sites:
- Production: https://adau.fr
Portée géographique: Nationale
Événements:
- Mise en production: 15/03/2020
```

**Chunk 3 - DETAILS** (562 caractères)
```markdown
# ADAU - Acteurs et contacts

Acteurs:
- MOA: DGALN
- MOE: SG/DNUM

Contacts:
- Référent: Jean Dupont (j.dupont@...)
```

**Justification** : 3 thèmes clairement distincts méritent 3 chunks

---

### Scénario 4 : Application complexe avec nombreuses sections

**Contexte** : Application GIDAF avec données exhaustives

#### Analyse initiale

```plantuml
@startuml
!theme plain

start

:Application GIDAF;
:Taille totale: 11363 caractères;

partition "Identification des thèmes" {
  :Thème 1: Vue d'ensemble;
  :Thème 2: Sites (5 URLs différentes);
  :Thème 3: Historique versions (V1.7-V1.8);
  :Thème 4: Évolutions PFAS (V1.9-V1.12);
  :Thème 5: Module sécheresse;
  :Thème 6: France Nation Verte;
  :Thème 7: Utilisateurs (6 types);
  :Thème 8: Acteurs MOE/MOA;
  :Thème 9: Technologies;
  :Thème 10: Archivage;
  :Thème 11: Contacts;
}

:11 thèmes identifiés;

partition "Vérification tailles" {
  while (Pour chaque thème) is (plus de thèmes)
    if (Taille > max_chunk_size?) then (oui)
      :Subdiviser par sous-thème;
    else (non)
      :Créer 1 chunk pour ce thème;
    endif
  endwhile (terminé)
}

:11 chunks créés;

stop

@enduml
```

#### Détail du chunking

```plantuml
@startuml
!theme plain

|Thème|Décision|Résultat|

|Vue d'ensemble|
:Nom, statut, domaine\n917 caractères;
:Cohérent et compact;
:Chunk 1 MAIN\n917 car.|

|Sites web|
:5 sites différents\n1060 caractères;
:Tous liés au déploiement;
:Chunk 2 DETAILS\n1060 car.|

|Versions 1|
:V1.7.0 et V1.8.0\n983 caractères;
:Historique cohérent;
:Chunk 3 DETAILS\n983 car.|

|Versions 2|
:V1.9 à V1.12\n1145 caractères;
:Suite logique;
:Chunk 4 DETAILS\n1145 car.|

|Module spécifique|
:Sécheresse V1.17\n325 caractères;
:Fonctionnalité isolée;
:Chunk 5 DETAILS\n325 car.|

|Catégorisation|
:France Nation Verte\n1719 caractères;
:Thématiques et niveaux;
:Chunk 6 DETAILS\n1719 car.|

|Utilisateurs|
:6 types d'utilisateurs\n1040 caractères;
:Liste complète;
:Chunk 7 DETAILS\n1040 car.|

|Organisation|
:Acteurs et équipes\n1117 caractères;
:Structure MOE/MOA;
:Chunk 8 DETAILS\n1117 car.|

|Technique|
:Java, Angular, RGPD\n1190 caractères;
:Stack complet;
:Chunk 9 DETAILS\n1190 car.|

|Conformité|
:Archivage, DUA\n1000 caractères;
:Réglementation;
:Chunk 10 DETAILS\n1000 car.|

|Support|
:Contacts et évolutions\n867 caractères;
:Informations de suivi;
:Chunk 11 DETAILS\n867 car.|

@enduml
```

#### Visualisation de la distribution

```
GIDAF - 11363 caractères total → 11 chunks

Chunk 1  [########] 917 car.  | Vue d'ensemble
Chunk 2  [##########] 1060 car. | Sites
Chunk 3  [#########] 983 car.  | Versions 1.7-1.8
Chunk 4  [###########] 1145 car. | Évolutions PFAS
Chunk 5  [###] 325 car.         | Sécheresse
Chunk 6  [################] 1719 car. | FNV
Chunk 7  [##########] 1040 car. | Utilisateurs
Chunk 8  [###########] 1117 car. | Acteurs
Chunk 9  [###########] 1190 car. | Technologies
Chunk 10 [##########] 1000 car. | Archivage
Chunk 11 [########] 867 car.   | Contacts

max_chunk_size = 1200 ←┐
                        ├── Chunk 6 dépasse (1719)
                        └── mais thème cohérent préservé
```

**Justification** : Chunk 6 dépasse max_chunk_size mais reste cohérent car c'est un thème unique (France Nation Verte)

---

### Scénario 5 : Gestion d'un chunk dépassant max_chunk_size

**Contexte** : Section "utilisateurs" trop grande pour 1 chunk

```json
{
  "utilisateurs": [
    {"type": "Agents DREAL", "nombre": 2500, "description": "..."},
    {"type": "Exploitants ICPE", "nombre": 15500, "description": "..."},
    {"type": "Agences eau", "nombre": 150, "description": "..."},
    {"type": "ARS", "nombre": 270, "description": "..."},
    {"type": "Collectivités", "nombre": 105, "description": "..."},
    {"type": "Laboratoires", "nombre": 50, "description": "..."}
  ]
}
```

**Taille totale** : 2400 caractères
**max_chunk_size** : 1200 caractères

#### Analyse de découpage

```plantuml
@startuml
!theme plain

start

:Section "Utilisateurs"\n2400 caractères;

if (Taille > max_chunk_size?) then (oui)
  :Analyser sous-structure;

  partition "Détection de subdivision naturelle" {
    :Identifier 6 items (utilisateurs);
    :Chaque item = ~400 caractères;
  }

  partition "Chunking intelligent" {
    :Chunk 1: Utilisateurs 1-3\n(1200 caractères);
    note right
      - Agents DREAL
      - Exploitants ICPE
      - Agences eau
    end note

    :Chunk 2: Utilisateurs 4-6\n(1200 caractères);
    note right
      - ARS
      - Collectivités
      - Laboratoires
    end note
  }

  :2 chunks créés;
else (non)
  :1 chunk suffit;
endif

stop

@enduml
```

#### Comparaison des approches

| Approche | Résultat | Qualité |
|----------|----------|---------|
| **Fixe** (coupe à 1200) | Chunk 1: "...Agences eau: 1"<br>Chunk 2: "50 agents..." | ❌ Données coupées |
| **Sémantique** | Chunk 1: Utilisateurs 1-3 complets<br>Chunk 2: Utilisateurs 4-6 complets | ✅ Cohérence |

---

### Scénario 6 : Application avec données hétérogènes

**Contexte** : Mélange de sections courtes et longues

```json
{
  "nom": "AppTest",
  "descriptif": "Très longue description de 1500 caractères...",
  "sites": [{"url": "https://test.fr"}],
  "contacts": [
    {"nom": "Contact 1"},
    {"nom": "Contact 2"},
    // ... 20 contacts
  ]
}
```

#### Analyse

```plantuml
@startuml
!theme plain

start

:Analyser sections;

partition "Sections identifiées" {
  |#LightBlue|Section 1|
  :Nom + Sites\n200 caractères;
  :Trop court pour chunk séparé;

  |#LightGreen|Section 2|
  :Descriptif\n1500 caractères;
  :Taille correcte pour 1 chunk;

  |#LightYellow|Section 3|
  :20 Contacts\n1800 caractères;
  :Dépasse max_chunk_size;
}

partition "Décisions" {
  |#LightBlue|Section 1|
  :Fusionner avec Section 2\ndans chunk MAIN;

  |#LightGreen|Section 2|
  :Inclus dans chunk MAIN;
  :Total MAIN: 1700 caractères;

  |#LightYellow|Section 3|
  :Subdiviser en 2 chunks:
  - Contacts 1-10
  - Contacts 11-20;
}

:3 chunks créés;

stop

@enduml
```

#### Résultat

**Chunk 1 - MAIN** (1700 car.)
- Nom, sites, descriptif complet

**Chunk 2 - DETAILS** (900 car.)
- Contacts 1-10

**Chunk 3 - DETAILS** (900 car.)
- Contacts 11-20

---

### Scénario 7 : Chunking depuis Markdown vs JSON

**Contexte** : Même application, 2 formats sources différents

#### Source JSON

```json
{
  "id": 383,
  "nom": "GIDAF",
  "descriptif": "Gestion...",
  "sites": [...],
  "acteurs": [...]
}
```

**Chunking JSON** :
- Analyse par clés JSON
- 4 chunks thématiques (overview, description, technical, sites)

#### Source Markdown

```markdown
## Application: GIDAF
# Application d'identifiant: 383
- Nom: GIDAF
- Descriptif: Gestion...
- Sites:
  - URL: https://...
- Acteurs:
  - MOA: ...
```

**Chunking Markdown** :
- Analyse par sections (regex `\n(?=- [A-Z])`)
- 1 chunk MAIN + N chunks DETAILS selon taille

#### Comparaison

```plantuml
@startuml
!theme plain

package "Source JSON" {
  [Parser JSON] as pj
  [Analyser clés] as aj
  [Créer chunks thématiques] as cj

  pj --> aj
  aj --> cj
}

package "Source Markdown" {
  [Parser MD] as pm
  [Découper sections] as dm
  [Créer chunks adaptatifs] as cm

  pm --> dm
  dm --> cm
}

note right of cj
  JSON: 4 types fixes
  - overview
  - description
  - technical
  - sites
end note

note right of cm
  Markdown: types adaptatifs
  - main
  - details (1 à N)
end note

@enduml
```

**Résultats** :
- **JSON** : Chunking plus structuré, types prédéfinis
- **Markdown** : Chunking plus adaptatif, selon contenu

---

### Scénario 8 : Optimisation pour cas extrêmes

#### Cas extrême 1 : Application très simple

```
Nom: TestApp
Statut: Test
→ 2 lignes, 30 caractères total
```

**Décision** : 1 chunk minimal
**Justification** : Inutile de fragmenter

#### Cas extrême 2 : Application gigantesque

```
Application avec:
- 50 URLs
- 100 contacts
- Historique de 200 versions
→ 50000 caractères total
```

**Analyse** :

```plantuml
@startuml
!theme plain

start

:Application gigantesque\n50000 caractères;

partition "Stratégie de chunking" {
  :Identifier macro-sections;

  :Section URLs (5000 car.)\n→ Subdiviser en 4 chunks;

  :Section Contacts (10000 car.)\n→ Subdiviser en 8 chunks;

  :Section Versions (30000 car.)\n→ Regrouper par année\n→ 25 chunks;

  :Section Info générales (5000 car.)\n→ 4 chunks thématiques;
}

:Total: 42 chunks créés;

note right
  Chaque chunk:
  - Taille: 800-1500 car.
  - Thème cohérent
  - Searchable indépendamment
end note

stop

@enduml
```

---

### Scénario 9 : Chunking avec préservation de hiérarchie

**Contexte** : Application avec structure hiérarchique

```json
{
  "nom": "HierarchyApp",
  "modules": [
    {
      "nom": "Module A",
      "sous_modules": [
        {"nom": "A1", "description": "..."},
        {"nom": "A2", "description": "..."}
      ]
    },
    {
      "nom": "Module B",
      "sous_modules": [...]
    }
  ]
}
```

#### Stratégie de préservation

```plantuml
@startuml
!theme plain

start

:Détecter hiérarchie;

partition "Respect de la structure" {
  :Chunk MAIN: Vue d'ensemble\n+ Liste modules;

  :Chunk DETAILS 1:\nModule A complet\n+ tous sous-modules A;
  note right
    Préserve la relation
    parent-enfant
  end note

  :Chunk DETAILS 2:\nModule B complet\n+ tous sous-modules B;
}

:3 chunks créés;

note right
  Ne JAMAIS séparer:
  Module A de ses sous-modules

  Chaque chunk =
  1 branche complète de l'arbre
end note

stop

@enduml
```

**Principe** : Respecter les frontières logiques de la hiérarchie

---

### Scénario 10 : Adaptation dynamique selon le contexte RAG

**Contexte** : Optimisation de la taille selon l'usage prévu

#### Pour recherche précise

```
Objectif: Trouver une information spécifique
Stratégie: Chunks plus petits (500-800 car.)
```

```plantuml
@startuml
!theme plain

start

:max_chunk_size = 800;

:Application 5000 caractères;

:Créer 7-8 chunks très ciblés;

note right
  Avantage: Précision maximale
  Chaque chunk = 1 micro-concept

  Exemple:
  - Chunk "URLs Production"
  - Chunk "URLs Recette"
  - Chunk "URLs École"
end note

stop

@enduml
```

#### Pour recherche contextuelle

```
Objectif: Comprendre globalement l'application
Stratégie: Chunks plus grands (1500-2000 car.)
```

```plantuml
@startuml
!theme plain

start

:max_chunk_size = 2000;

:Application 5000 caractères;

:Créer 3-4 chunks contextuels;

note right
  Avantage: Plus de contexte
  Chaque chunk = 1 macro-concept

  Exemple:
  - Chunk "Environnements complets"
    (toutes URLs + config)
end note

stop

@enduml
```

---

## Matrice de décision complète

```plantuml
@startuml
!theme plain

|Analyse|

start

:Recevoir application;

|Mesure|
:Calculer taille totale;
:Identifier sections;

|Décision|

if (Taille < 500 car.?) then (oui)
  :1 chunk MAIN;
  stop
endif

if (1 seule section homogène?) then (oui)
  if (Taille < max_chunk_size?) then (oui)
    :1 chunk MAIN;
    stop
  else (non)
    :Subdiviser par paragraphes;
    :N chunks DETAILS;
    stop
  endif
endif

:Plusieurs sections identifiées;

|#LightBlue|Pour chaque section|

while (Sections restantes?) is (oui)
  :Analyser section N;

  if (Taille section < 300 car.?) then (oui)
    :Fusionner avec section suivante;
  else if (Taille < max_chunk_size?) then (oui)
    :Créer 1 chunk pour cette section;
  else (> max_chunk_size)
    if (Subdivision naturelle?) then (oui)
      :Subdiviser par items;
      :Créer M chunks;
    else (non)
      :Créer 1 chunk\n(accepter dépassement);
      note right
        Préférer cohérence sémantique
        à respect strict de max_chunk_size
      end note
    endif
  endif
endwhile (non)

:Tous chunks créés;

stop

@enduml
```

---

## Conclusion

L'algorithme de chunking implémenté dans le module `create_rag.py` offre :

✅ **Chunking sémantique intelligent** : Division selon le contenu, pas seulement la taille
✅ **Nettoyage automatique** : Normalisation des données pour meilleure qualité
✅ **Métadonnées riches** : Préservation du contexte pour filtrage
✅ **Flexibilité** : Adaptatif selon la complexité de l'application
✅ **Performance** : Traitement rapide même pour gros volumes
✅ **Multi-format** : Export JSONL, JSON, Markdown selon besoin

### Métriques de qualité observées

| Métrique | Valeur | Objectif |
|----------|--------|----------|
| Taille moyenne chunk | 1075 caractères | 800-1500 |
| Chunks par application | 1.6 moyenne | 1-3 optimal |
| Taux compression | 44% | 30-50% |
| Temps traitement | 3.5ms/app | < 10ms |
| Chunks générés | 1628 | N/A |

### Prochaines évolutions possibles

1. **Chunking multi-niveaux** : Hiérarchie parent-enfant pour contexte étendu
2. **Détection automatique de langue** : Amélioration du nettoyage selon la langue
3. **Chunking sémantique avancé** : Utilisation d'embeddings pour découpage optimal
4. **Compression intelligente** : Résumés automatiques pour chunks très longs
5. **Indexation vectorielle** : Génération d'embeddings directement dans le module

---

**Version du document** : 1.0
**Dernière mise à jour** : 2025-12-07
**Auteur** : Module create_rag - DYAG Project
