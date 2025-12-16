"""
Système de Q&A avec RAG pour interroger les chunks d'applications.

Ce module permet de poser des questions en langage naturel et obtenir
des réponses précises basées sur les chunks indexés.
"""

import chromadb
from sentence_transformers import SentenceTransformer
import os
import sys
import io
from typing import List, Dict, Optional
from pathlib import Path
import json
from dotenv import load_dotenv

# Fixer l'encodage UTF-8 pour Windows (seulement si exécuté comme script principal)
if sys.platform == 'win32' and __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Support pour import direct ou module
try:
    from .llm_providers import LLMProviderFactory
except ImportError:
    # Ajouter le répertoire parent au path pour import direct
    sys.path.insert(0, str(Path(__file__).parent))
    from llm_providers import LLMProviderFactory

# Charger les variables d'environnement depuis .env
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


class RAGQuerySystem:
    """
    Système de Q&A avec Retrieval Augmented Generation.

    Permet de poser des questions en langage naturel et obtenir des
    réponses précises basées sur les chunks d'applications.
    """

    def __init__(
        self,
        chroma_path: str = "./chroma_db",
        collection_name: str = "applications",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialise le système RAG.

        Args:
            chroma_path: Chemin vers la base ChromaDB
            collection_name: Nom de la collection ChromaDB
            embedding_model: Modèle Sentence Transformers pour embeddings
            llm_provider: Provider LLM ('openai', 'anthropic', 'claude', 'ollama')
                         Si None, détecté automatiquement depuis .env
            llm_model: Modèle LLM spécifique
                      Si None, utilise le modèle par défaut du provider
            api_key: Clé API du provider
                    Si None, récupérée depuis les variables d'environnement
            timeout: Timeout en secondes (uniquement pour Ollama)
                    Si None, utilise OLLAMA_TIMEOUT depuis .env (défaut: 300s)
        """
        # ChromaDB
        self.chroma_path = Path(chroma_path)
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))

        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            raise ValueError(
                f"Collection '{collection_name}' non trouvée. "
                f"Veuillez d'abord indexer vos chunks avec index_chunks.py"
            )

        # Modèle d'embedding
        print(f"Chargement du modèle d'embedding: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # LLM Provider
        print(f"Initialisation du provider LLM...")
        try:
            self.llm_provider = LLMProviderFactory.create_provider(
                provider=llm_provider,
                model=llm_model,
                api_key=api_key,
                timeout=timeout
            )
            print(f"[OK] Provider LLM: {self.llm_provider.get_model_name()}")
        except Exception as e:
            raise ValueError(f"Erreur d'initialisation du provider LLM: {e}")

    def search_chunks(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Recherche les chunks les plus pertinents pour une question.

        Args:
            query: Question en langage naturel
            n_results: Nombre de chunks à récupérer (top K)
            filter_metadata: Filtres optionnels sur les métadonnées
                           Ex: {"source_id": "383"} pour une app spécifique

        Returns:
            Liste de chunks avec leurs scores de similarité
        """
        # Générer embedding de la question
        query_embedding = self.embedding_model.encode(query).tolist()

        # Rechercher dans ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )

        # Formater résultats
        chunks = []
        for i in range(len(results['ids'][0])):
            chunks.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return chunks

    def generate_answer(
        self,
        question: str,
        chunks: List[Dict],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Génère une réponse avec le LLM basée sur les chunks de contexte.

        Args:
            question: Question de l'utilisateur
            chunks: Chunks de contexte récupérés
            system_prompt: Prompt système personnalisé (optionnel)
            temperature: Créativité du modèle (0=précis, 1=créatif)
            max_tokens: Longueur maximale de la réponse

        Returns:
            Dictionnaire avec réponse, sources, et métadonnées
        """
        # Construire le contexte à partir des chunks
        context = "\n\n---\n\n".join([
            f"[Chunk {i+1} - ID: {c['id']}]\n{c['content']}"
            for i, c in enumerate(chunks)
        ])

        # Prompt système par défaut
        if system_prompt is None:
            system_prompt = """Tu es un assistant spécialisé dans les applications informatiques.
Réponds aux questions en te basant UNIQUEMENT sur le contexte fourni.
Si l'information n'est pas dans le contexte, dis-le clairement.
Cite toujours tes sources en indiquant les IDs des chunks utilisés.
Sois précis, détaillé et professionnel."""

        # Prompt utilisateur
        user_prompt = f"""Contexte:
{context}

Question: {question}

Instructions:
- Réponds de manière précise et détaillée
- Base-toi UNIQUEMENT sur le contexte fourni
- Cite tes sources (IDs des chunks) entre crochets
- Si tu ne sais pas ou si l'information n'est pas dans le contexte, dis-le clairement
- Structure ta réponse de façon claire"""

        # Appel au LLM via le provider
        response = self.llm_provider.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            'answer': response['content'],
            'sources': [c['id'] for c in chunks],
            'chunks_used': chunks,
            'model': self.llm_provider.get_model_name(),
            'tokens_used': response['usage']['total_tokens'],
            'prompt_tokens': response['usage']['prompt_tokens'],
            'completion_tokens': response['usage']['completion_tokens']
        }

    def ask(
        self,
        question: str,
        n_chunks: int = 5,
        filter_metadata: Optional[Dict] = None,
        temperature: float = 0.3
    ) -> Dict:
        """
        Méthode tout-en-un pour poser une question.

        Args:
            question: Question en langage naturel
            n_chunks: Nombre de chunks à utiliser comme contexte
            filter_metadata: Filtres optionnels sur les métadonnées
            temperature: Créativité du modèle (0=précis, 1=créatif)

        Returns:
            Réponse complète avec sources et métadonnées

        Example:
            >>> rag = RAGQuerySystem()
            >>> result = rag.ask("Qui héberge GIDAF ?")
            >>> print(result['answer'])
        """
        # 1. Rechercher chunks pertinents
        chunks = self.search_chunks(question, n_chunks, filter_metadata)

        if not chunks:
            return {
                'question': question,
                'answer': "Aucun chunk pertinent trouvé pour cette question.",
                'sources': [],
                'chunks_used': [],
                'tokens_used': 0
            }

        # 2. Générer réponse
        result = self.generate_answer(question, chunks, temperature=temperature)

        # 3. Ajouter la question
        result['question'] = question

        return result

    def get_stats(self) -> Dict:
        """
        Récupère les statistiques de la base vectorielle.

        Returns:
            Statistiques (nombre de chunks, etc.)
        """
        count = self.collection.count()

        return {
            'total_chunks': count,
            'collection_name': self.collection.name,
            'embedding_model': self.embedding_model,
            'llm_model': self.llm_provider.get_model_name()
        }


def main():
    """
    Fonction principale pour tester le système en ligne de commande.
    """
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Système de Q&A avec RAG pour interroger les applications"
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Question à poser (mode non-interactif)'
    )
    parser.add_argument(
        '--n-chunks',
        type=int,
        default=5,
        help='Nombre de chunks de contexte (défaut: 5)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        help='Timeout en secondes pour Ollama (défaut: 300s ou OLLAMA_TIMEOUT dans .env)'
    )

    args = parser.parse_args()

    print("Initialisation du système RAG...")
    rag = RAGQuerySystem(timeout=args.timeout)

    print(f"\nStatistiques:")
    stats = rag.get_stats()
    print(f"  - Chunks indexés: {stats['total_chunks']}")
    print(f"  - Modèle LLM: {stats['llm_model']}")

    # Mode question directe
    if args.query:
        print(f"\n❓ Question: {args.query}")
        print("\n🔍 Recherche en cours...")

        result = rag.ask(args.query, n_chunks=args.n_chunks)

        print(f"\n💬 Réponse:")
        print(result['answer'])

        print(f"\n📊 Métadonnées:")
        print(f"  - Sources: {len(result['sources'])} chunks")
        print(f"  - Tokens: {result['tokens_used']}")
        print(f"  - IDs: {', '.join(result['sources'][:3])}...")

        return

    # Mode interactif
    print("\n" + "=" * 60)
    print("Mode interactif - Posez vos questions (Ctrl+C pour quitter)")
    print("=" * 60)

    while True:
        try:
            question = input("\n❓ Question: ")

            if not question.strip():
                continue

            print("\n🔍 Recherche en cours...")
            result = rag.ask(question)

            print(f"\n💬 Réponse:")
            print(result['answer'])

            print(f"\n📊 Métadonnées:")
            print(f"  - Sources: {len(result['sources'])} chunks")
            print(f"  - Tokens: {result['tokens_used']}")
            print(f"  - IDs: {', '.join(result['sources'][:3])}...")

        except KeyboardInterrupt:
            print("\n\nAu revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")


if __name__ == '__main__':
    main()
