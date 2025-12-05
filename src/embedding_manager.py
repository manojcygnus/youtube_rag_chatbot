"""
Embedding Manager Module

This module handles embedding creation and vector database operations for the
YouTube RAG chatbot. It uses Voyage AI for creating embeddings and ChromaDB
for storing and retrieving them.
"""

import chromadb
from chromadb.config import Settings
import voyageai
from typing import List, Dict, Any, Optional
from src.config import (
    VOYAGE_API_KEY,
    VOYAGE_MODEL,
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIRECTORY
)


class EmbeddingManager:
    """
    Manages embedding creation and vector database operations.

    This class provides a high-level interface for:
    1. Creating embeddings from text using Voyage AI
    2. Storing embeddings and metadata in ChromaDB
    3. Searching for similar text chunks using semantic similarity

    How ChromaDB Collections Work:
    -------------------------------
    ChromaDB organizes embeddings into "collections" (similar to tables in SQL databases).
    Each collection:
    - Has a unique name
    - Stores vectors (embeddings) with their associated documents and metadata
    - Uses a distance metric (default: cosine similarity) to compare embeddings
    - Can be queried to find the most similar items to a given query

    Collections are persistent - they're saved to disk and can be reloaded across
    application restarts, avoiding the need to re-embed all your data each time.

    Metadata Storage:
    -----------------
    For each chunk we store, we include metadata:
    - video_id: Unique identifier for the YouTube video
    - video_url: Full URL to the source video
    - chunk_index: Position of this chunk in the original transcript (0, 1, 2, ...)
    - video_title: Optional title of the video for display

    This metadata enables:
    - Source attribution: "This information comes from video X at timestamp Y"
    - Filtering: Search only within specific videos
    - Deduplication: Avoid re-processing videos we've already embedded
    - User experience: Show users which video answered their question

    How Similarity Search Works:
    -----------------------------
    1. Query Embedding: Your search question is converted to a vector (embedding)
       using the same embedding model that was used for the document chunks.

    2. Distance Calculation: ChromaDB compares the query embedding to all stored
       chunk embeddings using a distance metric (e.g., cosine similarity).
       - Cosine similarity: Measures the angle between vectors (0 to 1)
       - Closer to 1 = more similar
       - This captures semantic meaning, not just keyword matches

    3. Ranking: Chunks are ranked by similarity score (highest = most relevant)

    4. Top-K Retrieval: The top K most similar chunks are returned

    Why this works: Text with similar meanings produces similar embeddings, even if
    they use different words. For example:
    - "machine learning algorithms" and "ML models" will have similar embeddings
    - "cat" and "feline" will be close in embedding space
    - "king - man + woman ≈ queen" in vector space!
    """

    def __init__(self):
        """
        Initialize the EmbeddingManager with Voyage AI and ChromaDB clients.
        """
        # Initialize Voyage AI client for creating embeddings
        if not VOYAGE_API_KEY:
            raise ValueError(
                "VOYAGE_API_KEY not found. Please set it in your .env file. "
                "See .env.example for instructions."
            )

        self.voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)
        self.voyage_model = VOYAGE_MODEL

        # ChromaDB client and collection will be initialized when needed
        self.chroma_client: Optional[chromadb.ClientAPI] = None
        self.collection: Optional[chromadb.Collection] = None
        self.collection_name = CHROMA_COLLECTION_NAME
        self.persist_directory = CHROMA_PERSIST_DIRECTORY

    def initialize_chromadb(self) -> None:
        """
        Initialize ChromaDB client and collection.

        ChromaDB Setup:
        ---------------
        - PersistentClient: Saves embeddings to disk (vs. in-memory EphemeralClient)
        - persist_directory: Where ChromaDB stores its data on disk
        - Collection: A named group of embeddings with consistent schema

        Collections in ChromaDB:
        ------------------------
        Think of a collection as a table in a database, but for vectors:
        - Each "row" contains: ID, embedding vector, document text, and metadata
        - Collections have a name and can be retrieved later
        - get_or_create: Returns existing collection if it exists, creates if not
        - This means your embeddings persist across application restarts!

        Distance Metrics:
        -----------------
        ChromaDB supports different distance metrics:
        - cosine: Measures angle between vectors (default, best for most text)
        - l2: Euclidean distance (geometric distance)
        - ip: Inner product (dot product)

        We use cosine similarity because it's most effective for text embeddings,
        as it captures semantic similarity regardless of vector magnitude.
        """
        print(f"Initializing ChromaDB at {self.persist_directory}...")

        # Create a persistent ChromaDB client
        # This saves all data to disk so embeddings persist across runs
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False  # Disable telemetry for privacy
            )
        )

        # Get or create a collection for storing video transcript embeddings
        # If the collection already exists, it loads it with all previous embeddings
        # If it doesn't exist, it creates a new empty collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "YouTube video transcript embeddings for RAG chatbot"}
        )

        # Get collection stats
        count = self.collection.count()
        print(f"✓ ChromaDB initialized successfully")
        print(f"✓ Collection '{self.collection_name}' ready ({count} existing embeddings)")

    def add_video_chunks(
        self,
        video_id: str,
        video_url: str,
        chunks: List[str],
        video_title: Optional[str] = None
    ) -> int:
        """
        Add video transcript chunks to the vector database.

        This method:
        1. Checks if video already exists in the database (deduplication)
        2. Creates embeddings for all chunks using Voyage AI
        3. Stores embeddings, text, and metadata in ChromaDB

        How Embeddings Are Created:
        ----------------------------
        Voyage AI's embedding models convert text into dense vectors (arrays of numbers).
        For example, a sentence might become a 1024-dimensional vector like:
        [0.23, -0.45, 0.78, ...] (1024 numbers)

        These vectors are created using deep learning models trained to place
        semantically similar text close together in vector space.

        Batch Processing:
        -----------------
        We send all chunks to Voyage AI at once (batch processing) because:
        - More efficient than one-at-a-time (fewer API calls)
        - Faster overall processing
        - Most embedding APIs support batching

        ChromaDB Storage:
        -----------------
        For each chunk, we store:
        - id: Unique identifier (video_id + chunk_index)
        - embedding: The vector representation of the text
        - document: The actual text content (for retrieval)
        - metadata: Additional information (video_url, chunk_index, title)

        The ID format "video_id:chunk_index" allows us to:
        - Avoid duplicates (same ID will update, not create new)
        - Easily identify which video and chunk a result came from
        - Query specific videos if needed

        Args:
            video_id (str): Unique identifier for the video (e.g., YouTube video ID)
            video_url (str): Full URL to the video
            chunks (List[str]): List of text chunks to embed
            video_title (Optional[str]): Optional title of the video

        Returns:
            int: Number of chunks successfully added to the database

        Raises:
            ValueError: If ChromaDB hasn't been initialized
            Exception: If embedding creation or storage fails
        """
        if self.collection is None:
            raise ValueError(
                "ChromaDB not initialized. Call initialize_chromadb() first."
            )

        if not chunks:
            print("⚠ No chunks provided, nothing to add")
            return 0

        print(f"\nProcessing video: {video_id}")
        print(f"Number of chunks: {len(chunks)}")

        # Check if this video already exists in the database
        # This prevents re-processing videos we've already embedded
        existing = self.collection.get(
            where={"video_id": video_id}
        )
        if existing and existing["ids"]:
            print(f"⚠ Video {video_id} already exists in database ({len(existing['ids'])} chunks)")
            print("Skipping to avoid duplicates. Delete the collection to re-process.")
            return 0

        try:
            # Create embeddings for all chunks using Voyage AI
            # This is a batch operation - all chunks are embedded in one API call
            print("Creating embeddings with Voyage AI...")
            result = self.voyage_client.embed(
                texts=chunks,
                model=self.voyage_model,
                input_type="document"  # Optimized for storing documents (vs "query" for searches)
            )

            # Extract the embedding vectors from the response
            embeddings = result.embeddings

            # Prepare data for ChromaDB storage
            # We need: IDs, embeddings, documents (text), and metadata
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

            # Add all embeddings to ChromaDB in one operation
            # ChromaDB automatically handles indexing for fast similarity search
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
        video_id_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for chunks most similar to the given question.

        How This Works:
        ---------------
        1. Question Embedding: The question is converted to a vector using Voyage AI
           - Uses input_type="query" (optimized for search queries)
           - Same model as used for documents ensures compatibility

        2. Similarity Comparison: ChromaDB compares the question embedding to all
           stored document embeddings using cosine similarity
           - Cosine similarity = dot(A, B) / (||A|| * ||B||)
           - Range: -1 to 1, where 1 = identical, 0 = orthogonal, -1 = opposite
           - ChromaDB returns this as a "distance" (lower = more similar)

        3. Ranking & Retrieval: The top n_results most similar chunks are returned
           - Each result includes: document text, metadata, and similarity distance
           - Results are sorted by relevance (most similar first)

        Why Semantic Search Is Powerful:
        ---------------------------------
        Unlike keyword search, this finds chunks that mean similar things:
        - Question: "How do I train a neural network?"
        - Will match: "Training deep learning models requires..."
        - Even though words "train" and "neural network" might not appear!

        The embedding model learned semantic relationships during training on
        massive text corpora, so it "understands" that "train" relates to "training"
        and "neural network" relates to "deep learning models".

        Filtering:
        ----------
        You can optionally filter results to only search within specific videos
        using the video_id_filter parameter. This is useful when you want to
        restrict the search scope (e.g., "Find info in THIS specific video").

        Args:
            question (str): The user's question to search for
            n_results (int): Number of similar chunks to return (default: 5)
            video_id_filter (Optional[str]): Only search within this video ID

        Returns:
            List[Dict[str, Any]]: List of similar chunks with their metadata
                Each dict contains:
                - text: The chunk text content
                - metadata: video_id, video_url, chunk_index, video_title
                - distance: Similarity score (lower = more similar)

        Raises:
            ValueError: If ChromaDB hasn't been initialized
            Exception: If search fails
        """
        if self.collection is None:
            raise ValueError(
                "ChromaDB not initialized. Call initialize_chromadb() first."
            )

        try:
            # Create an embedding for the question using Voyage AI
            # input_type="query" optimizes the embedding for search queries
            # (as opposed to "document" for texts we're storing)
            result = self.voyage_client.embed(
                texts=[question],
                model=self.voyage_model,
                input_type="query"
            )
            query_embedding = result.embeddings[0]

            # Build the query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }

            # Add video filter if specified
            # This restricts search to only chunks from a specific video
            if video_id_filter:
                query_params["where"] = {"video_id": video_id_filter}

            # Query ChromaDB for similar chunks
            # ChromaDB uses an efficient vector index (HNSW by default) to quickly
            # find similar embeddings without comparing to every single item
            results = self.collection.query(**query_params)

            # Format results into a more user-friendly structure
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

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.

        Returns:
            Dict containing collection statistics
        """
        if self.collection is None:
            return {"error": "ChromaDB not initialized"}

        count = self.collection.count()

        # Get all unique video IDs
        all_items = self.collection.get()
        video_ids = set()
        if all_items and all_items["metadatas"]:
            for metadata in all_items["metadatas"]:
                if "video_id" in metadata:
                    video_ids.add(metadata["video_id"])

        return {
            "total_chunks": count,
            "total_videos": len(video_ids),
            "collection_name": self.collection_name,
            "video_ids": list(video_ids)
        }

    def delete_video(self, video_id: str) -> int:
        """
        Delete all chunks for a specific video from the database.

        Args:
            video_id (str): The video ID to delete

        Returns:
            int: Number of chunks deleted
        """
        if self.collection is None:
            raise ValueError("ChromaDB not initialized")

        # Get all chunks for this video
        results = self.collection.get(
            where={"video_id": video_id}
        )

        if not results or not results["ids"]:
            print(f"No chunks found for video {video_id}")
            return 0

        # Delete the chunks
        self.collection.delete(ids=results["ids"])

        print(f"✓ Deleted {len(results['ids'])} chunks for video {video_id}")
        return len(results["ids"])


if __name__ == "__main__":
    # Example usage and testing
    print("=" * 70)
    print("Embedding Manager Test")
    print("=" * 70)

    # Initialize the embedding manager
    manager = EmbeddingManager()
    manager.initialize_chromadb()

    # Show current collection stats
    print("\nCurrent Collection Stats:")
    print("-" * 70)
    stats = manager.get_collection_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Example: Add some test chunks (commented out to avoid API usage)
    # test_chunks = [
    #     "Machine learning is a subset of artificial intelligence.",
    #     "Neural networks are inspired by biological neurons.",
    #     "Deep learning uses multiple layers to learn representations."
    # ]
    #
    # manager.add_video_chunks(
    #     video_id="test123",
    #     video_url="https://youtube.com/watch?v=test123",
    #     chunks=test_chunks,
    #     video_title="Machine Learning Basics"
    # )
    #
    # # Example: Search for similar chunks
    # results = manager.search_similar_chunks("What is neural network?", n_results=3)
    # print("\nSearch Results:")
    # for i, result in enumerate(results, 1):
    #     print(f"\n{i}. Distance: {result['distance']:.4f}")
    #     print(f"   Text: {result['text']}")
    #     print(f"   Video: {result['metadata']['video_title']}")

    print("\n" + "=" * 70)
