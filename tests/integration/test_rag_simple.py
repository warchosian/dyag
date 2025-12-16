"""Test simple du module create_rag avec le fichier Markdown."""

from src.dyag.commands.create_rag import create_rag_from_file
from pathlib import Path


def main():
    """Test simple."""
    print("=" * 70)
    print("Test simple du module create_rag")
    print("=" * 70)

    input_md = "examples/test-mygusi/applicationsIA_mini_opt.md"
    output_jsonl = "examples/test-mygusi/test_rag_output.jsonl"

    if not Path(input_md).exists():
        print(f"Erreur: Fichier {input_md} non trouve")
        return

    print(f"\nSource      : {input_md}")
    print(f"Destination : {output_jsonl}")
    print(f"Format      : JSONL")
    print(f"Chunk size  : 1500 caracteres\n")

    try:
        create_rag_from_file(
            input_file=input_md,
            output_file=output_jsonl,
            output_format='jsonl',
            max_chunk_size=1500
        )

        # Afficher quelques statistiques
        output_path = Path(output_jsonl)
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\nTaille du fichier genere: {size_mb:.2f} MB")

            # Compter les lignes
            with open(output_jsonl, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            print(f"Nombre de chunks: {line_count}")

            # Afficher le premier chunk
            print("\n" + "=" * 70)
            print("Premier chunk genere:")
            print("=" * 70)
            import json
            with open(output_jsonl, 'r', encoding='utf-8') as f:
                first_chunk = json.loads(f.readline())
                print(f"ID: {first_chunk['id']}")
                print(f"Type: {first_chunk['chunk_type']}")
                print(f"Titre: {first_chunk['title']}")
                print(f"Taille: {len(first_chunk['content'])} caracteres")
                print(f"\nContenu (100 premiers caracteres):")
                print(first_chunk['content'][:100] + "...")

        print("\n" + "=" * 70)
        print("Test termine avec succes!")
        print("=" * 70)

    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
