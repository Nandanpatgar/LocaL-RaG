
import hashlib
from pathlib import Path

from chunker import chunk_text
from embedding_model import load_embedding_model
from vector_store import create_vector_store, index_chunks


DOCUMENTS_DIR = Path("documents")

CHUNK_SIZE = 200
CHUNK_OVERLAP = 40
CHUNKING_VERSION = "v4"


def calculate_hash(text):
    """Calculate the SHA-256 hash of document content."""

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def load_documents():
    """Load all .txt files, including empty files for cleanup."""

    documents = []

    if not DOCUMENTS_DIR.exists():
        print(f"Documents directory not found: {DOCUMENTS_DIR}")
        return documents

    for file_path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        documents.append({
            "source": file_path.name,
            "text": text,
            "document_hash": calculate_hash(text)
        })

    return documents


def prepare_chunks(document):
    """Split a document and attach indexing metadata."""

    text_chunks = chunk_text(
        document["text"],
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP
    )

    chunks = []

    for chunk_index, text in enumerate(text_chunks):
        chunks.append({
            "text": text,
            "source": document["source"],
            "document_hash": document["document_hash"],
            "chunk_index": chunk_index,
            "chunking_version": CHUNKING_VERSION
        })

    return chunks


def get_indexed_metadata(collection):
    """
    Return stored metadata grouped by source filename.

    Example:
        {
            "python.txt": [
                {
                    "document_hash": "...",
                    "chunking_version": "v2"
                }
            ]
        }
    """

    indexed_metadata = {}

    records = collection.get(
        include=["metadatas"]
    )

    for metadata in records["metadatas"]:
        if not metadata:
            continue

        source = metadata.get("source")

        if source:
            indexed_metadata.setdefault(
                source, []
            ).append(metadata)

    return indexed_metadata


def remove_document_chunks(collection, source):
    """Remove all chunks associated with a source document."""

    existing = collection.get(
        where={"source": source},
        include=["metadatas"]
    )

    if existing["ids"]:
        collection.delete(
            ids=existing["ids"]
        )

        return len(existing["ids"])

    return 0


def index_documents():
    print("=" * 55)
    print("              LocalRAG Indexer")
    print("=" * 55)

    if not DOCUMENTS_DIR.exists():
        print(f"\nCreate the folder: {DOCUMENTS_DIR}")
        return

    documents = load_documents()

    print(f"\nDocuments discovered: {len(documents)}")

    client, collection = create_vector_store()

    indexed_metadata = get_indexed_metadata(collection)

    current_sources = {
        document["source"]
        for document in documents
    }

    # Remove documents that no longer exist in the folder.
    for old_source in indexed_metadata:
        if old_source not in current_sources:
            print(f"Deleted document detected: {old_source}")

            remove_document_chunks(
                collection,
                old_source
            )

    documents_to_index = []

    for document in documents:
        source = document["source"]
        current_hash = document["document_hash"]

        existing_records = indexed_metadata.get(
            source, []
        )

        # An empty document must not retain old chunks.
        if not document["text"]:
            if existing_records:
                print(f"Empty document detected: {source}")

                remove_document_chunks(
                    collection,
                    source
                )
            else:
                print(f"Skipping empty document: {source}")

            continue

        # Skip only when all stored chunks match the current
        # content hash and chunking version.
        unchanged = (
            bool(existing_records)
            and all(
                metadata.get("document_hash") == current_hash
                and metadata.get("chunking_version")
                == CHUNKING_VERSION
                for metadata in existing_records
            )
        )

        if unchanged:
            print(f"Unchanged; skipping: {source}")
            continue

        print(f"New or modified document: {source}")

        # Remove previous versions before inserting the new one.
        remove_document_chunks(
            collection,
            source
        )

        documents_to_index.append(document)

    if not documents_to_index:
        print("\nNo documents require indexing.")
        print(f"Total records: {collection.count()}")
        return

    print("\nLoading embedding model...")
    model = load_embedding_model()

    total_chunks = 0

    for document in documents_to_index:
        chunks = prepare_chunks(document)

        if not chunks:
            continue

        indexed_count = index_chunks(
            collection,
            chunks,
            model
        )

        total_chunks += indexed_count

    print("\n" + "=" * 55)
    print("             INDEXING COMPLETE")
    print("=" * 55)

    print(f"Documents processed: {len(documents_to_index)}")
    print(f"Chunks indexed: {total_chunks}")
    print(f"Total records in ChromaDB: {collection.count()}")


if __name__ == "__main__":
    index_documents()

