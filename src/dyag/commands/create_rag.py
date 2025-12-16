"""
Module de création de documents optimisés pour RAG (Retrieval Augmented Generation).

Ce module permet de transformer des fichiers JSON ou Markdown en formats optimisés
pour les systèmes RAG en créant des chunks sémantiques avec métadonnées.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class RAGChunk:
    """Représente un chunk de données optimisé pour RAG."""

    id: str  # Identifiant unique du chunk
    source_id: str  # ID de l'application source
    title: str  # Titre du chunk
    content: str  # Contenu textuel principal
    metadata: Dict[str, Any]  # Métadonnées additionnelles
    chunk_type: str  # Type de chunk (application, description, etc.)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le chunk en dictionnaire."""
        return asdict(self)


class DataCleaner:
    """Nettoie et normalise les données sources."""

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Nettoie un texte en supprimant les caractères indésirables.

        Args:
            text: Texte à nettoyer

        Returns:
            Texte nettoyé
        """
        if not text:
            return ""

        # Remplacer les séquences 'r n' par de vrais sauts de ligne
        text = text.replace(' r n', '\n').replace('r n', '\n')

        # Normaliser les espaces multiples
        text = re.sub(r' +', ' ', text)

        # Supprimer les espaces en début et fin de ligne
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)

        return text.strip()

    @staticmethod
    def restore_url(url: str) -> str:
        """
        Restaure une URL normalisée en format valide.

        Args:
            url: URL normalisée (avec espaces au lieu de caractères spéciaux)

        Returns:
            URL restaurée
        """
        if not url:
            return ""

        # Restaurer les protocoles
        url = url.replace('https ', 'https://').replace('http ', 'http://')
        url = url.replace('https  ', 'https://').replace('http  ', 'http://')

        # Supprimer les espaces
        url = url.replace(' ', '')

        return url

    @staticmethod
    def clean_metadata_value(value: Any) -> Any:
        """
        Nettoie une valeur de métadonnée.

        Args:
            value: Valeur à nettoyer

        Returns:
            Valeur nettoyée
        """
        if isinstance(value, str):
            return DataCleaner.clean_text(value)
        elif isinstance(value, list):
            return [DataCleaner.clean_metadata_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: DataCleaner.clean_metadata_value(v) for k, v in value.items()}
        return value


class ApplicationChunker:
    """Crée des chunks sémantiques à partir de données d'applications."""

    def __init__(self, max_chunk_size: int = 1000):
        """
        Initialise le chunker.

        Args:
            max_chunk_size: Taille maximale d'un chunk en caractères
        """
        self.max_chunk_size = max_chunk_size
        self.cleaner = DataCleaner()

    def _generate_chunk_id(self, source_id: str, chunk_type: str, index: int = 0) -> str:
        """
        Génère un ID unique pour un chunk.

        Args:
            source_id: ID de la source
            chunk_type: Type de chunk
            index: Index du chunk

        Returns:
            ID unique du chunk
        """
        content = f"{source_id}_{chunk_type}_{index}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _extract_metadata(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait et nettoie les métadonnées importantes.

        Args:
            app_data: Données de l'application

        Returns:
            Métadonnées nettoyées
        """
        metadata = {}

        # Champs importants pour la recherche
        important_fields = [
            'id', 'nom', 'nom long', 'statut si', 'portee geographique',
            'famille d applications', 'domaines et sous domaines',
            'thematiques et sous thematiques france nation verte',
            'date et heure de creation de la fiche',
            'date et heure de modification de la fiche'
        ]

        for field in important_fields:
            if field in app_data:
                metadata[field] = self.cleaner.clean_metadata_value(app_data[field])

        # Extraire les URLs
        if 'sites' in app_data and isinstance(app_data['sites'], list):
            urls = []
            for site in app_data['sites']:
                if isinstance(site, dict) and 'url' in site:
                    urls.append(self.cleaner.restore_url(site['url']))
            if urls:
                metadata['urls'] = urls

        # Extraire les domaines métiers
        if 'domaines et sous domaines' in app_data:
            domaines = app_data['domaines et sous domaines']
            if isinstance(domaines, list):
                metadata['domaines_metier'] = [
                    d.get('domaine metier', '') for d in domaines if isinstance(d, dict)
                ]

        return metadata

    def chunk_application_from_json(self, app_data: Dict[str, Any]) -> List[RAGChunk]:
        """
        Crée des chunks à partir d'une application au format JSON.

        Args:
            app_data: Données de l'application

        Returns:
            Liste de chunks RAG
        """
        chunks = []
        source_id = str(app_data.get('id', 'unknown'))
        app_name = app_data.get('nom', 'Application inconnue')

        # Extraire les métadonnées communes
        common_metadata = self._extract_metadata(app_data)

        # Chunk 1: Vue d'ensemble (résumé de l'application)
        overview_parts = []
        overview_parts.append(f"# {app_name}")

        if 'nom long' in app_data:
            overview_parts.append(f"\n**Nom complet**: {app_data['nom long']}")

        if 'statut si' in app_data:
            overview_parts.append(f"**Statut**: {app_data['statut si']}")

        if 'portee geographique' in app_data:
            overview_parts.append(f"**Portée géographique**: {app_data['portee geographique']}")

        if 'famille d applications' in app_data:
            overview_parts.append(f"**Famille**: {app_data['famille d applications']}")

        overview_content = self.cleaner.clean_text('\n'.join(overview_parts))

        chunks.append(RAGChunk(
            id=self._generate_chunk_id(source_id, 'overview'),
            source_id=source_id,
            title=f"{app_name} - Vue d'ensemble",
            content=overview_content,
            metadata=common_metadata,
            chunk_type='overview'
        ))

        # Chunk 2: Description détaillée
        if 'descriptif' in app_data and app_data['descriptif']:
            description = self.cleaner.clean_text(app_data['descriptif'])
            if description:
                chunks.append(RAGChunk(
                    id=self._generate_chunk_id(source_id, 'description'),
                    source_id=source_id,
                    title=f"{app_name} - Description",
                    content=description,
                    metadata=common_metadata,
                    chunk_type='description'
                ))

        # Chunk 3: Informations techniques (domaines, acteurs, contacts)
        tech_parts = []
        tech_parts.append(f"# {app_name} - Informations techniques")

        if 'domaines et sous domaines' in app_data:
            tech_parts.append("\n## Domaines métier")
            for domaine in app_data['domaines et sous domaines']:
                if isinstance(domaine, dict):
                    if 'domaine metier' in domaine:
                        tech_parts.append(f"- Domaine: {domaine['domaine metier']}")
                    if 'sous domaine metier' in domaine:
                        tech_parts.append(f"  - Sous-domaine: {domaine['sous domaine metier']}")

        if 'acteurs' in app_data and isinstance(app_data['acteurs'], list):
            tech_parts.append("\n## Acteurs")
            for acteur in app_data['acteurs']:
                if isinstance(acteur, dict):
                    role = acteur.get('role d acteur', '')
                    nom = acteur.get('acteur', '')
                    if role and nom:
                        tech_parts.append(f"- {role}: {nom}")

        if 'contacts' in app_data and isinstance(app_data['contacts'], list):
            tech_parts.append("\n## Contacts")
            for contact in app_data['contacts']:
                if isinstance(contact, dict):
                    role = contact.get('role de contact', '')
                    nom = contact.get('contact', '')
                    email = contact.get('courriel', '')
                    if role and (nom or email):
                        contact_str = f"- {role}: "
                        if nom:
                            contact_str += nom
                        if email:
                            contact_str += f" ({email})"
                        tech_parts.append(contact_str)

        tech_content = self.cleaner.clean_text('\n'.join(tech_parts))
        if len(tech_content) > len(f"# {app_name} - Informations techniques"):
            chunks.append(RAGChunk(
                id=self._generate_chunk_id(source_id, 'technical'),
                source_id=source_id,
                title=f"{app_name} - Informations techniques",
                content=tech_content,
                metadata=common_metadata,
                chunk_type='technical'
            ))

        # Chunk 4: Sites et URLs
        if 'sites' in app_data and isinstance(app_data['sites'], list):
            sites_parts = [f"# {app_name} - Sites web"]
            for site in app_data['sites']:
                if isinstance(site, dict):
                    nature = site.get('nature de l url', 'Site')
                    url = self.cleaner.restore_url(site.get('url', ''))
                    if url:
                        sites_parts.append(f"- {nature}: {url}")

            sites_content = self.cleaner.clean_text('\n'.join(sites_parts))
            if len(sites_parts) > 1:
                chunks.append(RAGChunk(
                    id=self._generate_chunk_id(source_id, 'sites'),
                    source_id=source_id,
                    title=f"{app_name} - Sites web",
                    content=sites_content,
                    metadata=common_metadata,
                    chunk_type='sites'
                ))

        return chunks

    def chunk_application_from_markdown(self, md_text: str, app_id: Optional[str] = None) -> List[RAGChunk]:
        """
        Crée des chunks à partir d'une application au format Markdown.

        Args:
            md_text: Texte markdown de l'application
            app_id: ID optionnel de l'application

        Returns:
            Liste de chunks RAG
        """
        chunks = []

        # Extraire le nom de l'application
        title_match = re.search(r'^## Application:\s*(.+)$', md_text, re.MULTILINE)
        app_name = title_match.group(1) if title_match else "Application inconnue"

        # Extraire l'ID
        if not app_id:
            id_match = re.search(r'# Application d\'identifiant:\s*(\d+)', md_text)
            app_id = id_match.group(1) if id_match else hashlib.md5(app_name.encode()).hexdigest()[:8]

        # Diviser en sections
        sections = re.split(r'\n(?=- [A-Z])', md_text)

        metadata = {'id': app_id, 'nom': app_name}

        # Créer un chunk principal avec les premières informations
        main_content_parts = [f"# {app_name}"]

        for section in sections[:5]:  # Premières sections
            cleaned = self.cleaner.clean_text(section)
            if cleaned and len('\n'.join(main_content_parts)) + len(cleaned) < self.max_chunk_size:
                main_content_parts.append(cleaned)

        chunks.append(RAGChunk(
            id=self._generate_chunk_id(app_id, 'main'),
            source_id=app_id,
            title=f"{app_name} - Informations principales",
            content=self.cleaner.clean_text('\n'.join(main_content_parts)),
            metadata=metadata,
            chunk_type='main'
        ))

        # Créer des chunks additionnels si nécessaire
        current_chunk = []
        chunk_index = 1

        for section in sections[5:]:
            cleaned = self.cleaner.clean_text(section)
            if not cleaned:
                continue

            current_size = len('\n'.join(current_chunk))
            if current_size + len(cleaned) > self.max_chunk_size and current_chunk:
                # Sauvegarder le chunk actuel
                chunks.append(RAGChunk(
                    id=self._generate_chunk_id(app_id, 'details', chunk_index),
                    source_id=app_id,
                    title=f"{app_name} - Détails {chunk_index}",
                    content='\n'.join(current_chunk),
                    metadata=metadata,
                    chunk_type='details'
                ))
                current_chunk = [cleaned]
                chunk_index += 1
            else:
                current_chunk.append(cleaned)

        # Sauvegarder le dernier chunk
        if current_chunk:
            chunks.append(RAGChunk(
                id=self._generate_chunk_id(app_id, 'details', chunk_index),
                source_id=app_id,
                title=f"{app_name} - Détails {chunk_index}",
                content='\n'.join(current_chunk),
                metadata=metadata,
                chunk_type='details'
            ))

        return chunks


class RAGExporter:
    """Exporte les chunks RAG dans différents formats."""

    @staticmethod
    def export_jsonl(chunks: List[RAGChunk], output_path: Path) -> None:
        """
        Exporte les chunks au format JSON-Lines.

        Args:
            chunks: Liste de chunks à exporter
            output_path: Chemin du fichier de sortie
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                json.dump(chunk.to_dict(), f, ensure_ascii=False)
                f.write('\n')

    @staticmethod
    def export_json(chunks: List[RAGChunk], output_path: Path) -> None:
        """
        Exporte les chunks au format JSON.

        Args:
            chunks: Liste de chunks à exporter
            output_path: Chemin du fichier de sortie
        """
        data = [chunk.to_dict() for chunk in chunks]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_markdown(chunks: List[RAGChunk], output_path: Path) -> None:
        """
        Exporte les chunks au format Markdown.

        Args:
            chunks: Liste de chunks à exporter
            output_path: Chemin du fichier de sortie
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(f"---\n")
                f.write(f"id: {chunk.id}\n")
                f.write(f"source_id: {chunk.source_id}\n")
                f.write(f"type: {chunk.chunk_type}\n")
                f.write(f"metadata: {json.dumps(chunk.metadata, ensure_ascii=False)}\n")
                f.write(f"---\n\n")
                f.write(f"# {chunk.title}\n\n")
                f.write(f"{chunk.content}\n\n")
                f.write(f"\n\n")


class RAGCreator:
    """Classe principale pour créer des documents RAG."""

    def __init__(self, max_chunk_size: int = 1000):
        """
        Initialise le créateur RAG.

        Args:
            max_chunk_size: Taille maximale d'un chunk en caractères
        """
        self.chunker = ApplicationChunker(max_chunk_size=max_chunk_size)
        self.exporter = RAGExporter()

    def process_json_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        output_format: str = 'jsonl'
    ) -> int:
        """
        Traite un fichier JSON et génère un fichier RAG.

        Args:
            input_path: Chemin du fichier JSON source
            output_path: Chemin du fichier de sortie
            output_format: Format de sortie ('jsonl', 'json', 'markdown')

        Returns:
            Nombre de chunks créés
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        # Charger le JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extraire les applications
        applications = []
        if isinstance(data, dict):
            # Chercher la clé contenant les applications
            for key in data:
                if isinstance(data[key], list):
                    applications = data[key]
                    break
        elif isinstance(data, list):
            applications = data

        # Créer les chunks
        all_chunks = []
        for app_data in applications:
            if isinstance(app_data, dict):
                chunks = self.chunker.chunk_application_from_json(app_data)
                all_chunks.extend(chunks)

        # Exporter
        if output_format == 'jsonl':
            self.exporter.export_jsonl(all_chunks, output_path)
        elif output_format == 'json':
            self.exporter.export_json(all_chunks, output_path)
        elif output_format == 'markdown':
            self.exporter.export_markdown(all_chunks, output_path)
        else:
            raise ValueError(f"Format non supporté: {output_format}")

        return len(all_chunks)

    def process_markdown_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        output_format: str = 'jsonl'
    ) -> int:
        """
        Traite un fichier Markdown et génère un fichier RAG.

        Args:
            input_path: Chemin du fichier Markdown source
            output_path: Chemin du fichier de sortie
            output_format: Format de sortie ('jsonl', 'json', 'markdown')

        Returns:
            Nombre de chunks créés
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        # Charger le Markdown
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Diviser par application (sections commençant par ## Application:)
        applications = re.split(r'(?=^## Application:)', content, flags=re.MULTILINE)

        # Créer les chunks
        all_chunks = []
        for app_md in applications:
            app_md = app_md.strip()
            if app_md and app_md.startswith('## Application:'):
                chunks = self.chunker.chunk_application_from_markdown(app_md)
                all_chunks.extend(chunks)

        # Exporter
        if output_format == 'jsonl':
            self.exporter.export_jsonl(all_chunks, output_path)
        elif output_format == 'json':
            self.exporter.export_json(all_chunks, output_path)
        elif output_format == 'markdown':
            self.exporter.export_markdown(all_chunks, output_path)
        else:
            raise ValueError(f"Format non supporté: {output_format}")

        return len(all_chunks)


def create_rag_from_file(
    input_file: str,
    output_file: str,
    output_format: str = 'jsonl',
    max_chunk_size: int = 1000
) -> None:
    """
    Fonction utilitaire pour créer un fichier RAG à partir d'un fichier source.

    Args:
        input_file: Chemin du fichier source (JSON ou Markdown)
        output_file: Chemin du fichier de sortie
        output_format: Format de sortie ('jsonl', 'json', 'markdown')
        max_chunk_size: Taille maximale d'un chunk en caractères
    """
    creator = RAGCreator(max_chunk_size=max_chunk_size)
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {input_file}")

    # Détecter le format d'entrée
    if input_path.suffix.lower() == '.json':
        chunk_count = creator.process_json_file(input_file, output_file, output_format)
    elif input_path.suffix.lower() in ['.md', '.markdown']:
        chunk_count = creator.process_markdown_file(input_file, output_file, output_format)
    else:
        raise ValueError(f"Format de fichier non supporté: {input_path.suffix}")

    print(f"OK - {chunk_count} chunks crees avec succes")
    print(f"OK - Fichier RAG genere: {output_file}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python create_rag.py <input_file> <output_file> [format] [max_chunk_size]")
        print("Formats disponibles: jsonl (défaut), json, markdown")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    output_format = sys.argv[3] if len(sys.argv) > 3 else 'jsonl'
    max_chunk_size = int(sys.argv[4]) if len(sys.argv) > 4 else 1000

    try:
        create_rag_from_file(input_file, output_file, output_format, max_chunk_size)
    except Exception as e:
        print(f"✗ Erreur: {e}")
        sys.exit(1)
