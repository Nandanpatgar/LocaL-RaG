
import chromadb

from embedding_model import (
    load_embedding_model,
    generate_embeddings
)


COLLECTION_NAME = "localrag_documents"


def create_vector_store():
    """Connect to the persistent ChromaDB collection."""

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return client, collection


def index_chunks(collection, chunks, model):
    """Generate embeddings and store document chunks."""

    if not chunks:
        print("No chunks available for indexing.")
        return 0

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        source = chunk["source"]
        text = chunk["text"]
        document_hash = chunk["document_hash"]
        chunk_index = chunk["chunk_index"]
        chunking_version = chunk["chunking_version"]

        chunk_id = (
            f"{source}_{document_hash[:12]}_"
            f"{chunking_version}_{chunk_index}"
        )

        ids.append(chunk_id)
        documents.append(text)

        metadatas.append({
            "source": source,
            "document_hash": document_hash,
            "chunk_index": chunk_index,
            "chunking_version": chunking_version
        })

    embeddings = generate_embeddings(
        documents,
        model
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    print(f"Chunks indexed: {len(ids)}")

    return len(ids)


def search_chunks(
    collection,
    query,
    model,
    top_k=3,
    max_cosine_distance=1.0
):
    """
    Retrieve chunks using semantic similarity.

    A distance threshold of 1.0 is used by default for
    diagnostic testing. Lower cosine distances indicate
    greater similarity.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    if max_cosine_distance < 0:
        raise ValueError(
            "Cosine distance threshold cannot be negative."
        )

    total_records = collection.count()

    if total_records == 0:
        return []

    query_embedding = generate_embeddings(
        [query],
        model
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=min(top_k, total_records),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    if not results["ids"] or not results["ids"][0]:
        return retrieved_chunks

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]
        distance = float(results["distances"][0][index])

        # Apply the configurable distance threshold.
        if distance > max_cosine_distance:
            continue

        retrieved_chunks.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "document_hash": metadata.get("document_hash", ""),
            "chunk_index": metadata.get("chunk_index", -1),
            "chunking_version": metadata.get(
                "chunking_version", "unknown"
            ),
            "distance": distance
        })

    return retrieved_chunks


if __name__ == "__main__":
    print("=" * 50)
    print("       LocalRAG Retrieval Diagnostic")
    print("=" * 50)

    print("\nLoading embedding model...")
    model = load_embedding_model()

    client, collection = create_vector_store()

    print("\nChromaDB connection successful.")
    print("Collection:", collection.name)
    print("Existing records:", collection.count())

    query = input(
        "\nEnter a retrieval test question: "
    ).strip()

    if not query:
        print("Please enter a question.")
    else:
        results = search_chunks(
            collection=collection,
            query=query,
            model=model,
            top_k=3,
            max_cosine_distance=1.0
        )

        if not results:
            print("\nNo results found.")
        else:
            print("\nRaw retrieval results:")

            for rank, result in enumerate(results, start=1):
                print(f"\nRank: {rank}")
                print(f"Source: {result['source']}")
                print(
                    f"Cosine distance: "
                    f"{result['distance']:.4f}"
                )
                print(f"Text: {result['text']}")

    print("\nDiagnostic complete.")

