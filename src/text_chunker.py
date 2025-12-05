"""
Text Chunking Module

This module handles splitting long text (like video transcripts) into smaller,
manageable chunks for embedding and vector storage in a RAG system.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List


def chunk_transcript(transcript: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split a transcript into overlapping chunks for embedding and retrieval.

    This function uses LangChain's RecursiveCharacterTextSplitter, which attempts
    to keep semantically related text together by splitting on natural boundaries
    (paragraphs, sentences, words) rather than arbitrary character positions.

    Why we use overlapping chunks:
    -------------------------------
    Overlap between chunks is crucial for RAG systems because:

    1. **Preserves Context at Boundaries**: Without overlap, important context that
       spans chunk boundaries could be lost. For example, if a sentence is split
       across two chunks, neither chunk alone provides complete information.

    2. **Improves Retrieval Accuracy**: When a user's query relates to content near
       a chunk boundary, the overlap ensures that relevant information appears in
       multiple chunks, increasing the chances of retrieving the right context.

    3. **Handles Multi-Sentence Concepts**: Many concepts require multiple sentences
       to fully explain. Overlap helps ensure that these explanations remain intact
       in at least one chunk.

    Example with overlap:
    Chunk 1: "...explaining machine learning. Machine learning is a subset of AI..."
    Chunk 2: "Machine learning is a subset of AI that focuses on..."
                ^^^^ This overlap ensures the concept isn't fragmented ^^^^

    What happens if chunks are too large:
    -------------------------------------
    - **Embedding Quality Degrades**: Embedding models have optimal input lengths.
      Very long texts get compressed into a fixed-size vector, losing nuance.

    - **Retrieval Becomes Less Precise**: Large chunks contain many different topics,
      making it harder to match specific queries. You might retrieve a 5000-character
      chunk when only 200 characters are actually relevant.

    - **Context Window Issues**: When passing retrieved chunks to an LLM, you consume
      more of its context window, limiting how many chunks you can include.

    - **Slower Processing**: Larger chunks take longer to embed and process.

    What happens if chunks are too small:
    -------------------------------------
    - **Context Loss**: Chunks might be too short to be meaningful. A 100-character
      chunk might not contain enough context to understand what it's discussing.

    - **Fragmented Information**: Related sentences get separated, making it hard
      for the system to retrieve complete answers.

    - **Increased Storage & Computation**: More chunks means more embeddings to store
      and more similarity comparisons during retrieval.

    - **Redundancy**: With small chunks and significant overlap, you end up with
      many nearly-identical chunks, wasting storage and reducing retrieval quality.

    Optimal chunk size (1000 characters, ~200 words):
    -------------------------------------------------
    - Balances context preservation with retrieval precision
    - Fits well within embedding model token limits
    - Typically contains 2-4 complete ideas or concepts
    - Works well for most conversational AI applications

    How RecursiveCharacterTextSplitter works:
    -----------------------------------------
    Unlike simple character splitting, it tries to split on:
    1. Double newlines (paragraph breaks) - most semantic boundary
    2. Single newlines
    3. Spaces (sentence/word boundaries)
    4. Characters (last resort)

    This hierarchy ensures chunks break at natural boundaries whenever possible.

    Args:
        transcript (str): The full transcript text to split
        chunk_size (int): Target size for each chunk in characters (default: 1000)
        chunk_overlap (int): Number of overlapping characters between chunks (default: 200)

    Returns:
        List[str]: List of text chunks, each approximately chunk_size characters

    Example:
        >>> transcript = "This is a long video transcript..."
        >>> chunks = chunk_transcript(transcript)
        >>> print(f"Created {len(chunks)} chunks")
        >>> print(f"First chunk: {chunks[0][:100]}...")
    """

    # Validate inputs
    if not transcript or not transcript.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
        )

    # Create the text splitter with our configuration
    # RecursiveCharacterTextSplitter will attempt to split on natural boundaries
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,  # Use character count (can also use token count)
        separators=["\n\n", "\n", ". ", " ", ""],  # Priority order for splitting
        is_separator_regex=False,  # Treat separators as literal strings
    )

    # Split the text into chunks
    chunks = text_splitter.split_text(transcript)

    return chunks


def chunk_transcript_with_metadata(
    transcript: str,
    video_url: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[dict]:
    """
    Split transcript into chunks and attach metadata to each chunk.

    This is useful for RAG systems where you want to track which chunks
    came from which video, enabling source attribution in responses.

    Args:
        transcript (str): The full transcript text to split
        video_url (str): The YouTube URL for source attribution
        chunk_size (int): Target size for each chunk in characters (default: 1000)
        chunk_overlap (int): Number of overlapping characters between chunks (default: 200)

    Returns:
        List[dict]: List of dictionaries with 'text', 'video_url', and 'chunk_index'

    Example:
        >>> chunks = chunk_transcript_with_metadata(transcript, "https://youtube.com/watch?v=123")
        >>> print(chunks[0])
        {
            'text': 'This is the first chunk...',
            'video_url': 'https://youtube.com/watch?v=123',
            'chunk_index': 0
        }
    """

    # Get the text chunks
    text_chunks = chunk_transcript(transcript, chunk_size, chunk_overlap)

    # Attach metadata to each chunk
    chunks_with_metadata = [
        {
            "text": chunk,
            "video_url": video_url,
            "chunk_index": idx,
        }
        for idx, chunk in enumerate(text_chunks)
    ]

    return chunks_with_metadata


if __name__ == "__main__":
    # Example usage and testing
    sample_transcript = """
    Welcome to this tutorial on machine learning. Machine learning is a subset of artificial
    intelligence that focuses on building systems that learn from data. In this video, we'll
    explore the fundamentals of machine learning and how it works.

    First, let's understand what machine learning really means. Traditional programming involves
    writing explicit rules for a computer to follow. Machine learning, on the other hand,
    allows computers to learn patterns from data without being explicitly programmed.

    There are three main types of machine learning: supervised learning, unsupervised learning,
    and reinforcement learning. Supervised learning uses labeled data to train models. The model
    learns to map inputs to outputs based on example input-output pairs.

    Unsupervised learning works with unlabeled data. The algorithm tries to find hidden patterns
    or structures in the data without any predefined labels. Common techniques include clustering
    and dimensionality reduction.

    Reinforcement learning is about training agents to make sequences of decisions. The agent
    learns by interacting with an environment and receiving rewards or penalties based on its
    actions. This is commonly used in game playing and robotics.
    """

    print("Testing text chunking...")
    print("=" * 70)

    chunks = chunk_transcript(sample_transcript, chunk_size=300, chunk_overlap=50)

    print(f"Original transcript length: {len(sample_transcript)} characters")
    print(f"Number of chunks created: {len(chunks)}")
    print(f"Chunk size target: 300 characters")
    print(f"Overlap: 50 characters\n")

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1} ({len(chunk)} chars):")
        print("-" * 70)
        print(chunk.strip())
        print()

    # Test metadata version
    print("\n" + "=" * 70)
    print("Testing chunking with metadata...")
    print("=" * 70 + "\n")

    chunks_with_meta = chunk_transcript_with_metadata(
        sample_transcript,
        "https://youtube.com/watch?v=example123",
        chunk_size=300,
        chunk_overlap=50
    )

    for chunk_data in chunks_with_meta[:2]:  # Show first 2
        print(f"Chunk Index: {chunk_data['chunk_index']}")
        print(f"Video URL: {chunk_data['video_url']}")
        print(f"Text Length: {len(chunk_data['text'])} chars")
        print(f"Text Preview: {chunk_data['text'][:100]}...")
        print()
