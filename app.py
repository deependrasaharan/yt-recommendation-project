"""
AI E-Learning Platform - COMPLETE VERSION
- Advanced YouTube Analysis (engagement, comments, etc.)
- Learning Points & Topics
- Related Video Recommendations  
- Working Flashcards & Quiz (template-based, reliable)
"""

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from googleapiclient.discovery import build
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("⚠️ YOUTUBE_API_KEY not found in .env file. Please add it to continue.")

print(f"✅ YouTube Key loaded successfully")

app = FastAPI(title="AI E-Learning Platform - Complete")

# ============================================
# YOUTUBE ADVANCED FUNCTIONS
# ============================================
def extract_video_id(url_or_id: str):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return None

def get_video_statistics(youtube, video_id: str):
    """Get detailed video statistics"""
    try:
        stats_response = youtube.videos().list(
            part='statistics,contentDetails,snippet',
            id=video_id
        ).execute()
        
        if not stats_response.get('items'):
            return {}
            
        item = stats_response['items'][0]
        stats = item.get('statistics', {})
        snippet = item.get('snippet', {})
        
        return {
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments_count': int(stats.get('commentCount', 0)),
            'tags': snippet.get('tags', [])
        }
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}

def get_video_comments(youtube, video_id: str, max_comments: int = 20):
    """Get top comments from video"""
    try:
        comments_response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_comments,
            order='relevance',
            textFormat='plainText'
        ).execute()
        
        comments = []
        for item in comments_response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'text': comment['textDisplay'],
                'author': comment['authorDisplayName'],
                'likes': comment['likeCount'],
                'published': comment['publishedAt']
            })
        return comments
    except Exception as e:
        print(f"Error getting comments: {e}")
        return []

def calculate_engagement_score(stats):
    """Calculate engagement score based on metrics"""
    views = stats.get('views', 0)
    likes = stats.get('likes', 0)
    comments = stats.get('comments_count', 0)
    
    if views == 0:
        return 0.0
    
    like_rate = (likes / views) * 100
    comment_rate = (comments / views) * 100
    engagement = like_rate * 0.7 + comment_rate * 0.3
    score = min(engagement * 2, 10)
    return round(score, 1)

def analyze_video_content(video_data, comments):
    """Analyze video and generate learning insights (template-based)"""
    title = video_data['title'].lower()
    description = video_data['description'].lower()
    
    # Extract key topics from title and description
    common_topics = [
        'introduction', 'basics', 'fundamentals', 'getting started',
        'advanced', 'tutorial', 'guide', 'course', 'examples',
        'practical', 'projects', 'hands-on', 'deep dive'
    ]
    
    topics = []
    words = (title + ' ' + description).split()
    
    # Find important words (capitalize them as topics)
    for word in words:
        clean_word = re.sub(r'[^a-z0-9]', '', word)
        if len(clean_word) > 3 and clean_word not in common_topics:
            if clean_word.upper() in title.upper():
                topics.append(clean_word.capitalize())
    
    # Limit to 5 unique topics
    topics = list(dict.fromkeys(topics))[:5]
    if not topics:
        topics = ['Introduction', 'Core Concepts', 'Examples', 'Practice', 'Summary']
    
    # Generate learning points based on video title
    subject = video_data['title'].split('-')[0].split('|')[0].split(':')[0].strip()
    
    learning_points = [
        f"Understand the fundamental concepts of {subject}",
        f"Learn practical techniques and best practices",
        f"Apply {subject} to real-world scenarios",
        f"Master essential skills through examples",
        f"Build confidence with hands-on practice"
    ]
    
    # Determine target audience from title/description
    target_audience = "All levels"
    if any(word in title for word in ['beginner', 'introduction', 'getting started', 'basics']):
        target_audience = "Beginners"
    elif any(word in title for word in ['advanced', 'expert', 'deep dive', 'master']):
        target_audience = "Advanced"
    elif any(word in title for word in ['intermediate', 'beyond basics']):
        target_audience = "Intermediate"
    
    # Estimate study time based on views and engagement
    engagement = video_data.get('engagement_score', 5)
    time_estimate = "2-3 hours" if engagement > 7 else "3-4 hours"
    
    # Analyze comments for feedback
    positive_words = ['great', 'excellent', 'amazing', 'helpful', 'clear', 'best', 'thanks', 'perfect']
    comment_texts = ' '.join([c['text'].lower() for c in comments[:10]])
    positive_count = sum(comment_texts.count(word) for word in positive_words)
    
    audience_feedback = "Highly praised by viewers" if positive_count > 5 else "Positive viewer reception"
    
    strengths = [
        "Clear explanations and structure",
        "Practical examples and demonstrations",
        "Engaging presentation style",
        "Comprehensive coverage of topic"
    ]
    
    rating = min(max(video_data.get('engagement_score', 7), 6), 10)
    
    return {
        'summary': f"Educational tutorial covering {subject}. Provides clear explanations with practical examples and demonstrations.",
        'learning_value': f"High-quality content suitable for {target_audience.lower()}. Structured approach to learning key concepts.",
        'audience_feedback': audience_feedback,
        'strengths': strengths,
        'rating': rating,
        'key_topics': topics,
        'learning_points': learning_points,
        'target_audience': target_audience,
        'time_estimate': time_estimate
    }

def get_related_videos(youtube, topics, exclude_video_id, max_results=5):
    """Get related videos based on topics"""
    try:
        if not topics:
            return []
        
        search_query = ' '.join(topics[:3])
        
        search_response = youtube.search().list(
            q=search_query,
            part='id,snippet',
            maxResults=max_results + 1,
            type='video',
            order='relevance',
            videoDuration='medium'
        ).execute()
        
        related_videos = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            
            if video_id == exclude_video_id:
                continue
                
            snippet = item['snippet']
            stats = get_video_statistics(youtube, video_id)
            engagement_score = calculate_engagement_score(stats)
            
            related_videos.append({
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'][:200] + '...',
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel_title': snippet['channelTitle'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'views': stats.get('views', 0),
                'likes': stats.get('likes', 0),
                'engagement_score': engagement_score
            })
            
            if len(related_videos) >= max_results:
                break
        
        related_videos.sort(key=lambda x: x['engagement_score'], reverse=True)
        return related_videos[:max_results]
        
    except Exception as e:
        print(f"Error getting related videos: {e}")
        return []

def search_youtube_videos_enhanced(query, max_results=6):
    """Enhanced YouTube search with full analysis"""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results * 2,
            type='video',
            order='relevance',
            videoDuration='medium'
        ).execute()
        
        videos = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            print(f"Analyzing: {snippet['title'][:50]}...")
            
            stats = get_video_statistics(youtube, video_id)
            comments = get_video_comments(youtube, video_id, max_comments=20)
            engagement_score = calculate_engagement_score(stats)
            
            video_data = {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel_title': snippet['channelTitle'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'views': stats.get('views', 0),
                'likes': stats.get('likes', 0),
                'comments_count': stats.get('comments_count', 0),
                'published_at': snippet.get('publishedAt', ''),
                'engagement_score': engagement_score,
                'top_comments': comments[:5]
            }
            
            analysis = analyze_video_content(video_data, comments)
            video_data['ai_analysis'] = analysis
            
            videos.append(video_data)
        
        videos.sort(key=lambda x: (
            x['engagement_score'] * 0.5 + 
            x['ai_analysis']['rating'] * 0.5
        ), reverse=True)
        
        return videos[:max_results]
        
    except Exception as e:
        print(f"YouTube Error: {e}")
        return []

def analyze_single_video(video_url: str):
    """Analyze a single video from URL with related videos"""
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}
        
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        video_response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            return {"error": "Video not found"}
        
        item = video_response['items'][0]
        snippet = item['snippet']
        stats = item['statistics']
        
        comments = get_video_comments(youtube, video_id, max_comments=30)
        
        engagement_score = calculate_engagement_score({
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments_count': int(stats.get('commentCount', 0))
        })
        
        video_data = {
            'video_id': video_id,
            'title': snippet['title'],
            'description': snippet['description'],
            'thumbnail': snippet['thumbnails']['high']['url'],
            'channel_title': snippet['channelTitle'],
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0)),
            'comments_count': int(stats.get('commentCount', 0)),
            'published_at': snippet.get('publishedAt', ''),
            'engagement_score': engagement_score,
            'top_comments': comments[:10]
        }
        
        print("Analyzing video content...")
        analysis = analyze_video_content(video_data, comments)
        video_data['ai_analysis'] = analysis
        
        print("Finding related videos...")
        related_videos = get_related_videos(
            youtube, 
            analysis.get('key_topics', []), 
            video_id,
            max_results=5
        )
        video_data['related_videos'] = related_videos
        
        return video_data
        
    except Exception as e:
        print(f"Error analyzing video: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# ============================================
# FLASHCARD & QUIZ GENERATION
# ============================================
def generate_flashcards(topic):
    """Generate 10 quality flashcards"""
    flashcards = [
        {
            'question': f'What is {topic}?',
            'answer': f'{topic} is an important concept in computer science and programming that helps solve real-world problems through systematic approaches.',
            'difficulty': 'Easy'
        },
        {
            'question': f'Why should you learn {topic}?',
            'answer': f'Learning {topic} helps you develop problem-solving skills, understand core programming concepts, and opens up career opportunities in technology.',
            'difficulty': 'Easy'
        },
        {
            'question': f'What are the key components of {topic}?',
            'answer': f'The main components include theoretical foundations, practical implementation, syntax and structure, and real-world application patterns.',
            'difficulty': 'Medium'
        },
        {
            'question': f'How is {topic} used in industry?',
            'answer': f'{topic} is widely used across software development, data analysis, web applications, automation, and many other practical business applications.',
            'difficulty': 'Medium'
        },
        {
            'question': f'What challenges exist when learning {topic}?',
            'answer': f'Common challenges include understanding abstract concepts, debugging errors, memorizing syntax, and applying theory to practice.',
            'difficulty': 'Medium'
        },
        {
            'question': f'What prerequisites are needed for {topic}?',
            'answer': f'Basic prerequisites include logical thinking, computer literacy, patience for problem-solving, and willingness to practice regularly.',
            'difficulty': 'Easy'
        },
        {
            'question': f'What tools are commonly used with {topic}?',
            'answer': f'Common tools include integrated development environments (IDEs), code editors, version control systems, and various libraries and frameworks.',
            'difficulty': 'Medium'
        },
        {
            'question': f'How long does it take to learn {topic}?',
            'answer': f'Learning basics typically takes several weeks to months, but achieving mastery requires continuous practice and years of hands-on experience.',
            'difficulty': 'Easy'
        },
        {
            'question': f'What are best practices for {topic}?',
            'answer': f'Best practices include daily practice, working on projects, reading documentation, learning from others, and regularly reviewing concepts.',
            'difficulty': 'Medium'
        },
        {
            'question': f'What career paths involve {topic}?',
            'answer': f'Career opportunities include software developer, data scientist, system administrator, web developer, and many other technology-focused roles.',
            'difficulty': 'Medium'
        }
    ]
    print(f"✅ Created {len(flashcards)} flashcards")
    return flashcards

def generate_quiz(topic):
    """Generate 5 quality quiz questions"""
    quiz = [
        {
            'id': 1,
            'question': f'What is the primary purpose of learning {topic}?',
            'options': {
                'A': 'To memorize syntax and commands',
                'B': 'To develop problem-solving and computational thinking skills',
                'C': 'To impress others with technical knowledge',
                'D': 'To complete academic requirements only'
            },
            'correct_answer': 'B',
            'explanation': f'The main goal of learning {topic} is to develop problem-solving skills and computational thinking that apply beyond just coding.',
            'difficulty': 'Easy'
        },
        {
            'id': 2,
            'question': f'Which is essential when learning {topic}?',
            'options': {
                'A': 'Expensive equipment',
                'B': 'Perfect memory',
                'C': 'Regular practice and hands-on experience',
                'D': 'Advanced mathematics degree'
            },
            'correct_answer': 'C',
            'explanation': 'Regular practice and hands-on experience are crucial for mastering any technical concept.',
            'difficulty': 'Easy'
        },
        {
            'id': 3,
            'question': f'What is a common mistake when learning {topic}?',
            'options': {
                'A': 'Trying to understand everything before practicing',
                'B': 'Writing too much code',
                'C': 'Using online resources',
                'D': 'Working on small projects'
            },
            'correct_answer': 'A',
            'explanation': 'Beginners often try to understand everything theoretically before practicing, but hands-on experience is essential.',
            'difficulty': 'Medium'
        },
        {
            'id': 4,
            'question': f'Which approach works best for {topic}?',
            'options': {
                'A': 'Only reading books',
                'B': 'Only watching videos',
                'C': 'Combining theory with practical projects',
                'D': 'Memorizing code examples'
            },
            'correct_answer': 'C',
            'explanation': 'The most effective learning combines theoretical understanding with practical application through projects.',
            'difficulty': 'Medium'
        },
        {
            'id': 5,
            'question': f'What indicates real progress in {topic}?',
            'options': {
                'A': 'Knowing all syntax by heart',
                'B': 'Ability to solve new problems independently',
                'C': 'Reading advanced textbooks',
                'D': 'Completing courses quickly'
            },
            'correct_answer': 'B',
            'explanation': 'True progress is shown by the ability to solve new problems and debug errors independently, not just memorization.',
            'difficulty': 'Hard'
        }
    ]
    print(f"✅ Created {len(quiz)} questions")
    return quiz

# ============================================
# API ENDPOINTS
# ============================================
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

@app.post("/api/learn")
async def learn(topic: str = Form(...)):
    try:
        print(f"\n{'='*60}")
        print(f"Creating learning session for: {topic}")
        print(f"{'='*60}")
        
        print("\n[1/3] Searching and analyzing YouTube videos...")
        videos = search_youtube_videos_enhanced(f"{topic} tutorial", max_results=6)
        print(f"     ✅ Analyzed {len(videos)} videos")
        
        print("\n[2/3] Generating flashcards...")
        flashcards = generate_flashcards(topic)
        
        print("\n[3/3] Generating quiz...")
        quiz = generate_quiz(topic)
        
        print(f"\n{'='*60}")
        print("✅ SUCCESS!")
        print(f"{'='*60}\n")
        
        return JSONResponse({
            "success": True,
            "topic": topic,
            "videos": videos,
            "flashcards": flashcards,
            "quiz": quiz
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/api/analyze-video")
async def analyze_video_endpoint(video_url: str = Form(...)):
    """Analyze a specific YouTube video"""
    try:
        print(f"Analyzing video URL: {video_url}")
        result = analyze_single_video(video_url)
        
        if "error" in result:
            return JSONResponse({
                "success": False,
                "error": result["error"]
            }, status_code=400)
        
        return JSONResponse({
            "success": True,
            "video": result
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# HTML with all features included
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI E-Learning Platform - Complete</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --success: #10b981;
            --danger: #ef4444;
            --dark: #1e293b;
            --gray: #64748b;
            --light-gray: #f1f5f9;
            --white: #ffffff;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
            color: var(--dark);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 15px;
        }
        
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            margin: 5px;
        }
        
        .search-section {
            background: white;
            padding: 50px;
            border-radius: 24px;
            box-shadow: var(--shadow-xl);
            margin-bottom: 40px;
        }
        
        .search-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .search-tab {
            padding: 12px 24px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            color: var(--gray);
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .search-tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        .search-content {
            display: none;
        }
        
        .search-content.active {
            display: block;
        }
        
        .search-box {
            display: flex;
            gap: 15px;
            max-width: 700px;
            margin: 0 auto;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 18px 24px;
            font-size: 1.05rem;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            font-family: inherit;
        }
        
        button.primary-btn {
            padding: 18px 40px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 1.05rem;
            font-weight: 600;
            cursor: pointer;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            background: white;
            border-radius: 24px;
            display: none;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 6px solid #f3f4f6;
            border-top: 6px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .tabs-container {
            background: white;
            border-radius: 24px;
            box-shadow: var(--shadow-xl);
            display: none;
        }
        
        .tabs {
            display: flex;
            background: var(--light-gray);
            padding: 8px;
        }
        
        .tab-button {
            flex: 1;
            padding: 16px;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--gray);
            border-radius: 14px;
        }
        
        .tab-button.active {
            background: white;
            color: var(--primary);
            box-shadow: var(--shadow);
        }
        
        .tab-content {
            display: none;
            padding: 40px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .videos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 30px;
        }
        
        .video-card {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid #f1f5f9;
            box-shadow: var(--shadow);
        }
        
        .video-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
            border-color: var(--primary);
        }
        
        .video-thumbnail {
            width: 100%;
            height: 220px;
            object-fit: cover;
        }
        
        .video-info {
            padding: 20px;
        }
        
        .video-title {
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 10px;
        }
        
        .video-stats {
            display: flex;
            gap: 15px;
            font-size: 0.85rem;
            color: var(--gray);
            margin: 10px 0;
        }
        
        .engagement-score {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px;
            background: var(--light-gray);
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .score-high { color: #10b981; }
        .score-medium { color: #f59e0b; }
        .score-low { color: #ef4444; }
        
        .learning-points-preview {
            border-top: 2px solid #f1f5f9;
            padding-top: 12px;
            margin-top: 12px;
        }
        
        .learning-points-list {
            margin-top: 8px;
            padding-left: 20px;
        }
        
        .learning-point-item {
            font-size: 0.85rem;
            color: var(--dark);
            margin-bottom: 6px;
        }
        
        .topics-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }
        
        .topic-tag {
            padding: 4px 10px;
            background: rgba(139, 92, 246, 0.1);
            color: var(--secondary);
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .expand-btn {
            margin-top: 10px;
            padding: 8px 16px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            width: 100%;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
        }
        
        .modal-content {
            max-width: 900px;
            margin: 50px auto;
            background: white;
            border-radius: 24px;
            padding: 40px;
        }
        
        .modal-close {
            float: right;
            font-size: 2rem;
            cursor: pointer;
            color: var(--gray);
            line-height: 1;
        }
        
        .related-video-item {
            display: flex;
            gap: 15px;
            padding: 15px;
            background: var(--light-gray);
            border-radius: 12px;
            margin-bottom: 12px;
            cursor: pointer;
        }
        
        .related-video-item:hover {
            background: white;
            box-shadow: var(--shadow);
        }
        
        .related-video-thumb {
            width: 120px;
            height: 68px;
            border-radius: 8px;
            object-fit: cover;
        }
        
        .flashcard {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 60px 40px;
            border-radius: 20px;
            min-height: 280px;
            cursor: pointer;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: var(--shadow-xl);
        }
        
        .flashcard-question, .flashcard-answer {
            font-size: 1.4rem;
            line-height: 1.8;
        }
        
        .flashcard-controls {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        
        .nav-button {
            padding: 12px 28px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .quiz-question {
            background: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: var(--shadow);
        }
        
        .question-text {
            font-size: 1.2rem;
            margin-bottom: 20px;
            font-weight: 600;
        }
        
        .quiz-option {
            padding: 16px;
            background: var(--light-gray);
            border: 2px solid transparent;
            border-radius: 12px;
            margin-bottom: 12px;
            cursor: pointer;
        }
        
        .quiz-option:hover {
            border-color: var(--primary);
        }
        
        .quiz-option.selected {
            background: rgba(99, 102, 241, 0.1);
            border-color: var(--primary);
        }
        
        .quiz-option.correct {
            background: rgba(16, 185, 129, 0.1);
            border-color: var(--success);
        }
        
        .quiz-option.incorrect {
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--danger);
        }
        
        .explanation {
            display: none;
            margin-top: 16px;
            padding: 16px;
            background: rgba(99, 102, 241, 0.05);
            border-left: 4px solid var(--primary);
            border-radius: 0 12px 12px 0;
        }
        
        .submit-quiz {
            padding: 18px 48px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            display: block;
            margin: 40px auto;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5rem;
            }
            .videos-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 AI E-Learning Platform</h1>
            <p style="font-size: 1.3rem; opacity: 0.95;">Advanced Analysis + Working Features</p>
            <div>
                <span class="badge">📊 Engagement Metrics</span>
                <span class="badge">💡 Learning Points</span>
                <span class="badge">🎬 Related Videos</span>
                <span class="badge">✅ 100% Working</span>
            </div>
        </div>

        <div class="search-section">
            <div class="search-tabs">
                <button class="search-tab active" onclick="switchSearchTab('topic')">📚 Search by Topic</button>
                <button class="search-tab" onclick="switchSearchTab('url')">🔗 Analyze Video URL</button>
            </div>
            
            <div id="topicSearch" class="search-content active">
                <div class="search-box">
                    <input type="text" id="topicInput" placeholder="Enter topic to learn...">
                    <button class="primary-btn" onclick="startLearning()">🚀 Start Learning</button>
                </div>
            </div>
            
            <div id="urlSearch" class="search-content">
                <div class="search-box">
                    <input type="text" id="videoUrlInput" placeholder="Paste YouTube URL...">
                    <button class="primary-btn" onclick="analyzeVideoUrl()">🔍 Analyze Video</button>
                </div>
            </div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <h3>Creating Your Learning Experience</h3>
            <p>Analyzing videos, generating content...</p>
        </div>

        <div class="tabs-container" id="tabsContainer">
            <div class="tabs">
                <button class="tab-button active" onclick="showTab('videos')">📹 Videos</button>
                <button class="tab-button" onclick="showTab('flashcards')">🗂️ Flashcards</button>
                <button class="tab-button" onclick="showTab('quiz')">📝 Quiz</button>
            </div>

            <div id="videos" class="tab-content active">
                <h2 style="margin-bottom: 30px;">📹 Educational Videos</h2>
                <div id="videosGrid" class="videos-grid"></div>
            </div>

            <div id="flashcards" class="tab-content">
                <h2 style="margin-bottom: 20px;">🗂️ Study Flashcards</h2>
                <div class="flashcard-controls">
                    <button onclick="previousCard()" class="nav-button">← Previous</button>
                    <span id="cardCounter">0 / 0</span>
                    <button onclick="nextCard()" class="nav-button">Next →</button>
                </div>
                <div id="flashcardsContainer"></div>
            </div>

            <div id="quiz" class="tab-content">
                <h2 style="margin-bottom: 20px;">📝 Test Your Knowledge</h2>
                <div id="quizContainer"></div>
            </div>
        </div>
    </div>

    <div id="videoModal" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        let flashcardsData = [];
        let currentCard = 0;
        let quizData = [];
        let userAnswers = [];
        let showingAnswer = false;
        let currentSearchTab = 'topic';

        function switchSearchTab(tab) {
            currentSearchTab = tab;
            document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.search-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab === 'topic' ? 'topicSearch' : 'urlSearch').classList.add('active');
        }

        function showTab(name) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
        }

        async function startLearning() {
            const topic = document.getElementById('topicInput').value.trim();
            if (!topic) {
                alert('Please enter a topic!');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('tabsContainer').style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('topic', topic);
                const response = await fetch('/api/learn', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    displayVideos(data.videos);
                    displayFlashcards(data.flashcards);
                    displayQuiz(data.quiz);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('tabsContainer').style.display = 'block';
                } else {
                    alert('Error: ' + data.error);
                    document.getElementById('loading').style.display = 'none';
                }
            } catch (error) {
                alert('Error: ' + error.message);
                document.getElementById('loading').style.display = 'none';
            }
        }

        async function analyzeVideoUrl() {
            const url = document.getElementById('videoUrlInput').value.trim();
            if (!url) {
                alert('Please enter a YouTube URL!');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('tabsContainer').style.display = 'none';

            try {
                const formData = new FormData();
                formData.append('video_url', url);
                const response = await fetch('/api/analyze-video', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    displayVideos([data.video]);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('tabsContainer').style.display = 'block';
                    showTab('videos');
                } else {
                    alert('Error: ' + data.error);
                    document.getElementById('loading').style.display = 'none';
                }
            } catch (error) {
                alert('Error: ' + error.message);
                document.getElementById('loading').style.display = 'none';
            }
        }

        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }

        function getScoreClass(score) {
            if (score >= 7) return 'score-high';
            if (score >= 4) return 'score-medium';
            return 'score-low';
        }

        function getScoreEmoji(score) {
            if (score >= 8) return '🔥';
            if (score >= 6) return '⭐';
            if (score >= 4) return '👍';
            return '📊';
        }

        function displayVideos(videos) {
            const grid = document.getElementById('videosGrid');
            if (!videos || videos.length === 0) {
                grid.innerHTML = '<div style="text-align: center; padding: 60px;">No videos found</div>';
                return;
            }

            grid.innerHTML = videos.map((v, index) => {
                const analysis = v.ai_analysis || {};
                const scoreClass = getScoreClass(v.engagement_score);
                const scoreEmoji = getScoreEmoji(v.engagement_score);
                const isRecommended = index === 0;
                const learningPoints = analysis.learning_points || [];
                const topics = analysis.key_topics || [];

                return `
                <div class="video-card" onclick="showVideoDetails(${index})">
                    <img src="${v.thumbnail}" class="video-thumbnail" alt="${v.title}">
                    ${isRecommended ? '<div style="position: absolute; top: 10px; right: 10px; padding: 6px 12px; background: linear-gradient(135deg, #10b981, #059669); color: white; border-radius: 8px; font-size: 0.85rem; font-weight: 600;">⭐ TOP PICK</div>' : ''}
                    <div class="video-info">
                        <div class="video-title">${v.title}</div>
                        <div style="color: var(--gray); font-size: 0.9rem; margin-bottom: 10px;">📺 ${v.channel_title}</div>

                        <div class="video-stats">
                            <span>👁️ ${formatNumber(v.views)}</span>
                            <span>👍 ${formatNumber(v.likes)}</span>
                            <span>💬 ${formatNumber(v.comments_count)}</span>
                        </div>

                        <div class="engagement-score">
                            <span style="font-size: 0.85rem; font-weight: 600; color: var(--gray);">Engagement</span>
                            <span class="${scoreClass}" style="font-weight: 700; font-size: 1.1rem;">
                                ${scoreEmoji} ${v.engagement_score}/10
                            </span>
                        </div>

                        ${topics.length > 0 ? `
                        <div style="margin-top: 10px;">
                            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--primary); letter-spacing: 0.5px; margin-bottom: 6px;">📚 Topics</div>
                            <div class="topics-tags">
                                ${topics.slice(0, 5).map(t => `<span class="topic-tag">${t}</span>`).join('')}
                            </div>
                        </div>
                        ` : ''}

                        ${learningPoints.length > 0 ? `
                        <div class="learning-points-preview">
                            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--primary); letter-spacing: 0.5px; margin-bottom: 6px;">💡 What You'll Learn</div>
                            <ul class="learning-points-list">
                                ${learningPoints.slice(0, 3).map(point => `<li class="learning-point-item">${point}</li>`).join('')}
                            </ul>
                            ${learningPoints.length > 3 ? `<p style="font-size: 0.8rem; color: var(--gray); margin-top: 6px;">+ ${learningPoints.length - 3} more...</p>` : ''}
                        </div>
                        ` : ''}

                        <button class="expand-btn" onclick="event.stopPropagation(); showVideoDetails(${index})">
                            View Full Analysis${v.related_videos && v.related_videos.length > 0 ? ' & Related Videos' : ''}
                        </button>
                    </div>
                </div>
                `;
            }).join('');

            window.videosData = videos;
        }

        function showVideoDetails(index) {
            const video = window.videosData[index];
            const analysis = video.ai_analysis || {};
            const comments = video.top_comments || [];
            const learningPoints = analysis.learning_points || [];
            const topics = analysis.key_topics || [];
            const relatedVideos = video.related_videos || [];

            const modalContent = `
                <h2 style="margin-bottom: 20px;">${video.title}</h2>

                <div style="margin-bottom: 20px;">
                    <a href="${video.url}" target="_blank" style="display: inline-block; padding: 12px 24px; background: #ff0000; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                        ▶️ Watch on YouTube
                    </a>
                </div>

                <div style="background: var(--light-gray); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                    <h3 style="margin-bottom: 15px;">📊 Video Statistics</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                        <div>
                            <div style="font-size: 0.85rem; color: var(--gray);">Views</div>
                            <div style="font-size: 1.5rem; font-weight: 700;">👁️ ${formatNumber(video.views)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.85rem; color: var(--gray);">Likes</div>
                            <div style="font-size: 1.5rem; font-weight: 700;">👍 ${formatNumber(video.likes)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.85rem; color: var(--gray);">Comments</div>
                            <div style="font-size: 1.5rem; font-weight: 700;">💬 ${formatNumber(video.comments_count)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.85rem; color: var(--gray);">Engagement</div>
                            <div style="font-size: 1.5rem; font-weight: 700;" class="${getScoreClass(video.engagement_score)}">
                                ${getScoreEmoji(video.engagement_score)} ${video.engagement_score}/10
                            </div>
                        </div>
                    </div>
                </div>

                <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05)); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid rgba(99, 102, 241, 0.2);">
                    <h3 style="margin-bottom: 15px;">🎓 Learning Analysis</h3>

                    <div style="margin-bottom: 15px;">
                        <strong style="color: var(--primary);">Summary:</strong>
                        <p>${analysis.summary || 'Educational content'}</p>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <strong style="color: var(--primary);">Learning Value (${analysis.rating}/10):</strong>
                        <p>${analysis.learning_value || 'Good resource'}</p>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <strong style="color: var(--primary);">Target Audience:</strong>
                        <p>${analysis.target_audience || 'All levels'}</p>
                    </div>

                    <div style="margin-bottom: 15px;">
                        <strong style="color: var(--primary);">Study Time:</strong>
                        <p>${analysis.time_estimate || '2-3 hours'}</p>
                    </div>
                </div>

                ${topics.length > 0 ? `
                <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: var(--shadow);">
                    <h3 style="margin-bottom: 15px;">📚 Topics Covered</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        ${topics.map(topic => `<span style="padding: 8px 16px; background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(99, 102, 241, 0.1)); color: var(--secondary); border-radius: 20px; font-weight: 600;">${topic}</span>`).join('')}
                    </div>
                </div>
                ` : ''}

                ${learningPoints.length > 0 ? `
                <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: var(--shadow);">
                    <h3 style="margin-bottom: 15px;">💡 Complete Learning Points</h3>
                    <ol style="padding-left: 20px; line-height: 2;">
                        ${learningPoints.map(point => `<li style="margin-bottom: 10px; color: var(--dark);"><strong>${point}</strong></li>`).join('')}
                    </ol>
                </div>
                ` : ''}

                ${comments.length > 0 ? `
                <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: var(--shadow);">
                    <h3 style="margin-bottom: 15px;">💬 Top Comments</h3>
                    ${comments.map(c => `
                        <div style="background: var(--light-gray); padding: 15px; border-radius: 10px; margin-bottom: 12px;">
                            <div style="font-weight: 600; margin-bottom: 6px; display: flex; justify-content: space-between;">
                                <span>${c.author}</span>
                                <span style="font-size: 0.85rem; color: var(--gray);">👍 ${c.likes}</span>
                            </div>
                            <div>${c.text}</div>
                        </div>
                    `).join('')}
                </div>
                ` : ''}

                ${relatedVideos.length > 0 ? `
                <div style="border-top: 3px solid #f1f5f9; padding-top: 30px; margin-top: 30px;">
                    <h3 style="margin-bottom: 15px;">🎬 Related Videos</h3>
                    ${relatedVideos.map(rv => `
                        <div class="related-video-item" onclick="window.open('${rv.url}', '_blank')">
                            <img src="${rv.thumbnail}" class="related-video-thumb" alt="${rv.title}">
                            <div style="flex: 1;">
                                <div style="font-weight: 600; margin-bottom: 5px;">${rv.title}</div>
                                <div style="color: var(--gray); font-size: 0.85rem; margin-bottom: 5px;">📺 ${rv.channel_title}</div>
                                <div style="display: flex; gap: 10px; font-size: 0.8rem; color: var(--gray);">
                                    <span>👁️ ${formatNumber(rv.views)}</span>
                                    <span>👍 ${formatNumber(rv.likes)}</span>
                                    <span class="${getScoreClass(rv.engagement_score)}" style="font-weight: 600;">
                                        ${getScoreEmoji(rv.engagement_score)} ${rv.engagement_score}/10
                                    </span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                ` : ''}
            `;

            document.getElementById('modalContent').innerHTML = modalContent;
            document.getElementById('videoModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('videoModal').style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('videoModal');
            if (event.target === modal) {
                closeModal();
            }
        }

        function displayFlashcards(cards) {
            flashcardsData = cards;
            currentCard = 0;
            showingAnswer = false;
            updateFlashcard();
        }

        function updateFlashcard() {
            const card = flashcardsData[currentCard];
            document.getElementById('cardCounter').textContent = `${currentCard + 1} / ${flashcardsData.length}`;
            document.getElementById('flashcardsContainer').innerHTML = `
                <div class="flashcard" onclick="flipCard()">
                    <div class="flashcard-${showingAnswer ? 'answer' : 'question'}">
                        ${showingAnswer ? card.answer : card.question}
                    </div>
                    <div style="margin-top: 30px; opacity: 0.9;">
                        ${showingAnswer ? '🔄 Click to see question' : '💡 Click to reveal answer'}
                    </div>
                </div>
            `;
        }

        function flipCard() {
            showingAnswer = !showingAnswer;
            updateFlashcard();
        }

        function previousCard() {
            if (currentCard > 0) {
                currentCard--;
                showingAnswer = false;
                updateFlashcard();
            }
        }

        function nextCard() {
            if (currentCard < flashcardsData.length - 1) {
                currentCard++;
                showingAnswer = false;
                updateFlashcard();
            }
        }

        function displayQuiz(questions) {
            quizData = questions;
            userAnswers = new Array(questions.length).fill(null);

            document.getElementById('quizContainer').innerHTML = questions.map((q, i) => `
                <div class="quiz-question" id="q${i}">
                    <div class="question-text">Question ${i + 1}: ${q.question}</div>
                    ${Object.entries(q.options).map(([letter, text]) => `
                        <div class="quiz-option" onclick="selectOption(${i}, '${letter}')">
                            <strong>${letter})</strong> ${text}
                        </div>
                    `).join('')}
                    <div class="explanation" id="exp${i}">
                        <strong>💡 Explanation:</strong>
                        ${q.explanation}
                    </div>
                </div>
            `).join('') + '<button class="submit-quiz" onclick="submitQuiz()">📊 Submit Quiz</button>';
        }

        function selectOption(qIndex, letter) {
            userAnswers[qIndex] = letter;
            const options = document.querySelectorAll(`#q${qIndex} .quiz-option`);
            options.forEach(opt => opt.classList.remove('selected'));
            event.target.classList.add('selected');
        }

        function submitQuiz() {
            let score = 0;
            quizData.forEach((q, i) => {
                const correct = q.correct_answer;
                const user = userAnswers[i];
                if (user === correct) score++;

                const options = document.querySelectorAll(`#q${i} .quiz-option`);
                options.forEach(opt => {
                    const letter = opt.textContent.trim()[0];
                    if (letter === correct) opt.classList.add('correct');
                    if (letter === user && user !== correct) opt.classList.add('incorrect');
                });
                document.getElementById(`exp${i}`).style.display = 'block';
            });

            const percent = Math.round((score / quizData.length) * 100);
            alert(`You scored ${score} out of ${quizData.length}! (${percent}%)`);
            document.querySelector('.submit-quiz').style.display = 'none';
        }

        document.getElementById('topicInput')?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') startLearning();
        });

        document.getElementById('videoUrlInput')?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') analyzeVideoUrl();
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AI E-Learning Platform - COMPLETE WORKING VERSION")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Advanced YouTube Analysis")
    print("  ✅ Engagement Scores & Comments")
    print("  ✅ Learning Points & Topics")
    print("  ✅ Related Video Recommendations")
    print("  ✅ Working Flashcards (10 cards)")
    print("  ✅ Working Quiz (5 questions)")
    print("  ✅ URL Analysis with Related Videos")
    
    # Get port from environment variable (for Railway/Heroku) or use default
    port = int(os.getenv("PORT", 8000))
    print(f"\n📍 Server: http://localhost:{port}")
    print("Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=port)