# Quick Start Guide for Instructors (Non-Technical)

This guide will help you run the YouTube RAG Chatbot project with minimal technical knowledge. Just follow these steps exactly as written.

---

## ⏱️ Time Estimate: 15-20 minutes

---

## 📋 What You'll Need

1. A computer (Mac, Windows, or Linux)
2. Internet connection
3. Free API keys (I'll show you how to get them)

---

## 🚀 Step-by-Step Setup

### Step 1: Check if Python is Installed

**On Mac:**
1. Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter)
2. Type this and press Enter:
   ```bash
   python3 --version
   ```
3. You should see something like `Python 3.9.6` or higher

**On Windows:**
1. Open **Command Prompt** (press Windows key, type "cmd", press Enter)
2. Type this and press Enter:
   ```bash
   python --version
   ```
3. You should see something like `Python 3.9` or higher

**If Python is NOT installed:**
- Mac: Visit https://www.python.org/downloads/ and download Python 3.9 or newer
- Windows: Visit https://www.python.org/downloads/ and download Python 3.9 or newer
  - ⚠️ **Important**: Check "Add Python to PATH" during installation!

---

### Step 2: Download the Project

**Option A: If you have the project as a ZIP file**
1. Unzip the file to your Desktop
2. You should see a folder called `youtube-rag-chatbot`

**Option B: If the project is on GitHub**
1. Go to the GitHub repository URL (the student will provide this)
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip to your Desktop

---

### Step 3: Get Your Free API Keys

You need 2 API keys (both are FREE):

#### 3.1: Get Google Gemini API Key (for AI responses)

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Click **"Create API key in new project"**
5. Copy the key (looks like: `AIzaSyB_fJT...`) and save it in a note

#### 3.2: Get Voyage AI API Key (for searching videos)

1. Go to https://www.voyageai.com/
2. Click **"Get Started"** or **"Sign Up"**
3. Create a free account
4. Go to your dashboard: https://dash.voyageai.com/
5. Click **"API Keys"** in the left menu
6. Click **"Create new API key"**
7. Copy the key (looks like: `pa-jY8gbIPm...`) and save it in a note

**Important**: Keep these keys private! Don't share them publicly.

---

### Step 4: Set Up the Project

#### 4.1: Open Terminal/Command Prompt in Project Folder

**On Mac:**
1. Open **Finder**
2. Navigate to Desktop → `youtube-rag-chatbot` folder
3. Right-click the folder
4. Hold `Option` key and select **"Copy 'youtube-rag-chatbot' as Pathname"**
5. Open **Terminal** (press `Cmd + Space`, type "Terminal")
6. Type `cd` (with a space after it), then paste the path, press Enter
   - Example: `cd /Users/yourname/Desktop/youtube-rag-chatbot`

**On Windows:**
1. Open **File Explorer**
2. Navigate to Desktop → `youtube-rag-chatbot` folder
3. Click in the address bar at the top
4. Type `cmd` and press Enter
5. A Command Prompt will open in that folder

#### 4.2: Create Virtual Environment

In Terminal/Command Prompt, type these commands one at a time:

**On Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

✅ You should see `(venv)` appear at the start of your command line.

#### 4.3: Install Required Software

Copy and paste this entire command and press Enter:

**On Mac/Linux:**
```bash
pip install -r requirements.txt
```

**On Windows:**
```bash
pip install -r requirements.txt
```

⏳ This will take 2-3 minutes. You'll see lots of text scrolling—this is normal!

---

### Step 5: Add Your API Keys

1. In the `youtube-rag-chatbot` folder, find the file named `.env.example`
2. Make a copy of this file
3. Rename the copy to `.env` (just `.env` with a dot at the start)
   - **On Mac**: You might need to press `Cmd + Shift + .` to see files starting with a dot
4. Open the `.env` file in a text editor (Notepad on Windows, TextEdit on Mac)
5. Replace the placeholder text with your actual API keys:

```bash
# Replace with YOUR actual keys
GEMINI_API_KEY=paste_your_gemini_key_here
VOYAGE_API_KEY=paste_your_voyage_key_here

# Keep these settings as-is
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

6. **Save** the file

---

### Step 6: Run the Application

You have two options:

#### Option A: Web Interface (Recommended - Easier to Use)

1. Make sure you're in the project folder with `(venv)` showing
2. Type this command:

**On Mac/Windows:**
```bash
streamlit run streamlit_app.py
```

3. Your web browser will automatically open to `http://localhost:8501`
4. You'll see a beautiful web interface!

**What you can do:**
- 💬 **Chat**: Ask questions about videos
- 📥 **Add Video**: Process a new YouTube video
- 📚 **My Videos**: View all processed videos
- 📊 **Statistics**: See database stats

#### Option B: Command Line Interface

1. Make sure you're in the project folder with `(venv)` showing
2. Type this command:

```bash
python main.py
```

3. You'll see a menu with numbered options
4. Type a number (1-6) and press Enter to select an option

---

## 🎯 How to Use the Chatbot

### Adding Your First Video

1. **In Web Interface:**
   - Click **"📥 Add Video"** in the sidebar
   - Paste a YouTube URL (example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
   - Optional: Give it a custom title
   - Click **"🚀 Process Video"**
   - Wait 30-60 seconds (you'll see a progress bar)

2. **In Command Line:**
   - Select option **1** (Add a new video)
   - Paste the YouTube URL when prompted
   - Press Enter
   - Wait for processing to complete

### Asking Questions

1. **In Web Interface:**
   - Click **"💬 Chat"** in the sidebar
   - Type your question in the chat box at the bottom
   - Press Enter
   - The AI will respond with an answer and show its sources!

2. **In Command Line:**
   - Select option **3** (Chat with videos)
   - Type your question and press Enter
   - Type 'exit' to go back to the menu

### Example Questions to Try

Once you've processed a video, try asking:
- "What is the main topic of this video?"
- "Summarize the key points discussed"
- "What did the speaker say about [specific topic]?"
- "What examples were mentioned?"

---

## 🛑 Stopping the Application

**To stop the web interface:**
1. Go to the Terminal/Command Prompt window
2. Press `Ctrl + C`
3. Type `Y` if asked to confirm

**To stop the command line interface:**
- Type `6` to exit, or press `Ctrl + C`

---

## ❓ Troubleshooting Common Issues

### Issue 1: "Command not found: python3" (Mac)

**Solution**: Try `python` instead of `python3`

### Issue 2: "pip is not recognized" (Windows)

**Solution**:
1. Reinstall Python from python.org
2. During installation, check ✅ "Add Python to PATH"

### Issue 3: "Configuration Error" when running

**Possible causes:**
1. **API keys not set correctly**
   - Check your `.env` file exists (not `.env.example`)
   - Make sure you copied the keys correctly (no extra spaces)
   - Make sure the keys are on the right lines

2. **Wrong model name**
   - In `.env`, make sure it says `GEMINI_MODEL=gemini-2.5-flash`
   - NOT `gemini-1.5-flash`

### Issue 4: White screen in web browser

**Solution**: Wait 10-30 seconds—the app is loading. Check the Terminal for errors.

### Issue 5: "Too Many Requests" error

**Solution**: Wait a few minutes. YouTube might be rate-limiting. Try a different video.

### Issue 6: Can't see .env file (Mac)

**Solution**:
1. Open Finder
2. Press `Cmd + Shift + .` (dot) to show hidden files
3. Now you'll see files starting with a dot

---

## 📱 Quick Reference Card

Print this and keep it handy:

```
╔════════════════════════════════════════╗
║   YOUTUBE RAG CHATBOT QUICK GUIDE     ║
╠════════════════════════════════════════╣
║ 1. Open Terminal/Command Prompt       ║
║ 2. Navigate to project folder:        ║
║    cd path/to/youtube-rag-chatbot     ║
║                                        ║
║ 3. Activate environment:              ║
║    Mac:     source venv/bin/activate  ║
║    Windows: venv\Scripts\activate     ║
║                                        ║
║ 4. Run web interface:                 ║
║    streamlit run streamlit_app.py     ║
║                                        ║
║ 5. Open browser to:                   ║
║    http://localhost:8501              ║
║                                        ║
║ 6. Stop: Press Ctrl+C in Terminal     ║
╚════════════════════════════════════════╝
```

---

## 🎓 For Grading/Evaluation

### What to Look For:

1. **Functionality**:
   - ✅ Can process YouTube videos successfully
   - ✅ Can ask questions and get relevant answers
   - ✅ Answers include source attribution (which video chunk)
   - ✅ Clean, modern web interface

2. **Code Quality**:
   - ✅ Well-organized file structure
   - ✅ Comprehensive documentation in code
   - ✅ Proper error handling
   - ✅ Configuration management (.env)

3. **Understanding**:
   - Ask the student to explain:
     - What is RAG and why is it better than plain LLMs?
     - How do embeddings work?
     - Why use ChromaDB for storage?
     - Trade-offs between Gemini and Claude

### Test Cases to Try:

1. **Basic Functionality**:
   - Process a short video (5-10 minutes)
   - Ask: "What is this video about?"
   - Verify answer is relevant

2. **Multiple Videos**:
   - Add 2-3 different videos
   - Ask questions specific to one video
   - Check if answers come from correct video

3. **Source Attribution**:
   - After any answer, expand "View Sources"
   - Verify it shows which video/chunk was used

4. **Error Handling**:
   - Try an invalid YouTube URL
   - Check if error message is clear and helpful

---

## 📞 Need Help?

If you encounter issues:

1. **Check the main README.md** - Has detailed troubleshooting
2. **Check GITHUB_SETUP.md** - Common Git issues
3. **Check the .env file** - Most issues are API key problems

Common fixes:
- Restart Terminal/Command Prompt
- Deactivate and reactivate virtual environment
- Check API keys are correct
- Make sure you're in the right folder

---

## 🎉 You're Done!

You should now be able to:
- ✅ Run the web interface
- ✅ Process YouTube videos
- ✅ Ask questions and get AI-powered answers
- ✅ See source attribution

**Time to run**: Once set up, takes 10 seconds to start next time!

---

## 💡 Tips for Evaluation

- The web interface is more impressive visually
- Try asking complex questions that require understanding context
- Check that answers cite specific sources
- Notice the gradient animations and modern UI design
- Ask the student about trade-offs and design decisions

---

**Last Updated**: December 2025
**Estimated Setup Time**: 15-20 minutes (first time only)
**Estimated Run Time**: 10 seconds (after setup)
