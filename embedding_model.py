from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model():
    model = SentenceTransformer(MODEL_NAME)
    return model


def generate_embeddings(texts, model):
    if not texts:
        return []

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embeddings


if __name__ == "__main__":
    model = load_embedding_model()

    sample_texts = [
        "Supervised learning uses labeled training data.",
        "Python is a high-level programming language.",
        "How do machines learn from examples with known outputs?"
    ]

    embeddings = generate_embeddings(sample_texts, model)

    print("Number of texts:", len(sample_texts))
    print("Embedding matrix shape:", embeddings.shape)

    for text, embedding in zip(sample_texts, embeddings):
        print("\nText:", text)
        print("Vector dimensions:", len(embedding))
        print("First five values:", embedding[:5])