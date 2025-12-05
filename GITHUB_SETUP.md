# GitHub Setup Guide

This guide will help you push your YouTube RAG Chatbot project to GitHub.

## ✅ What's Already Done

- ✓ Git repository initialized
- ✓ All project files committed
- ✓ `.env` file excluded from tracking (API keys are safe!)
- ✓ `.gitignore` configured properly
- ✓ README.md, LICENSE, and CONTRIBUTING.md created

## 🚀 Steps to Push to GitHub

### Step 1: Configure Git User (First Time Only)

Set your name and email for commits:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Optional**: Update the commit author if needed:
```bash
cd "/Users/manoj/Desktop/AI Project/Youtube Video chatbot/youtube-rag-chatbot"
git commit --amend --reset-author --no-edit
```

### Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com/) and sign in
2. Click the **"+"** icon in the top-right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `youtube-rag-chatbot`
   - **Description**: `A RAG chatbot for YouTube videos using Gemini/Claude, Voyage AI, and ChromaDB`
   - **Visibility**: Choose **Public** (recommended) or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these!)
4. Click **"Create repository"**

### Step 3: Connect Local Repository to GitHub

GitHub will show you commands like these. Copy your repository URL and run:

```bash
cd "/Users/manoj/Desktop/AI Project/Youtube Video chatbot/youtube-rag-chatbot"

# Add GitHub as remote origin
git remote add origin https://github.com/YOUR_USERNAME/youtube-rag-chatbot.git

# Verify remote was added
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/youtube-rag-chatbot.git (fetch)
origin  https://github.com/YOUR_USERNAME/youtube-rag-chatbot.git (push)
```

### Step 4: Push to GitHub

Push your code to GitHub:

```bash
# Push to main branch
git push -u origin main
```

If using SSH instead of HTTPS:
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/youtube-rag-chatbot.git
git push -u origin main
```

### Step 5: Verify on GitHub

1. Go to `https://github.com/YOUR_USERNAME/youtube-rag-chatbot`
2. You should see:
   - ✅ README.md displayed beautifully
   - ✅ All source files
   - ✅ NO .env file (API keys safe!)
   - ✅ 19 files committed

## 🔒 Security Checklist

Before pushing, verify these:

- [ ] `.env` file is NOT in the repository
- [ ] `.gitignore` includes `.env`
- [ ] No API keys in any committed files
- [ ] `data/chroma_db/` is ignored (database not pushed)
- [ ] `venv/` is ignored (dependencies not pushed)

**Verify with:**
```bash
cd "/Users/manoj/Desktop/AI Project/Youtube Video chatbot/youtube-rag-chatbot"

# Check tracked files
git ls-files

# Confirm .env is NOT in the list
git ls-files | grep -E "^\.env$" && echo "⚠️ WARNING: .env is tracked!" || echo "✓ Safe: .env not tracked"
```

## 📝 After Pushing

### Update README

Edit `README.md` and replace:
```markdown
git clone https://github.com/yourusername/youtube-rag-chatbot.git
```

With your actual GitHub URL:
```markdown
git clone https://github.com/YOUR_ACTUAL_USERNAME/youtube-rag-chatbot.git
```

Then commit and push:
```bash
git add README.md
git commit -m "docs: update clone URL with actual username"
git push
```

### Add Topics (Tags)

On GitHub, click **"Add topics"** and add:
- `python`
- `rag`
- `chatbot`
- `youtube`
- `gemini`
- `chromadb`
- `streamlit`
- `langchain`
- `embeddings`
- `ai`

### Enable Features

On GitHub, go to **Settings** → **Features** and enable:
- ✅ Issues (for bug reports and feature requests)
- ✅ Discussions (for Q&A and community)
- ✅ Projects (optional, for roadmap)

### Add Badges

Update README.md with actual badges:

```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/youtube-rag-chatbot?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/youtube-rag-chatbot?style=social)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/youtube-rag-chatbot)
```

## 🔄 Making Future Changes

### Basic Workflow

```bash
cd "/Users/manoj/Desktop/AI Project/Youtube Video chatbot/youtube-rag-chatbot"

# Check status
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add timestamp links to sources"

# Push to GitHub
git push
```

### Good Commit Messages

Follow this format:

```
type: short description

Optional longer explanation
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style (formatting)
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: add video timestamp links"
git commit -m "fix: handle rate limiting errors"
git commit -m "docs: improve installation guide"
git commit -m "refactor: simplify embedding manager"
```

## 🌿 Branching Strategy

For new features, use branches:

```bash
# Create and switch to new branch
git checkout -b feature/add-export

# Make changes, commit them
git add .
git commit -m "feat: add chat export functionality"

# Push branch to GitHub
git push -u origin feature/add-export

# Create Pull Request on GitHub
# After merging, switch back to main
git checkout main
git pull

# Delete local branch
git branch -d feature/add-export
```

## 🆘 Common Issues

### Issue: Large Files Rejected

**Error**: `remote: error: File too large`

**Solution**: Add large files to `.gitignore`:
```bash
echo "large_file.mp4" >> .gitignore
git rm --cached large_file.mp4
git commit -m "chore: remove large file"
git push
```

### Issue: Authentication Failed

**Error**: `fatal: Authentication failed`

**Solution 1** - Use Personal Access Token:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` permissions
3. Use token as password when pushing

**Solution 2** - Use SSH:
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub → Settings → SSH Keys
# Then change remote URL
git remote set-url origin git@github.com:YOUR_USERNAME/youtube-rag-chatbot.git
```

### Issue: Accidentally Committed .env

**⚠️ IMPORTANT**: If you accidentally commit `.env` with API keys:

```bash
# Remove from history (⚠️ THIS REWRITES HISTORY)
git rm --cached .env
git commit -m "security: remove .env file"
git push -f

# Then IMMEDIATELY:
# 1. Rotate ALL API keys (Gemini, Anthropic, Voyage)
# 2. Never use --force on shared repositories
```

### Issue: Merge Conflicts

If someone else made changes:

```bash
# Pull latest changes
git pull origin main

# If conflicts occur, edit files to resolve
# Then:
git add .
git commit -m "merge: resolve conflicts"
git push
```

## 📊 GitHub Features to Use

### GitHub Actions (CI/CD)

Create `.github/workflows/test.yml` for automated testing:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/
```

### GitHub Issues Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md` for structured bug reports.

### GitHub Projects

Use Projects tab to track:
- Todo
- In Progress
- Done

## 🎯 Next Steps

After pushing to GitHub:

1. **Share your project**:
   - Tweet about it
   - Post on Reddit (r/Python, r/MachineLearning)
   - Share on LinkedIn
   - Add to your portfolio

2. **Monitor activity**:
   - Watch for issues and PRs
   - Respond to questions
   - Accept contributions

3. **Keep improving**:
   - Add new features
   - Fix bugs
   - Update documentation
   - Respond to feedback

4. **Make it discoverable**:
   - Add screenshots to README
   - Create demo video
   - Write blog post about it
   - Submit to awesome-lists

## 📚 Resources

- [GitHub Documentation](https://docs.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Need help?** Open an issue on GitHub or check the troubleshooting section in README.md

Good luck with your project! 🚀
