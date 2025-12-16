"""
Script de test pour vérifier que les providers LLM fonctionnent correctement.

Usage:
    python test_llm_provider.py [openai|anthropic]
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dyag.llm_providers import LLMProviderFactory, test_provider


def main():
    """Test le provider LLM configuré."""

    # Déterminer quel provider tester
    provider_name = None
    if len(sys.argv) > 1:
        provider_name = sys.argv[1]

    print("\n" + "=" * 70)
    print("TEST DU PROVIDER LLM")
    print("=" * 70)

    if provider_name:
        print(f"\nTest du provider spécifié: {provider_name}")
    else:
        print("\nTest du provider auto-détecté depuis .env")

    try:
        test_provider(provider_name)

        print("\n" + "=" * 70)
        print("[OK] Tous les tests ont reussi!")
        print("=" * 70)
        print("\nVous pouvez maintenant utiliser le chat RAG:")
        print("  python scripts/chat.py")
        print("\n")

    except Exception as e:
        print("\n" + "=" * 70)
        print("[ERREUR] Erreur lors du test")
        print("=" * 70)
        print(f"\n{e}\n")

        print("Suggestions:")
        print("  1. Vérifiez que votre clé API est correcte dans .env")
        print("  2. Assurez-vous que LLM_PROVIDER est bien configuré")
        print("  3. Vérifiez votre connexion internet")
        print("\nFichier .env attendu:")
        print("  ANTHROPIC_API_KEY=sk-ant-votre-cle")
        print("  LLM_PROVIDER=anthropic")
        print("\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
