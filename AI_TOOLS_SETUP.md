# AI Tools Setup Summary

## Tool Selection and Rationale

### 1. Google Gemini 2.5 Flash (Primary LLM)

**Purpose:** Generate natural language answers based on retrieved context

**Why Chosen:**
- **Free Tier Available:** 15 requests/minute, 1M tokens/day - perfect for development and class projects
- **Performance:** Fast response times (2-3 seconds average)
- **Quality:** Comparable to GPT-3.5, sufficient for RAG applications
- **Multimodal Capable:** Supports text and images (future expansion possibility)
- **Google Integration:** Easy authentication and well-documented API

**Alternatives Considered:**
- Anthropic Claude 3.5 Sonnet (better quality but requires paid credits)
- OpenAI GPT-4 (expensive, $10 per 1M input tokens)

**Setup Process:**
1. Created Google AI Studio account at https://makersuite.google.com
2. Generated API key from API Keys section
3. Added to `.env` file: `GEMINI_API_KEY=your_key_here`
4. Installed SDK: `pip install google-generativeai==0.8.3`
5. Tested with simple prompt to verify connection

**Challenges:**
- Initial confusion between Gemini model names (gemini-1.5-flash vs gemini-2.5-flash)
- Rate limiting required implementing retry logic with exponential backoff

---

### 2. Voyage AI (Embedding Model)

**Purpose:** Convert text chunks into 1024-dimensional vector embeddings for semantic search

**Why Chosen:**
- **Best-in-Class Quality:** Outperforms OpenAI embeddings on MTEB benchmark
- **Optimized for RAG:** voyage-3 model specifically designed for retrieval tasks
- **Generous Free Tier:** 30M tokens free (enough for 500+ videos)
- **High Dimensionality:** 1024 dimensions capture nuanced semantic meaning
- **Fast:** Processes 1000 chunks in ~30 seconds

**Alternatives Considered:**
- OpenAI text-embedding-3-small (good but more expensive after free tier)
- Cohere Embed v3 (comparable but less proven for RAG)
- Sentence Transformers (free but requires local GPU, slower)

**Setup Process:**
1. Signed up at https://www.voyageai.com/
2. Obtained API key from dashboard
3. Added to `.env`: `VOYAGE_API_KEY=your_key_here`
4. Installed SDK: `pip install voyageai==0.3.5`
5. Tested embedding generation with sample text

**Challenges:**
- API documentation initially unclear about batch processing
- Had to implement chunking for large documents (max 128 texts per request)
- Rate limiting required careful batching strategy

---

### 3. ChromaDB (Vector Database)

**Purpose:** Store and retrieve vector embeddings with semantic similarity search

**Why Chosen:**
- **Zero Configuration:** Works out-of-the-box with no server setup
- **Persistent Storage:** Saves embeddings to disk for reuse across sessions
- **Python Native:** Seamless integration with Python ecosystem
- **Open Source:** No API costs, fully local
- **LangChain Compatible:** First-class integration with LangChain

**Alternatives Considered:**
- Pinecone (cloud-based but requires account, 1M free vectors)
- Weaviate (more complex setup, overkill for this project)
- FAISS (Facebook's library, no metadata support)

**Setup Process:**
1. Installed: `pip install chromadb==1.3.5`
2. Created persistent directory: `./data/chroma_db`
3. Initialized collection with Voyage embeddings
4. Configured similarity search with cosine distance

**Challenges:**
- **Major Challenge:** ChromaDB doesn't persist in Streamlit Cloud ephemeral storage
  - Solved for local development, cloud persistence remains a limitation
  - Users must re-process videos after app restarts on cloud
- Understanding collection vs. database terminology
- Optimizing query parameters (n_results, where filters)

---

### 4. LangChain (RAG Framework)

**Purpose:** Orchestrate the RAG pipeline (text splitting, retrieval, prompt generation)

**Why Chosen:**
- **Industry Standard:** Most popular RAG framework
- **Comprehensive:** Includes text splitters, vector store integrations, LLM chains
- **Abstractions:** Simplifies complex RAG workflows
- **Active Development:** Regular updates and community support
- **Modular:** Can use only needed components

**Alternatives Considered:**
- LlamaIndex (similar but less mature)
- Building from scratch (time-consuming, reinventing the wheel)

**Setup Process:**
1. Installed core: `pip install langchain==0.3.27`
2. Installed community integrations: `pip install langchain-community==0.3.31`
3. Imported specific modules (RecursiveCharacterTextSplitter, PromptTemplate)

**Challenges:**
- **Dependency Conflict:** langchain-community required numpy≥2.1.0, Streamlit 1.31.1 required numpy<2
  - Solution: Upgraded Streamlit to 1.40.2
- Steep learning curve understanding abstractions (Chains, Retrievers, Memory)
- Documentation sometimes outdated for latest version

---

### 5. yt-dlp (YouTube Transcript Extraction)

**Purpose:** Extract transcripts from YouTube videos

**Why Chosen:**
- **Reliable:** Maintained fork of youtube-dl with active development
- **Comprehensive:** Handles various transcript formats (auto-generated, manual, translated)
- **Fast:** Fetches transcripts without downloading video files
- **Free:** No API key required, no rate limits

**Alternatives Considered:**
- YouTube Transcript API (Python library, less robust)
- youtube-dl (original project, slower updates)
- Official YouTube Data API (requires API key, quota limits)

**Setup Process:**
1. Installed: `pip install yt-dlp==2025.10.14`
2. Tested with sample video to extract transcript
3. Handled cases: no transcript, auto-generated only, multiple languages

**Challenges:**
- Some videos don't have transcripts (livestreams, music videos)
- Auto-generated transcripts have timing inconsistencies
- Occasional HTTP 429 errors (rate limiting) required retry logic

---

### 6. Streamlit (Web Framework)

**Purpose:** Build interactive web interface for the chatbot

**Why Chosen:**
- **Python-Native:** No JavaScript required
- **Rapid Development:** Beautiful UI in minimal code
- **Free Deployment:** Streamlit Community Cloud hosting
- **Components:** Built-in chat interface, file uploaders, forms
- **Secrets Management:** Built-in support for API keys

**Alternatives Considered:**
- Flask/FastAPI + React (more flexible but 10x development time)
- Gradio (simpler but less customizable)

**Setup Process:**
1. Installed: `pip install streamlit==1.40.2` (upgraded from 1.31.1)
2. Created multi-page app structure
3. Added custom CSS for styling
4. Deployed to Streamlit Cloud

**Challenges:**
- **Critical Issue:** Streamlit Cloud uses `st.secrets` instead of `os.getenv()`
  - Solution: Created `_get_secret()` helper to support both environments
  - Refactored entire `config.py` for dual compatibility
- Understanding session state for chat history
- Custom CSS styling limitations (some Streamlit elements hard to override)

---

## Development Environment Setup

**Operating System:** macOS (also tested on Windows)

**Python Version:** 3.9.18 (installed via Homebrew)

**Virtual Environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

**IDE:** Visual Studio Code with Python extension

**Version Control:** Git + GitHub for repository hosting

---

## Setup Time Breakdown

| Component | Setup Time | Challenges Encountered |
|-----------|-----------|------------------------|
| Python & Venv | 15 min | None |
| Google Gemini | 20 min | Model name confusion |
| Voyage AI | 15 min | Batch processing docs unclear |
| ChromaDB | 30 min | Persistence in cloud |
| LangChain | 45 min | Dependency conflicts |
| yt-dlp | 10 min | Transcript availability |
| Streamlit | 60 min | Secrets management on cloud |
| **Total** | **3 hours** | |

---

## Key Learnings from Setup

1. **Free Tiers Are Viable:** Entire project runs on free API tiers - proof that cost isn't a barrier to learning AI
2. **Dependency Management Is Critical:** numpy conflict taught me importance of version pinning
3. **Environment Differences Matter:** Local vs. cloud deployment requires different configurations
4. **Documentation Quality Varies:** Some tools (Streamlit) have excellent docs, others (Voyage) need improvement
5. **Start Simple, Then Optimize:** Used default parameters first, optimized later based on results

---

**Total Setup Cost:** $0
**Ongoing Costs:** $0 (within free tier limits)

---

**Last Updated:** December 2025
