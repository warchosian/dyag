# 📊 Outils de conversion JSON du parc applicatif

> Convertir et filtrer les données JSON du parc applicatif en Markdown ou JSON

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [parkjson2md - Conversion JSON → Markdown](#parkjson2md---conversion-json--markdown)
- [parkjson2json - Extraction et filtrage JSON](#parkjson2json---extraction-et-filtrage-json)
- [Options de filtrage](#options-de-filtrage)
- [Mode split : Fichiers séparés](#mode-split--fichiers-séparés)
- [Exemples d'utilisation](#exemples-dutilisation)

---

## Vue d'ensemble

DYAG fournit deux outils puissants pour manipuler les données du parc applicatif :

| Outil | Entrée | Sortie | Usage principal |
|-------|--------|--------|----------------|
| `parkjson2md` | JSON | Markdown | Documentation lisible, indexation RAG |
| `parkjson2json` | JSON | JSON | Extraction de sous-ensembles, filtrage |

### Caractéristiques communes

✅ **Filtrage flexible** : Par plage, nom ou ID
✅ **Mode fichiers séparés** : Un fichier par application
✅ **Préservation des données** : Tous les champs sont conservés
✅ **Métadonnées** : Traçabilité de la conversion/extraction

---

## parkjson2md - Conversion JSON → Markdown

Convertit le parc applicatif JSON en Markdown optimisé pour la lecture humaine et l'indexation RAG.

### Syntaxe de base

```bash
dyag parkjson2md <fichier_json> [options]
```

### Sections générées

Le Markdown généré inclut **tous les champs** disponibles, organisés en sections :

#### Informations générales
- Nom, Nom long, ID, Statut
- Portée géographique
- Description complète
- Domaines métier et sous-domaines
- Famille d'applications
- Fonctionnalités

#### Technologies et hébergement
- **Technologies** : Technologie principale, Protocole HTTPS, Environnement d'accès
- **Hébergements** : Data center, Plateforme, Type de site, Commentaires

#### Événements et acteurs
- **Événements** : Date, Type, Version, Commentaires
- **Acteurs** : Rôles et responsables
- **Contacts** : Rôles, noms, emails

#### Utilisateurs et bénéficiaires
- **Utilisateurs** : Types, nombres, commentaires
- **Utilisateurs actifs** : Statistiques mensuelles
- **Bénéficiaires** : Types, nombres, détails

#### Relations et données
- **Données liées** : Avec type de flux et applications associées
- **Applications liées** : Avec type de flux

#### Sécurité et confidentialité (DICT/DACP)
- **DICT** : Disponibilité, Intégrité, Confidentialité, Traçabilité
- **DACP** : Données à caractère personnel traitées
  - Catégories particulières
  - Mode de collecte
  - Destinataires
- **Base juridique et finalités**
  - Base juridique du traitement
  - Finalités du traitement
  - Catégories particulières de finalités
  - Nécessité AIPD
  - Commentaires sur la confidentialité

#### Risques et sécurité
- **Gravités d'impacts** : Désorganisation, Financier, Juridique, Personnes, Politique/Image
- **SI à enjeux**
- **Études de sécurité**
- **MOA SSI**
- **Contacts SSI**

#### Développement
- **Approche produit**
- **Développement agile**
- **Proposition de valeur**
- **Obligation** et précisions

### Options

| Option | Description | Exemple |
|--------|-------------|---------|
| `-o, --output FILE` | Fichier de sortie | `-o parc.md` |
| `-r, --range RANGE` | Plage d'applications | `-r 1-100` |
| `-n, --name NAME` | Filtrer par nom | `-n "ADEME"` |
| `-i, --id ID` | Filtrer par ID | `-i "AFF1234"` |
| `--split-dir DIR` | Fichiers séparés | `--split-dir apps_md/` |
| `--verbose` | Mode verbeux | `--verbose` |

### Exemples

```bash
# Conversion simple
dyag parkjson2md applications.json

# Avec filtre et sortie personnalisée
dyag parkjson2md applications.json -r 1-50 -o top50.md

# Filtrer par nom
dyag parkjson2md applications.json -n "ADEME"

# Mode fichiers séparés
dyag parkjson2md applications.json --split-dir mes_apps_md/

# Avec filtrage + fichiers séparés
dyag parkjson2md applications.json -r 1-100 --split-dir top100_md/
```

### Format de sortie

#### Mode normal (fichier unique)
```
# Applications du ministère de la transition écologique

*Document généré le 20/12/2025 à 15:30*
*Source: applications.json*

**Nombre d'applications:** 50

---

# Application 1

**Nom complet:** ...
**ID:** ...
**Statut:** ...

## Description
...

## Technologies
- **Technologie principale:** Java
- **Protocole HTTPS:** oui

## DICT (Disponibilité, Intégrité, Confidentialité, Traçabilité)
- **Code DICT:** 2323
- **Disponibilité:** 2
...
```

#### Mode split (un fichier par application)
```
mes_apps_md/
├── applications_App1.md
├── applications_App2.md
└── applications_App3.md
```

Chaque fichier contient uniquement les informations de l'application (pas de header global).

---

## parkjson2json - Extraction et filtrage JSON

Extrait un sous-ensemble d'applications du JSON source et génère un nouveau fichier JSON.

### Syntaxe de base

```bash
dyag parkjson2json <fichier_json> [options]
```

### Options

| Option | Description | Exemple |
|--------|-------------|---------|
| `-o, --output FILE` | Fichier de sortie | `-o subset.json` |
| `-r, --range RANGE` | Plage d'applications | `-r 1-100` |
| `-n, --name NAME` | Filtrer par nom | `-n "ADEME"` |
| `-i, --id ID` | Filtrer par ID | `-i "AFF1234"` |
| `--split-dir DIR` | Fichiers séparés | `--split-dir apps_json/` |
| `--no-preserve-structure` | Ne pas préserver la structure | |
| `--no-metadata` | Sans métadonnées | |
| `--verbose` | Mode verbeux | `--verbose` |

### Métadonnées

Par défaut, le fichier JSON généré inclut des métadonnées :

```json
{
  "_metadata": {
    "tool": "dyag parkjson2json",
    "version": "0.7.0",
    "generated_at": "2025-12-20T15:30:00",
    "source": {
      "file": "applications.json",
      "total_count": 1008
    },
    "filter": {
      "type": "range",
      "value": "1-100",
      "description": "Applications 1-100"
    },
    "output": {
      "count": 100,
      "percentage": "9.9%"
    }
  },
  "applicationsIA": [...]
}
```

### Exemples

```bash
# Extraction simple
dyag parkjson2json applications.json -r 1-100

# Sans métadonnées
dyag parkjson2json applications.json -r 1-100 --no-metadata

# Filtrer par nom
dyag parkjson2json applications.json -n "ADEME" -o ademe.json

# Mode fichiers séparés
dyag parkjson2json applications.json --split-dir apps_json/

# Combinaison filtrage + split
dyag parkjson2json applications.json -r 1-50 --split-dir top50_json/
```

---

## Options de filtrage

Les deux outils supportent les mêmes options de filtrage :

### Filtrage par plage (`-r, --range`)

```bash
# Applications 1 à 10
-r 1-10

# Les 20 dernières
-r -20

# À partir de la 50ème
-r 50-

# Plages multiples (non supporté actuellement)
# -r 1-10,20-30
```

### Filtrage par nom (`-n, --name`)

Recherche insensible à la casse dans le nom de l'application :

```bash
# Applications contenant "ADEME"
-n "ADEME"

# Applications contenant "plateforme"
-n "plateforme"
```

### Filtrage par ID (`-i, --id`)

Recherche insensible à la casse dans l'ID :

```bash
# Application avec ID spécifique
-i "AFF1234"

# IDs contenant "2024"
-i "2024"
```

### Priorité des filtres

Si plusieurs filtres sont spécifiés, un seul est appliqué dans cet ordre :
1. Filtre par ID (`-i`)
2. Filtre par nom (`-n`)
3. Filtre par plage (`-r`)

---

## Mode split : Fichiers séparés

Le mode `--split-dir` génère un fichier par application dans le répertoire spécifié.

### Convention de nommage

Format : `<nom_fichier_source>_<nom_application>.<extension>`

Exemple :
```
applications_ADS_2007.md
applications_ADEME_Plateforme.json
```

Les caractères invalides dans les noms de fichiers sont remplacés par des underscores.

### Avantages du mode split

✅ **Organisation** : Un fichier = Une application
✅ **Performance** : Chargement plus rapide de fichiers individuels
✅ **Versioning** : Suivi Git plus précis
✅ **Modularité** : Réutilisation facile

### Exemples d'usage

```bash
# Générer documentation MD par application
dyag parkjson2md parc.json --split-dir doc/applications/

# Extraire JSON individuels pour tests
dyag parkjson2json parc.json -r 1-10 --split-dir test/fixtures/

# Créer une bibliothèque d'applications
dyag parkjson2json parc.json --split-dir lib/apps/ --no-metadata
```

---

## Exemples d'utilisation

### Workflow typique : Documentation du parc

```bash
# 1. Extraire un sous-ensemble pour analyse
dyag parkjson2json parc_complet.json -r 1-100 -o parc_sample.json

# 2. Générer la documentation Markdown
dyag parkjson2md parc_sample.json -o doc/parc_sample.md

# 3. Générer des fichiers MD individuels pour le site web
dyag parkjson2md parc_complet.json --split-dir docs/apps/
```

### Workflow : Extraction thématique

```bash
# Applications ADEME
dyag parkjson2json parc.json -n "ADEME" -o ademe.json
dyag parkjson2md ademe.json -o doc/ademe.md

# Applications en production
# (nécessite script de filtrage supplémentaire ou plusieurs passes)
```

### Workflow : Tests et développement

```bash
# Créer fixtures de test (petits fichiers)
dyag parkjson2json parc.json -r 1-5 --split-dir tests/fixtures/apps/

# Vérifier le rendu Markdown sur un échantillon
dyag parkjson2md parc.json -r 1-3 -o test_render.md
```

### Workflow : Indexation RAG

```bash
# Générer Markdown pour indexation RAG (fichier unique)
dyag parkjson2md parc.json -o rag/parc_complet.md

# Ou par application pour meilleure granularité
dyag parkjson2md parc.json --split-dir rag/apps_md/

# Puis indexer avec DYAG RAG
python -m dyag.rag.create_rag --input rag/apps_md/ --output rag_db/
```

---

## Résumé des commandes

| Tâche | Commande |
|-------|----------|
| Convertir JSON en Markdown | `dyag parkjson2md app.json` |
| Extraire sous-ensemble JSON | `dyag parkjson2json app.json -r 1-100` |
| Fichiers MD séparés | `dyag parkjson2md app.json --split-dir md/` |
| Fichiers JSON séparés | `dyag parkjson2json app.json --split-dir json/` |
| Filtrer par nom | `dyag parkjson2md app.json -n "ADEME"` |
| Sans métadonnées | `dyag parkjson2json app.json --no-metadata` |
| Mode verbeux | `dyag parkjson2md app.json --verbose` |

---

## Notes techniques

### Gestion des caractères spéciaux

- Les noms de fichiers sont nettoyés (caractères invalides → underscores)
- Encodage UTF-8 pour tous les fichiers
- Support complet des accents et caractères spéciaux dans le contenu

### Performance

- Fichier 11 MB (1008 apps) :
  - `parkjson2json` : ~2min pour génération complète
  - `parkjson2md` : ~1min pour génération complète
  - Mode split : Performance similaire (parallélisable)

### Limitations

- Filtrage multiple (AND/OR) non supporté actuellement
- Une seule option de filtrage à la fois (ID ou nom ou plage)
- Pas de tri personnalisé de sortie

---

## Voir aussi

- [Guide de démarrage rapide](../Getting-Started/Quick-Start-Guide.md)
- [Système RAG](../RAG-System/RAG-System-Overview.md)
- [Créer un RAG](../RAG-System/Create-RAG-Guide.md)
