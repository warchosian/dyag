"""
Commande markdown-to-rag : Pipeline complet Markdown vers RAG.

Ce module permet de créer un pipeline complet en une seule commande :
1. Préparation et chunking du Markdown
2. Validation des chunks
3. Indexation dans ChromaDB

Cela élimine le besoin d'exécuter manuellement prepare-rag, puis index-rag.
"""

import os
import sys
import io
from pathlib import Path
from typing import Dict
import tempfile
import time
from datetime import datetime

# Fixer l'encodage UTF-8 pour Windows
if sys.platform == 'win32' and __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import des fonctions des autres modules
from dyag.commands.prepare_rag import (
    extract_sections,
    extract_markdown_sections,
    chunk_by_size,
    validate_chunks
)
from dyag.commands.index_rag import ChunkIndexer


def markdown_to_rag_pipeline(
    input_file: str,
    collection: str,
    chunk_mode: str = 'markdown-headers',
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    embedding_model: str = 'all-MiniLM-L6-v2',
    chroma_path: str = './chroma_db',
    reset: bool = False,
    check: bool = True,
    keep_intermediate: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Pipeline complet : Markdown -> Chunks -> ChromaDB

    Args:
        input_file: Fichier Markdown source
        collection: Nom de la collection ChromaDB
        chunk_mode: Mode de chunking (markdown-headers, section, size)
        chunk_size: Taille des chunks (pour mode size)
        chunk_overlap: Overlap entre chunks (pour mode size)
        embedding_model: Modèle d'embedding Sentence Transformers
        chroma_path: Chemin vers ChromaDB
        reset: Recréer la collection si elle existe
        check: Valider les chunks avant indexation
        keep_intermediate: Garder les fichiers intermédiaires (JSON)
        verbose: Affichage détaillé

    Returns:
        Statistiques du pipeline
    """
    start_time = time.time()

    print("=" * 80)
    print("PIPELINE MARKDOWN-TO-RAG")
    print("=" * 80)
    print(f"Input: {input_file}")
    print(f"Collection: {collection}")
    print(f"Chunk mode: {chunk_mode}")
    print("=" * 80)
    print()

    # Créer un répertoire temporaire pour les fichiers intermédiaires
    temp_dir = None
    if not keep_intermediate:
        temp_dir = tempfile.mkdtemp(prefix='dyag_rag_')
        temp_json = Path(temp_dir) / 'chunks.json'
    else:
        temp_json = Path(f"chunks_{collection}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    try:
        # ========================================================================
        # PHASE 1 : Préparation et chunking
        # ========================================================================
        print("[1/3] Preparation et chunking...")
        print("-" * 80)

        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {input_file}")

        # Lire le contenu
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraire les chunks selon le mode
        chunks = []
        if chunk_mode == 'markdown-headers':
            sections = extract_markdown_sections(content, verbose=verbose)
            chunks = sections
            print(f"  [OK] {len(chunks)} sections extraites (markdown-headers)")
        elif chunk_mode == 'section':
            sections = extract_sections(content, verbose=verbose)
            chunks = sections
            print(f"  [OK] {len(chunks)} sections extraites (section)")
        elif chunk_mode == 'size':
            size_chunks = chunk_by_size(
                content,
                chunk_size=chunk_size,
                overlap=chunk_overlap,
                verbose=verbose
            )
            # Convertir au format avec title/source
            chunks = []
            for i, chunk in enumerate(size_chunks):
                chunks.append({
                    'id': chunk['id'],
                    'title': f'Chunk {i+1}',
                    'source': input_path.name,
                    'content': chunk['content']
                })
            print(f"  [OK] {len(chunks)} chunks créés (size={chunk_size}, overlap={chunk_overlap})")
        else:
            raise ValueError(f"Mode de chunking inconnu: {chunk_mode}")

        if not chunks:
            raise ValueError("Aucun chunk extrait. Vérifiez le format du fichier.")

        # Préparer le JSON
        import json
        data = {
            'metadata': {
                'source': str(input_path),
                'chunk_mode': chunk_mode,
                'chunk_size': chunk_size if chunk_mode == 'size' else None,
                'total_chunks': len(chunks),
                'created_at': datetime.now().isoformat()
            },
            'chunks': chunks
        }

        # Validation
        if check:
            print(f"  [OK] Validation des chunks...")
            valid, errors = validate_chunks(data, verbose=verbose)
            if not valid:
                print(f"  [ERROR] {len(errors)} erreurs de validation:")
                for error in errors[:10]:  # Afficher max 10 erreurs
                    print(f"    - {error}")
                raise ValueError("Validation échouée")
            print(f"  [OK] Validation: 0 erreurs")

        # Sauvegarder le JSON temporaire
        with open(temp_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print()

        # ========================================================================
        # PHASE 2 & 3 : Génération embeddings + Indexation ChromaDB
        # ========================================================================
        print("[2/3] Generation des embeddings et indexation...")
        print("-" * 80)

        # Créer l'indexeur
        indexer = ChunkIndexer(
            chroma_path=chroma_path,
            collection_name=collection,
            embedding_model=embedding_model,
            reset_collection=reset
        )

        print(f"  [OK] Modele charge: {embedding_model}")
        print(f"  [OK] Collection: {collection}")
        print()

        print("[3/3] Indexation ChromaDB...")
        print("-" * 80)

        # Indexer les chunks
        stats = indexer.index_chunks(
            chunks=chunks,
            batch_size=100,
            show_progress=True
        )

        # Statistiques finales
        print()
        print("=" * 80)
        print("PIPELINE TERMINE")
        print("=" * 80)

        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\nTemps total: {minutes}m {seconds}s")
        print(f"Chunks indexes: {stats['indexed']}/{stats['total']}")
        print(f"Taux de reussite: {stats['success_rate']:.1f}%")

        if stats['errors'] > 0:
            print(f"\n[WARNING] {stats['errors']} erreurs lors de l'indexation")

        print(f"\nCollection: {collection}")
        print(f"Chunks disponibles: {stats['indexed']}")
        print()
        print("Vous pouvez maintenant interroger le RAG:")
        print(f"  dyag query-rag --collection {collection}")
        print()
        print("Ou evaluer la qualite:")
        print(f"  dyag evaluate-rag dataset.jsonl --collection {collection}")
        print("=" * 80)

        return {
            'success': True,
            'chunks_created': len(chunks),
            'chunks_indexed': stats['indexed'],
            'errors': stats['errors'],
            'elapsed_time': elapsed,
            'collection': collection,
            'intermediate_file': str(temp_json) if keep_intermediate else None
        }

    except Exception as e:
        print()
        print("=" * 80)
        print(f"[ERROR] Pipeline echoue: {e}")
        print("=" * 80)
        raise

    finally:
        # Nettoyer les fichiers temporaires si demandé
        if not keep_intermediate and temp_dir and Path(temp_dir).exists():
            import shutil
            try:
                shutil.rmtree(temp_dir)
                if verbose:
                    print(f"[OK] Fichiers temporaires supprimes: {temp_dir}")
            except Exception as e:
                if verbose:
                    print(f"[WARNING] Impossible de supprimer {temp_dir}: {e}")


def execute(args):
    """Exécute la commande markdown-to-rag."""
    try:
        result = markdown_to_rag_pipeline(
            input_file=args.input,
            collection=args.collection,
            chunk_mode=args.chunk_mode,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            embedding_model=args.embedding_model,
            chroma_path=args.chroma_path,
            reset=args.reset,
            check=args.check,
            keep_intermediate=args.keep_intermediate,
            verbose=args.verbose
        )

        return 0 if result['success'] and result['errors'] == 0 else 1

    except Exception as e:
        print(f"\n[ERROR] {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_markdown_to_rag_command(subparsers):
    """Enregistre la commande markdown-to-rag."""
    parser = subparsers.add_parser(
        'markdown-to-rag',
        help='Pipeline complet: Markdown -> Chunks -> ChromaDB (1 commande)'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Fichier Markdown source'
    )
    parser.add_argument(
        '--collection',
        type=str,
        required=True,
        help='Nom de la collection ChromaDB'
    )
    parser.add_argument(
        '--chunk-mode',
        type=str,
        choices=['markdown-headers', 'section', 'size'],
        default='markdown-headers',
        help='Mode de chunking (defaut: markdown-headers)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Taille des chunks en mode "size" (defaut: 1000)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=200,
        help='Overlap entre chunks en mode "size" (defaut: 200)'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='all-MiniLM-L6-v2',
        help='Modele d\'embedding Sentence Transformers (defaut: all-MiniLM-L6-v2)'
    )
    parser.add_argument(
        '--chroma-path',
        type=str,
        default='./chroma_db',
        help='Chemin vers ChromaDB (defaut: ./chroma_db)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Supprimer et recreer la collection si elle existe'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        default=True,
        help='Valider les chunks avant indexation (defaut: True)'
    )
    parser.add_argument(
        '--no-check',
        dest='check',
        action='store_false',
        help='Desactiver la validation des chunks'
    )
    parser.add_argument(
        '--keep-intermediate',
        action='store_true',
        help='Garder les fichiers intermediaires (JSON)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Affichage detaille'
    )

    parser.set_defaults(func=execute)
