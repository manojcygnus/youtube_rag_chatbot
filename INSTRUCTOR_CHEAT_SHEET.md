# Instructor Cheat Sheet - YouTube RAG Chatbot

**⏱️ First-Time Setup: 15 minutes | Next Time: 10 seconds**

---

## 🚀 First Time Setup (Do Once)

### 1. Get API Keys (5 minutes)

| API | Where to Get | What It's For |
|-----|-------------|---------------|
| **Google Gemini** | https://makersuite.google.com/app/apikey | AI responses (FREE) |
| **Voyage AI** | https://dash.voyageai.com/ | Video search (FREE) |

💡 Save these keys in a text file!

### 2. Setup Project (10 minutes)

```bash
# Navigate to project folder
cd path/to/youtube-rag-chatbot

# Create virtual environment
python3 -m venv venv           # Mac/Linux
python -m venv venv            # Windows

# Activate it
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# Install everything
pip install -r requirements.txt
```

### 3. Add API Keys

1. Copy `.env.example` → rename to `.env`
2. Open `.env` in text editor
3. Paste your API keys:
```bash
GEMINI_API_KEY=your_actual_key_here
VOYAGE_API_KEY=your_actual_key_here
```
4. Save file

---

## ▶️ Every Time You Run It (10 seconds)

```bash
# 1. Open Terminal in project folder
cd path/to/youtube-rag-chatbot

# 2. Activate environment (you'll see "(venv)" appear)
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# 3. Run the web interface
streamlit run streamlit_app.py

# 4. Browser opens automatically to http://localhost:8501
```

**To Stop**: Press `Ctrl + C` in Terminal

---

## 📱 Using the Web Interface

### Add a Video
1. Click **"📥 Add Video"**
2. Paste YouTube URL
3. Click **"🚀 Process Video"**
4. Wait ~30 seconds

### Ask Questions
1. Click **"💬 Chat"**
2. Type question in box at bottom
3. Press Enter
4. See answer + sources!

### View Videos
1. Click **"📚 My Videos"**
2. See all processed videos
3. Delete videos if needed

---

## ⚠️ Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Configuration Error" | Check `.env` file has correct API keys |
| White screen | Wait 30 seconds for loading |
| "Command not found" | Make sure Python is installed |
| Can't see `.env` | Press `Cmd+Shift+.` on Mac to show hidden files |
| "Too many requests" | Wait 5 minutes, try different video |

---

## ✅ What to Test for Grading

### Functionality Tests
- [ ] Process a YouTube video successfully
- [ ] Ask a question and get relevant answer
- [ ] Answer shows source attribution
- [ ] Web interface loads and looks professional
- [ ] Can add multiple videos
- [ ] Can filter by specific video in chat

### Questions to Ask Student
1. "Explain what RAG is and why it's useful"
2. "How do embeddings work in your project?"
3. "Why did you choose Gemini over other options?"
4. "Show me how source attribution works"
5. "What challenges did you face and how did you solve them?"

### Code Quality to Check
- [ ] Clean file organization
- [ ] Comprehensive code documentation
- [ ] Proper error handling
- [ ] Security (API keys not in git)
- [ ] Requirements.txt complete

---

## 💡 Impressive Features to Notice

1. **Modern UI**: Gradient animations, glassmorphism effects
2. **Dual Providers**: Supports both Gemini (free) and Claude
3. **Source Attribution**: Shows exactly where answers come from
4. **Vector Search**: Uses state-of-the-art embeddings
5. **Persistent Storage**: ChromaDB saves processed videos
6. **Documentation**: Excellent README and guides

---

## 📊 Example Test Workflow (5 minutes)

```
1. Start application (10 seconds)
   → streamlit run streamlit_app.py

2. Add test video (60 seconds)
   → Use: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   → Click "Add Video"
   → Wait for processing

3. Ask questions (30 seconds each)
   → "What is this video about?"
   → "Summarize the key points"
   → Check that answers cite sources

4. Verify sources (10 seconds)
   → Click "View Sources" under answer
   → See video chunk references

5. Test video list (10 seconds)
   → Go to "My Videos"
   → Verify video appears

Total: ~3 minutes of actual testing
```

---

## 🎯 Expected Outputs

**When Adding Video:**
```
✅ Video processed successfully!
Video ID: dQw4w9WgXcQ
Chunks Created: 19
Transcript Length: 14,268 chars
```

**When Asking Question:**
```
[AI-generated answer based on video content]

Sources:
1. Video Title (Chunk 3) | Similarity: 0.876
   Preview: "In the video, the speaker explains..."
```

---

## 📞 Quick Help

**Most Common Issue**: API key problems
- Check `.env` exists (not `.env.example`)
- No spaces around the `=` sign
- Keys copied completely

**Second Most Common**: Environment not activated
- You should see `(venv)` at start of command line
- If not, run activate command again

---

## 🎓 Grading Rubric Suggestions

| Category | Points | What to Check |
|----------|--------|---------------|
| **Functionality** | 30 | Works end-to-end |
| **Code Quality** | 25 | Clean, documented, organized |
| **Understanding** | 25 | Can explain architecture |
| **Documentation** | 15 | README, comments, guides |
| **Innovation** | 5 | UI design, features |

---

**Print this sheet and keep it at your desk!**

Last Updated: December 2025
