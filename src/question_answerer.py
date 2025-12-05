"""
Question Answerer Module

This module handles question-answering using Retrieval-Augmented Generation (RAG).
It retrieves relevant context from the vector database and uses an LLM
(Google Gemini or Anthropic Claude) to generate accurate, grounded answers.
"""

from typing import Optional, List, Dict, Any
from anthropic import Anthropic
import google.generativeai as genai
from src.embedding_manager import EmbeddingManager
from src.config import (
    GEMINI_API_KEY, GEMINI_MODEL,
    ANTHROPIC_API_KEY, CLAUDE_MODEL,
    LLM_PROVIDER
)


class QuestionAnswerer:
    """
    Handles question-answering using RAG (Retrieval-Augmented Generation).

    What is RAG and Why Use It?
    ----------------------------
    RAG combines two powerful techniques:

    1. **Retrieval**: Finding relevant information from a knowledge base
       - Uses semantic search to find chunks related to the question
       - Ensures answers are grounded in specific source material

    2. **Generation**: Using an LLM to synthesize natural language answers
       - The LLM (Gemini or Claude) reads the retrieved context
       - Generates a coherent, accurate answer based on that context

    Why RAG is More Reliable Than General Knowledge:
    -------------------------------------------------

    1. **Factual Grounding**:
       - Without RAG: Claude might make up plausible-sounding but incorrect information
         (hallucination), especially for specific details, recent events, or niche topics
       - With RAG: Claude's answer is constrained to information in the retrieved chunks,
         which come from verified sources (your video transcripts)

    2. **Source Attribution**:
       - Without RAG: Users can't verify where information came from
       - With RAG: You can show users exactly which video/timestamp the answer came from

    3. **Up-to-Date Information**:
       - Without RAG: Claude's knowledge is frozen at training time (cutoff date)
       - With RAG: Your knowledge base can include the latest videos, constantly updated

    4. **Domain-Specific Knowledge**:
       - Without RAG: Claude has general knowledge but may lack depth in your specific domain
       - With RAG: You control the knowledge base, ensuring expertise in your area

    5. **Reduced Hallucinations**:
       - Without RAG: Claude might confidently state incorrect information
       - With RAG: If information isn't in the context, Claude can say "I don't know"

    6. **Privacy & Control**:
       - Without RAG: You'd need to fine-tune Claude on your data (expensive, complex)
       - With RAG: Your data stays in your vector database, easily updateable

    Example Comparison:
    -------------------
    Question: "What did the instructor say about learning rate in episode 47?"

    Without RAG (General Knowledge):
    - Claude might give generic advice about learning rates
    - Can't reference the specific episode
    - Might make up details that sound plausible but are wrong

    With RAG:
    - Retrieves actual transcript from episode 47
    - Quotes or paraphrases what was actually said
    - Can say "Episode 47 doesn't discuss learning rates" if not present
    - Provides source: "According to the transcript from episode 47..."
    """

    def __init__(self, embedding_manager: EmbeddingManager):
        """
        Initialize the QuestionAnswerer with selected LLM provider.

        Args:
            embedding_manager: An initialized EmbeddingManager for retrieving context
        """
        # Store reference to embedding manager for retrieving context
        self.embedding_manager = embedding_manager

        # Set up the LLM provider based on configuration
        self.provider = LLM_PROVIDER.lower()

        if self.provider == "gemini":
            # Initialize Google Gemini
            if not GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY not found. Please set it in your .env file. "
                    "See .env.example for instructions."
                )
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = GEMINI_MODEL
            self.client = genai.GenerativeModel(self.model)

        elif self.provider == "anthropic":
            # Initialize Anthropic Claude
            if not ANTHROPIC_API_KEY:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. Please set it in your .env file. "
                    "See .env.example for instructions."
                )
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            self.model = CLAUDE_MODEL

        else:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {LLM_PROVIDER}. "
                "Must be either 'gemini' or 'anthropic'. "
                "Please check your .env file."
            )

    def _construct_prompt(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Construct a prompt for Claude that includes retrieved context and the question.

        Prompt Engineering Principles Applied Here:
        -------------------------------------------

        1. **Clear Role Definition**:
           - We tell Claude it's a helpful assistant answering questions about videos
           - This frames the task and sets expectations for tone/style

        2. **Context Before Question**:
           - Provide relevant information first, then ask the question
           - Mirrors natural information processing (learn, then apply)

        3. **Explicit Constraints**:
           - "Answer ONLY based on the provided context"
           - Prevents hallucinations by constraining Claude's knowledge source
           - Critical for factual accuracy in RAG systems

        4. **Handling Uncertainty**:
           - Instruct Claude to say when information is insufficient
           - Better to admit ignorance than make up answers
           - Builds user trust in the system

        5. **Source Attribution**:
           - Ask Claude to reference which chunks information comes from
           - Enables verification and transparency
           - Users can check the original video

        6. **Structured Output**:
           - Request clear, concise answers
           - Specify when to use bullet points or paragraphs
           - Improves user experience

        7. **Context Formatting**:
           - Number each chunk for easy reference
           - Include metadata (video title, chunk index)
           - Helps Claude and users track information sources

        Why This Prompt Structure Works:
        ---------------------------------
        - Clear instructions reduce ambiguity
        - Constraints prevent hallucinations
        - Structure makes answers more useful
        - Metadata enables source attribution
        - Admitting uncertainty maintains credibility

        Args:
            question: The user's question
            context_chunks: Retrieved relevant chunks with metadata

        Returns:
            A formatted prompt string for Claude
        """
        # Build the context section with all retrieved chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            video_title = chunk["metadata"].get("video_title", "Unknown Video")
            chunk_index = chunk["metadata"].get("chunk_index", "?")
            text = chunk["text"]

            context_parts.append(
                f"[Chunk {i}]\n"
                f"Video: {video_title}\n"
                f"Chunk Index: {chunk_index}\n"
                f"Content: {text}\n"
            )

        context_text = "\n---\n\n".join(context_parts)

        # Construct the complete prompt
        # This is the crucial part where we engineer the prompt for optimal results
        prompt = f"""You are a helpful AI assistant that answers questions about YouTube videos based on their transcripts.

CONTEXT FROM VIDEO TRANSCRIPTS:
================================
{context_text}

================================

INSTRUCTIONS:
1. Answer the user's question ONLY based on the context provided above
2. If the context doesn't contain enough information to answer the question, say so clearly
3. When possible, reference which chunk(s) your answer comes from (e.g., "According to Chunk 2...")
4. Be concise but complete in your answer
5. If multiple chunks provide relevant information, synthesize them into a coherent response
6. Do NOT use information from your general knowledge that isn't in the provided context
7. If the user asks about something not covered in the transcripts, politely state that the information isn't available in the provided videos

USER QUESTION:
{question}

ANSWER:"""

        return prompt

    def answer_question(
        self,
        question: str,
        n_context_chunks: int = 5,
        video_id_filter: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG (Retrieval-Augmented Generation).

        This is the main method that orchestrates the RAG pipeline:
        1. Retrieve relevant context from vector database
        2. Construct a prompt with context and question
        3. Call Claude to generate an answer
        4. Return the answer with metadata

        RAG Pipeline Explained:
        -----------------------

        Step 1: RETRIEVAL
        - User asks a question
        - Question is embedded into a vector
        - Vector database finds similar transcript chunks
        - Most relevant chunks are retrieved (default: top 5)

        Step 2: AUGMENTATION
        - Retrieved chunks are formatted into a prompt
        - Prompt includes clear instructions for Claude
        - Context is presented before the question

        Step 3: GENERATION
        - Prompt is sent to Claude API
        - Claude reads the context and question
        - Claude generates a grounded, accurate answer
        - Answer is constrained to the provided context

        Why This Approach Works:
        ------------------------
        - Semantic search finds relevant information even with different wording
        - Claude's language understanding interprets complex queries
        - Grounding in specific text prevents hallucinations
        - Source tracking enables verification

        Temperature Parameter:
        ----------------------
        Temperature controls randomness in Claude's responses:
        - 0.0 = Deterministic, focused (best for factual Q&A)
        - 1.0 = Creative, varied (good for brainstorming)
        - 0.7 = Balanced (default, good for most uses)

        For RAG systems, lower temperatures (0.0-0.5) are often better because:
        - We want consistent, factual answers
        - Creativity might introduce information not in context
        - Repeatability helps with testing and debugging

        Max Tokens:
        -----------
        Controls the maximum length of Claude's response:
        - 1024 tokens ≈ 750 words (suitable for most answers)
        - Increase for longer, detailed explanations
        - Decrease for concise, quick responses

        Args:
            question: The user's question
            n_context_chunks: Number of relevant chunks to retrieve (default: 5)
            video_id_filter: Optional filter to search only in specific video
            max_tokens: Maximum length of response (default: 1024)
            temperature: Sampling temperature 0.0-1.0 (default: 0.7)

        Returns:
            Dictionary containing:
                - answer: Claude's response text
                - context_chunks: The chunks used as context (for source attribution)
                - metadata: Additional info (model, token count, etc.)

        Raises:
            ValueError: If embedding manager isn't initialized
            Exception: If API call fails
        """
        # Step 1: RETRIEVE relevant context from vector database
        print(f"\nRetrieving relevant context for: \"{question}\"")

        context_chunks = self.embedding_manager.search_similar_chunks(
            question=question,
            n_results=n_context_chunks,
            video_id_filter=video_id_filter
        )

        if not context_chunks:
            # No relevant context found
            return {
                "answer": (
                    "I couldn't find any relevant information in the video transcripts "
                    "to answer your question. This might mean the topic isn't covered in "
                    "the available videos, or you might need to rephrase your question."
                ),
                "context_chunks": [],
                "metadata": {
                    "model": self.model,
                    "no_context_found": True
                }
            }

        print(f"✓ Found {len(context_chunks)} relevant chunks")

        # Show which chunks were retrieved (for debugging/transparency)
        for i, chunk in enumerate(context_chunks, 1):
            video_title = chunk["metadata"].get("video_title", "Unknown")
            distance = chunk.get("distance", 0)
            similarity = 1 - distance
            print(f"  {i}. {video_title} (similarity: {similarity:.3f})")

        # Step 2: AUGMENT - Construct prompt with context and question
        print("\nConstructing prompt with context...")
        prompt = self._construct_prompt(question, context_chunks)

        # Step 3: GENERATE - Call LLM to get answer
        print(f"Generating answer using {self.model} ({self.provider})...")

        try:
            if self.provider == "gemini":
                # Call Google Gemini API
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    )
                )

                # Extract the answer from Gemini's response
                answer = response.text

                print("✓ Answer generated successfully")

                # Return answer with context and metadata
                return {
                    "answer": answer,
                    "context_chunks": context_chunks,
                    "metadata": {
                        "model": self.model,
                        "provider": self.provider,
                        "input_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                        "output_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None,
                        "temperature": temperature,
                        "num_context_chunks": len(context_chunks)
                    }
                }

            elif self.provider == "anthropic":
                # Call Claude API
                # We use the Messages API which is Claude's recommended interface
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                # Extract the answer from Claude's response
                answer = message.content[0].text

                print("✓ Answer generated successfully")

                # Return answer with context and metadata
                # This enables source attribution and transparency
                return {
                    "answer": answer,
                    "context_chunks": context_chunks,
                    "metadata": {
                        "model": self.model,
                        "provider": self.provider,
                        "input_tokens": message.usage.input_tokens,
                        "output_tokens": message.usage.output_tokens,
                        "temperature": temperature,
                        "num_context_chunks": len(context_chunks)
                    }
                }

        except Exception as e:
            print(f"❌ Error generating answer: {str(e)}")
            raise

    def format_answer_with_sources(self, result: Dict[str, Any]) -> str:
        """
        Format the answer result into a user-friendly string with source attribution.

        This demonstrates good UX for RAG systems:
        - Show the answer prominently
        - Provide sources for verification
        - Include metadata for transparency

        Args:
            result: The result dictionary from answer_question()

        Returns:
            Formatted string with answer and sources
        """
        output = []

        # Main answer
        output.append("ANSWER:")
        output.append("=" * 70)
        output.append(result["answer"])
        output.append("=" * 70)

        # Sources section
        if result.get("context_chunks"):
            output.append("\nSOURCES:")
            output.append("-" * 70)

            for i, chunk in enumerate(result["context_chunks"], 1):
                metadata = chunk["metadata"]
                video_title = metadata.get("video_title", "Unknown Video")
                video_url = metadata.get("video_url", "")
                chunk_index = metadata.get("chunk_index", "?")

                output.append(f"\n{i}. {video_title}")
                output.append(f"   Chunk: {chunk_index}")
                if video_url:
                    output.append(f"   URL: {video_url}")

            output.append("-" * 70)

        # Metadata (optional, for transparency)
        if "metadata" in result and not result["metadata"].get("no_context_found"):
            meta = result["metadata"]
            output.append("\nMETADATA:")
            output.append(f"Model: {meta.get('model', 'Unknown')}")
            if "input_tokens" in meta:
                output.append(
                    f"Tokens: {meta['input_tokens']} input, "
                    f"{meta['output_tokens']} output"
                )

        return "\n".join(output)


if __name__ == "__main__":
    # Example usage (requires initialized embedding manager and data)
    print("=" * 70)
    print("Question Answerer Module")
    print("=" * 70)
    print("\nThis module requires:")
    print("  1. An initialized EmbeddingManager")
    print("  2. Video chunks stored in ChromaDB")
    print("  3. LLM API key in your .env file:")
    print("     - GEMINI_API_KEY (recommended, free tier)")
    print("     - or ANTHROPIC_API_KEY (requires paid credits)")
    print("  4. Set LLM_PROVIDER='gemini' or 'anthropic' in .env")
    print("\nRun test_embeddings.py first to set up test data,")
    print("then use this module in your main application.")
    print("=" * 70)
