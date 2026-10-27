
import re


def split_sentences(text):
    """Normalize whitespace and split text into sentences."""
    text = re.sub(r"\s+", " ", text.strip())

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def split_long_sentence(sentence, chunk_size):
    """Split long sentences into pieces without breaking normal words."""
    words = sentence.split()
    pieces = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                pieces.append(current)

            if len(word) > chunk_size:
                # Split only exceptionally long individual tokens.
                for start in range(0, len(word), chunk_size):
                    pieces.append(word[start:start + chunk_size])
                current = ""
            else:
                current = word

    if current:
        pieces.append(current)

    return pieces


def get_overlap_text(text, overlap):
    """
    Return a suffix of at most `overlap` characters.

    Prefer starting at a word boundary to avoid partial words.
    """
    text = text.strip()

    if not text or overlap <= 0:
        return ""

    if len(text) <= overlap:
        return text

    suffix = text[-overlap:]

    # Find the first complete word in the suffix.
    first_space = suffix.find(" ")

    if first_space == -1:
        return ""

    return suffix[first_space + 1:].strip()


def chunk_text(text, chunk_size=200, overlap=40):
    """
    Split text into sentence-aware chunks with approximate overlap.

    Args:
        text: Input document.
        chunk_size: Maximum number of characters per chunk.
        overlap: Approximate maximum overlap in characters.

    Returns:
        A list of text chunks.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    sentences = split_sentences(text)

    if not sentences:
        return []

    # Split sentences that exceed the configured chunk size.
    segments = []

    for sentence in sentences:
        if len(sentence) > chunk_size:
            segments.extend(split_long_sentence(sentence, chunk_size))
        else:
            segments.append(sentence)

    chunks = []
    current = ""

    for segment in segments:
        if not current:
            current = segment
            continue

        candidate = f"{current} {segment}"

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        # Store the current chunk before starting another.
        chunks.append(current)

        # Reuse a short suffix from the previous chunk.
        overlap_text = get_overlap_text(current, overlap)

        if overlap_text:
            candidate = f"{overlap_text} {segment}"
        else:
            candidate = segment

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            current = segment

    if current:
        chunks.append(current)

    return chunks


if __name__ == "__main__":
    sample_text = (
        "A Database Management System (DBMS) is software used to create, "
        "manage, store, and retrieve data. "
        "Database normalization organizes tables to reduce redundancy "
        "and prevent insertion, update, and deletion anomalies. "
        "The ACID properties of database transactions are Atomicity, "
        "Consistency, Isolation, and Durability. "
        "A primary key uniquely identifies each record in a table. "
        "A foreign key establishes a relationship between tables."
    )

    chunk_size = 200
    overlap = 40

    chunks = chunk_text(
        sample_text,
        chunk_size=chunk_size,
        overlap=overlap
    )

    print("=" * 55)
    print("CHUNKER DIAGNOSTIC")
    print("=" * 55)
    print(f"Chunk size: {chunk_size}")
    print(f"Overlap: {overlap}")
    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {index} ({len(chunk)} characters):")
        print(chunk)

    assert all(len(chunk) <= chunk_size for chunk in chunks), (
        "A chunk exceeds the configured size."
    )

    assert all(chunk == chunk.strip() for chunk in chunks), (
        "A chunk contains leading or trailing whitespace."
    )

    assert all(
        re.search(r"\w\s+\w", chunk) or len(chunk.split()) <= 1
        for chunk in chunks
    ), "A possible missing space between words was detected."

    print("\nPASS: Chunk size and whitespace checks passed.")

