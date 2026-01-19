# 🚀 Quick Deployment Commands

## Initial Setup (First Time Only)

```bash
# 1. Initialize Git
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit - Ready for Railway"

# 4. Create GitHub repo and push
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/yt-recommendation-project.git
git branch -M main
git push -u origin main
```

## Then Deploy on Railway:
1. Go to https://railway.app
2. Sign in with GitHub
3. New Project → Deploy from GitHub repo
4. Select your repository
5. Add environment variable:
   - `YOUTUBE_API_KEY` = your_api_key_here
6. Settings → Generate Domain
7. Done! ✅

## Updating After Changes

```bash
# After making changes to your code
git add .
git commit -m "Describe your changes"
git push origin main

# Railway will automatically redeploy!
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Access at: http://localhost:8000
```

## Verify Deployment Files

Make sure you have these files:
- ✅ app.py (main application)
- ✅ requirements.txt (dependencies)
- ✅ Procfile (Railway start command)
- ✅ railway.json (Railway config)
- ✅ .env (your local API key - NOT committed)
- ✅ .env.example (template)
- ✅ .gitignore (protects .env)
- ✅ README.md (documentation)
- ✅ DEPLOYMENT.md (full guide)

## Environment Variables Needed on Railway

| Variable | Value |
|----------|-------|
| YOUTUBE_API_KEY | Your YouTube Data API v3 key |

That's it! Your app will be live at: `https://[your-app-name].up.railway.app`
