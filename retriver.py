import numpy as np

from embedding_model import (
    load_embedding_model,
    generate_embeddings
)


def retrieve_relevant_chunks(
    query,
    chunks,
    model,
    top_k=3
):
    if not query.strip():
        raise ValueError("Query cannot be empty")

    if not chunks:
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    # Extract the text from each chunk.
    chunk_texts = [chunk["text"] for chunk in chunks]

    # Generate the query embedding.
    query_embedding = generate_embeddings(
        [query],
        model
    )[0]

    # Generate embeddings for the document chunks.
    chunk_embeddings = generate_embeddings(
        chunk_texts,
        model
    )

    # Calculate cosine similarity.
    similarities = chunk_embeddings @ query_embedding

    # Get the indices of the highest-scoring chunks.
    ranked_indices = np.argsort(similarities)[::-1]

    # Return the top-k results.
    results = []

    for index in ranked_indices[:top_k]:
        results.append({
            "text": chunks[index]["text"],
            "source": chunks[index]["source"],
            "score": float(similarities[index])
        })

    return results


if __name__ == "__main__":
    model = load_embedding_model()

    chunks = [
        {
            "text": "Python is a high-level programming language.",
            "source": "python.txt"
        },
        {
            "text": "Supervised learning uses labeled training data.",
            "source": "machine_learning.txt"
        },
        {
            "text": (
                "Classification predicts discrete categories, "
                "while regression predicts continuous numerical values."
            ),
            "source": "machine_learning.txt"
        }
    ]

    query = "How do machines learn from examples with known outputs?"

    results = retrieve_relevant_chunks(
        query=query,
        chunks=chunks,
        model=model,
        top_k=3
    )

    print("\nQuery:", query)

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Source: {result['source']}")
        print(f"Similarity: {result['score']:.4f}")
        print(f"Text: {result['text']}")