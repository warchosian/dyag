"""
Tests unitaires pour dyag.rag.core.retriever

Tests exhaustifs du système RAG de requête et récupération.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from dyag.rag.core.retriever import RAGQuerySystem


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
@pytest.mark.requires_chromadb
class TestRAGQuerySystemInit:
    """Tests d'initialisation du système RAG."""

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_init_default_parameters(self, mock_transformer, mock_chroma):
        """Test initialisation avec paramètres par défaut."""
        # Mock ChromaDB
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        # Mock SentenceTransformer
        mock_transformer.return_value = MagicMock()

        rag = RAGQuerySystem()

        assert rag is not None
        assert rag.chroma_path == Path("./chroma_db")
        mock_transformer.assert_called_once()

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_init_custom_parameters(self, mock_transformer, mock_chroma):
        """Test initialisation avec paramètres personnalisés."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client
        mock_transformer.return_value = MagicMock()

        rag = RAGQuerySystem(
            chroma_path="./custom_db",
            collection_name="custom_collection",
            embedding_model="custom-model",
            llm_provider="openai",
            llm_model="gpt-4"
        )

        assert rag.chroma_path == Path("./custom_db")
        mock_client.get_collection.assert_called_with("custom_collection")

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_init_missing_collection(self, mock_transformer, mock_chroma):
        """Test erreur si collection n'existe pas."""
        mock_client = MagicMock()
        mock_client.get_collection.side_effect = Exception("Collection not found")
        mock_chroma.return_value = mock_client

        with pytest.raises(ValueError, match="Collection.*non trouvée"):
            RAGQuerySystem()


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestRAGQuerySystemQuery:
    """Tests de requête du système RAG."""

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    @patch('dyag.rag.core.retriever.LLMProviderFactory')
    def test_query_success(self, mock_llm_factory, mock_transformer, mock_chroma):
        """Test requête réussie."""
        # Setup mocks
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Document content"]],
            "metadatas": [[{"app": "test"}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1, 0.2, 0.3]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        mock_llm = MagicMock()
        mock_llm.chat_completion.return_value = {
            'content': "Réponse générée",
            'usage': {'total_tokens': 10, 'prompt_tokens': 5, 'completion_tokens': 5}
        }
        mock_llm.get_model_name.return_value = "test-model"
        mock_llm_factory.create_provider.return_value = mock_llm

        # Test
        rag = RAGQuerySystem()
        response = rag.ask("Test question")

        assert response is not None
        assert isinstance(response, dict)
        assert "answer" in response
        assert response["answer"] == "Réponse générée"
        mock_collection.query.assert_called_once()

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_query_with_app_filter(self, mock_transformer, mock_chroma):
        """Test requête avec filtre d'application."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "metadatas": [[{"app": "6Tzen"}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1, 0.2, 0.3]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem()
        rag.ask("Test", filter_metadata={"app": "6Tzen"})

        # Vérifier que le filtre est appliqué
        call_kwargs = mock_collection.query.call_args.kwargs
        assert "where" in call_kwargs
        assert call_kwargs["where"]["app"] == "6Tzen"

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_query_n_results(self, mock_transformer, mock_chroma):
        """Test requête avec nombre de résultats personnalisé."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["Doc1", "Doc2", "Doc3"]],
            "metadatas": [[{}, {}, {}]],
            "distances": [[0.1, 0.2, 0.3]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem()
        rag.ask("Test", n_chunks=10, use_reranking=False)

        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["n_results"] == 10

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_query_empty_results(self, mock_transformer, mock_chroma):
        """Test requête sans résultats."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem()
        response = rag.ask("Test")

        # Devrait gérer gracieusement l'absence de résultats
        assert response is not None


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestRAGQuerySystemReranking:
    """Tests du reranking avec CrossEncoder."""

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    @patch('dyag.rag.core.retriever.CrossEncoder')
    def test_reranking_enabled(self, mock_cross_encoder, mock_transformer, mock_chroma):
        """Test reranking activé."""
        # Setup mocks
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["Content1", "Content2"]],
            "metadatas": [[{}, {}]],
            "distances": [[0.1, 0.2]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        # Mock reranker
        mock_reranker = MagicMock()
        mock_reranker.predict.return_value = [0.9, 0.3]  # Scores inversés
        mock_cross_encoder.return_value = mock_reranker

        rag = RAGQuerySystem(rerank_model="test-reranker")
        rag.ask("Test", use_reranking=True)

        # Le reranker devrait être appelé
        mock_reranker.predict.assert_called_once()

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_reranking_disabled(self, mock_transformer, mock_chroma):
        """Test reranking désactivé."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "metadatas": [[{}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem(rerank_model=None)
        rag.ask("Test", use_reranking=False)

        # Devrait fonctionner sans reranking
        assert True  # Pas d'erreur


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestRAGQuerySystemFormatting:
    """Tests du formatage de réponse."""

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    @patch('dyag.rag.core.retriever.LLMProviderFactory')
    def test_response_includes_metadata(self, mock_llm_factory, mock_transformer, mock_chroma):
        """Test que la réponse inclut les métadonnées."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "metadatas": [[{"app": "6Tzen", "section": "intro"}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        mock_llm = MagicMock()
        mock_llm.chat_completion.return_value = {
            'content': "Response",
            'usage': {'total_tokens': 10, 'prompt_tokens': 5, 'completion_tokens': 5}
        }
        mock_llm.get_model_name.return_value = "test-model"
        mock_llm_factory.create_provider.return_value = mock_llm

        rag = RAGQuerySystem()
        response = rag.ask("Test")

        # Devrait retourner un dict avec métadonnées
        assert response is not None
        assert isinstance(response, dict)
        assert "sources" in response
        assert "chunks_used" in response
        assert "answer" in response

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_response_without_llm(self, mock_transformer, mock_chroma):
        """Test réponse sans génération LLM (juste retrieval)."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Retrieved content"]],
            "metadatas": [[{}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem()
        chunks = rag.search_chunks("Test", n_results=5)

        # Devrait retourner les chunks récupérés
        assert chunks is not None
        assert len(chunks) > 0


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestRAGQuerySystemEdgeCases:
    """Tests de cas limites."""

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    @patch('dyag.rag.core.retriever.LLMProviderFactory')
    def test_empty_query(self, mock_llm_factory, mock_transformer, mock_chroma):
        """Test requête vide."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = []
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        mock_llm = MagicMock()
        mock_llm.chat_completion.return_value = {"choices": [{"message": {"content": ""}}], "usage": {"total_tokens": 0}}
        mock_llm.get_model_name.return_value = "test-model"
        mock_llm_factory.create_provider.return_value = mock_llm

        rag = RAGQuerySystem()

        # Devrait gérer une requête vide gracieusement
        response = rag.ask("")
        assert response is not None
        assert isinstance(response, dict)

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_very_long_query(self, mock_transformer, mock_chroma):
        """Test requête très longue."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "metadatas": [[{}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem()

        long_query = "Quelle est " + "très " * 1000 + "longue question"
        # Devrait gérer sans crasher
        response = rag.ask(long_query)
        assert response is not None

    @patch('dyag.rag.core.retriever.chromadb.PersistentClient')
    @patch('dyag.rag.core.retriever.SentenceTransformer')
    def test_special_characters_query(self, mock_transformer, mock_chroma):
        """Test requête avec caractères spéciaux."""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["doc1"]],
            "documents": [["Content"]],
            "metadatas": [[{}]],
            "distances": [[0.1]]
        }
        mock_client.get_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        mock_embedder = MagicMock()
        mock_embedding = MagicMock()
        mock_embedding.tolist.return_value = [0.1]
        mock_embedder.encode.return_value = mock_embedding
        mock_transformer.return_value = mock_embedder

        rag = RAGQuerySystem()

        special_query = "Qu'est-ce que <test> & [brackets] {curly} ?"
        # Devrait gérer les caractères spéciaux
        response = rag.ask(special_query)
        assert response is not None
