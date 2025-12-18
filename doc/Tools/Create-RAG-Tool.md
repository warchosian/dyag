Voici les arguments du module create_rag :

  📋 Arguments de create_rag

  Utilisation en ligne de commande

  python -m dyag.commands.create_rag <input_file> <output_file> [format] [max_chunk_size]

  Arguments détaillés

  | Position | Argument       | Type   | Requis | Défaut  | Description                                       |
  |----------|----------------|--------|--------|---------|---------------------------------------------------|
  | 1        | input_file     | string | ✅ Oui  | -       | Chemin du fichier source (JSON ou Markdown)       |
  | 2        | output_file    | string | ✅ Oui  | -       | Chemin du fichier de sortie                       |
  | 3        | format         | string | ❌ Non  | 'jsonl' | Format de sortie : 'jsonl', 'json', ou 'markdown' |
  | 4        | max_chunk_size | int    | ❌ Non  | 1000    | Taille maximale d'un chunk en caractères          |

  ---
  🔍 Détail des arguments

  1. input_file (obligatoire)

  Type : Chaîne de caractères (chemin de fichier)

  Description : Chemin vers le fichier source à traiter

  Formats acceptés :
  - .json - Fichier JSON structuré
  - .md ou .markdown - Fichier Markdown

  Exemples :
  # JSON
  examples/test-mygusi/applicationsIA_mini_normalized.json

  # Markdown
  examples/test-mygusi/applicationsIA_mini_opt.md

  Validation :
  - Le fichier doit exister
  - L'extension doit être .json, .md ou .markdown
  - Sinon : FileNotFoundError ou ValueError

  ---
  2. output_file (obligatoire)

  Type : Chaîne de caractères (chemin de fichier)

  Description : Chemin où sera créé le fichier RAG généré

  Exemples :
  # JSONL
  output/applications_rag.jsonl

  # JSON
  output/applications_rag.json

  # Markdown
  output/applications_rag.md

  Notes :
  - Le fichier sera écrasé s'il existe déjà
  - Le répertoire parent doit exister
  - L'extension n'a pas besoin de correspondre au format (défini par l'argument 3)

  ---
  3. format (optionnel)

  Type : Chaîne de caractères

  Valeur par défaut : 'jsonl'

  Description : Format du fichier de sortie

  Valeurs possibles :

  | Format   | Description                   | Usage recommandé                               | Structure          |
  |----------|-------------------------------|------------------------------------------------|--------------------|
  | jsonl    | JSON-Lines1 chunk par ligne   | Bases vectoriellesChromaDB, Pinecone, Weaviate | Compact, streaming |
  | json     | JSON formatéTableau de chunks | Analyse, manipulationLangChain, LlamaIndex     | Lisible, indenté   |
  | markdown | Markdown avec frontmatter     | DocumentationLecture humaine                   | YAML + Markdown    |

  Exemples :

  # Format JSONL (défaut)
  python -m dyag.commands.create_rag input.json output.jsonl

  # Format JSON
  python -m dyag.commands.create_rag input.json output.json json

  # Format Markdown
  python -m dyag.commands.create_rag input.md output.md markdown

  Validation :
  - Si la valeur n'est pas 'jsonl', 'json' ou 'markdown' : ValueError

  ---
  4. max_chunk_size (optionnel)

  Type : Entier

  Valeur par défaut : 1000

  Description : Taille maximale suggérée d'un chunk en caractères

  ⚠️ Important : Ce n'est PAS une taille fixe !
  - C'est un guide pour l'algorithme de chunking sémantique
  - Les chunks peuvent être plus petits (si le contenu est court)
  - Les chunks peuvent être plus grands (pour préserver la cohérence sémantique)

  Recommandations selon l'usage :

  | Taille    | Usage                    | Avantages                         | Inconvénients            |
  |-----------|--------------------------|-----------------------------------|--------------------------|
  | 500-800   | Recherche très précise   | Précision maximaleMicro-concepts  | Moins de contexte        |
  | 1000-1500 | ✅ Équilibré (recommandé) | Bon compromisContexte + précision | -                        |
  | 1500-2000 | Recherche contextuelle   | Plus de contexteMacro-concepts    | Moins de précision       |
  | >2000     | Documentation            | Contexte maximal                  | Peut réduire qualité RAG |

  Exemples :

  # Taille par défaut (1000)
  python -m dyag.commands.create_rag input.json output.jsonl

  # Chunks plus petits (précision)
  python -m dyag.commands.create_rag input.json output.jsonl jsonl 800

  # Chunks plus grands (contexte)
  python -m dyag.commands.create_rag input.json output.jsonl jsonl 1500

  Impact réel :

  max_chunk_size = 1000
  → Taille moyenne observée : 1075 caractères
  → Min : 8 caractères
  → Max : 6606 caractères
  → Écart-type : 650 caractères

  Preuve du chunking adaptatif, pas fixe !

  ---
  📝 Exemples complets

  Exemple 1 : Utilisation minimale

  python -m dyag.commands.create_rag \
    examples/test-mygusi/applicationsIA_mini_normalized.json \
    output/my_rag.jsonl

  Résultat :
  - Format : JSONL (défaut)
  - Taille chunks : ~1000 caractères (défaut)

  ---
  Exemple 2 : Personnalisation complète

  python -m dyag.commands.create_rag \
    examples/test-mygusi/applicationsIA_mini_opt.md \
    output/my_rag.json \
    json \
    1500

  Résultat :
  - Source : Markdown
  - Format : JSON
  - Taille chunks : ~1500 caractères

  ---
  Exemple 3 : Documentation lisible

  python -m dyag.commands.create_rag \
    examples/test-mygusi/applicationsIA_mini_normalized.json \
    doc/applications_rag.md \
    markdown \
    2000

  Résultat :
  - Format : Markdown avec frontmatter YAML
  - Chunks plus grands pour plus de contexte

  ---
  🐍 Utilisation en Python

  from dyag.commands.create_rag import create_rag_from_file

  # Utilisation simple
  create_rag_from_file(
      input_file='data/applications.json',
      output_file='output/rag.jsonl'
  )

  # Avec tous les paramètres
  create_rag_from_file(
      input_file='data/applications.md',
      output_file='output/rag.json',
      output_format='json',
      max_chunk_size=1500
  )

  ---
  ✅ Validation et erreurs

  | Erreur                          | Cause                   | Solution                               |
  |---------------------------------|-------------------------|----------------------------------------|
  | FileNotFoundError               | input_file n'existe pas | Vérifier le chemin                     |
  | ValueError: Format non supporté | Extension incorrecte    | Utiliser .json, .md ou .markdown       |
  | ValueError: Format non supporté | output_format invalide  | Utiliser 'jsonl', 'json' ou 'markdown' |
  | JSONDecodeError                 | JSON source mal formé   | Corriger le JSON source                |

  ---
  📊 Sortie du programme

  $ python -m dyag.commands.create_rag input.json output.jsonl

  OK - 1628 chunks crees avec succes
  OK - Fichier RAG genere: output.jsonl

  Code de sortie :
  - 0 : Succès
  - 1 : Erreur

  Voilà tous les arguments disponibles pour create_rag ! 🎯ask A 