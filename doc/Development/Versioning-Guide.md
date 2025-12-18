# Guide de Versioning et Distribution du Package

Ce document explique comment gérer les versions, générer les packages et les installer sur d'autres postes.

## Table des matières

1. [Gestion des versions avec Commitizen](#gestion-des-versions-avec-commitizen)
2. [Génération des packages](#génération-des-packages)
3. [Installation sur d'autres postes](#installation-sur-dautres-postes)

---

## Gestion des versions avec Commitizen

### Prérequis

Le projet utilise **Commitizen** pour automatiser le versioning et la génération du CHANGELOG.

### Créer des commits standardisés

Utilisez la commande interactive pour créer des commits suivant les conventions :

```bash
poetry run cz commit
```

Ou en version courte :

```bash
poetry run cz c
```

Cette commande vous guide pour créer des commits au format Conventional Commits :
- `feat:` - Nouvelle fonctionnalité (MINOR bump)
- `fix:` - Correction de bug (PATCH bump)
- `BREAKING CHANGE:` - Changement non rétrocompatible (MAJOR bump)
- `docs:`, `style:`, `refactor:`, `test:`, `chore:` - Pas de bump de version

### Bumper la version automatiquement

Une fois que vous avez des commits prêts, bumpez la version :

```bash
poetry run cz bump --yes
```

Cette commande va :
- Analyser les commits depuis la dernière version
- Déterminer le type de bump (MAJOR, MINOR, PATCH)
- Mettre à jour `pyproject.toml` et `src/pythonpackage/__init__.py`
- Générer/mettre à jour `CHANGELOG.md`
- Créer un commit de bump
- Créer un tag Git (ex: `v0.3.0`)

### Bumper manuellement avec un type spécifique

```bash
# Version majeure : 0.3.0 → 1.0.0
poetry run cz bump --increment MAJOR --yes

# Version mineure : 0.3.0 → 0.4.0
poetry run cz bump --increment MINOR --yes

# Version patch : 0.3.0 → 0.3.1
poetry run cz bump --increment PATCH --yes
```

### Gestion des pre-releases

#### Créer une version alpha

```bash
poetry run cz bump --prerelease alpha --yes
# 0.3.0 → 0.4.0a0
```

#### Créer une version beta

```bash
poetry run cz bump --prerelease beta --yes
# 0.4.0a0 → 0.4.0b0
```

#### Créer une release candidate

```bash
poetry run cz bump --prerelease rc --yes
# 0.4.0b0 → 0.4.0rc0
```

#### Incrémenter une pre-release

```bash
poetry run cz bump --prerelease alpha --increment PRERELEASE --yes
# 0.4.0a0 → 0.4.0a1
```

#### Sortir de pre-release vers stable

```bash
poetry run cz bump --yes
# 0.4.0rc0 → 0.4.0
```

### Workflow de versioning recommandé

```bash
# 1. Développer et faire des commits avec cz
poetry run cz commit

# 2. Répéter pour chaque changement
poetry run cz commit

# 3. Quand prêt pour une release alpha
poetry run cz bump --prerelease alpha --yes

# 4. Tests et corrections avec commits
poetry run cz commit

# 5. Passer en beta
poetry run cz bump --prerelease beta --yes

# 6. Tests finaux et passer en RC
poetry run cz bump --prerelease rc --yes

# 7. Release stable
poetry run cz bump --yes

# 8. Générer le package
poetry build
```

### Consulter le CHANGELOG

Le fichier `CHANGELOG.md` est automatiquement mis à jour lors des bumps.

Pour régénérer manuellement le CHANGELOG :

```bash
poetry run cz changelog
```

---

## Génération des packages

### Builder le package

```bash
poetry build
```

Cette commande génère deux types de packages dans le dossier `dist/` :

1. **Wheel** (`.whl`) - Format binaire, installation rapide
   - Exemple : `pythonpackage-0.3.0a0-py3-none-any.whl`

2. **Source Distribution** (`.tar.gz`) - Format source
   - Exemple : `pythonpackage-0.3.0a0.tar.gz`

### Vérifier le contenu des packages

```bash
# Contenu du wheel
unzip -l dist/pythonpackage-*.whl

# Contenu du tar.gz
tar -tzf dist/pythonpackage-*.tar.gz
```

### Nettoyer les anciens builds

```bash
rm -rf dist/
poetry build
```

---

## Installation sur d'autres postes

### Option 1 : Installation depuis un fichier wheel (Recommandé)

#### Étape 1 : Transférer le fichier

Copiez le fichier `.whl` depuis le dossier `dist/` vers l'autre poste :

```bash
# Par SCP
scp dist/pythonpackage-0.3.0a0-py3-none-any.whl user@remote-host:/tmp/

# Par clé USB, email, serveur web, etc.
```

#### Étape 2 : Installer sur l'autre poste

```bash
pip install pythonpackage-0.3.0a0-py3-none-any.whl
```

Ou avec pip3 :

```bash
pip3 install pythonpackage-0.3.0a0-py3-none-any.whl
```

#### Étape 3 : Utiliser la commande

```bash
pythonpackage
```

**Output attendu :**
```
pythonpackage v0.3.0a0
```

### Option 2 : Installation depuis le tar.gz

```bash
pip install pythonpackage-0.3.0a0.tar.gz
```

### Option 3 : Installation via serveur HTTP local

Sur le poste avec le package :

```bash
cd dist/
python3 -m http.server 8000
```

Sur l'autre poste :

```bash
pip install http://192.168.1.100:8000/pythonpackage-0.3.0a0-py3-none-any.whl
```

### Option 4 : Installation depuis Git

Si le code est poussé sur un dépôt Git :

```bash
# Installation depuis la branche principale
pip install git+https://github.com/username/pythonpackage.git

# Installation depuis un tag spécifique
pip install git+https://github.com/username/pythonpackage.git@v0.3.0a0
```

### Résolution des problèmes

#### Commande `pythonpackage` non trouvée

Si après installation, la commande n'est pas trouvée :

```bash
# Trouver le chemin d'installation
python3 -m site --user-base

# Ajouter au PATH temporairement
export PATH="$HOME/.local/bin:$PATH"

# Ou de façon permanente
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Vérifier l'installation

```bash
# Vérifier le package installé
pip list | grep pythonpackage

# Vérifier la version
python3 -c "import pythonpackage; print(pythonpackage.__version__)"

# Tester le module
python3 -m pythonpackage.main
```

### Désinstallation

```bash
pip uninstall pythonpackage
```

---

## Publication sur PyPI (Optionnel)

### Configuration

```bash
# Pour PyPI de test (recommandé pour débuter)
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi your-test-token

# Pour PyPI de production
poetry config pypi-token.pypi your-token
```

### Publication

```bash
# Build et publish sur TestPyPI
poetry publish --build -r testpypi

# Build et publish sur PyPI
poetry publish --build
```

### Installation depuis PyPI

Une fois publié :

```bash
# Depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ pythonpackage

# Depuis PyPI
pip install pythonpackage
```

---

## Résumé des commandes essentielles

```bash
# Commit standardisé
poetry run cz commit

# Bump version automatique
poetry run cz bump --yes

# Générer le package
poetry build

# Installer localement
pip install dist/pythonpackage-*.whl

# Publier sur PyPI
poetry publish --build
```

---

## Références

- [Commitizen Documentation](https://commitizen-tools.github.io/commitizen/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
