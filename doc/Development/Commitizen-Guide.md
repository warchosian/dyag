Parfait ! Commitizen fonctionne parfaitement. Voici ce qui s'est passé :

  Résultat du cz bump

  1. Version mise à jour : 0.1.2 → 0.2.0
    - pyproject.toml:3 maintenant à 0.2.0
    - __init__.py:3 mis à jour à 0.2.0
  2. CHANGELOG généré automatiquement (CHANGELOG.md:21)
    - Nouvelle section ## v0.2.0 (2025-11-28)
    - Liste les features du commit
  3. Commit créé automatiquement : bump: version 0.1.2 → 0.2.0
  4. Tag Git créé : v0.2.0

  Prochaines utilisations

  Pour les prochaines versions :
  # 1. Faire des commits avec cz
  poetry run cz commit

  # 2. Quand prêt pour une release, bumper la version
  poetry run cz bump --yes

  # Ou pour un type spécifique
  poetry run cz bump --increment MAJOR  # 0.2.0 → 1.0.0
  poetry run cz bump --increment MINOR  # 0.2.0 → 0.3.0
  poetry run cz bump --increment PATCH  # 0.2.0 → 0.2.1

  L'historique des versions est maintenant géré automatiquement !

> comment fait il pour les prerelease alpha et beta et rc 

● Les pre-releases avec commitizen utilisent des arguments spécifiques :

  Pre-releases avec commitizen

  # Alpha
  poetry run cz bump --prerelease alpha --yes
  # 0.2.0 → 0.2.1a0

  # Beta
  poetry run cz bump --prerelease beta --yes
  # 0.2.1a0 → 0.2.1b0

  # Release Candidate
  poetry run cz bump --prerelease rc --yes
  # 0.2.1b0 → 0.2.1rc0

  # Incrémenter une pre-release existante
  poetry run cz bump --prerelease alpha --increment PRERELEASE --yes
  # 0.2.1a0 → 0.2.1a1

  # Sortir de la pre-release vers stable
  poetry run cz bump --yes
  # 0.2.1rc0 → 0.2.1

  Workflow typique

  # 1. Commencer une nouvelle feature avec alpha
  poetry run cz bump --prerelease alpha --yes
  # Version: 0.2.1a0

  # 2. Passer en beta quand stabilisé
  poetry run cz bump --prerelease beta --yes
  # Version: 0.2.1b0

  # 3. Release candidate pour tests finaux
  poetry run cz bump --prerelease rc --yes
  # Version: 0.2.1rc0

  # 4. Release finale
  poetry run cz bump --yes
  # Version: 0.2.1

  Format des versions

  Commitizen suit PEP 440 :
  - 0.2.1a0, 0.2.1a1 - Alpha
  - 0.2.1b0, 0.2.1b1 - Beta
  - 0.2.1rc0, 0.2.1rc1 - Release Candidate
  - 0.2.1 - Stable

  Voulez-vous tester une pre-release ?

> oui 

● Bash(export PATH="$HOME/.local/bin:$PATH" && poetry run cz bump --prerelease alpha --yes)
  ⎿  Running…

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Bash command

   export PATH="$HOME/.local/bin:$PATH" && poetry run cz bump --prerelease alpha --yes
   Create alpha pre-release