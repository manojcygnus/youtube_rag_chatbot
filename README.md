# YouTube RAG Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot that allows you to ask questions about YouTube video transcripts using AI. Built with Python, ChromaDB, Voyage AI embeddings, and Google Gemini/Anthropic Claude.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.1-FF4B4B.svg)

---

## 📚 Quick Navigation

**👨‍🏫 For Instructors/Evaluators:**
- **[Quick Start Guide](QUICK_START_GUIDE.md)** - Step-by-step setup for non-technical users (15 min)
- **[Instructor Cheat Sheet](INSTRUCTOR_CHEAT_SHEET.md)** - One-page reference for running and grading

**👨‍💻 For Developers:**
- **[GitHub Setup Guide](GITHUB_SETUP.md)** - How to push this project to GitHub
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to this project

**📖 You're reading:** Technical documentation (below)

---

## Features

- **Extract YouTube Transcripts**: Automatically extract transcripts from any YouTube video using yt-dlp
- **Semantic Search**: Find relevant information using state-of-the-art Voyage AI embeddings (1024-dimensional vectors)
- **RAG-Powered Q&A**: Get accurate, grounded answers using Google Gemini or Anthropic Claude
- **Vector Database**: Persistent storage with ChromaDB for efficient similarity search
- **Dual Interface**:
  - Beautiful web interface with Streamlit (gradients, glassmorphism, animations)
  - Command-line interface for power users
- **Source Attribution**: See exactly which video segments were used to generate each answer
- **Free Tier Support**: Works with Google Gemini's free tier (15 RPM, 1M tokens/day)

## Architecture

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                    RAG Pipeline                          │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐              │
│  │ Retrieve│──▶│ Augment │──▶│ Generate │              │
│  │ Context │   │ Prompt  │   │ Answer   │              │
│  └─────────┘   └─────────┘   └──────────┘              │
└─────────────────────────────────────────────────────────┘
       │                                │
       ▼                                ▼
┌─────────────┐                  ┌──────────────┐
│  ChromaDB   │                  │ Google Gemini│
│  (Vectors)  │                  │  or Claude   │
└─────────────┘                  └──────────────┘
```

### How RAG Works

1. **Retrieval**: When you ask a question, it's converted to a vector embedding and compared against stored video transcript chunks using semantic similarity
2. **Augmentation**: The most relevant chunks are retrieved and formatted into a prompt with clear instructions
3. **Generation**: The LLM (Gemini/Claude) reads the context and generates an accurate answer grounded in the source material

This approach prevents hallucinations and ensures answers are based on actual video content.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.9+ | Core application |
| **LLM** | Google Gemini 2.5 Flash / Claude 3.5 Sonnet | Answer generation |
| **Embeddings** | Voyage AI (voyage-3) | Text → 1024-dim vectors |
| **Vector DB** | ChromaDB 1.3.5 | Persistent embedding storage |
| **Framework** | LangChain 0.3.27 | RAG orchestration |
| **Web UI** | Streamlit 1.31.1 | Interactive interface |
| **Transcript** | yt-dlp 2025.10.14 | YouTube transcript extraction |

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- API Keys (free options available):
  - **Voyage AI API Key** (required) - [Get it here](https://www.voyageai.com/)
  - **Google Gemini API Key** (recommended, free tier) - [Get it here](https://makersuite.google.com/app/apikey)
  - **OR Anthropic API Key** (optional, paid) - [Get it here](https://console.anthropic.com/)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/youtube-rag-chatbot.git
cd youtube-rag-chatbot
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- yt-dlp (YouTube transcripts)
- python-dotenv (environment variables)
- langchain & langchain-community (RAG framework)
- chromadb (vector database)
- anthropic (Claude API)
- google-generativeai (Gemini API)
- voyageai (embeddings)
- streamlit (web interface)

### 4. Configure API Keys

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Option 1: Google Gemini (RECOMMENDED - Free tier available)
GEMINI_API_KEY=your_gemini_api_key_here

# Option 2: Anthropic Claude (Requires paid credits)
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Required: Voyage AI for embeddings
VOYAGE_API_KEY=your_voyage_api_key_here

# Optional: Configuration
LLM_PROVIDER=gemini  # or "anthropic"
GEMINI_MODEL=gemini-2.5-flash
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 5. Verify Installation

```bash
python src/config.py
```

You should see:
```
Configuration Status
======================================================================
LLM_PROVIDER: gemini
GEMINI_API_KEY: ✓ Set
VOYAGE_API_KEY: ✓ Set
✓ Configuration is valid!
```

## Usage

### Option 1: Web Interface (Recommended)

Start the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**Features:**
- 💬 **Chat**: Ask questions about processed videos
- 📥 **Add Video**: Process new YouTube videos
- 📚 **My Videos**: View and manage processed videos
- 📊 **Statistics**: See database stats

### Option 2: Command Line Interface

Run the CLI:

```bash
python main.py
```

**Menu Options:**
1. Add a new video
2. List all processed videos
3. Chat with videos
4. Delete a video
5. Show database statistics
6. Exit

## Project Structure

```
youtube-rag-chatbot/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Your API keys (create this)
├── .gitignore                   # Git ignore rules
│
├── main.py                      # CLI interface
├── streamlit_app.py             # Web interface
│
├── src/                         # Core modules
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── transcript_extractor.py  # YouTube transcript extraction
│   ├── text_chunker.py          # Text chunking with overlap
│   ├── embedding_manager.py     # Voyage AI + ChromaDB
│   ├── metadata_manager.py      # Video metadata tracking
│   ├── question_answerer.py     # RAG Q&A with Gemini/Claude
│   └── pipeline.py              # Orchestration pipeline
│
├── data/                        # Generated data (not in git)
│   ├── chroma_db/               # ChromaDB persistent storage
│   └── videos.json              # Video metadata
│
├── test_manual.py               # Manual testing script
└── test_embeddings.py           # Embedding testing script
```

## Example Workflow

### 1. Add a Video

**Web Interface:**
1. Navigate to "📥 Add Video" page
2. Paste YouTube URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. Optional: Add custom title
4. Click "Process Video"
5. Wait 30-60 seconds for processing

**CLI:**
```bash
python main.py
# Select option 1
# Enter URL when prompted
```

### 2. Ask Questions

**Web Interface:**
1. Go to "💬 Chat" page
2. Type your question: "What is the main topic of this video?"
3. Press Enter
4. View answer with source attribution

**CLI:**
```bash
python main.py
# Select option 3
# Type your questions
```

### 3. View Sources

Every answer includes:
- The generated response
- Source chunks used (with similarity scores)
- Video title and chunk index
- Token usage and model information

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | LLM provider: `gemini` or `anthropic` |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model to use |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Claude model to use |
| `VOYAGE_MODEL` | `voyage-3` | Voyage embedding model |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `CHROMA_COLLECTION_NAME` | `youtube_transcripts` | ChromaDB collection name |
| `CHROMA_PERSIST_DIRECTORY` | `./data/chroma_db` | Database storage path |

### Model Options

**Google Gemini (Free Tier):**
- `gemini-2.5-flash` (recommended) - Fast, efficient
- `gemini-2.5-pro` - More capable, slower
- Rate limits: 15 RPM, 1M tokens/day

**Anthropic Claude (Paid):**
- `claude-3-5-sonnet-20241022` - Most capable
- `claude-3-5-haiku-20241022` - Fast, efficient
- Requires API credits

## API Rate Limits & Costs

### Google Gemini (Free Tier)
- **Cost**: FREE
- **Rate Limit**: 15 requests/minute, 1M tokens/day
- **Best for**: Testing, personal projects, learning

### Anthropic Claude (Paid)
- **Cost**: ~$3 per million input tokens, ~$15 per million output tokens
- **Rate Limit**: Based on your tier
- **Best for**: Production, high-volume usage

### Voyage AI
- **Free Tier**: 30M tokens
- **Paid**: $0.12 per 1M tokens
- **Rate Limit**: 300 requests/minute (free tier)

## Troubleshooting

### "Configuration Error" on startup

**Problem**: Missing or invalid API keys

**Solution**:
1. Check `.env` file exists (not `env`)
2. Verify API keys are correct
3. Run `python src/config.py` to diagnose

### "HTTP Error 429: Too Many Requests"

**Problem**: YouTube rate limiting

**Solution**: Wait a few minutes before trying again

### "models/gemini-1.5-flash is not found"

**Problem**: Incorrect model name

**Solution**: Update `.env`:
```bash
GEMINI_MODEL=gemini-2.5-flash
```

### "Your credit balance is too low" (Anthropic)

**Problem**: Out of Claude API credits

**Solution**: Switch to Gemini (free):
```bash
LLM_PROVIDER=gemini
```

### Streamlit shows white screen

**Solution**: Wait 10-30 seconds for initialization. Check terminal for errors.

### "No module named 'streamlit'"

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Development

### Running Tests

```bash
# Test transcript extraction
python test_manual.py

# Test embeddings and search
python test_embeddings.py
```

### Adding New Features

The modular architecture makes it easy to extend:

- **New LLM providers**: Modify `src/question_answerer.py`
- **Different embeddings**: Update `src/embedding_manager.py`
- **Custom chunking**: Edit `src/text_chunker.py`
- **UI improvements**: Enhance `streamlit_app.py`

## Performance Considerations

- **Embedding dimensions**: 1024 (voyage-3) - high quality, moderate speed
- **Chunk size**: 1000 chars - balances context vs. precision
- **Chunk overlap**: 200 chars - preserves context at boundaries
- **Context chunks**: Default 5 - adjustable in chat interface
- **ChromaDB**: Persistent storage - no re-embedding needed

## Security Best Practices

1. **Never commit `.env` file** - Contains sensitive API keys
2. **Use `.gitignore`** - Already configured to exclude `.env` and `data/`
3. **Rotate API keys** - If accidentally exposed
4. **Rate limiting** - Implemented in all API calls
5. **Input validation** - Sanitizes YouTube URLs

## Limitations

- **Video length**: Very long videos (>2 hours) may hit API limits
- **Languages**: Works best with English transcripts
- **No captions**: Videos without transcripts cannot be processed
- **Rate limits**: Free tier has request/token limits
- **Accuracy**: Depends on transcript quality and LLM capabilities

## Roadmap

- [ ] Support for multiple languages
- [ ] Audio file upload (not just YouTube)
- [ ] Chat history persistence
- [ ] Export conversations
- [ ] Batch video processing
- [ ] Video timestamp links in sources
- [ ] Custom embedding models
- [ ] Docker containerization
- [ ] API endpoint for integration

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [LangChain](https://www.langchain.com/) - RAG framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Voyage AI](https://www.voyageai.com/) - Embeddings
- [Google Gemini](https://ai.google.dev/) - LLM (free tier)
- [Anthropic Claude](https://www.anthropic.com/) - LLM
- [Streamlit](https://streamlit.io/) - Web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube extraction

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [closed issues](https://github.com/yourusername/youtube-rag-chatbot/issues?q=is%3Aissue+is%3Aclosed)
3. Open a [new issue](https://github.com/yourusername/youtube-rag-chatbot/issues/new) with:
   - Error message
   - Steps to reproduce
   - Python version (`python --version`)
   - OS (macOS/Linux/Windows)

## Author

Created with ❤️ by [Your Name]

---

**Star this repo if you find it useful!** ⭐
