# YouTube RAG Chatbot - Complete High-Level Overview with Code

**For Teaching LLM Models About This Project**

---

## 🎯 What This Project Does

**In One Sentence:** A web application that lets you ask questions about YouTube videos in natural language and get accurate, source-cited answers using AI.

**The Problem It Solves:**
- ❌ **Without this tool:** Watch entire 2-hour lecture to find one concept
- ✅ **With this tool:** Ask "Explain gradient descent" → Get answer in 3 seconds with exact timestamp

---

## 🧠 Core Concept: RAG (Retrieval-Augmented Generation)

### What is RAG?

**Traditional Approach (Just LLM):**
```
User Question → LLM → Answer (might hallucinate)
```

**RAG Approach (This Project):**
```
User Question → Semantic Search → Retrieve Relevant Chunks → LLM + Context → Grounded Answer
```

### Why RAG is Better

| Aspect | Without RAG | With RAG |
|--------|-------------|----------|
| **Accuracy** | May hallucinate facts | Grounded in source material |
| **Sources** | No attribution | Shows exact video chunks used |
| **Recency** | Knowledge cutoff date | Always current (latest videos) |
| **Domain Expertise** | General knowledge | Specialized (your video library) |

**Example:**

**Question:** "What did the instructor say about backpropagation in lecture 3?"

**Without RAG (Claude alone):**
> "Backpropagation is a technique for training neural networks..."
> *(Generic answer, not from lecture 3)*

**With RAG (This project):**
> "According to lecture 3, backpropagation works by calculating gradients layer by layer..."
> *Source: Video "Lecture 3" | Chunk 12 | Similarity: 0.92*

---

## 📊 Complete System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION LAYER                      │
│                  (Streamlit Web Interface)                      │
│  Pages: Chat | Add Video | My Videos | Statistics              │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                             │
│                   (Python Backend)                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. VIDEO PROCESSING PIPELINE                             │  │
│  │    Input: YouTube URL                                     │  │
│  │    ↓                                                      │  │
│  │    Extract Video ID (regex parsing)                      │  │
│  │    ↓                                                      │  │
│  │    Fetch Transcript (yt-dlp)                             │  │
│  │    ↓                                                      │  │
│  │    Chunk Text (RecursiveCharacterTextSplitter)           │  │
│  │    ↓                                                      │  │
│  │    Generate Embeddings (Voyage AI API)                   │  │
│  │    ↓                                                      │  │
│  │    Store Vectors + Metadata (ChromaDB)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. QUESTION-ANSWERING PIPELINE                           │  │
│  │    Input: User Question                                   │  │
│  │    ↓                                                      │  │
│  │    Embed Question (Voyage AI)                            │  │
│  │    ↓                                                      │  │
│  │    Semantic Search (ChromaDB cosine similarity)          │  │
│  │    ↓                                                      │  │
│  │    Retrieve Top 5 Chunks                                 │  │
│  │    ↓                                                      │  │
│  │    Construct Prompt (Question + Context)                 │  │
│  │    ↓                                                      │  │
│  │    Generate Answer (Google Gemini / Claude)              │  │
│  │    ↓                                                      │  │
│  │    Return Answer + Sources                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                  │
│                                                                  │
│  ┌─────────────────────┐  ┌────────────────────────────────┐   │
│  │ ChromaDB            │  │ videos.json                     │   │
│  │ (Vector Database)   │  │ (Metadata Storage)              │   │
│  │                     │  │                                 │   │
│  │ • Embeddings        │  │ • Video ID                      │   │
│  │ • Text chunks       │  │ • Title                         │   │
│  │ • Metadata          │  │ • URL                           │   │
│  │ • Similarity index  │  │ • Date added                    │   │
│  └─────────────────────┘  └────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                   EXTERNAL APIS                                 │
│                                                                  │
│  • YouTube (yt-dlp)      → Transcript extraction                │
│  • Voyage AI             → Embedding generation (1024-dim)      │
│  • Google Gemini         → Answer generation (free tier)        │
│  • Anthropic Claude      → Alternative LLM (paid)               │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Module-by-Module Code Breakdown

### Module 1: Configuration Management (`src/config.py`)

**Purpose:** Centralized configuration for API keys, environment handling

**Key Innovation:** Dual-environment support (local `.env` + Streamlit Cloud)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Try to import Streamlit (available on cloud, not always local)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def _get_secret(key: str) -> str:
    """
    Smart secret retrieval that works in both environments:
    - Local development: Reads from .env file via os.getenv()
    - Streamlit Cloud: Reads from st.secrets (TOML format)

    This pattern enables:
    1. Easy local testing without modifying code
    2. Secure cloud deployment without exposing secrets
    3. Single codebase for both environments
    """
    # Try Streamlit secrets first (cloud deployment)
    if HAS_STREAMLIT:
        try:
            if key in st.secrets:
                return st.secrets[key]  # Dictionary access
        except (AttributeError, FileNotFoundError, KeyError):
            pass

    # Fall back to environment variables (local development)
    return os.getenv(key)

# API Keys with validation
def get_gemini_api_key() -> str:
    api_key = _get_secret("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Set it in .env (local) or Streamlit secrets (cloud)"
        )
    return api_key

# Configuration with defaults
GEMINI_MODEL = _get_secret("GEMINI_MODEL") or "gemini-2.5-flash"
CHUNK_SIZE = int(_get_secret("CHUNK_SIZE") or "1000")
CHUNK_OVERLAP = int(_get_secret("CHUNK_OVERLAP") or "200")
```

**Key Learnings:**
- **Why dual environment?** Local dev needs `.env`, cloud needs `st.secrets`
- **Why validation?** Fail fast with clear error messages
- **Why defaults?** Sensible fallbacks if user doesn't configure

---

### Module 2: Transcript Extraction (`src/transcript_extractor.py`)

**Purpose:** Extract text transcripts from YouTube videos

**How yt-dlp Works:**
1. Parse YouTube URL → Extract video ID
2. Make API request to YouTube → Get video metadata
3. Download subtitle files (VTT, JSON, or SRT format)
4. Parse subtitle content → Extract text

```python
import yt_dlp

def extract_transcript(youtube_url: str) -> str:
    """
    Extract transcript from YouTube video without downloading video file.

    How it works:
    1. yt-dlp fetches video metadata from YouTube
    2. Checks for available subtitles (manual or auto-generated)
    3. Downloads subtitle file (preferably JSON format)
    4. Parses subtitle content to extract text
    5. Returns concatenated transcript
    """

    # Configure yt-dlp options
    ydl_opts = {
        'skip_download': True,  # We only want subtitles, not the video
        'writesubtitles': True,  # Enable subtitle extraction
        'writeautomaticsub': True,  # Include auto-generated if no manual
        'subtitleslangs': ['en'],  # Prefer English
        'quiet': True,  # Suppress console output
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info (makes HTTP request to YouTube)
            info_dict = ydl.extract_info(youtube_url, download=False)

            # Get available subtitles
            subtitles = info_dict.get('subtitles', {})
            automatic_captions = info_dict.get('automatic_captions', {})

            # Priority: Manual subtitles > Auto-generated
            subtitle_data = None
            if 'en' in subtitles:
                subtitle_data = subtitles['en']  # More accurate
            elif 'en' in automatic_captions:
                subtitle_data = automatic_captions['en']  # Fallback
            else:
                raise RuntimeError("No English transcript available")

            # Find JSON format (easiest to parse)
            json_subtitle = next(
                (s for s in subtitle_data if s.get('ext') == 'json3'),
                subtitle_data[0]  # Fallback to first format
            )

            # Download subtitle content
            subtitle_url = json_subtitle.get('url')
            subtitle_content = ydl.urlopen(subtitle_url).read().decode('utf-8')

            # Parse based on format
            transcript_text = _parse_subtitle_content(
                subtitle_content,
                json_subtitle.get('ext')
            )

            return transcript_text

    except yt_dlp.utils.DownloadError as e:
        # Handle specific errors (404, 403, 429)
        if "429" in str(e):
            raise RuntimeError("Rate limited. Wait a few minutes.")
        elif "404" in str(e):
            raise ValueError("Video not found. Check URL.")
        # ... more error handling

def _parse_subtitle_content(content: str, format_ext: str) -> str:
    """
    Parse subtitle content based on format.

    Formats:
    - JSON3: YouTube's JSON with events and segments
    - VTT: WebVTT with timestamps
    - SRT: SubRip with numbered entries
    """
    import json

    if format_ext == 'json3':
        # Parse JSON structure
        data = json.loads(content)
        transcript_parts = []

        # Extract text from segments
        for event in data.get('events', []):
            for segment in event.get('segs', []):
                text = segment.get('utf8', '').strip()
                if text:
                    transcript_parts.append(text)

        return ' '.join(transcript_parts)

    elif format_ext in ['vtt', 'srv3']:
        # Parse VTT format (remove timestamps)
        lines = content.split('\n')
        transcript_parts = []

        for line in lines:
            line = line.strip()
            # Skip headers, timestamps, and empty lines
            if line and not line.startswith('WEBVTT') and '-->' not in line:
                transcript_parts.append(line)

        return ' '.join(transcript_parts)

    # ... more format handling
```

**Key Learnings:**
- **Why yt-dlp?** More reliable than YouTube Data API, no quota limits
- **Why prioritize manual subtitles?** More accurate than auto-generated
- **Why JSON format?** Easiest to parse programmatically

---

### Module 3: Text Chunking (`src/text_chunker.py`)

**Purpose:** Split transcript into manageable chunks with context preservation

**The Chunking Problem:**
- Too large → Retrieval is imprecise (finds irrelevant text)
- Too small → Loses context (incomplete sentences)
- No overlap → Context lost at boundaries

**Solution:** Fixed-size chunks with overlap

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Split text into chunks with overlap for context preservation.

    How it works:
    1. Try to split at natural boundaries (paragraphs, sentences)
    2. If still too large, split at word boundaries
    3. Maintain overlap between consecutive chunks

    Example with chunk_size=20, overlap=5:
    Original: "The quick brown fox jumps over the lazy dog"

    Chunk 1: "The quick brown fox " (0-20)
    Chunk 2: "fox jumps over the " (15-35) ← 5 char overlap with Chunk 1
    Chunk 3: "the lazy dog"         (30-42) ← 5 char overlap with Chunk 2
    """

    # RecursiveCharacterTextSplitter tries multiple split strategies
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Priority order
    )

    chunks = text_splitter.split_text(text)

    return chunks
```

**Visual Example:**

```
Original Transcript (3000 characters):
┌────────────────────────────────────────────────────────────┐
│ "In this lecture, we'll discuss neural networks. Neural    │
│  networks are inspired by biological neurons. They consist │
│  of layers of interconnected nodes. Each node performs..."  │
└────────────────────────────────────────────────────────────┘

After Chunking (size=1000, overlap=200):

Chunk 0 (0-1000):
┌────────────────────────────────────────────────────────────┐
│ "In this lecture, we'll discuss neural networks. Neural    │
│  networks are inspired by biological neurons. They consist │
│  of layers..." [continues to 1000 chars]                   │
└────────────────────────────────────────────────────────────┘

Chunk 1 (800-1800):  ← 200 char overlap
┌────────────────────────────────────────────────────────────┐
│ "...of layers of interconnected nodes. Each node performs  │
│  a simple computation. The power comes from..." [continues]│
└────────────────────────────────────────────────────────────┘

Chunk 2 (1600-2600):  ← 200 char overlap
┌────────────────────────────────────────────────────────────┐
│ "...from combining many simple computations. Training..."  │
└────────────────────────────────────────────────────────────┘
```

**Why Overlap Matters:**

```
Without Overlap:
Chunk 1: "...the activation function is very import"
Chunk 2: "ant for non-linearity. It allows..."
❌ "important" split across chunks - context lost

With Overlap (200 chars):
Chunk 1: "...the activation function is very important for non-"
Chunk 2: "important for non-linearity. It allows neural networks..."
✅ Both chunks have complete context
```

---

### Module 4: Embedding and Vector Storage (`src/embedding_manager.py`)

**Purpose:** Convert text to vectors and enable semantic search

**What are Embeddings?**

Embeddings transform text into high-dimensional vectors (arrays of numbers) where semantically similar text has similar vectors.

```python
# Conceptual example (actual embeddings are 1024 dimensions)
"neural network" → [0.8, 0.3, -0.5, 0.1, ...]
"deep learning"  → [0.7, 0.4, -0.4, 0.2, ...]  ← Similar!
"banana recipe"  → [-0.2, -0.8, 0.9, -0.3, ...] ← Different!
```

**Full Implementation:**

```python
import chromadb
import voyageai
from typing import List, Dict, Any

class EmbeddingManager:
    """
    Manages embedding creation (Voyage AI) and vector storage (ChromaDB).

    Key Concepts:
    1. Embeddings: Text → 1024-dimensional vectors
    2. Vector Database: Efficient similarity search over embeddings
    3. Metadata: Associate chunks with source video information
    """

    def __init__(self):
        # Initialize Voyage AI for creating embeddings
        self.voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)
        self.voyage_model = "voyage-3"  # Latest model, 1024 dimensions

        # ChromaDB client (initialized later)
        self.chroma_client = None
        self.collection = None

    def initialize_chromadb(self):
        """
        Set up persistent vector database.

        ChromaDB Concepts:
        - PersistentClient: Saves data to disk (vs in-memory)
        - Collection: Group of embeddings (like a table)
        - get_or_create: Loads existing or creates new
        """
        # Create persistent client (data survives restarts)
        self.chroma_client = chromadb.PersistentClient(
            path="./data/chroma_db"
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="youtube_transcripts",
            metadata={"description": "YouTube video embeddings"}
        )

        print(f"ChromaDB ready with {self.collection.count()} embeddings")

    def add_video_chunks(
        self,
        video_id: str,
        chunks: List[str],
        video_title: str
    ) -> int:
        """
        Embed and store video chunks.

        Process:
        1. Check if video already exists (avoid duplicates)
        2. Create embeddings for all chunks (batch API call)
        3. Store embeddings + text + metadata in ChromaDB
        """

        # Check for duplicates
        existing = self.collection.get(where={"video_id": video_id})
        if existing and existing["ids"]:
            print(f"Video {video_id} already processed")
            return 0

        # Create embeddings (batch operation for efficiency)
        print(f"Creating embeddings for {len(chunks)} chunks...")
        result = self.voyage_client.embed(
            texts=chunks,
            model=self.voyage_model,
            input_type="document"  # Optimized for storing documents
        )
        embeddings = result.embeddings  # List of 1024-dim vectors

        # Prepare data for storage
        ids = [f"{video_id}:{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "video_id": video_id,
                "video_title": video_title,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        # Store in ChromaDB
        self.collection.add(
            ids=ids,                  # Unique identifiers
            embeddings=embeddings,    # 1024-dim vectors
            documents=chunks,         # Original text
            metadatas=metadatas       # Source information
        )

        print(f"✓ Added {len(chunks)} chunks to database")
        return len(chunks)

    def search_similar_chunks(
        self,
        question: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Find chunks most similar to the question.

        How Semantic Search Works:
        1. Embed the question using same model
        2. Compare question embedding to all stored embeddings
        3. Use cosine similarity as distance metric
        4. Return top N most similar chunks

        Cosine Similarity:
        - Measures angle between vectors (not magnitude)
        - Range: -1 to 1 (1 = identical, 0 = orthogonal)
        - Perfect for text: "ML" and "machine learning" → high similarity
        """

        # Embed the question
        result = self.voyage_client.embed(
            texts=[question],
            model=self.voyage_model,
            input_type="query"  # Optimized for search queries
        )
        query_embedding = result.embeddings[0]

        # Search ChromaDB for similar embeddings
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],  # Lower = more similar
                "similarity": 1 - results["distances"][0][i]  # Higher = more similar
            })

        return formatted_results
```

**How ChromaDB Stores Data:**

```
Collection: "youtube_transcripts"
┌──────────────┬─────────────────────────────┬───────────────────┬─────────────────┐
│ ID           │ Embedding (1024-dim vector) │ Document (text)   │ Metadata        │
├──────────────┼─────────────────────────────┼───────────────────┼─────────────────┤
│ abc123:0     │ [0.23, -0.45, 0.78, ...]   │ "Neural networks" │ {video_id: ..., │
│              │                             │ "are inspired..." │  chunk_index: 0}│
├──────────────┼─────────────────────────────┼───────────────────┼─────────────────┤
│ abc123:1     │ [0.19, -0.52, 0.81, ...]   │ "Deep learning"   │ {video_id: ..., │
│              │                             │ "uses multiple"   │  chunk_index: 1}│
├──────────────┼─────────────────────────────┼───────────────────┼─────────────────┤
│ xyz789:0     │ [-0.12, 0.34, -0.21, ...]  │ "Calculus is..."  │ {video_id: ..., │
│              │                             │                   │  chunk_index: 0}│
└──────────────┴─────────────────────────────┴───────────────────┴─────────────────┘
```

**Semantic Search Visualization:**

```
Question: "What is backpropagation?"
   ↓
Embed question: [0.22, -0.48, 0.76, ...]
   ↓
Compare to all stored embeddings:

Chunk 1: "Neural networks..."
Embedding: [0.23, -0.45, 0.78, ...]
Cosine Similarity: 0.95 ✓ (Very similar!)

Chunk 2: "Deep learning..."
Embedding: [0.19, -0.52, 0.81, ...]
Cosine Similarity: 0.89 ✓ (Similar)

Chunk 3: "Calculus is..."
Embedding: [-0.12, 0.34, -0.21, ...]
Cosine Similarity: 0.12 ✗ (Not similar)

   ↓
Return top 5 chunks sorted by similarity:
1. Chunk 1 (0.95)
2. Chunk 2 (0.89)
3. ... (top 5 total)
```

---

### Module 5: Question Answering (`src/question_answerer.py`)

**Purpose:** Generate answers using retrieved context + LLM

**Key Concept: RAG (Retrieval-Augmented Generation)**

```python
from anthropic import Anthropic
import google.generativeai as genai

class QuestionAnswerer:
    """
    Implements RAG: Retrieval + Augmentation + Generation

    Why RAG vs. Just Using Claude/Gemini:
    - Prevents hallucinations (LLM can only use provided context)
    - Provides source attribution (know where answer came from)
    - Always up-to-date (your latest videos, not training cutoff)
    - Domain-specific (your content, not general knowledge)
    """

    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager

        # Initialize Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.provider = "gemini"

    def _construct_prompt(self, question: str, context_chunks: List[Dict]) -> str:
        """
        Build prompt with retrieved context.

        Prompt Engineering Principles:
        1. Clear role definition
        2. Context before question
        3. Explicit constraints (use ONLY provided context)
        4. Handle uncertainty (say when info is missing)
        5. Request citations
        """

        # Format context chunks
        context_text = "\n\n".join([
            f"[Source {i+1} - {chunk['metadata']['video_title']}]:\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])

        # Construct prompt
        prompt = f"""You are a helpful assistant that answers questions based on YouTube video transcripts.

IMPORTANT RULES:
1. Answer ONLY based on the provided context below
2. If the context doesn't contain enough information, say "I don't have enough information to answer this question"
3. Cite which source(s) you used in your answer
4. Be concise but complete

CONTEXT FROM YOUTUBE VIDEOS:
{context_text}

USER QUESTION:
{question}

YOUR ANSWER:"""

        return prompt

    def answer_question(
        self,
        question: str,
        n_chunks: int = 5
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline:
        1. Retrieve relevant chunks
        2. Augment prompt with context
        3. Generate answer with LLM

        Returns answer + sources + metadata
        """

        # STEP 1: RETRIEVAL
        print(f"\n🔍 Searching for relevant content...")
        context_chunks = self.embedding_manager.search_similar_chunks(
            question=question,
            n_results=n_chunks
        )

        if not context_chunks:
            return {
                "answer": "No relevant information found in the database.",
                "sources": [],
                "model": self.model
            }

        # Show retrieved chunks
        print(f"✓ Found {len(context_chunks)} relevant chunks")
        for i, chunk in enumerate(context_chunks):
            sim = chunk['similarity']
            title = chunk['metadata']['video_title']
            print(f"  {i+1}. {title} (similarity: {sim:.3f})")

        # STEP 2: AUGMENTATION (construct prompt)
        prompt = self._construct_prompt(question, context_chunks)

        # STEP 3: GENERATION
        print(f"\n🤖 Generating answer using {self.provider}...")

        if self.provider == "gemini":
            # Use Gemini
            response = self.model.generate_content(prompt)
            answer_text = response.text

        elif self.provider == "anthropic":
            # Use Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            answer_text = response.content[0].text

        print("✓ Answer generated")

        # Return complete result
        return {
            "answer": answer_text,
            "sources": context_chunks,
            "model": self.model,
            "provider": self.provider
        }
```

**RAG Flow Visualization:**

```
User asks: "What is gradient descent?"

┌─────────────────────────────────────────────────────────────┐
│ STEP 1: RETRIEVAL (Semantic Search)                         │
├─────────────────────────────────────────────────────────────┤
│ Embed question → [0.34, -0.21, ...]                        │
│ Search ChromaDB → Find top 5 similar chunks:                │
│                                                              │
│ Chunk 1: "Gradient descent is an optimization algorithm..." │
│          Similarity: 0.94                                    │
│                                                              │
│ Chunk 2: "To minimize loss, we calculate gradients..."      │
│          Similarity: 0.87                                    │
│                                                              │
│ ... (3 more chunks)                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: AUGMENTATION (Build Prompt)                         │
├─────────────────────────────────────────────────────────────┤
│ You are a helpful assistant...                              │
│                                                              │
│ CONTEXT:                                                     │
│ [Source 1]: "Gradient descent is an optimization..."        │
│ [Source 2]: "To minimize loss, we calculate..."             │
│ ...                                                          │
│                                                              │
│ QUESTION: What is gradient descent?                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: GENERATION (LLM Creates Answer)                     │
├─────────────────────────────────────────────────────────────┤
│ Gemini/Claude reads context and generates:                  │
│                                                              │
│ "Gradient descent is an optimization algorithm used to      │
│  minimize the loss function in machine learning models.     │
│  It works by calculating gradients and iteratively          │
│  updating parameters in the direction that reduces loss.    │
│  (Source: Video 'ML Basics', Chunk 12)"                     │
└─────────────────────────────────────────────────────────────┘
```

---

### Module 6: Complete Pipeline (`src/pipeline.py`)

**Purpose:** Orchestrate the entire RAG system

```python
from src.transcript_extractor import extract_transcript
from src.text_chunker import chunk_text
from src.embedding_manager import EmbeddingManager
from src.question_answerer import QuestionAnswerer
from src.metadata_manager import MetadataManager

class Pipeline:
    """
    End-to-end RAG pipeline orchestration.

    Handles:
    1. Video processing (URL → chunks in database)
    2. Question answering (question → answer + sources)
    """

    def __init__(self):
        # Initialize components
        self.embedding_manager = EmbeddingManager()
        self.embedding_manager.initialize_chromadb()

        self.question_answerer = QuestionAnswerer(self.embedding_manager)
        self.metadata_manager = MetadataManager()

    def process_video(self, youtube_url: str, custom_title: str = None):
        """
        Complete video processing pipeline.

        Steps:
        1. Extract video ID from URL
        2. Fetch transcript using yt-dlp
        3. Chunk transcript (1000 chars, 200 overlap)
        4. Generate embeddings (Voyage AI)
        5. Store in ChromaDB
        6. Save metadata
        """

        print("\n" + "="*70)
        print("VIDEO PROCESSING PIPELINE")
        print("="*70)

        # Extract video ID from URL
        import re
        match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})', youtube_url)
        if not match:
            raise ValueError("Invalid YouTube URL")
        video_id = match.group(1)

        print(f"\n1️⃣ Extracting transcript...")
        transcript = extract_transcript(youtube_url)
        print(f"✓ Transcript extracted ({len(transcript)} characters)")

        print(f"\n2️⃣ Chunking text...")
        chunks = chunk_text(transcript, chunk_size=1000, chunk_overlap=200)
        print(f"✓ Created {len(chunks)} chunks")

        print(f"\n3️⃣ Generating embeddings and storing in database...")
        num_added = self.embedding_manager.add_video_chunks(
            video_id=video_id,
            chunks=chunks,
            video_title=custom_title or video_id
        )

        print(f"\n4️⃣ Saving metadata...")
        self.metadata_manager.add_video({
            "video_id": video_id,
            "title": custom_title or video_id,
            "url": youtube_url,
            "chunks_count": num_added
        })

        print("\n" + "="*70)
        print("✅ VIDEO PROCESSING COMPLETE")
        print("="*70)

        return {
            "video_id": video_id,
            "chunks_count": num_added,
            "transcript_length": len(transcript)
        }

    def answer_question(self, question: str, n_chunks: int = 5):
        """
        Answer question using RAG.

        Steps:
        1. Search for similar chunks (semantic search)
        2. Construct prompt with context
        3. Generate answer with LLM
        4. Return answer + sources
        """

        result = self.question_answerer.answer_question(
            question=question,
            n_chunks=n_chunks
        )

        return result
```

---

## 🎨 User Interface (Streamlit)

**Key Pages:**

### 1. Chat Page
```python
import streamlit as st
from src.pipeline import Pipeline

st.title("💬 Chat with Videos")

# Initialize pipeline
pipeline = Pipeline()

# Chat input
if question := st.chat_input("Ask a question about your videos"):
    # Display user message
    with st.chat_message("user"):
        st.write(question)

    # Get answer
    with st.spinner("Thinking..."):
        result = pipeline.answer_question(question)

    # Display AI response
    with st.chat_message("assistant"):
        st.write(result["answer"])

        # Show sources
        st.markdown("### 📚 Sources:")
        for i, source in enumerate(result["sources"], 1):
            with st.expander(f"Source {i}: {source['metadata']['video_title']}"):
                st.write(f"**Similarity:** {source['similarity']:.3f}")
                st.write(source["text"])
```

### 2. Add Video Page
```python
st.title("📥 Add New Video")

url = st.text_input("YouTube URL")
title = st.text_input("Custom Title (optional)")

if st.button("🚀 Process Video"):
    with st.spinner("Processing video..."):
        try:
            result = pipeline.process_video(url, title)
            st.success(f"✅ Video processed! {result['chunks_count']} chunks created")
        except Exception as e:
            st.error(f"Error: {e}")
```

---

## 🔄 Complete Data Flow Example

Let's walk through processing a video and answering a question:

### Example: "3Blue1Brown - Neural Networks"

**PART 1: Processing Video**

```
User Input:
  URL: https://www.youtube.com/watch?v=aircAruvnKk

Step 1: Extract Transcript
  yt-dlp fetches subtitle data → 14,268 characters of text

Step 2: Chunk Text
  RecursiveCharacterTextSplitter creates 14 chunks:

  Chunk 0 (0-1000 chars):
    "But what is a neural network? To learn about neural networks..."

  Chunk 1 (800-1800 chars):
    "...networks, we'll start with a neuron. The basic unit..."

  ... (12 more chunks)

Step 3: Create Embeddings
  Voyage AI API call:
    Input: 14 text chunks
    Output: 14 × 1024-dimensional vectors

  Example (conceptual, actual is 1024-dim):
    Chunk 0: [0.234, -0.156, 0.891, 0.023, ...]
    Chunk 1: [0.198, -0.201, 0.867, 0.045, ...]

Step 4: Store in ChromaDB
  Database entries:
    ID: "aircAruvnKk:0", Embedding: [...], Document: "But what...", Metadata: {video_id, chunk_index}
    ID: "aircAruvnKk:1", Embedding: [...], Document: "...networks, we'll...", Metadata: {...}
    ... (14 entries total)

Step 5: Save Metadata
  videos.json updated:
    {
      "video_id": "aircAruvnKk",
      "title": "But what is a neural network?",
      "url": "https://...",
      "chunks": 14,
      "date_added": "2025-12-05"
    }

✅ Processing complete! Video ready for querying.
```

**PART 2: Answering Question**

```
User Question: "How do neural networks learn?"

Step 1: Embed Question
  Voyage AI creates embedding:
    [0.267, -0.189, 0.823, 0.056, ...]  (1024 dimensions)

Step 2: Semantic Search
  ChromaDB compares question embedding to all stored embeddings:

  Results (sorted by similarity):
    1. Chunk 8 from "aircAruvnKk" - Similarity: 0.94
       "...networks learn through backpropagation. This involves..."

    2. Chunk 5 from "aircAruvnKk" - Similarity: 0.89
       "...adjusting weights based on error. The learning process..."

    3. Chunk 12 from "aircAruvnKk" - Similarity: 0.85
       "...gradient descent optimizes the network parameters..."

    ... (top 5 total)

Step 3: Construct Prompt
  System message + Retrieved chunks + Question:

  """
  You are a helpful assistant...

  CONTEXT:
  [Source 1 - But what is a neural network?]:
  networks learn through backpropagation. This involves...

  [Source 2 - But what is a neural network?]:
  adjusting weights based on error. The learning process...

  [Source 3 - But what is a neural network?]:
  gradient descent optimizes the network parameters...

  QUESTION: How do neural networks learn?
  """

Step 4: Generate Answer
  Google Gemini processes prompt and generates:

  "Neural networks learn through a process called backpropagation,
   which involves adjusting the weights based on the error between
   predicted and actual outputs. This learning process uses gradient
   descent to optimize the network parameters iteratively.

   (Sources: Video 'But what is a neural network?', Chunks 8, 5, 12)"

Step 5: Return Result
  {
    "answer": "Neural networks learn through...",
    "sources": [
      {
        "text": "networks learn through backpropagation...",
        "metadata": {"video_id": "aircAruvnKk", "chunk_index": 8},
        "similarity": 0.94
      },
      ... (4 more sources)
    ],
    "model": "gemini-2.5-flash",
    "provider": "gemini"
  }
```

---

## 🎓 Key Learnings for LLMs

### 1. **RAG Architecture**
- **Retrieval:** Semantic search finds relevant information
- **Augmentation:** Context is added to the prompt
- **Generation:** LLM creates grounded answer

### 2. **Vector Embeddings**
- Transform text → high-dimensional vectors
- Similar meaning → similar vectors
- Enable semantic search (meaning-based, not keyword-based)

### 3. **ChromaDB Concepts**
- **Collection:** Group of embeddings with metadata
- **Persistent Storage:** Data survives restarts
- **Similarity Search:** Cosine distance finds nearest neighbors

### 4. **Prompt Engineering**
- Clear instructions ("ONLY use provided context")
- Context before question
- Explicit constraints prevent hallucinations

### 5. **Chunking Strategy**
- Balance: Too large (imprecise) vs. too small (no context)
- Overlap preserves context at boundaries
- Optimal: 1000 chars, 200 overlap (for this use case)

### 6. **Dual Environment Pattern**
- Single codebase works locally AND in cloud
- Smart secret management (`.env` vs `st.secrets`)
- Critical for production deployment

---

## 📈 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Extract transcript | 5-10s | Depends on video length |
| Chunk text (15min video) | <1s | CPU operation, very fast |
| Generate embeddings (20 chunks) | 2-4s | API latency |
| Store in ChromaDB | <1s | Local disk write |
| Semantic search | <100ms | Efficient vector index (HNSW) |
| LLM generation | 2-4s | API latency |
| **Total (process video)** | **30-45s** | For typical 15min video |
| **Total (answer question)** | **2-4s** | End-to-end query |

---

## 💡 Why This Architecture Works

1. **Modular Design:** Each component has single responsibility
2. **Scalability:** Can swap ChromaDB → Pinecone for cloud scale
3. **Cost-Effective:** Entirely on free tiers
4. **Flexible:** Easy to add new LLM providers
5. **Production-Ready:** Error handling, validation, logging

---

**End of Overview**

This document provides a complete understanding of the YouTube RAG Chatbot architecture, implementation, and key concepts for teaching LLM models about retrieval-augmented generation systems.
