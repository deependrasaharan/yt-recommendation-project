# 🚂 Railway Deployment Guide - Step by Step

This guide will walk you through deploying your AI E-Learning Platform on Railway.

## 📋 Prerequisites

Before you start, make sure you have:
- ✅ A GitHub account
- ✅ Your YouTube API key
- ✅ Git installed on your computer
- ✅ Your project files ready

---

## 🎯 Step-by-Step Deployment Process

### Step 1: Prepare Your Code Repository

1. **Initialize Git (if not already done)**
   ```bash
   git init
   ```

2. **Add all files to Git**
   ```bash
   git add .
   ```

3. **Commit your files**
   ```bash
   git commit -m "Ready for Railway deployment"
   ```

4. **Create a GitHub repository**
   - Go to [github.com](https://github.com)
   - Click the "+" icon → "New repository"
   - Name it (e.g., "yt-recommendation-project")
   - Choose "Public" or "Private"
   - Click "Create repository"
   - **DO NOT** initialize with README (you already have one)

5. **Push your code to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/yt-recommendation-project.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Sign Up for Railway

1. **Visit Railway**
   - Go to [railway.app](https://railway.app)

2. **Sign up with GitHub**
   - Click "Login" in the top right
   - Click "Login with GitHub"
   - Authorize Railway to access your GitHub account

---

### Step 3: Create a New Project on Railway

1. **Start a new project**
   - Once logged in, click "New Project"

2. **Deploy from GitHub Repo**
   - Select "Deploy from GitHub repo"
   - If this is your first time, Railway will ask for permissions
   - Click "Configure GitHub App"
   - Select "All repositories" or choose specific repositories
   - Click "Install & Authorize"

3. **Select Your Repository**
   - Find and click on "yt-recommendation-project" (or your repo name)
   - Railway will automatically start building

---

### Step 4: Configure Environment Variables

This is **CRITICAL** - your app won't work without the API key!

1. **Wait for initial deploy to complete** (it might fail, that's okay)

2. **Open your project dashboard**
   - You'll see your service/deployment

3. **Click on your service**
   - Click on the service name (it might be called "app" or your repo name)

4. **Go to Variables tab**
   - Click "Variables" in the top menu

5. **Add your YouTube API Key**
   - Click "+ New Variable"
   - **Variable name**: `YOUTUBE_API_KEY`
   - **Value**: Paste your actual YouTube API key (e.g., AIzaSy...)
   - Click "Add"

6. **The app will automatically redeploy** with the new environment variable

---

### Step 5: Generate a Public URL

1. **Go to Settings tab**
   - Click "Settings" in the top menu

2. **Generate Domain**
   - Scroll down to "Domains" section
   - Click "Generate Domain"
   - Railway will create a public URL like: `your-app-name.up.railway.app`

3. **Wait for deployment to complete**
   - Go to "Deployments" tab to monitor progress
   - Status should show "Success" with a green checkmark
   - This usually takes 2-5 minutes

---

### Step 6: Access Your Deployed App

1. **Copy your Railway URL**
   - It will look like: `https://yt-recommendation-project-production.up.railway.app`

2. **Open in browser**
   - Click the URL or paste it in your browser
   - Your AI E-Learning Platform should load!

3. **Test the functionality**
   - Try searching for a topic (e.g., "Python programming")
   - Generate flashcards
   - Try the quiz feature
   - Analyze a YouTube video URL

---

## 🔍 Monitoring Your Deployment

### View Logs

1. **Go to Deployments tab**
2. **Click on latest deployment**
3. **Click "View Logs"**
4. **Check for any errors**

Common log messages:
- ✅ `✅ YouTube Key loaded successfully` - API key is working
- ❌ `YOUTUBE_API_KEY not found` - Environment variable not set
- ✅ `Uvicorn running on...` - Server started successfully

### Check Metrics

1. **Click "Metrics" tab**
2. **Monitor**:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request counts

---

## 🛠️ Troubleshooting

### Problem: Deployment Failed

**Solution:**
- Check the build logs in "Deployments" tab
- Ensure `requirements.txt` is correct
- Make sure all files are committed and pushed to GitHub

### Problem: App crashes or shows "Application Error"

**Solution:**
1. Check if `YOUTUBE_API_KEY` environment variable is set
2. View logs to see the error message
3. Ensure your YouTube API key is valid
4. Check if you've exceeded YouTube API quota

### Problem: "YOUTUBE_API_KEY not found" error

**Solution:**
1. Go to Variables tab
2. Make sure variable name is exactly: `YOUTUBE_API_KEY` (case-sensitive)
3. Paste your API key without quotes or extra spaces
4. Save and wait for automatic redeploy

### Problem: Can't access the public URL

**Solution:**
1. Make sure domain is generated in Settings → Domains
2. Check if deployment status is "Success"
3. Wait a few minutes - DNS propagation can take time
4. Try accessing with `https://` prefix

---

## 💰 Railway Pricing

Railway offers:
- **Hobby Plan**: $5/month with $5 included usage credit
- **Free Trial**: $5 credit to test (no credit card required initially)
- **Usage-based**: You only pay for what you use

Your app should cost approximately:
- Small traffic: ~$2-3/month
- Medium traffic: ~$5-8/month

---

## 🔄 Updating Your App

When you make changes to your code:

1. **Commit changes locally**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

2. **Push to GitHub**
   ```bash
   git push origin main
   ```

3. **Railway auto-deploys**
   - Railway automatically detects the push
   - Rebuilds and redeploys your app
   - No manual intervention needed!

---

## 🎉 You're Done!

Your AI E-Learning Platform is now live on the internet!

**Your Railway URL**: `https://[your-app-name].up.railway.app`

Share this URL with anyone to let them use your platform!

---

## 📞 Need Help?

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: Join for community support
- **Check Logs**: Always start by checking deployment logs

---

## ✅ Deployment Checklist

Use this checklist to ensure everything is set up:

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] GitHub repo connected to Railway
- [ ] `YOUTUBE_API_KEY` environment variable set
- [ ] Public domain generated
- [ ] Deployment status shows "Success"
- [ ] App accessible via Railway URL
- [ ] Search functionality works
- [ ] Flashcards generate correctly
- [ ] Quiz works properly
- [ ] Video URL analysis works

---

**🎊 Congratulations! Your app is now deployed and accessible worldwide!**
