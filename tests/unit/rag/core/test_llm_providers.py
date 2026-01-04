"""
Tests unitaires pour dyag.rag.core.llm_providers

Tests exhaustifs de la factory de providers LLM (Ollama, OpenAI, Anthropic, Claude).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dyag.rag.core.llm_providers import LLMProviderFactory


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestLLMProviderFactory:
    """Tests de la factory de providers LLM."""

    def test_factory_singleton(self):
        """Vérifie que la factory est un singleton."""
        factory1 = LLMProviderFactory
        factory2 = LLMProviderFactory
        assert factory1 is factory2

    @patch.dict('os.environ', {
        'OLLAMA_BASE_URL': 'http://localhost:11434',
        'OLLAMA_MODEL': 'llama2',
        'OLLAMA_TIMEOUT': '300'
    })
    @patch('requests.get')
    @patch('requests.post')
    def test_create_ollama_provider(self, mock_post, mock_get):
        """Test création d'un provider Ollama."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        # Mock de la réponse Ollama
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Test response",
            "done": True
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        provider = LLMProviderFactory.create_provider(
            provider="ollama",
            model="llama2"
        )

        assert provider is not None
        assert provider.provider_name == "ollama"
        assert provider.model == "llama2"

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123'})
    @patch('openai.OpenAI')
    def test_create_openai_provider(self, mock_openai_class):
        """Test création d'un provider OpenAI."""
        # Mock du client OpenAI
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test-key-123"
        )

        assert provider is not None
        assert provider.provider_name == "openai"
        assert provider.model == "gpt-3.5-turbo"
        # Vérifier que OpenAI a été appelé avec la bonne clé API
        mock_openai_class.assert_called_once()
        call_kwargs = mock_openai_class.call_args.kwargs
        assert call_kwargs['api_key'] == "test-key-123"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-anthropic-key'})
    @patch('anthropic.Anthropic')
    def test_create_anthropic_provider(self, mock_anthropic_class):
        """Test création d'un provider Anthropic."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            provider="anthropic",
            model="claude-3-sonnet",
            api_key="test-anthropic-key"
        )

        assert provider is not None
        assert provider.provider_name == "anthropic"
        assert provider.model == "claude-3-sonnet"

    def test_create_invalid_provider(self):
        """Test échec avec un provider invalide."""
        with pytest.raises(ValueError, match="Provider 'invalid' non supporte"):
            LLMProviderFactory.create_provider(
                provider="invalid",
                model="test"
            )

    @patch.dict('os.environ', {}, clear=True)
    @patch('requests.get')
    def test_auto_detect_provider_no_env(self, mock_get):
        """Test auto-détection sans variables d'environnement."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        # Devrait retourner Ollama par défaut
        provider = LLMProviderFactory.create_provider()
        assert provider.provider_name == "ollama"

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'key123'}, clear=True)
    @patch('openai.OpenAI')
    def test_auto_detect_openai(self, mock_openai_class):
        """Test auto-détection avec OPENAI_API_KEY."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider()
        assert provider.provider_name == "openai"

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'key456'}, clear=True)
    @patch('anthropic.Anthropic')
    def test_auto_detect_anthropic(self, mock_anthropic_class):
        """Test auto-détection avec ANTHROPIC_API_KEY."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider()
        assert provider.provider_name == "anthropic"


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
@pytest.mark.llm
class TestOllamaProvider:
    """Tests du provider Ollama."""

    @patch('requests.get')
    @patch('requests.post')
    def test_generate_success(self, mock_post, mock_get):
        """Test génération réussie avec Ollama."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Réponse générée",
            "done": True
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        provider = LLMProviderFactory.create_provider("ollama", "llama2")
        response = provider.generate("Test prompt")

        assert response == "Réponse générée"
        mock_post.assert_called_once()

    @patch('requests.get')
    @patch('requests.post')
    def test_generate_with_context(self, mock_post, mock_get):
        """Test génération avec contexte."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Réponse avec contexte",
            "done": True
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        provider = LLMProviderFactory.create_provider("ollama", "llama2")
        context = "Contexte important"
        response = provider.generate("Question", context=context)

        assert response == "Réponse avec contexte"
        # Vérifier que le contexte est inclus dans le prompt
        call_args = mock_post.call_args
        assert context in str(call_args)

    @patch('requests.get')
    @patch('requests.post')
    def test_generate_timeout(self, mock_post, mock_get):
        """Test timeout lors de la génération."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        import requests
        mock_post.side_effect = requests.Timeout("Connection timeout")

        provider = LLMProviderFactory.create_provider("ollama", "llama2")

        with pytest.raises(Exception, match="timeout|Timeout"):
            provider.generate("Test")

    @patch('requests.get')
    @patch('requests.post')
    def test_is_available_success(self, mock_post, mock_get):
        """Test vérification de disponibilité (succès)."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        provider = LLMProviderFactory.create_provider("ollama", "llama2")
        assert provider.is_available() is True

    @patch('requests.get')
    @patch('requests.post')
    def test_is_available_failure(self, mock_post, mock_get):
        """Test vérification de disponibilité (échec)."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        import requests
        mock_post.side_effect = requests.RequestException("Connection failed")

        provider = LLMProviderFactory.create_provider("ollama", "llama2")
        assert provider.is_available() is False


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
@pytest.mark.llm
class TestOpenAIProvider:
    """Tests du provider OpenAI."""

    @patch('openai.OpenAI')
    def test_generate_success(self, mock_openai_class):
        """Test génération réussie avec OpenAI."""
        # Mock de la réponse OpenAI
        mock_client = MagicMock()
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message=Mock(content="Réponse OpenAI"))
        ]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            "openai",
            "gpt-3.5-turbo",
            api_key="test-key"
        )
        response = provider.generate("Test question")

        assert response == "Réponse OpenAI"
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_generate_with_temperature(self, mock_openai_class):
        """Test génération avec paramètre temperature."""
        mock_client = MagicMock()
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            "openai",
            "gpt-4",
            api_key="test-key"
        )
        provider.generate("Test", temperature=0.7)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs.get('temperature') == 0.7

    @patch('openai.OpenAI')
    def test_api_error_handling(self, mock_openai_class):
        """Test gestion des erreurs API."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            "openai",
            "gpt-3.5-turbo",
            api_key="test-key"
        )

        with pytest.raises(Exception, match="API Error"):
            provider.generate("Test")


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
@pytest.mark.llm
class TestAnthropicProvider:
    """Tests du provider Anthropic."""

    @patch('anthropic.Anthropic')
    def test_generate_success(self, mock_anthropic_class):
        """Test génération réussie avec Anthropic."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.content = [Mock(text="Réponse Claude")]
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 20
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            "anthropic",
            "claude-3-sonnet",
            api_key="test-key"
        )
        response = provider.generate("Test question")

        assert response == "Réponse Claude"

    @patch('anthropic.Anthropic')
    def test_generate_with_max_tokens(self, mock_anthropic_class):
        """Test génération avec max_tokens."""
        mock_client = MagicMock()
        mock_message = Mock()
        mock_message.content = [Mock(text="Response")]
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 20
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        provider = LLMProviderFactory.create_provider(
            "anthropic",
            "claude-3-opus",
            api_key="test-key"
        )
        provider.generate("Test", max_tokens=2000)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs.get('max_tokens') == 2000


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.rag
class TestProviderComparison:
    """Tests comparatifs entre providers."""

    @patch('openai.OpenAI')
    @patch('requests.post')
    @patch('requests.get')
    def test_all_providers_same_interface(self, mock_get, mock_post, mock_openai_class):
        """Vérifie que tous les providers ont la même interface."""
        # Mock de la vérification de connexion Ollama
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        # Setup mocks Ollama
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"response": "ollama", "done": True}
        mock_post.return_value = mock_post_response

        # Setup mocks OpenAI
        mock_openai_client = MagicMock()
        mock_openai_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="openai"))]
        )
        mock_openai_class.return_value = mock_openai_client

        ollama = LLMProviderFactory.create_provider("ollama")
        openai = LLMProviderFactory.create_provider("openai", api_key="key")

        # Vérifier les méthodes communes
        assert hasattr(ollama, 'generate')
        assert hasattr(openai, 'generate')
        assert hasattr(ollama, 'is_available')
        assert hasattr(openai, 'is_available')

        # Vérifier que generate() fonctionne
        assert ollama.generate("test") == "ollama"
        assert openai.generate("test") == "openai"
