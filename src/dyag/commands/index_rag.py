"""
Commande d'indexation des chunks dans ChromaDB.

Ce module permet d'indexer des chunks dans une base vectorielle ChromaDB
pour permettre la recherche sémantique via RAG.
"""

import os
# Configurer HF_HOME avant d'importer sentence_transformers
# (remplace l'ancien TRANSFORMERS_CACHE qui est déprécié)
if 'TRANSFORMERS_CACHE' in os.environ and 'HF_HOME' not in os.environ:
    os.environ['HF_HOME'] = os.environ['TRANSFORMERS_CACHE']

import chromadb
from sentence_transformers import SentenceTransformer
import json
import sys
import io
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

# Fixer l'encodage UTF-8 pour Windows (seulement si exécuté comme script principal)
if sys.platform == 'win32' and __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ChunkIndexer:
    """
    Indexe les chunks RAG dans ChromaDB avec embeddings.
    """

    def __init__(
        self,
        chroma_path: str = "./chroma_db",
        collection_name: str = "applications",
        embedding_model: str = "all-MiniLM-L6-v2",
        reset_collection: bool = False
    ):
        """
        Initialise l'indexeur.

        Args:
            chroma_path: Chemin vers la base ChromaDB
            collection_name: Nom de la collection
            embedding_model: Modèle Sentence Transformers
            reset_collection: Si True, supprime la collection existante
        """
        self.chroma_path = Path(chroma_path)
        self.chroma_path.mkdir(parents=True, exist_ok=True)

        print(f"Connexion à ChromaDB: {self.chroma_path}")
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))

        # Gérer la collection
        if reset_collection:
            try:
                self.client.delete_collection(collection_name)
                print(f"Collection '{collection_name}' supprimée")
            except Exception:
                pass

        # Créer ou récupérer la collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Chunks d'applications pour RAG"}
        )

        print(f"Chargement du modèle d'embedding: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print(f"Modèle chargé avec dimension: {self.embedding_model.get_sentence_embedding_dimension()}")

    def load_chunks_from_jsonl(self, jsonl_path: Path) -> List[Dict]:
        """
        Charge les chunks depuis un fichier JSONL.

        Args:
            jsonl_path: Chemin vers le fichier JSONL

        Returns:
            Liste de dictionnaires de chunks
        """
        chunks = []
        print(f"\nChargement des chunks depuis: {jsonl_path}")

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    chunk = json.loads(line.strip())
                    chunks.append(chunk)
                except json.JSONDecodeError as e:
                    print(f"Erreur ligne {line_num}: {e}")
                    continue

        print(f"Chunks chargés: {len(chunks)}")
        return chunks

    def load_chunks_from_json(self, json_path: Path) -> List[Dict]:
        """
        Charge les chunks depuis un fichier JSON.

        Args:
            json_path: Chemin vers le fichier JSON

        Returns:
            Liste de dictionnaires de chunks
        """
        print(f"\nChargement des chunks depuis: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        chunks = data.get('chunks', [])
        print(f"Chunks chargés: {len(chunks)}")
        return chunks

    def index_chunks(
        self,
        chunks: List[Dict],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> Dict:
        """
        Indexe les chunks dans ChromaDB avec embeddings.

        Args:
            chunks: Liste de chunks à indexer
            batch_size: Taille des lots pour l'indexation
            show_progress: Afficher la barre de progression

        Returns:
            Statistiques d'indexation
        """
        if not chunks:
            print("Aucun chunk à indexer")
            return {'indexed': 0, 'errors': 0}

        print(f"\nIndexation de {len(chunks)} chunks...")
        print(f"Taille des lots: {batch_size}")

        indexed = 0
        errors = 0

        # Préparer les chunks pour ChromaDB
        ids = []
        documents = []
        metadatas = []

        iterator = tqdm(chunks) if show_progress else chunks

        for chunk in iterator:
            try:
                # ID du chunk
                chunk_id = chunk.get('id', '')
                if not chunk_id:
                    errors += 1
                    continue

                # Contenu textuel
                content = chunk.get('content', '')
                if not content:
                    errors += 1
                    continue

                # Métadonnées
                metadata = chunk.get('metadata', {})
                # Ajouter chunk_type et title au niveau racine
                metadata['chunk_type'] = chunk.get('chunk_type', 'unknown')
                metadata['title'] = chunk.get('title', '')

                ids.append(chunk_id)
                documents.append(content)
                metadatas.append(metadata)

            except Exception as e:
                print(f"\nErreur préparation chunk {chunk.get('id', '?')}: {e}")
                errors += 1
                continue

        # Indexer par lots
        print(f"\nGénération des embeddings et indexation...")
        total_batches = (len(documents) + batch_size - 1) // batch_size

        for i in range(0, len(documents), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]

            try:
                # Générer embeddings
                embeddings = self.embedding_model.encode(
                    batch_docs,
                    show_progress_bar=False,
                    convert_to_numpy=True
                ).tolist()

                # Ajouter à ChromaDB
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_metas,
                    embeddings=embeddings
                )

                indexed += len(batch_ids)

                if show_progress:
                    batch_num = (i // batch_size) + 1
                    print(f"Lot {batch_num}/{total_batches}: {len(batch_ids)} chunks indexés")

            except Exception as e:
                print(f"\nErreur indexation lot {i//batch_size + 1}: {e}")
                errors += len(batch_ids)
                continue

        stats = {
            'indexed': indexed,
            'errors': errors,
            'total': len(chunks),
            'success_rate': (indexed / len(chunks) * 100) if chunks else 0
        }

        print(f"\nIndexation terminée:")
        print(f"  - Indexés: {stats['indexed']}")
        print(f"  - Erreurs: {stats['errors']}")
        print(f"  - Taux de réussite: {stats['success_rate']:.1f}%")

        return stats

    def get_stats(self) -> Dict:
        """
        Récupère les statistiques de la collection.

        Returns:
            Statistiques (nombre de chunks, etc.)
        """
        count = self.collection.count()

        # Récupérer quelques échantillons pour analyse
        if count > 0:
            sample = self.collection.get(limit=min(100, count))
            chunk_types = {}

            for meta in sample['metadatas']:
                chunk_type = meta.get('chunk_type', 'unknown')
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

            return {
                'total_chunks': count,
                'collection_name': self.collection.name,
                'chunk_types_sample': chunk_types
            }
        else:
            return {
                'total_chunks': 0,
                'collection_name': self.collection.name,
                'chunk_types_sample': {}
            }


def execute(args):
    """Exécute la commande index-rag."""
    # Vérifier le fichier d'entrée
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fichier non trouvé: {input_path}")
        return 1

    # Créer l'indexeur
    print("=" * 70)
    print("INDEXATION DES CHUNKS DANS CHROMADB")
    print("=" * 70)

    try:
        indexer = ChunkIndexer(
            chroma_path=args.chroma_path,
            collection_name=args.collection,
            embedding_model=args.embedding_model,
            reset_collection=args.reset
        )
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return 1

    # Charger les chunks
    try:
        if input_path.suffix == '.jsonl':
            chunks = indexer.load_chunks_from_jsonl(input_path)
        elif input_path.suffix == '.json':
            chunks = indexer.load_chunks_from_json(input_path)
        else:
            print(f"❌ Format non supporté: {input_path.suffix}")
            print("Formats acceptés: .jsonl, .json")
            return 1
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        return 1

    if not chunks:
        print("❌ Aucun chunk trouvé dans le fichier")
        return 1

    # Indexer
    stats = indexer.index_chunks(
        chunks,
        batch_size=args.batch_size,
        show_progress=not args.no_progress
    )

    # Afficher les statistiques finales
    print("\n" + "=" * 70)
    print("STATISTIQUES DE LA COLLECTION")
    print("=" * 70)

    collection_stats = indexer.get_stats()
    print(f"\nTotal chunks indexés: {collection_stats['total_chunks']}")
    print(f"Collection: {collection_stats['collection_name']}")

    if collection_stats['chunk_types_sample']:
        print(f"\nTypes de chunks (échantillon):")
        for chunk_type, count in collection_stats['chunk_types_sample'].items():
            print(f"  - {chunk_type}: {count}")

    print("\n" + "=" * 70)
    print("[OK] INDEXATION TERMINÉE")
    print("=" * 70)
    print(f"\nVous pouvez maintenant interroger le RAG:")
    print(f"  dyag query-rag --collection {args.collection}")

    return 0 if stats['errors'] == 0 else 1


def register_index_rag_command(subparsers):
    """Enregistre la commande index-rag."""
    parser = subparsers.add_parser(
        'index-rag',
        help='Indexe des chunks dans ChromaDB pour le RAG'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Fichier JSONL ou JSON contenant les chunks'
    )
    parser.add_argument(
        '--chroma-path',
        type=str,
        default='./chroma_db',
        help='Chemin vers la base ChromaDB (défaut: ./chroma_db)'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default='applications',
        help='Nom de la collection (défaut: applications)'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Modèle d\'embedding (défaut: all-MiniLM-L6-v2)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Taille des lots pour indexation (défaut: 100)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Supprimer et recréer la collection'
    )
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Désactiver la barre de progression'
    )

    parser.set_defaults(func=execute)
