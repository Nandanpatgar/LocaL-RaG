
from embedding_model import load_embedding_model
from vector_store import create_vector_store, search_chunks
from llm import generate_answer


TOP_K = 3
MAX_COSINE_DISTANCE = 0.70


def main():
    print("=" * 50)
    print("          LocalRAG Document Assistant")
    print("=" * 50)

    print("\nLoading embedding model...")
    model = load_embedding_model()

    print("\nConnecting to ChromaDB...")
    client, collection = create_vector_store()

    total_records = collection.count()

    if total_records == 0:
        print("\nYour document index is empty.")
        print("Run 'python indexer.py' before asking questions.")
        return

    print(f"Indexed chunks available: {total_records}")
    print("\nReady! Ask questions about your documents.")

    while True:
        question = input(
            "\nAsk a question (or type 'exit' to quit): "
        ).strip()

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            print("\nSearching indexed documents...")

            retrieved_chunks = search_chunks(
                collection=collection,
                query=question,
                model=model,
                top_k=TOP_K,
                max_cosine_distance=MAX_COSINE_DISTANCE
            )

            if not retrieved_chunks:
                print(
                    "\nI couldn't find sufficiently relevant "
                    "information in your indexed documents "
                    "to answer that question."
                )
                continue

            print(
                f"Relevant chunks retrieved: "
                f"{len(retrieved_chunks)}"
            )

            print("Generating answer with Llama 3.2...")

            answer = generate_answer(
                question,
                retrieved_chunks
            )

            print("\n" + "=" * 50)
            print("ANSWER")
            print("=" * 50)
            print(answer)

            print("\nSOURCES")
            print("-" * 50)

            displayed_sources = set()

            for chunk in retrieved_chunks:
                source = chunk["source"]

                if source not in displayed_sources:
                    print(f"- {source}")
                    displayed_sources.add(source)

            print("\nRETRIEVAL DETAILS")
            print("-" * 50)

            for chunk in retrieved_chunks:
                print(
                    f"Source: {chunk['source']} | "
                    f"Cosine distance: {chunk['distance']:.4f}"
                )

            print("=" * 50)

        except Exception as error:
            print(f"\nAn error occurred: {error}")


if __name__ == "__main__":
    main()

