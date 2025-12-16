"""
Abstraction pour supporter plusieurs providers LLM (OpenAI, Anthropic, etc.).

Ce module permet d'utiliser différents fournisseurs LLM de manière uniforme.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
# Cherche le fichier .env à la racine du projet
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Sinon charge depuis le répertoire courant
    load_dotenv()


class LLMProvider(ABC):
    """
    Classe abstraite pour les providers LLM.

    Chaque provider doit implémenter la méthode chat_completion.
    """

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Génère une réponse de chat.

        Args:
            messages: Liste de messages [{"role": "system|user|assistant", "content": "..."}]
            temperature: Créativité (0=précis, 1=créatif)
            max_tokens: Longueur max de la réponse

        Returns:
            Dict avec: {
                'content': str,  # Réponse générée
                'usage': {       # Statistiques d'usage
                    'prompt_tokens': int,
                    'completion_tokens': int,
                    'total_tokens': int
                }
            }
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Retourne le nom du modèle utilisé."""
        pass


class OpenAIProvider(LLMProvider):
    """Provider pour OpenAI (GPT-4, GPT-4o-mini, etc.) et API compatibles (Scaleway, etc.)."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = None):
        """
        Initialise le provider OpenAI.

        Args:
            api_key: Clé API OpenAI (ou Scaleway, etc.)
            model: Nom du modèle (gpt-4o-mini, qwen3-235b-a22b-instruct-2507, etc.)
            base_url: URL de base pour l'API (optionnel, pour Scaleway par exemple)
        """
        from openai import OpenAI

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.model = model
        self.base_url = base_url

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict:
        """Génère une réponse via OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return {
            'content': response.choices[0].message.content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        }

    def get_model_name(self) -> str:
        """Retourne le nom du modèle."""
        return f"openai/{self.model}"


class OllamaProvider(LLMProvider):
    """Provider pour Ollama (modèles locaux gratuits : LLaMA, Mistral, etc.)."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434", timeout: int = None):
        """
        Initialise le provider Ollama.

        Args:
            model: Nom du modèle Ollama (llama3.2, mistral, codellama, etc.)
            base_url: URL de l'API Ollama (par défaut: http://localhost:11434)
            timeout: Timeout en secondes pour les requêtes (par défaut: 300s)
        """
        import requests
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout if timeout is not None else int(os.getenv('OLLAMA_TIMEOUT', '300'))
        self.requests = requests

        # Vérifier que Ollama est accessible
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError("Ollama n'est pas accessible")
        except Exception as e:
            raise ConnectionError(
                f"Impossible de se connecter à Ollama sur {base_url}. "
                f"Assurez-vous que Ollama est installé et en cours d'exécution. "
                f"Erreur: {e}"
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict:
        """Génère une réponse via Ollama."""
        # Ollama utilise une API compatible OpenAI
        # Construire le prompt à partir des messages
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")

        prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"

        try:
            # Appel à l'API Ollama
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=self.timeout
            )

            if response.status_code != 200:
                raise Exception(f"Erreur Ollama: {response.text}")

            result = response.json()

            # Ollama ne fournit pas toujours les tokens détaillés
            prompt_tokens = result.get('prompt_eval_count', 0)
            completion_tokens = result.get('eval_count', 0)

            return {
                'content': result['response'].strip(),
                'usage': {
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens
                }
            }

        except self.requests.exceptions.Timeout:
            raise TimeoutError(
                f"Le modele Ollama '{self.model}' a mis trop de temps a repondre (timeout: {self.timeout}s). "
                f"Solutions: "
                f"1) Augmentez le timeout (--timeout ou OLLAMA_TIMEOUT dans .env), "
                f"2) Utilisez un modele plus leger (llama3.2:1b), "
                f"3) Reduisez le nombre de chunks dans la question RAG, "
                f"4) Utilisez un provider cloud (OpenAI/Anthropic)"
            )
        except self.requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Impossible de se connecter a Ollama sur {self.base_url}. "
                f"Verifiez que Ollama est en cours d'execution: 'ollama serve'. "
                f"Erreur: {e}"
            )
        except Exception as e:
            # Pour toute autre erreur, propager avec contexte
            raise Exception(f"Erreur lors de l'appel a Ollama: {e}")

    def get_model_name(self) -> str:
        """Retourne le nom du modèle."""
        return f"ollama/{self.model}"


class AnthropicProvider(LLMProvider):
    """Provider pour Anthropic Claude (Claude 3.5 Sonnet, etc.)."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialise le provider Anthropic.

        Args:
            api_key: Clé API Anthropic
            model: Nom du modèle (claude-3-5-sonnet-20241022, claude-3-opus-20240229, etc.)
        """
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)
        self.model = model

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> Dict:
        """Génère une réponse via Anthropic Claude."""
        # Anthropic nécessite de séparer le system prompt
        system_message = None
        user_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                user_messages.append(msg)

        # Appel à l'API Anthropic
        kwargs = {
            'model': self.model,
            'messages': user_messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        if system_message:
            kwargs['system'] = system_message

        response = self.client.messages.create(**kwargs)

        return {
            'content': response.content[0].text,
            'usage': {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
        }

    def get_model_name(self) -> str:
        """Retourne le nom du modèle."""
        return f"anthropic/{self.model}"


class LLMProviderFactory:
    """
    Factory pour créer le bon provider selon la configuration.

    Supporte actuellement:
    - Ollama (llama3.2, mistral, codellama, etc.) - GRATUIT, local
    - OpenAI (gpt-4o-mini, gpt-4o, gpt-4-turbo, etc.)
    - Anthropic (claude-3-5-sonnet, claude-3-opus, etc.)
    """

    @staticmethod
    def create_provider(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> LLMProvider:
        """
        Crée un provider LLM.

        Args:
            provider: Nom du provider ('openai', 'anthropic', 'claude', 'ollama')
                     Si None, détecté automatiquement depuis les variables d'env
            model: Nom du modèle spécifique
                   Si None, utilise le modèle par défaut du provider
            api_key: Clé API
                    Si None, récupérée depuis les variables d'env
            timeout: Timeout en secondes (uniquement pour Ollama)
                    Si None, utilise OLLAMA_TIMEOUT depuis .env (défaut: 300s)

        Returns:
            Instance de LLMProvider

        Raises:
            ValueError: Si le provider n'est pas supporté ou si la clé API manque

        Examples:
            >>> # Auto-détection depuis variables d'env
            >>> provider = LLMProviderFactory.create_provider()

            >>> # Spécifier OpenAI
            >>> provider = LLMProviderFactory.create_provider('openai', 'gpt-4o-mini')

            >>> # Spécifier Claude
            >>> provider = LLMProviderFactory.create_provider('anthropic', 'claude-3-5-sonnet-20241022')

            >>> # Spécifier Ollama avec timeout custom
            >>> provider = LLMProviderFactory.create_provider('ollama', timeout=600)
        """
        # Auto-détection du provider si non spécifié
        if provider is None:
            # D'abord vérifier la variable LLM_PROVIDER
            provider = os.getenv('LLM_PROVIDER')

            # Sinon détecter automatiquement selon les clés API disponibles
            if provider is None:
                if os.getenv('ANTHROPIC_API_KEY'):
                    provider = 'anthropic'
                elif os.getenv('OPENAI_API_KEY'):
                    provider = 'openai'
                else:
                    # Par défaut, essayer Ollama (gratuit, local)
                    provider = 'ollama'

        # Normaliser le nom du provider
        provider = provider.lower()

        # Créer le provider approprié
        if provider == 'ollama':
            model = model or os.getenv('LLM_MODEL', 'llama3.2')
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            return OllamaProvider(model=model, base_url=base_url, timeout=timeout)

        elif provider == 'openai':
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "Clé API OpenAI requise. "
                    "Définissez OPENAI_API_KEY dans .env ou passez api_key"
                )

            model = model or os.getenv('LLM_MODEL', 'gpt-4o-mini')
            base_url = os.getenv('OPENAI_BASE_URL')  # Support pour Scaleway AI, etc.
            return OpenAIProvider(api_key=api_key, model=model, base_url=base_url)

        elif provider in ['anthropic', 'claude']:
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError(
                    "Clé API Anthropic requise. "
                    "Définissez ANTHROPIC_API_KEY dans .env ou passez api_key"
                )

            model = model or os.getenv('LLM_MODEL', 'claude-3-5-sonnet-20241022')
            return AnthropicProvider(api_key=api_key, model=model)

        else:
            raise ValueError(
                f"Provider '{provider}' non supporte. "
                f"Providers disponibles: ollama, openai, anthropic, claude"
            )

    @staticmethod
    def list_providers() -> Dict[str, List[str]]:
        """
        Liste les providers et modèles disponibles.

        Returns:
            Dict avec providers et leurs modèles
        """
        return {
            'ollama': [
                'llama3.2',         # Recommandé (gratuit, local, performant)
                'llama3.2:1b',      # Plus rapide, moins précis
                'llama3.1',         # Version précédente
                'mistral',          # Alternative performante
                'codellama',        # Spécialisé code
                'phi3',             # Petit et rapide
            ],
            'openai': [
                'gpt-4o-mini',      # Recommandé (rapide, économique)
                'gpt-4o',           # Plus performant
                'gpt-4-turbo',
                'gpt-4',
                'gpt-3.5-turbo'
            ],
            'anthropic': [
                'claude-3-5-sonnet-20241022',  # Recommandé (équilibré)
                'claude-3-opus-20240229',      # Plus performant
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307'      # Plus rapide
            ]
        }


# Helper pour tester les providers
def test_provider(provider_name: str = None):
    """
    Teste un provider avec une question simple.

    Args:
        provider_name: Nom du provider à tester (openai, anthropic)
                      Si None, teste celui qui est configuré
    """
    try:
        print(f"\n{'='*60}")
        print(f"Test du provider: {provider_name or 'auto-detecte'}")
        print(f"{'='*60}\n")

        # Créer le provider
        provider = LLMProviderFactory.create_provider(provider_name)
        print(f"[OK] Provider cree: {provider.get_model_name()}\n")

        # Question de test
        messages = [
            {"role": "system", "content": "Tu es un assistant utile et concis."},
            {"role": "user", "content": "Dis bonjour en une phrase courte."}
        ]

        print("Envoi de la question test...")
        result = provider.chat_completion(messages, temperature=0.7, max_tokens=50)

        print(f"\n{'='*60}")
        print("Réponse:")
        print(f"{'='*60}")
        print(result['content'])
        print(f"\n{'='*60}")
        print(f"Tokens: {result['usage']['total_tokens']} "
              f"(prompt: {result['usage']['prompt_tokens']}, "
              f"completion: {result['usage']['completion_tokens']})")
        print(f"{'='*60}\n")

        print("[OK] Test reussi!")

    except Exception as e:
        print(f"\n[ERREUR] {e}\n")
        raise


if __name__ == '__main__':
    """Test les providers disponibles."""
    import sys

    if len(sys.argv) > 1:
        # Test d'un provider spécifique
        test_provider(sys.argv[1])
    else:
        # Test auto
        print("Usage: python llm_providers.py [openai|anthropic]")
        print("\nOu testez le provider auto-détecté:")
        test_provider()
