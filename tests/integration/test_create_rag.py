"""
Script de test pour le module create_rag.

Ce script teste la création de fichiers RAG à partir des exemples disponibles.
"""

from pathlib import Path
from src.dyag.commands.create_rag import RAGCreator, create_rag_from_file


def test_json_to_rag():
    """Test de conversion JSON vers RAG."""
    print("=" * 60)
    print("Test 1: Conversion JSON → RAG (JSONL)")
    print("=" * 60)

    input_file = Path("examples/test-mygusi/applicationsIA_mini_normalized.json")
    output_file = Path("examples/test-mygusi/applicationsIA_rag.jsonl")

    if not input_file.exists():
        print(f"✗ Fichier source non trouvé: {input_file}")
        return

    try:
        creator = RAGCreator(max_chunk_size=1500)
        chunk_count = creator.process_json_file(
            input_file,
            output_file,
            output_format='jsonl'
        )
        print(f"✓ {chunk_count} chunks créés")
        print(f"✓ Fichier généré: {output_file}")
        print(f"✓ Taille: {output_file.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_json_to_json():
    """Test de conversion JSON vers RAG JSON."""
    print("\n" + "=" * 60)
    print("Test 2: Conversion JSON → RAG (JSON)")
    print("=" * 60)

    input_file = Path("examples/test-mygusi/applicationsIA_mini_normalized.json")
    output_file = Path("examples/test-mygusi/applicationsIA_rag.json")

    if not input_file.exists():
        print(f"✗ Fichier source non trouvé: {input_file}")
        return

    try:
        creator = RAGCreator(max_chunk_size=1500)
        chunk_count = creator.process_json_file(
            input_file,
            output_file,
            output_format='json'
        )
        print(f"✓ {chunk_count} chunks créés")
        print(f"✓ Fichier généré: {output_file}")
        print(f"✓ Taille: {output_file.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_markdown_to_rag():
    """Test de conversion Markdown vers RAG."""
    print("\n" + "=" * 60)
    print("Test 3: Conversion Markdown → RAG (JSONL)")
    print("=" * 60)

    input_file = Path("examples/test-mygusi/applicationsIA_mini_opt.md")
    output_file = Path("examples/test-mygusi/applicationsIA_md_rag.jsonl")

    if not input_file.exists():
        print(f"✗ Fichier source non trouvé: {input_file}")
        return

    try:
        creator = RAGCreator(max_chunk_size=1500)
        chunk_count = creator.process_markdown_file(
            input_file,
            output_file,
            output_format='jsonl'
        )
        print(f"✓ {chunk_count} chunks créés")
        print(f"✓ Fichier généré: {output_file}")
        print(f"✓ Taille: {output_file.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_markdown_to_markdown():
    """Test de conversion Markdown vers RAG Markdown."""
    print("\n" + "=" * 60)
    print("Test 4: Conversion Markdown → RAG (Markdown)")
    print("=" * 60)

    input_file = Path("examples/test-mygusi/applicationsIA_mini_opt.md")
    output_file = Path("examples/test-mygusi/applicationsIA_rag.md")

    if not input_file.exists():
        print(f"✗ Fichier source non trouvé: {input_file}")
        return

    try:
        creator = RAGCreator(max_chunk_size=1500)
        chunk_count = creator.process_markdown_file(
            input_file,
            output_file,
            output_format='markdown'
        )
        print(f"✓ {chunk_count} chunks créés")
        print(f"✓ Fichier généré: {output_file}")
        print(f"✓ Taille: {output_file.stat().st_size / 1024:.2f} KB")

        # Afficher un exemple de chunk
        print("\n--- Exemple de chunk (premières lignes) ---")
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:30]
            print(''.join(lines))
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_utility_function():
    """Test de la fonction utilitaire."""
    print("\n" + "=" * 60)
    print("Test 5: Fonction utilitaire create_rag_from_file")
    print("=" * 60)

    input_file = "examples/test-mygusi/applicationsIA_mini_normalized.json"
    output_file = "examples/test-mygusi/applicationsIA_utility_rag.jsonl"

    if not Path(input_file).exists():
        print(f"✗ Fichier source non trouvé: {input_file}")
        return

    try:
        create_rag_from_file(
            input_file,
            output_file,
            output_format='jsonl',
            max_chunk_size=2000
        )
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def display_statistics():
    """Affiche des statistiques sur les fichiers générés."""
    print("\n" + "=" * 60)
    print("Statistiques des fichiers RAG générés")
    print("=" * 60)

    files = [
        "examples/test-mygusi/applicationsIA_rag.jsonl",
        "examples/test-mygusi/applicationsIA_rag.json",
        "examples/test-mygusi/applicationsIA_md_rag.jsonl",
        "examples/test-mygusi/applicationsIA_rag.md",
        "examples/test-mygusi/applicationsIA_utility_rag.jsonl",
    ]

    print(f"\n{'Fichier':<50} {'Taille':<15} {'Statut'}")
    print("-" * 75)

    for file_path in files:
        path = Path(file_path)
        if path.exists():
            size_kb = path.stat().st_size / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.2f} KB"
            else:
                size_str = f"{size_kb / 1024:.2f} MB"
            print(f"{path.name:<50} {size_str:<15} ✓")
        else:
            print(f"{path.name:<50} {'N/A':<15} ✗")


def main():
    """Fonction principale."""
    print("\n" + "=" * 60)
    print("Test du module create_rag")
    print("=" * 60 + "\n")

    # Exécuter tous les tests
    test_json_to_rag()
    test_json_to_json()
    test_markdown_to_rag()
    test_markdown_to_markdown()
    test_utility_function()

    # Afficher les statistiques
    display_statistics()

    print("\n" + "=" * 60)
    print("Tests terminés")
    print("=" * 60)


if __name__ == '__main__':
    main()
