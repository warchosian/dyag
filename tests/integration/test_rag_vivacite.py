"""Test RAG pour la question sur Vivacité."""

import sys
import io

# Fixer l'encodage UTF-8 pour Windows (seulement si exécuté comme script principal)
if sys.platform == 'win32' and __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import chromadb
from chromadb.config import Settings

def test_rag_vivacite():
    """Teste le RAG avec la question sur Vivacité."""

    print("=" * 70)
    print("TEST RAG - Vivacité")
    print("=" * 70)

    # Charger ChromaDB
    client = chromadb.PersistentClient(
        path="chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )

    # Récupérer la collection
    collection = client.get_collection("applications")

    print(f"\n✓ Collection chargée: {collection.count()} documents\n")

    # Query sur Vivacité
    query = "Quelles technologies utilise Vivacité ?"

    print(f"Question: {query}\n")
    print("-" * 70)

    # Chercher les documents pertinents
    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    print("\n📚 Documents trouvés:\n")

    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"\n{i}. Chunk ID: {metadata.get('id', 'N/A')}")
        print(f"   Source: {metadata.get('source_id', 'N/A')}")
        print(f"   Distance: {distance:.4f}")
        print(f"   Contenu: {doc[:300]}...")
        print("-" * 70)

    # Réponse basée sur le contexte
    print("\n✅ RÉPONSE RAG (basée sur les chunks trouvés):\n")

    # Analyser les chunks pour trouver les technologies
    for doc in results['documents'][0]:
        if 'Vivacité' in doc or 'VIV@CITÉ' in doc:
            if 'Technologie' in doc or 'technologie' in doc:
                # Extraire les lignes pertinentes
                lines = doc.split('\n')
                for line in lines:
                    if 'technolog' in line.lower():
                        print(f"  {line.strip()}")
                break

if __name__ == '__main__':
    test_rag_vivacite()
