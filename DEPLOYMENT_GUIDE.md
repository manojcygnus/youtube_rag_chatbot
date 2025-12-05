# Deployment Guide - Host Your YouTube RAG Chatbot

This guide shows you how to deploy your app so you can access it from any device (mobile, tablet, etc.) via a public URL.

---

## 🚀 Option 1: Streamlit Community Cloud (FREE - RECOMMENDED)

**Perfect for:** Class projects, portfolios, demos
**Cost:** FREE forever
**URL:** `https://your-app-name.streamlit.app`
**Time to deploy:** 10 minutes

### Prerequisites

- ✅ GitHub account (free)
- ✅ Project pushed to GitHub (see GITHUB_SETUP.md)
- ✅ API keys (Gemini, Voyage)

### Step-by-Step Deployment

#### 1. Prepare Your Repository

Your project is already ready! But verify:

```bash
cd "/Users/manoj/Desktop/AI Project/Youtube Video chatbot/youtube-rag-chatbot"

# Check that these files exist:
ls streamlit_app.py      # ✓ Main app file
ls requirements.txt      # ✓ Dependencies
ls .gitignore           # ✓ Protects secrets
git ls-files .env       # Should return nothing (✓ .env not tracked)
```

#### 2. Push to GitHub

If you haven't already:

```bash
# Follow GITHUB_SETUP.md instructions
git remote add origin https://github.com/YOUR_USERNAME/youtube-rag-chatbot.git
git push -u origin main
```

#### 3. Sign Up for Streamlit Community Cloud

1. Go to https://streamlit.io/cloud
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your GitHub

#### 4. Deploy Your App

1. On Streamlit Cloud dashboard, click **"New app"**
2. Fill in the details:
   - **Repository:** `YOUR_USERNAME/youtube-rag-chatbot`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a custom name (e.g., `youtube-rag-chatbot`)

3. Click **"Advanced settings"**

4. Add your **Secrets** (API keys):
   ```toml
   # Copy your .env file contents here but in TOML format:
   GEMINI_API_KEY = "your_actual_gemini_key_here"
   VOYAGE_API_KEY = "your_actual_voyage_key_here"
   LLM_PROVIDER = "gemini"
   GEMINI_MODEL = "gemini-2.5-flash"
   ```

5. Click **"Deploy!"**

#### 5. Wait for Deployment

- Initial deployment takes 2-5 minutes
- You'll see a build log
- Once done, your app will be live!

#### 6. Access Your App

Your app will be available at:
```
https://your-chosen-name.streamlit.app
```

**Share this URL with anyone!** They can access it from:
- 📱 Mobile phones (iOS, Android)
- 💻 Laptops/Desktops
- 📱 Tablets
- 🌍 Any browser, anywhere

---

## 📱 Mobile Experience

Once deployed, your app will be fully responsive on mobile:

### What Works on Mobile:
- ✅ All pages (Chat, Add Video, My Videos, Statistics)
- ✅ Chat interface (type questions)
- ✅ Add YouTube videos
- ✅ View processed videos
- ✅ Source attribution
- ✅ All animations and styling

### Mobile-Specific Tips:
- Use landscape mode for better experience
- Sidebar auto-collapses (tap hamburger menu)
- Chat input expands when tapped
- All features fully functional

---

## 🔐 Security Considerations

### ⚠️ IMPORTANT: Your App Will Be Public

Since you're using the FREE tier of Streamlit Cloud:
- **Anyone with the URL can access your app**
- **Anyone can add videos and ask questions**
- **Your API keys are hidden** (only you see them in Secrets)

### To Protect Your API Costs:

#### Option 1: Add Authentication (Recommended)

Create a simple password protection:

```python
# Add to top of streamlit_app.py
import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.write("*Please enter the password to access the app.*")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

# Add this at the start of main()
if not check_password():
    st.stop()
```

Then add to Streamlit Secrets:
```toml
app_password = "your_secure_password_here"
```

#### Option 2: Monitor Usage

Check Streamlit Cloud dashboard:
- **Metrics** → See traffic, API calls
- **Logs** → Monitor activity
- Set up alerts for unusual activity

#### Option 3: Use API Key Rate Limiting

In `.streamlit/secrets.toml`, add:
```toml
# Limit usage to prevent abuse
MAX_VIDEOS_PER_USER = 5
MAX_QUESTIONS_PER_DAY = 100
```

---

## 💰 Cost Considerations

### Free Tier (Streamlit Cloud):
- **Hosting:** FREE
- **API Costs:**
  - Google Gemini: 15 requests/min, 1M tokens/day (FREE)
  - Voyage AI: 30M tokens free tier

**If 10 people use your app:**
- Processing 10 videos: ~$0 (within free limits)
- 100 questions/day: ~$0 (Gemini free tier)
- **Total: $0/month**

**If 1000 people use your app:**
- You might exceed free tier
- Consider adding authentication or rate limiting
- Estimated: $5-20/month depending on usage

---

## 🔄 Updating Your Deployed App

Every time you push to GitHub, Streamlit Cloud auto-updates:

```bash
# Make changes locally
git add .
git commit -m "feat: add new feature"
git push

# Streamlit Cloud automatically redeploys (2-3 minutes)
```

**No manual redeployment needed!**

---

## 🌍 Custom Domain (Optional)

Want `chatbot.yourdomain.com` instead of `*.streamlit.app`?

### Requirements:
- Own a domain ($10-15/year)
- Streamlit Teams plan ($20/month) or Enterprise

### Steps:
1. Upgrade to Streamlit Teams
2. Settings → Custom domain
3. Add CNAME record in your DNS
4. Wait for propagation (24-48 hours)

**For class projects:** The free `.streamlit.app` domain is perfectly fine!

---

## 🚀 Option 2: Deploy to Render.com (Always-On)

If you need your app to stay awake (no cold starts):

### Step-by-Step:

#### 1. Create `Dockerfile`

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
```

#### 2. Create `render.yaml`

```yaml
services:
  - type: web
    name: youtube-rag-chatbot
    env: docker
    plan: free  # or 'starter' for $7/month (always-on)
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: VOYAGE_API_KEY
        sync: false
      - key: LLM_PROVIDER
        value: gemini
```

#### 3. Deploy to Render

1. Go to https://render.com/
2. Sign up with GitHub
3. New → Web Service
4. Connect your GitHub repo
5. Add environment variables (API keys)
6. Click "Create Web Service"

**URL:** `https://your-app-name.onrender.com`

---

## 🚀 Option 3: Deploy to Railway.app

### Quick Deploy:

1. Go to https://railway.app/
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Add environment variables
5. Railway auto-detects Python and deploys

**URL:** `https://your-app-name.railway.app`

---

## 📊 Comparison Table

| Feature | Streamlit Cloud | Render Free | Railway | Google Cloud Run |
|---------|----------------|-------------|---------|-----------------|
| **Cost** | FREE | FREE | $5/month | Pay-per-use |
| **Always-on** | ❌ (sleeps) | ❌ (sleeps) | ✅ Yes | ✅ Yes |
| **Cold start** | ~30 sec | ~2 min | ~10 sec | ~5 sec |
| **Setup difficulty** | Easy | Medium | Easy | Hard |
| **Custom domain** | Paid only | Free | Free | Free |
| **Best for** | Demos, portfolios | Side projects | Production | Scale |

---

## 🎯 Recommended Strategy

### For Your Class Project:
1. **Deploy to Streamlit Cloud** (free, easy)
2. **Add password protection** (prevent abuse)
3. **Share URL with instructor**
4. **Monitor usage** (check dashboard)

### For Portfolio:
1. **Keep on Streamlit Cloud**
2. **Add to LinkedIn/Resume**
3. **Link from GitHub README**
4. **Optionally upgrade to paid for always-on**

### For Production (Real Users):
1. **Start with Railway** ($5/month)
2. **Add authentication**
3. **Set up monitoring**
4. **Scale as needed**

---

## 🔗 Adding to Your README

Update your README.md with:

```markdown
## 🌐 Live Demo

Try the live app: **[https://your-app.streamlit.app](https://your-app.streamlit.app)**

Works on:
- 📱 Mobile (iOS, Android)
- 💻 Desktop (Mac, Windows, Linux)
- 📱 Tablet
- 🌍 Any modern browser
```

---

## 📱 QR Code for Mobile Access

Generate a QR code for easy mobile access:

1. Go to https://qr-code-generator.com/
2. Enter your Streamlit URL
3. Download QR code
4. Add to your README or presentation

```markdown
## 📱 Scan to Access on Mobile

![QR Code](qr-code.png)
```

---

## 🐛 Troubleshooting Deployment

### "App failed to start"

**Check:**
- `requirements.txt` has all dependencies
- No hardcoded file paths (use relative paths)
- Secrets are properly configured

### "ModuleNotFoundError"

**Fix:**
```bash
# Regenerate requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: update requirements"
git push
```

### "API key not found"

**Fix:** Check Streamlit Secrets syntax:
```toml
# Correct:
GEMINI_API_KEY = "your_key"

# Wrong:
GEMINI_API_KEY=your_key  # Missing quotes
```

### "Out of memory"

**Solutions:**
1. Upgrade to Streamlit Teams ($20/month, 2GB RAM)
2. Optimize ChromaDB storage
3. Limit number of videos processed
4. Use smaller embedding models

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] App loads successfully
- [ ] Can add a YouTube video
- [ ] Can ask questions and get answers
- [ ] Sources display correctly
- [ ] Works on mobile browser
- [ ] API keys are hidden (not in logs)
- [ ] URL is shareable
- [ ] (Optional) Password protection works

---

## 📞 Get Help

- **Streamlit Community Forum:** https://discuss.streamlit.io/
- **Streamlit Discord:** https://discord.gg/streamlit
- **GitHub Issues:** (your repo issues page)

---

## 🎓 For Your Class Submission

Include in your documentation:

```markdown
## 🌐 Access the Live App

The application is deployed and accessible at:
**https://your-app.streamlit.app**

### Instructions for Instructor:
1. Click the link above
2. (If password protected) Use password: `[provide password]`
3. Try adding a YouTube video (takes ~30 seconds to process)
4. Ask questions in the Chat tab
5. View Sources to see attribution

### Mobile Testing:
- Works on iOS and Android
- Fully responsive design
- All features functional

### Note on Cold Starts:
- The free tier sleeps after inactivity
- First load may take 30 seconds to wake up
- This is normal for free hosting
```

---

**Ready to deploy? Start with Streamlit Cloud - it's free and takes 10 minutes!**

Last Updated: December 2025
