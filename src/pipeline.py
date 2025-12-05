"""
Video RAG Pipeline Module

This module orchestrates the entire RAG workflow, from processing YouTube videos
to answering questions about them. It integrates all components of the system
into a clean, high-level API.
"""

import logging
import re
from typing import Dict, Any, Optional
from src.transcript_extractor import extract_transcript
from src.text_chunker import chunk_transcript
from src.embedding_manager import EmbeddingManager
from src.question_answerer import QuestionAnswerer
from src.metadata_manager import VideoMetadataManager
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

# Configure logging
# Logging helps us track what's happening at each stage and debug issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class VideoRAGPipeline:
    """
    Orchestrates the complete Video RAG workflow.

    This pipeline integrates all components:
    1. Transcript Extraction (yt-dlp)
    2. Text Chunking (LangChain)
    3. Embedding Creation & Storage (Voyage AI + ChromaDB)
    4. Question Answering (Claude via RAG)

    Why Use a Pipeline Class?
    --------------------------
    1. **Abstraction**: Hide complexity from users
       - Users don't need to know about embeddings, chunking, etc.
       - Simple API: process_video(url) and chat(video_id, question)

    2. **State Management**: Keep track of initialized components
       - EmbeddingManager stays initialized across operations
       - Avoid redundant initialization

    3. **Error Handling**: Centralized error handling and logging
       - Each stage can fail independently
       - Pipeline handles failures gracefully
       - Clear error messages for debugging

    4. **Consistency**: Ensure all operations use the same configuration
       - Same chunk size, overlap, models throughout
       - Configuration loaded from one place (config.py)

    5. **Testability**: Easy to mock and test individual stages
       - Can test end-to-end workflow
       - Can test individual components

    Pipeline Flow:
    --------------
    PROCESS VIDEO:
    YouTube URL → Extract Transcript → Chunk Text → Create Embeddings → Store in DB

    CHAT:
    Question → Retrieve Relevant Chunks → Generate Answer with Claude → Return Response
    """

    def __init__(self):
        """
        Initialize the RAG pipeline with all required components.

        This sets up:
        - EmbeddingManager for vector operations
        - QuestionAnswerer for RAG-based Q&A
        - VideoMetadataManager for tracking processed videos
        - Logging for tracking operations
        """
        logger.info("Initializing Video RAG Pipeline")

        try:
            # Initialize metadata manager for tracking videos
            logger.info("Setting up VideoMetadataManager...")
            self.metadata_manager = VideoMetadataManager()

            # Initialize embedding manager for vector operations
            logger.info("Setting up EmbeddingManager...")
            self.embedding_manager = EmbeddingManager()
            self.embedding_manager.initialize_chromadb()

            # Initialize question answerer for RAG
            logger.info("Setting up QuestionAnswerer...")
            self.question_answerer = QuestionAnswerer(self.embedding_manager)

            logger.info("✓ Pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {str(e)}")
            raise

    def _extract_video_id(self, youtube_url: str) -> str:
        """
        Extract video ID from a YouTube URL.

        YouTube URLs come in various formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/watch?v=VIDEO_ID&t=123s
        - https://m.youtube.com/watch?v=VIDEO_ID

        This function normalizes all formats to extract just the video ID.

        Args:
            youtube_url: Full YouTube URL

        Returns:
            Video ID string (11 characters)

        Raises:
            ValueError: If URL format is invalid or video ID can't be extracted
        """
        # Pattern to match YouTube video IDs
        # Video IDs are always 11 characters: letters, numbers, hyphens, underscores
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',  # Most common formats
            r'youtu\.be/([0-9A-Za-z_-]{11})',   # Shortened youtu.be links
        ]

        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)

        raise ValueError(
            f"Could not extract video ID from URL: {youtube_url}. "
            "Please ensure it's a valid YouTube URL."
        )

    def process_video(
        self,
        youtube_url: str,
        video_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a YouTube video through the complete RAG pipeline.

        This is the main ingestion method that:
        1. Extracts video transcript from YouTube
        2. Splits transcript into overlapping chunks
        3. Creates embeddings for each chunk
        4. Stores embeddings in ChromaDB with metadata

        Error Handling Strategy:
        ------------------------
        Each stage can fail independently, so we handle errors at each step:

        1. **Transcript Extraction Failures**:
           - Invalid URL → Clear error message to user
           - No subtitles → Inform user video lacks captions
           - Network issues → Suggest retry
           - Rate limiting → Inform user to wait

        2. **Chunking Failures**:
           - Empty transcript → Return early, don't proceed
           - Invalid parameters → Use defaults

        3. **Embedding Failures**:
           - API errors → Catch and report
           - Invalid API key → Clear instructions to user
           - Rate limits → Inform user

        4. **Storage Failures**:
           - Database errors → Report and cleanup
           - Disk space issues → Inform user

        Why Each Stage is Separate:
        ---------------------------
        - Allows resuming from failures (e.g., if storage fails, don't re-extract)
        - Easier to debug (know exactly which stage failed)
        - Better logging (track progress through pipeline)
        - Can optimize individual stages independently

        Args:
            youtube_url: Full YouTube URL (e.g., https://youtube.com/watch?v=abc123)
            video_title: Optional custom title (if None, uses video ID)

        Returns:
            Dictionary containing:
                - success: Boolean indicating if processing completed
                - video_id: Extracted video ID
                - num_chunks: Number of chunks created and stored
                - message: Status message
                - error: Error message if failed (only if success=False)

        Raises:
            Exception: Re-raises exceptions after logging for caller to handle
        """
        logger.info(f"Starting video processing for: {youtube_url}")

        try:
            # ===================================================================
            # STAGE 1: Extract Video ID
            # ===================================================================
            logger.info("Stage 1: Extracting video ID from URL")
            video_id = self._extract_video_id(youtube_url)
            logger.info(f"✓ Video ID: {video_id}")

            # Use video ID as title if none provided
            if not video_title:
                video_title = f"Video {video_id}"

            # ===================================================================
            # STAGE 2: Extract Transcript
            # ===================================================================
            logger.info("Stage 2: Extracting transcript from YouTube")
            logger.info("  This may take 10-30 seconds depending on video length...")

            try:
                transcript = extract_transcript(youtube_url)
                logger.info(f"✓ Transcript extracted: {len(transcript)} characters")
                logger.info(f"  (~{len(transcript.split())} words)")

            except ValueError as e:
                # Invalid URL or video not accessible
                logger.error(f"✗ Transcript extraction failed: {str(e)}")
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": str(e),
                    "message": "Failed to extract transcript. Check URL and video accessibility."
                }

            except RuntimeError as e:
                # No transcript available or HTTP errors
                logger.error(f"✗ Transcript not available: {str(e)}")
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": str(e),
                    "message": "Video transcript not available."
                }

            # Validate transcript isn't empty
            if not transcript or len(transcript.strip()) < 50:
                logger.warning("✗ Transcript is too short or empty")
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": "Transcript is empty or too short",
                    "message": "Could not extract meaningful content from video."
                }

            # ===================================================================
            # STAGE 3: Chunk Transcript
            # ===================================================================
            logger.info("Stage 3: Chunking transcript")
            logger.info(f"  Chunk size: {CHUNK_SIZE} characters")
            logger.info(f"  Overlap: {CHUNK_OVERLAP} characters")

            try:
                chunks = chunk_transcript(
                    transcript,
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP
                )
                logger.info(f"✓ Created {len(chunks)} chunks")

                # Log chunk statistics
                avg_length = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
                logger.info(f"  Average chunk length: {avg_length:.0f} characters")

            except Exception as e:
                logger.error(f"✗ Chunking failed: {str(e)}")
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": str(e),
                    "message": "Failed to chunk transcript."
                }

            if not chunks:
                logger.warning("✗ No chunks created")
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": "No chunks created",
                    "message": "Failed to create text chunks."
                }

            # ===================================================================
            # STAGE 4: Create Embeddings and Store in ChromaDB
            # ===================================================================
            logger.info("Stage 4: Creating embeddings and storing in database")
            logger.info("  This may take 10-60 seconds depending on number of chunks...")

            try:
                num_added = self.embedding_manager.add_video_chunks(
                    video_id=video_id,
                    video_url=youtube_url,
                    chunks=chunks,
                    video_title=video_title
                )

                if num_added == 0:
                    logger.warning("⚠ Video already exists in database")
                    return {
                        "success": True,
                        "video_id": video_id,
                        "num_chunks": len(chunks),
                        "message": "Video already processed and stored in database.",
                        "already_exists": True
                    }

                logger.info(f"✓ Successfully stored {num_added} chunks")

            except Exception as e:
                logger.error(f"✗ Failed to create/store embeddings: {str(e)}")
                return {
                    "success": False,
                    "video_id": video_id,
                    "error": str(e),
                    "message": "Failed to create embeddings or store in database."
                }

            # ===================================================================
            # SUCCESS - All stages completed
            # ===================================================================
            # Save video metadata
            logger.info("Saving video metadata...")
            self.metadata_manager.add_video(
                video_id=video_id,
                video_url=youtube_url,
                video_title=video_title,
                num_chunks=num_added,
                transcript_length=len(transcript)
            )
            logger.info("✓ Metadata saved")

            logger.info("=" * 70)
            logger.info("✓ VIDEO PROCESSING COMPLETE")
            logger.info(f"  Video ID: {video_id}")
            logger.info(f"  Title: {video_title}")
            logger.info(f"  Chunks stored: {num_added}")
            logger.info("=" * 70)

            return {
                "success": True,
                "video_id": video_id,
                "video_title": video_title,
                "num_chunks": num_added,
                "transcript_length": len(transcript),
                "message": f"Successfully processed video. {num_added} chunks stored in database."
            }

        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"✗ Unexpected error in video processing: {str(e)}")
            logger.exception("Full traceback:")
            return {
                "success": False,
                "video_id": video_id if 'video_id' in locals() else "unknown",
                "error": str(e),
                "message": "Unexpected error during video processing."
            }

    def chat(
        self,
        question: str,
        video_id_filter: Optional[str] = None,
        n_context_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.

        This method:
        1. Retrieves relevant chunks from the vector database
        2. Constructs a prompt with context
        3. Calls Claude to generate an answer
        4. Returns the answer with sources

        Error Handling:
        ---------------
        - Empty question → Return error message
        - No relevant context found → Inform user
        - API errors → Report and suggest solutions
        - Database errors → Check initialization

        Args:
            question: The user's question about video content
            video_id_filter: Optional video ID to search only in that video
            n_context_chunks: Number of relevant chunks to retrieve (default: 5)

        Returns:
            Dictionary containing:
                - success: Boolean indicating if answer was generated
                - question: The original question
                - answer: Claude's response
                - sources: List of source chunks with metadata
                - metadata: Additional info (model, tokens, etc.)
                - error: Error message if failed (only if success=False)

        Raises:
            Exception: Re-raises exceptions after logging
        """
        logger.info(f"Processing question: \"{question}\"")

        # Validate input
        if not question or not question.strip():
            logger.warning("Empty question provided")
            return {
                "success": False,
                "error": "Question cannot be empty",
                "message": "Please provide a valid question."
            }

        try:
            # Optional: Filter by specific video
            if video_id_filter:
                logger.info(f"Filtering results to video: {video_id_filter}")

            # ===================================================================
            # STAGE 1: Retrieve relevant context and generate answer
            # ===================================================================
            logger.info(f"Retrieving {n_context_chunks} relevant chunks...")

            result = self.question_answerer.answer_question(
                question=question,
                n_context_chunks=n_context_chunks,
                video_id_filter=video_id_filter
            )

            # Check if we got a valid answer
            if not result.get("answer"):
                logger.warning("No answer generated")
                return {
                    "success": False,
                    "question": question,
                    "error": "No answer generated",
                    "message": "Failed to generate an answer."
                }

            # ===================================================================
            # SUCCESS - Answer generated
            # ===================================================================
            logger.info("✓ Answer generated successfully")

            # Log metadata
            if "metadata" in result:
                meta = result["metadata"]
                if "input_tokens" in meta:
                    logger.info(f"  Tokens used: {meta['input_tokens']} input, "
                              f"{meta['output_tokens']} output")

            return {
                "success": True,
                "question": question,
                "answer": result["answer"],
                "sources": result.get("context_chunks", []),
                "metadata": result.get("metadata", {})
            }

        except ValueError as e:
            logger.error(f"✗ Configuration error: {str(e)}")
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "message": "Configuration error. Check your API keys and settings."
            }

        except Exception as e:
            logger.error(f"✗ Error during chat: {str(e)}")
            logger.exception("Full traceback:")
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "message": "Error generating answer. Please try again."
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pipeline and database.

        Returns:
            Dictionary with pipeline statistics
        """
        logger.info("Fetching pipeline statistics")

        try:
            stats = self.embedding_manager.get_collection_stats()
            return {
                "success": True,
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_video(self, video_id: str) -> Dict[str, Any]:
        """
        Delete a video and all its chunks from the database.

        Args:
            video_id: The video ID to delete

        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting video: {video_id}")

        try:
            # Delete from ChromaDB
            num_deleted = self.embedding_manager.delete_video(video_id)
            logger.info(f"✓ Deleted {num_deleted} chunks from database")

            # Delete from metadata
            metadata_deleted = self.metadata_manager.delete_video(video_id)
            if metadata_deleted:
                logger.info("✓ Deleted video metadata")
            else:
                logger.warning("⚠ Video metadata not found")

            return {
                "success": True,
                "video_id": video_id,
                "num_deleted": num_deleted,
                "message": f"Successfully deleted {num_deleted} chunks for video {video_id}"
            }

        except Exception as e:
            logger.error(f"✗ Error deleting video: {str(e)}")
            return {
                "success": False,
                "video_id": video_id,
                "error": str(e),
                "message": "Failed to delete video."
            }


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("Video RAG Pipeline")
    print("=" * 70)
    print("\nThis module orchestrates the entire RAG workflow.")
    print("\nUsage:")
    print("  from src.pipeline import VideoRAGPipeline")
    print("  ")
    print("  # Initialize pipeline")
    print("  pipeline = VideoRAGPipeline()")
    print("  ")
    print("  # Process a video")
    print("  result = pipeline.process_video('https://youtube.com/watch?v=...')")
    print("  ")
    print("  # Ask questions")
    print("  response = pipeline.chat('What is machine learning?')")
    print("  print(response['answer'])")
    print("=" * 70)
