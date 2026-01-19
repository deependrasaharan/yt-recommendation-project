# AI E-Learning Platform

A comprehensive AI-powered E-Learning platform that analyzes YouTube educational content, generates learning materials, and provides interactive learning tools.

## 🌟 Features

- **Advanced YouTube Analysis** - Analyze videos with engagement scores, statistics, and comments
- **Smart Content Analysis** - AI-powered analysis of video content and learning value
- **Related Video Recommendations** - Discover similar educational content
- **Learning Points & Topics** - Automatically extracted key learning objectives
- **Interactive Flashcards** - 10 quality flashcards for any topic
- **Quiz Generation** - 5-question quizzes to test your knowledge
- **URL Analysis** - Analyze specific YouTube videos with detailed insights

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key ([Get one here](https://console.cloud.google.com/apis/credentials))

### Local Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd yt-recommendation-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy the example env file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   
   Open your browser and navigate to: `http://localhost:8000`

## 🌐 Deploy to Railway

### Step 1: Prepare Your Repository

1. Make sure all files are committed to Git:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Push to GitHub (if not already):
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Railway

1. **Sign up for Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub (recommended)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select your repository

3. **Configure Environment Variables**
   - Once deployed, go to your project dashboard
   - Click on "Variables" tab
   - Add the following variable:
     - Key: `YOUTUBE_API_KEY`
     - Value: Your YouTube API key
   - Click "Add" to save

4. **Wait for Deployment**
   - Railway will automatically detect it's a Python app
   - It will install dependencies from `requirements.txt`
   - The app will start using the Procfile configuration

5. **Access Your App**
   - Once deployment is complete, Railway will provide a URL
   - Click "Generate Domain" in the Settings tab
   - Your app will be available at: `https://your-app-name.up.railway.app`

### Troubleshooting Railway Deployment

- **Check Logs**: Click on "Deployments" → Latest deployment → "View Logs"
- **Environment Variables**: Ensure `YOUTUBE_API_KEY` is set correctly
- **Build Failed**: Check if `requirements.txt` has all dependencies
- **Port Issues**: Railway automatically sets the PORT variable, which is handled by the app

## 📁 Project Structure

```
yt-recommendation-project/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── Procfile              # Railway/Heroku deployment config
├── railway.json          # Railway-specific configuration
├── .env                  # Environment variables (DO NOT COMMIT)
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Yes |
| `PORT` | Port number (auto-set by Railway) | No |

### Getting a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "YouTube Data API v3"
4. Go to "Credentials" and create an API key
5. (Recommended) Restrict the API key to YouTube Data API v3 only
6. Copy the key to your `.env` file

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **YouTube Integration**: Google API Python Client
- **Server**: Uvicorn (ASGI server)
- **Deployment**: Railway
- **Environment Management**: python-dotenv

## 📝 API Endpoints

- `GET /` - Home page with search interface
- `POST /search` - Search for educational videos
- `POST /flashcards` - Generate flashcards for a topic
- `POST /quiz` - Generate quiz questions for a topic
- `POST /analyze-video` - Analyze a specific YouTube video URL

## 🔒 Security

- API keys are stored in environment variables
- `.env` file is gitignored to prevent accidental commits
- Use `.env.example` as a template without exposing secrets

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ using FastAPI and YouTube Data API
