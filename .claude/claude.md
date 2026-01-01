# Règles Claude pour ce projet

## Git et GitHub

### Commits
- Ne créer des commits que lorsque explicitement demandé
- Messages de commit clairs et concis (en français de préférence)
- Format: `type: description courte`
  - Types: feat, fix, docs, refactor, test, chore
- Toujours ajouter la signature Claude en fin de message:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

### Sécurité Git
- JAMAIS de `git push --force` sur main/master sans confirmation explicite
- JAMAIS de modification de config git
- Ne JAMAIS commit de fichiers secrets (.env, credentials, etc.)
- Vérifier `git status` et `git diff` avant chaque commit

### Pull Requests
- Utiliser `gh pr create` avec résumé clair
- Format du PR:
  ```
  ## Résumé
  - Point 1
  - Point 2

  ## Plan de test
  - [ ] Test 1
  - [ ] Test 2

  🤖 Generated with [Claude Code](https://claude.com/claude-code)
  ```

### Branches
- Toujours vérifier la branche actuelle avant de travailler
- Utiliser des noms de branches descriptifs

## Général
- Toujours lire les fichiers avant de les modifier
- Préférer éditer les fichiers existants plutôt que d'en créer de nouveaux
- Utiliser TodoWrite pour planifier les tâches complexes
- Pas d'emojis sauf demande explicite
