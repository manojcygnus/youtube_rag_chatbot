"""
Test Script for Embedding Manager

This script demonstrates the embedding manager functionality with sample data.
It can work in two modes:
1. Real mode: Uses actual Voyage AI API for embeddings (requires API key)
2. Mock mode: Uses random vectors to test ChromaDB storage/retrieval logic

This allows you to test the database functionality even without API keys.
"""

import sys
import numpy as np
from typing import List
from src.embedding_manager import EmbeddingManager
from src.config import VOYAGE_API_KEY


class MockEmbeddingManager(EmbeddingManager):
    """
    Mock version of EmbeddingManager for testing without API keys.

    This class overrides the embedding creation to use random vectors instead
    of calling the Voyage AI API. This is useful for:
    - Testing ChromaDB storage and retrieval logic
    - Development without API keys
    - Faster testing (no API calls)

    Note: Mock embeddings won't have semantic meaning, so search results
    will be essentially random. But it tests the infrastructure!
    """

    def __init__(self, embedding_dimension: int = 1024):
        """
        Initialize mock embedding manager.

        Args:
            embedding_dimension: Size of embedding vectors (default: 1024, same as voyage-3)
        """
        self.embedding_dimension = embedding_dimension
        self.chroma_client = None
        self.collection = None
        self.collection_name = "youtube_transcripts"
        self.persist_directory = "./chroma_db"

        # We don't initialize Voyage client since we're mocking
        print("⚠️  Using MOCK embeddings (random vectors)")
        print(f"   Embedding dimension: {embedding_dimension}")

    def _create_mock_embedding(self, text: str) -> List[float]:
        """
        Create a mock embedding vector for text.

        Uses a simple hash of the text to seed a random number generator,
        ensuring the same text always gets the same embedding (deterministic).
        This maintains some consistency for testing.
        """
        # Use text hash as seed for reproducibility
        seed = abs(hash(text)) % (2**32)
        rng = np.random.RandomState(seed)

        # Generate random vector and normalize it (unit length)
        # Normalization is important for cosine similarity
        vector = rng.randn(self.embedding_dimension)
        vector = vector / np.linalg.norm(vector)

        return vector.tolist()

    def add_video_chunks(
        self,
        video_id: str,
        video_url: str,
        chunks: List[str],
        video_title: str = None
    ) -> int:
        """
        Add video chunks using mock embeddings.
        """
        if self.collection is None:
            raise ValueError("ChromaDB not initialized. Call initialize_chromadb() first.")

        if not chunks:
            print("⚠️  No chunks provided, nothing to add")
            return 0

        print(f"\nProcessing video: {video_id}")
        print(f"Number of chunks: {len(chunks)}")

        # Check for duplicates
        existing = self.collection.get(where={"video_id": video_id})
        if existing and existing["ids"]:
            print(f"⚠️  Video {video_id} already exists in database ({len(existing['ids'])} chunks)")
            print("Skipping to avoid duplicates.")
            return 0

        try:
            # Create mock embeddings for all chunks
            print("Creating MOCK embeddings...")
            embeddings = [self._create_mock_embedding(chunk) for chunk in chunks]

            # Prepare data for ChromaDB
            ids = [f"{video_id}:{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "video_id": video_id,
                    "video_url": video_url,
                    "chunk_index": i,
                    "video_title": video_title or video_id
                }
                for i in range(len(chunks))
            ]

            # Add to ChromaDB
            print("Storing embeddings in ChromaDB...")
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )

            print(f"✓ Successfully added {len(chunks)} chunks to the database")
            return len(chunks)

        except Exception as e:
            print(f"❌ Error adding video chunks: {str(e)}")
            raise

    def search_similar_chunks(
        self,
        question: str,
        n_results: int = 5,
        video_id_filter: str = None
    ) -> List[dict]:
        """
        Search using mock embedding for the question.
        """
        if self.collection is None:
            raise ValueError("ChromaDB not initialized. Call initialize_chromadb() first.")

        try:
            # Create mock embedding for question
            query_embedding = self._create_mock_embedding(question)

            # Build query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }

            if video_id_filter:
                query_params["where"] = {"video_id": video_id_filter}

            # Query ChromaDB
            results = self.collection.query(**query_params)

            # Format results
            formatted_results = []
            if results and results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })

            return formatted_results

        except Exception as e:
            print(f"❌ Error searching for similar chunks: {str(e)}")
            raise


def create_sample_chunks() -> tuple:
    """
    Create sample video transcript chunks for testing.

    Returns:
        Tuple of (video_id, video_url, chunks, video_title)
    """
    video_id = "sample_ml_tutorial"
    video_url = "https://youtube.com/watch?v=sample123"
    video_title = "Introduction to Machine Learning"

    chunks = [
        # Chunk 1: Introduction to ML
        "Machine learning is a branch of artificial intelligence that focuses on building "
        "systems that can learn from data. Instead of being explicitly programmed with rules, "
        "machine learning algorithms identify patterns in data and make predictions or decisions "
        "based on those patterns. This approach is particularly powerful when dealing with "
        "complex problems where traditional programming would be impractical.",

        # Chunk 2: Types of ML
        "There are three main types of machine learning: supervised learning, unsupervised learning, "
        "and reinforcement learning. Supervised learning uses labeled data to train models, where "
        "each example has an input and a known output. The model learns to map inputs to outputs. "
        "Common applications include image classification, spam detection, and price prediction.",

        # Chunk 3: Neural Networks
        "Neural networks are a type of machine learning model inspired by the human brain. "
        "They consist of layers of interconnected nodes, or neurons, that process information. "
        "Each connection has a weight that determines how much influence one neuron has on another. "
        "During training, these weights are adjusted to minimize prediction errors. Deep neural "
        "networks with many layers are called deep learning models.",

        # Chunk 4: Training Process
        "Training a machine learning model involves feeding it data and adjusting its parameters "
        "to improve performance. This is typically done using an optimization algorithm like "
        "gradient descent. The model makes predictions, compares them to the actual values, "
        "calculates an error (loss), and updates its parameters to reduce this error. "
        "This process is repeated many times over the training dataset.",

        # Chunk 5: Applications
        "Machine learning has revolutionized many industries. In healthcare, it helps diagnose "
        "diseases from medical images. In finance, it detects fraudulent transactions and predicts "
        "market trends. In technology, it powers recommendation systems, voice assistants, and "
        "autonomous vehicles. Natural language processing, a subfield of ML, enables computers to "
        "understand and generate human language, powering chatbots and translation services.",

        # Chunk 6: Data Importance
        "The quality and quantity of data are crucial for machine learning success. Models need "
        "diverse, representative datasets to learn effectively. Insufficient data can lead to "
        "poor performance, while biased data can result in unfair or inaccurate predictions. "
        "Data preprocessing, including cleaning, normalization, and feature engineering, is often "
        "one of the most time-consuming but important steps in building ML systems.",
    ]

    return video_id, video_url, chunks, video_title


def main():
    """
    Main test function.
    """
    print("=" * 70)
    print("Embedding Manager Test Script")
    print("=" * 70)
    print()

    # Determine which mode to use
    use_real_embeddings = VOYAGE_API_KEY is not None

    if use_real_embeddings:
        print("✓ Voyage API key found - using REAL embeddings")
        print(f"  API Key: {VOYAGE_API_KEY[:8]}..." if VOYAGE_API_KEY else "")
        manager = EmbeddingManager()
    else:
        print("⚠️  No Voyage API key found - using MOCK embeddings")
        print("  This will test ChromaDB storage/retrieval without API calls")
        print("  To use real embeddings, add VOYAGE_API_KEY to your .env file")
        manager = MockEmbeddingManager(embedding_dimension=1024)

    print()

    # Initialize ChromaDB
    print("-" * 70)
    print("Step 1: Initialize ChromaDB")
    print("-" * 70)
    manager.initialize_chromadb()

    # Show current stats
    print("\nCurrent database statistics:")
    stats = manager.get_collection_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Create sample chunks
    print("\n" + "-" * 70)
    print("Step 2: Create sample video chunks")
    print("-" * 70)
    video_id, video_url, chunks, video_title = create_sample_chunks()
    print(f"Video ID: {video_id}")
    print(f"Video Title: {video_title}")
    print(f"Number of chunks: {len(chunks)}")
    print("\nSample chunks:")
    for i, chunk in enumerate(chunks[:2], 1):  # Show first 2
        print(f"\n  Chunk {i}: {chunk[:100]}...")

    # Add chunks to database
    print("\n" + "-" * 70)
    print("Step 3: Add chunks to ChromaDB")
    print("-" * 70)
    num_added = manager.add_video_chunks(
        video_id=video_id,
        video_url=video_url,
        chunks=chunks,
        video_title=video_title
    )

    if num_added == 0:
        print("\nℹ️  Chunks already exist. To re-test, delete the chroma_db directory.")
        print("   Command: rm -rf chroma_db/")

    # Show updated stats
    print("\nUpdated database statistics:")
    stats = manager.get_collection_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test search functionality
    print("\n" + "=" * 70)
    print("Step 4: Test similarity search")
    print("=" * 70)

    # Define test questions
    test_questions = [
        "What is neural network?",
        "How does training work?",
        "What are applications of machine learning?",
    ]

    for question in test_questions:
        print(f"\nQuestion: \"{question}\"")
        print("-" * 70)

        # Search for similar chunks
        results = manager.search_similar_chunks(question, n_results=3)

        if not results:
            print("  No results found")
            continue

        print(f"Found {len(results)} relevant chunks:\n")

        for i, result in enumerate(results, 1):
            distance = result["distance"]
            text = result["text"]
            metadata = result["metadata"]

            # Display result
            print(f"{i}. Similarity Score: {1 - distance:.4f} (distance: {distance:.4f})")
            print(f"   Chunk Index: {metadata['chunk_index']}")
            print(f"   Video: {metadata['video_title']}")
            print(f"   Text Preview: {text[:150]}...")
            print()

        if not use_real_embeddings:
            print("   ⚠️  NOTE: Results are random with mock embeddings")
            print("   ⚠️  Real embeddings would return semantically relevant chunks")
            print()

    # Summary
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)
    print("\nWhat was tested:")
    print("  ✓ ChromaDB initialization and collection creation")
    print("  ✓ Embedding creation" + (" (MOCK)" if not use_real_embeddings else " (REAL)"))
    print("  ✓ Storing embeddings with metadata in ChromaDB")
    print("  ✓ Similarity search and retrieval")
    print("  ✓ Result formatting with metadata")

    if not use_real_embeddings:
        print("\nTo test with REAL embeddings:")
        print("  1. Get a Voyage AI API key from https://www.voyageai.com/")
        print("  2. Add it to your .env file: VOYAGE_API_KEY=your_key_here")
        print("  3. Delete the test database: rm -rf chroma_db/")
        print("  4. Run this script again")

    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
