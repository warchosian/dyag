"""
Parser pour convertir un fichier Markdown (généré par project2md) en structure de projet.

Ce module parse le format de sortie de project2md et extrait :
- Les chemins de fichiers depuis les headers ### 📄 `path`
- Le contenu des blocs de code associés
- Les métadonnées (language, taille, etc.)
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path


@dataclass
class FileEntry:
    """Représente un fichier extrait du Markdown"""

    path: str
    content: str
    language: Optional[str] = None
    size: Optional[int] = None
    lines: Optional[int] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convertir en dictionnaire"""
        return {
            "path": self.path,
            "content": self.content,
            "language": self.language,
            "size": self.size,
            "lines": self.lines,
            "metadata": self.metadata,
        }


@dataclass
class ProjectStructure:
    """Représente la structure complète d'un projet"""

    name: str
    files: List[FileEntry] = field(default_factory=list)
    root_path: Optional[str] = None
    total_files: Optional[int] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convertir en dictionnaire"""
        return {
            "name": self.name,
            "root_path": self.root_path,
            "total_files": self.total_files,
            "files": [f.to_dict() for f in self.files],
            "metadata": self.metadata,
        }


class Md2ProjectParser:
    """Parser pour fichiers Markdown générés par project2md"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def parse_file(self, md_path: str) -> ProjectStructure:
        """
        Parse un fichier Markdown et extrait la structure du projet.

        Args:
            md_path: Chemin vers le fichier Markdown

        Returns:
            ProjectStructure contenant tous les fichiers extraits
        """
        # Essayer plusieurs encodages (comme project2md)
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        last_error = None

        for encoding in encodings:
            try:
                content = Path(md_path).read_text(encoding=encoding)
                if self.verbose:
                    print(f"[INFO] Fichier lu avec encodage: {encoding}")
                break
            except (UnicodeDecodeError, LookupError) as e:
                last_error = e
                continue

        if content is None:
            raise last_error or Exception(f"Impossible de lire {md_path} avec les encodages supportés")

        return self.parse_content(content)

    def parse_content(self, content: str) -> ProjectStructure:
        """
        Parse le contenu Markdown et extrait la structure du projet.

        Args:
            content: Contenu Markdown à parser

        Returns:
            ProjectStructure contenant tous les fichiers extraits
        """
        # Extraire le nom du projet depuis "# Projet : nom"
        project_name = self._extract_project_name(content)

        if self.verbose:
            print(f"[PARSE] Projet : {project_name}")

        # Créer la structure de projet
        project = ProjectStructure(name=project_name)

        # Extraire métadonnées du header
        self._extract_header_metadata(content, project)

        # Extraire tous les fichiers depuis la section "Contenu des fichiers"
        files = self._extract_files(content)
        project.files = files

        if self.verbose:
            print(f"[OK] Extrait {len(files)} fichiers")

        return project

    def _extract_project_name(self, content: str) -> str:
        """Extraire le nom du projet depuis # Projet : nom"""
        match = re.search(r'^#\s+Projet\s*:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "unnamed_project"

    def _extract_header_metadata(self, content: str, project: ProjectStructure):
        """Extraire les métadonnées du header (chemin, nombre de fichiers)"""
        # Chemin : **Chemin** : `path`
        match = re.search(r'\*\*Chemin\*\*\s*:\s*`([^`]+)`', content)
        if match:
            project.root_path = match.group(1).strip()

        # Nombre de fichiers : **Fichiers** : X fichiers
        match = re.search(r'\*\*Fichiers\*\*\s*:\s*(\d+)', content)
        if match:
            project.total_files = int(match.group(1))

    def _extract_files(self, content: str) -> List[FileEntry]:
        """
        Extraire tous les fichiers depuis la section "Contenu des fichiers".

        Format attendu :
        ### 📄 `path/to/file.ext` [size octets]
        ### ?? `path/to/file.ext` [size octets]  (emojis corrompus)

        > **Chemin relatif** : `path`
        > **Taille** : X octets
        > **Lignes** : Y
        > **Type** : language

        ````language
        content
        ````
        """
        files = []

        # Trouver la section "Contenu des fichiers" (optionnel)
        # Accepter plusieurs formats:
        # - ## 📄 Contenu des fichiers (original UTF-8)
        # - ## ?? Contenu (emojis corrompus en latin-1)
        # - Ou scanner tout le document si pas de section
        content_section_match = re.search(
            r'##\s+(?:📄|📁|\?\?)\s+(?:Contenu des fichiers|Arborescence|Contenu)\s*\n(.+)',
            content,
            re.DOTALL
        )

        if content_section_match:
            content_section = content_section_match.group(1)
            if self.verbose:
                print("[INFO] Section 'Contenu' trouvée")
        else:
            # Pas de section trouvée, scanner tout le document
            if self.verbose:
                print("[WARNING] Section 'Contenu des fichiers' non trouvée - scan du document entier")
            content_section = content

        # Split par les headers de fichiers
        # Pattern ultra-flexible :
        # - ## ou ### ou #### (2+ dièses)
        # - Suivi de texte quelconque (??, "Fichier N:", emoji, etc.)
        # - Puis `nom_du_fichier` entre backticks
        # - Optionnellement [size] après
        # Note: On capture TOUT jusqu'au prochain header ou fin de doc
        file_pattern = re.compile(
            r'^#{2,}[^`]*`([^`]+)`(?:\s*\[([^\]]+)\])?(.*?)(?=^#{2,}[^`]*`|---.*?Généré par|\Z)',
            re.DOTALL | re.MULTILINE
        )

        for match in file_pattern.finditer(content_section):
            file_path = match.group(1).strip()
            size_str = match.group(2).strip() if match.group(2) else None
            file_content_block = match.group(3)

            if self.verbose:
                print(f"[EXTRACT] {file_path}")

            # Créer l'entrée de fichier
            file_entry = FileEntry(path=file_path, content="")

            # Extraire la taille (si présente)
            if size_str:
                size_match = re.search(r'([\d.]+)\s+octets', size_str)
                if size_match:
                    size_text = size_match.group(1).replace('.', '')  # Enlever séparateur de milliers
                    try:
                        file_entry.size = int(size_text)
                    except ValueError:
                        pass

            # Extraire les métadonnées du bloc quote
            self._extract_file_metadata(file_content_block, file_entry)

            # Extraire le contenu du code block
            code_content = self._extract_code_block(file_content_block, file_entry)
            file_entry.content = code_content

            files.append(file_entry)

        return files

    def _extract_file_metadata(self, block: str, file_entry: FileEntry):
        """Extraire les métadonnées du bloc quote (>, **Field** : value)"""
        # Type/Language : > **Type** : language
        match = re.search(r'>\s+\*\*Type\*\*\s*:\s*(.+)', block)
        if match:
            file_entry.language = match.group(1).strip()

        # Lignes : > **Lignes** : X
        match = re.search(r'>\s+\*\*Lignes\*\*\s*:\s*(\d+)', block)
        if match:
            file_entry.lines = int(match.group(1))

        # Taille : > **Taille** : X octets
        match = re.search(r'>\s+\*\*Taille\*\*\s*:\s*([\d.]+)\s+octets', block)
        if match:
            size_text = match.group(1).replace('.', '')
            try:
                file_entry.size = int(size_text)
            except ValueError:
                pass

    def _extract_code_block(self, block: str, file_entry: FileEntry) -> str:
        """
        Extraire le contenu du code block.

        Supporte :
        - Fences simples : ```language ... ```
        - Fences multiples : ````language ... ````
        - Blocs collapsibles : <details>...</details>
        """
        # Détecter le nombre de backticks (3, 4, 5, etc.)
        fence_match = re.search(r'(`{3,})(\w*)\n', block)
        if not fence_match:
            if self.verbose:
                print(f"[WARNING] Pas de code block trouvé pour {file_entry.path}")
            return ""

        fence = fence_match.group(1)  # Nombre de backticks
        language = fence_match.group(2)  # Language optionnel

        # Si language détecté et pas encore défini
        if language and not file_entry.language:
            file_entry.language = language

        # Pattern pour extraire le contenu entre les fences
        # Utilise re.DOTALL pour matcher sur plusieurs lignes
        # Rendre le newline final optionnel et accepter contenu vide
        pattern = re.escape(fence) + r'(?:\w*)\n(.*?)\n?' + re.escape(fence)
        content_match = re.search(pattern, block, re.DOTALL)

        if content_match:
            return content_match.group(1)

        # Fallback : chercher dans <details> si présent
        details_match = re.search(
            r'<details[^>]*>.*?<summary>.*?</summary>\s*' +
            re.escape(fence) + r'(?:\w*)\n(.+?)\n' + re.escape(fence),
            block,
            re.DOTALL
        )

        if details_match:
            return details_match.group(1)

        if self.verbose:
            print(f"[WARNING] Contenu vide pour {file_entry.path}")

        return ""

    def validate_structure(self, project: ProjectStructure) -> List[str]:
        """
        Valider la structure extraite.

        Args:
            project: Structure de projet à valider

        Returns:
            Liste d'erreurs/avertissements (vide si tout OK)
        """
        issues = []

        # Vérifier qu'il y a des fichiers
        if not project.files:
            issues.append("Aucun fichier extrait")

        # Vérifier les fichiers vides
        empty_files = [f.path for f in project.files if not f.content.strip()]
        if empty_files:
            issues.append(f"{len(empty_files)} fichiers vides : {', '.join(empty_files[:3])}")

        # Vérifier les chemins invalides
        for file_entry in project.files:
            try:
                Path(file_entry.path)
            except Exception as e:
                issues.append(f"Chemin invalide '{file_entry.path}': {e}")

        # Vérifier cohérence nombre de fichiers
        if project.total_files and len(project.files) != project.total_files:
            issues.append(
                f"Incohérence : {project.total_files} fichiers attendus, "
                f"{len(project.files)} extraits"
            )

        return issues
