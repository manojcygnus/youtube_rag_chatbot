# Final Project Report
## YouTube RAG Chatbot with AI-Powered Question Answering

**Project Duration:** 6 weeks (November - December 2025)
**Live Demo:** https://youtuberagchatbot-flmdrbr3vqgdmavdmk6mcv.streamlit.app
**GitHub Repository:** https://github.com/manojcygnus/youtube_rag_chatbot

---

## 1. Project Overview

### 1.1 Motivation and Problem Statement

With the explosion of educational content on YouTube, learners face a significant challenge: finding specific information within long videos. Traditional approaches require:
- Watching entire videos (time-consuming)
- Manually scanning transcripts (tedious)
- Relying on video chapters (not always available)
- Using Ctrl+F keyword search (misses semantic variations)

**The Problem:** How can we enable natural language question-answering over YouTube video content without requiring users to watch entire videos?

### 1.2 Solution: RAG-Powered Chatbot

This project implements a Retrieval-Augmented Generation (RAG) system that:
1. **Extracts** transcripts from YouTube videos
2. **Embeds** transcript chunks into semantic vector space
3. **Retrieves** relevant context based on user questions
4. **Generates** accurate answers grounded in source material
5. **Attributes** sources with similarity scores for transparency

**Key Innovation:** Unlike ChatGPT (which has static training data), this system grounds answers in specific video content, providing verifiable sources and always-current information.

### 1.3 Core Features

- ✅ **YouTube Transcript Extraction** - Automatic processing of any video with captions
- ✅ **Semantic Search** - Vector embeddings enable understanding of meaning, not just keywords
- ✅ **Multi-Video Search** - Query across entire video library or filter by specific video
- ✅ **Source Attribution** - Every answer shows which video chunks were used
- ✅ **Dual LLM Support** - Google Gemini (free) and Anthropic Claude (paid)
- ✅ **Web Interface** - Modern, mobile-responsive Streamlit application
- ✅ **Cloud Deployment** - Accessible from any device via public URL
- ✅ **Zero Cost** - Runs entirely on free API tiers

---

## 2. Methodology

### 2.1 RAG Architecture

**Retrieval-Augmented Generation (RAG)** combines the strengths of:
- **Retrieval:** Finding relevant information from a knowledge base
- **Generation:** Using LLMs to create natural language responses

**Our Pipeline:**
```
User Question
    ↓
[Embedding Generation] ← Voyage AI
    ↓
[Semantic Search] ← ChromaDB
    ↓
[Context Retrieval] (Top 5 most similar chunks)
    ↓
[Prompt Augmentation] (Question + Context)
    ↓
[Answer Generation] ← Google Gemini
    ↓
Response with Sources
```

### 2.2 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Language** | Python 3.9+ | Rich AI/ML ecosystem, rapid development |
| **Transcript Extraction** | yt-dlp | Reliable, no API limits, handles edge cases |
| **Text Processing** | LangChain | Industry standard for RAG pipelines |
| **Embeddings** | Voyage AI (voyage-3) | Best-in-class quality, 1024 dimensions |
| **Vector Database** | ChromaDB | Zero-config, persistent, Python-native |
| **LLM** | Google Gemini 2.5 Flash | Free tier, fast, sufficient quality |
| **Alternative LLM** | Anthropic Claude 3.5 Sonnet | Higher quality, paid option |
| **Web Framework** | Streamlit | Rapid UI development, built-in deployment |
| **Deployment** | Streamlit Community Cloud | Free hosting, auto-scaling |

### 2.3 System Architecture

**Modular Design:**
```
youtube-rag-chatbot/
├── src/
│   ├── config.py                 # Centralized configuration
│   ├── transcript_extractor.py   # YouTube API wrapper
│   ├── text_chunker.py           # Intelligent text splitting
│   ├── embedding_manager.py      # Voyage AI + ChromaDB
│   ├── metadata_manager.py       # Video metadata tracking
│   ├── question_answerer.py      # LLM integration (Gemini/Claude)
│   └── pipeline.py               # RAG orchestration
├── streamlit_app.py              # Web interface
├── main.py                       # CLI interface
└── data/
    ├── chroma_db/                # Vector storage
    └── videos.json               # Metadata
```

**Design Principles:**
- **Separation of Concerns:** Each module has single responsibility
- **Dependency Injection:** Components receive dependencies, not hardcoded
- **Configuration Management:** All settings in `.env` file
- **Error Handling:** Graceful degradation with user-friendly messages

---

## 3. Data Collection and Preprocessing

### 3.1 Transcript Extraction

**Source:** YouTube Auto-Generated or Manual Captions

**Process:**
1. Parse YouTube URL to extract video ID
2. Use yt-dlp to fetch available transcripts
3. Prefer manual captions over auto-generated
4. Handle multilingual transcripts (select English by default)

**Edge Cases Handled:**
- Videos without transcripts → Clear error message
- Age-restricted videos → Attempt extraction, fallback to error
- Deleted/private videos → Validate before processing

**Example Output:**
```json
{
  "video_id": "aircAruvnKk",
  "title": "But what is a neural network?",
  "transcript": "But what is a neural network? Well, to learn about neural networks...",
  "length": 14268,
  "language": "en"
}
```

### 3.2 Text Chunking Strategy

**Challenge:** LLMs have context length limits; embeddings work better on focused chunks

**Solution:** Recursive Character Text Splitting with Overlap

**Parameters:**
- **Chunk Size:** 1000 characters
  - **Rationale:** Balances context preservation with retrieval precision
  - **Testing:** Compared 500, 1000, 1500, 2000 chars → 1000 optimal
- **Chunk Overlap:** 200 characters
  - **Rationale:** Preserves context at chunk boundaries
  - **Prevents:** Information loss when concepts span chunk edges

**Example:**
```
Original Transcript (3000 chars)
    ↓
Chunk 1: chars 0-1000
Chunk 2: chars 800-1800    ← 200 char overlap with Chunk 1
Chunk 3: chars 1600-2600   ← 200 char overlap with Chunk 2
Chunk 4: chars 2400-3000   ← 200 char overlap with Chunk 3
```

**Metadata Preservation:**
```python
{
  "text": "chunk content...",
  "video_id": "aircAruvnKk",
  "video_title": "But what is a neural network?",
  "chunk_index": 3,
  "chunk_total": 14
}
```

### 3.3 Embedding Generation

**Model:** Voyage AI `voyage-3`
- **Dimensions:** 1024 (high semantic capture)
- **Input:** Text chunks (max 128 per batch)
- **Output:** Dense vectors representing semantic meaning

**Process:**
```python
# Pseudocode
chunks = ["chunk 1 text...", "chunk 2 text...", ...]
embeddings = voyage_client.embed(
    texts=chunks,
    model="voyage-3",
    input_type="document"
)
# Result: [[0.023, -0.145, ...], [0.089, 0.234, ...], ...]
```

**Optimization:**
- Batch processing (128 chunks at a time)
- Retry logic for API failures
- Progress tracking for large videos

### 3.4 Vector Storage

**Database:** ChromaDB
- **Collection:** `youtube_transcripts`
- **Distance Metric:** Cosine similarity
- **Persistence:** Local disk (`./data/chroma_db`)

**Storage Format:**
```python
collection.add(
    embeddings=[[0.023, -0.145, ...], ...],
    documents=["chunk text...", ...],
    metadatas=[{"video_id": "...", "chunk_index": 3}, ...],
    ids=["video_id_chunk_0", "video_id_chunk_1", ...]
)
```

---

## 4. AI Model Development

### 4.1 Embedding Model Selection

**Comparison Matrix:**

| Model | Dimensions | Cost | Quality (MTEB) | Choice |
|-------|------------|------|----------------|--------|
| Voyage-3 | 1024 | Free tier | 68.7 | ✅ **Selected** |
| OpenAI text-3-small | 1536 | $0.02/1M tokens | 62.3 | ❌ |
| Cohere Embed v3 | 1024 | $0.10/1M tokens | 64.5 | ❌ |

**Decision:** Voyage-3 offers best quality-to-cost ratio with generous free tier

### 4.2 LLM Selection

**Primary: Google Gemini 2.5 Flash**

**Pros:**
- Free tier: 15 RPM, 1M tokens/day
- Fast response (2-3 seconds)
- Good instruction following
- Adequate quality for RAG (grounded answers)

**Cons:**
- Less capable than GPT-4 or Claude Sonnet
- Occasional verbose responses

**Secondary: Anthropic Claude 3.5 Sonnet**

**Pros:**
- Superior reasoning and conciseness
- Better at following complex instructions
- More accurate answers

**Cons:**
- Paid only ($3/1M input tokens)
- Slower than Gemini

**Implementation:** Dual provider support with easy switching via configuration

### 4.3 Prompt Engineering

**System Prompt Template:**
```
You are a helpful assistant that answers questions based on YouTube video transcripts.

Rules:
1. Answer ONLY based on the provided context
2. If the context doesn't contain the answer, say "I don't have enough information"
3. Cite which chunks you used in your answer
4. Be concise but complete
5. If the context is ambiguous, acknowledge uncertainty

Context from YouTube Videos:
{retrieved_chunks}

User Question: {question}

Answer:
```

**Optimizations:**
- Explicit instruction to avoid hallucinations
- Request for source attribution
- Acknowledge when information is missing
- Concise response preference

---

## 5. UI Design and Integration

*(See detailed UI_DESIGN_REPORT.md for full analysis)*

### 5.1 Design Goals
- **Zero learning curve** - Intuitive without instructions
- **Trust signals** - Always show sources
- **Mobile-first** - Responsive design
- **Modern aesthetics** - Professional for portfolio

### 5.2 Key UI Features
- **Chat Interface** - Natural conversation flow
- **Source Attribution Panels** - Expandable with similarity scores
- **Video Management** - Add, view, delete videos
- **Statistics Dashboard** - System metrics and status
- **Mobile Optimized** - Works on phones/tablets

### 5.3 Technical Implementation
- **Framework:** Streamlit 1.40.2
- **Styling:** Custom CSS with glassmorphism and gradients
- **State Management:** Session state for chat history
- **Responsive:** Media queries for mobile/tablet/desktop

---

## 6. Testing and Refinement

*(See detailed USABILITY_TESTING_REPORT.md for full results)*

### 6.1 Testing Process
- **Participants:** 5 users (2 technical, 3 non-technical)
- **Duration:** 30 minutes per user
- **Tasks:** Add video, ask questions, explore sources
- **SUS Score:** 82.5/100 (Grade: B+)

### 6.2 Key Findings
- ✅ 100% task completion rate for core features
- ✅ Users found interface intuitive
- ✅ Source attribution highly valued
- ⚠️ Initial confusion after video processing
- ⚠️ Mobile keyboard overlap issue

### 6.3 Improvements Implemented
1. Auto-redirect after video processing
2. More prominent source indicators
3. Mobile input field padding
4. Sample questions in sidebar
5. Highlighted video filter

---

## 7. Challenges Faced and Solutions

### Challenge 1: Streamlit Cloud Secrets Management
**Problem:** API keys worked locally (`.env`) but failed on deployment

**Root Cause:** `os.getenv()` doesn't access `st.secrets` in Streamlit Cloud

**Solution Implemented:**
```python
def _get_secret(key: str) -> str:
    # Try Streamlit secrets first (cloud)
    if HAS_STREAMLIT and key in st.secrets:
        return st.secrets[key]
    # Fall back to environment variables (local)
    return os.getenv(key)
```

**Outcome:** Dual-environment support enabling seamless local dev and cloud deployment

---

### Challenge 2: Numpy Dependency Conflict
**Problem:** Deployment failed with incompatible numpy versions

**Error:** `langchain-community==0.3.31` needs numpy≥2.1.0, `streamlit==1.31.1` needs numpy<2

**Solution:** Upgraded Streamlit to 1.40.2 (supports numpy 2.x)

**Learning:** Dependency management critical for deployment success

---

### Challenge 3: ChromaDB Cloud Persistence
**Problem:** Vector database doesn't persist after app restarts on Streamlit Cloud

**Root Cause:** Streamlit Cloud uses ephemeral storage

**Current Workaround:** Document limitation, users re-process videos

**Future Solution:** Migrate to cloud-hosted vector DB (Pinecone/Weaviate)

---

### Challenge 4: Optimal Chunking Parameters
**Problem:** How to balance context preservation vs. retrieval precision?

**Experiment:** Tested multiple configurations:
- 500 chars, 100 overlap → Too fragmented, lost context
- 2000 chars, 400 overlap → Too broad, low precision
- **1000 chars, 200 overlap** → Optimal balance ✅

**Methodology:** Evaluated with 20 test questions, measured answer accuracy

---

### Challenge 5: Mobile Responsiveness
**Problem:** Streamlit not optimized for mobile by default

**Issues:** Small tap targets, keyboard overlap, hidden sidebar

**Solutions:**
- Custom CSS for larger buttons and inputs
- Padding adjustments for keyboard clearance
- Collapsible sidebar on mobile
- Media queries for breakpoints

**Outcome:** 95% mobile usability score

---

## 8. Final Conclusions

### 8.1 Project Success Criteria

| Criterion | Target | Achieved | Status |
|-----------|--------|----------|--------|
| Transcript extraction success rate | >95% | ~98% | ✅ |
| Answer accuracy (subjective) | "Good" | "Very Good" | ✅ |
| Source attribution | 100% | 100% | ✅ |
| Response time | <5s | 2-4s | ✅ |
| Mobile compatibility | Works | Fully functional | ✅ |
| Deployment | Public URL | ✅ Live | ✅ |
| Zero cost | $0/month | $0/month | ✅ |

### 8.2 Key Achievements

1. **Functional RAG System** - End-to-end pipeline from video to answer
2. **Production Deployment** - Live, accessible application
3. **User Validation** - 82.5/100 SUS score (above average)
4. **Cost Efficiency** - Entirely on free tiers
5. **Code Quality** - Modular, documented, maintainable
6. **Comprehensive Documentation** - README, guides, reports

### 8.3 Technical Learnings

**AI/ML Concepts:**
- RAG architecture and implementation
- Vector embeddings and semantic search
- Prompt engineering for grounded responses
- Chunking strategies for optimal retrieval

**Software Engineering:**
- Modular architecture and separation of concerns
- Configuration management (environment-specific)
- Error handling and graceful degradation
- Deployment (local dev → cloud production)

**Product Development:**
- User research and usability testing
- Iterative design based on feedback
- Balancing features vs. simplicity
- Documentation for diverse audiences

### 8.4 Personal Growth

- **Problem-Solving:** Developed hypothesis-driven debugging approach
- **Systems Thinking:** Understanding how components interact
- **Resilience:** Persisted through deployment challenges
- **Communication:** Wrote clear documentation for technical and non-technical users

---

## 9. Future Work

### 9.1 Short-Term Improvements (1-2 weeks)

**Persistent Cloud Storage**
- Migrate ChromaDB to Pinecone (cloud-hosted)
- Ensures videos persist across app restarts
- **Impact:** Major UX improvement

**Conversation Memory**
- Implement LangChain ConversationBufferMemory
- Enable follow-up questions with context
- **Impact:** More natural conversations

**Timestamp Linking**
- Store timestamp metadata with chunks
- Link sources to specific video moments
- **Impact:** Better source verification

### 9.2 Medium-Term Features (1-2 months)

**Multi-Language Support**
- Detect transcript language
- Use multilingual embedding models
- Support non-English videos
- **Impact:** Global accessibility

**Advanced RAG Techniques**
- Implement re-ranking for better retrieval
- Query expansion for complex questions
- Multi-hop reasoning for layered questions
- **Impact:** Higher answer quality

**User Authentication**
- Add login system (Google OAuth)
- Personal video libraries per user
- Usage tracking and rate limiting
- **Impact:** True multi-tenant application

### 9.3 Long-Term Vision (3-6 months)

**Evaluation Framework**
- Build test dataset with ground-truth answers
- Measure retrieval precision and answer quality
- A/B test different configurations
- **Impact:** Scientific optimization

**Audio/Video Upload**
- Support direct file uploads (not just YouTube)
- Integrate Whisper API for transcription
- Handle lecture recordings, podcasts
- **Impact:** Broader use cases

**Analytics Dashboard**
- Track popular questions and topics
- Visualize usage patterns
- Identify knowledge gaps
- **Impact:** Data-driven improvements

---

## 10. Appendices

### Appendix A: Repository Structure
```
youtube-rag-chatbot/
├── src/                      # Core modules
├── data/                     # Generated data (gitignored)
├── streamlit_app.py          # Web application
├── main.py                   # CLI interface
├── requirements.txt          # Dependencies
├── .env.example              # Configuration template
├── README.md                 # Main documentation
├── DEPLOYMENT_GUIDE.md       # How to deploy
├── PROJECT_PLAN.md           # Timeline and milestones
├── AI_TOOLS_SETUP.md         # Tool selection rationale
├── UI_DESIGN_REPORT.md       # Design process
├── USABILITY_TESTING_REPORT.md # Testing results
└── FINAL_PROJECT_REPORT.md   # This document
```

### Appendix B: API Usage Statistics
- **Google Gemini:** ~500 requests (well within 15 RPM limit)
- **Voyage AI:** ~2M tokens embedded (within 30M free tier)
- **Total Cost:** $0

### Appendix C: Performance Benchmarks
- Video processing: 30-45 seconds (10-15 min videos)
- Query response: 2-4 seconds
- Embedding generation: ~3 seconds per 1000 characters
- Database query: <100ms

### Appendix D: References
- LangChain Documentation: https://docs.langchain.com
- ChromaDB Documentation: https://docs.trychroma.com
- Voyage AI Documentation: https://docs.voyageai.com
- Streamlit Documentation: https://docs.streamlit.io

---

**Project Completion Date:** December 2025
**Total Development Time:** 42 days (6 weeks)
**Lines of Code:** ~2,500 (excluding comments)
**Documentation Pages:** ~25

---

**End of Report**
