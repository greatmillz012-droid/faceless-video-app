# Automated Video Generation Setup Guide

Your app is now ready to **automatically generate and post AI videos daily** to your YouTube channel!

## ✅ What's Already Done

- ✅ Backend running on `http://localhost:8000`
- ✅ Frontend running on `http://localhost:3000`
- ✅ SQLite database initialized
- ✅ YouTube account connected ("Hacks with joe")
- ✅ All API keys configured (OpenAI, ElevenLabs, Pexels)
- ✅ Celery & Celery Beat installed (task scheduler)

---

## 📋 Step 1: Configure Your Settings

The app needs to know **what to post and when**. Configure these settings via API:

```bash
curl -X PUT http://localhost:8000/api/settings \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "niche": "Hacks with joe",
    "posts_per_day": 3,
    "posting_times": "09:00,18:00",
    "video_length_seconds": 60,
    "voice_style": "professional",
    "auto_post_enabled": true
  }'
```

### Settings Explained:
- **niche**: Topic for video scripts (e.g., "Technology Hacks", "Business Tips")
- **posts_per_day**: How many videos per day (max 3)
- **posting_times**: When to post (24-hour format, comma-separated)
  - Example: `"09:00,18:00"` = Post at 9 AM and 6 PM
- **video_length_seconds**: Shorts duration (30-90 seconds)
- **voice_style**: Voice tone (`professional`, `casual`, `energetic`)
- **auto_post_enabled**: `true` to enable automation

### Get Your JWT Token:

1. Register on http://localhost:3000/register
2. Login and get the JWT token from the response
3. Use it in the `Authorization: Bearer <TOKEN>` header

**OR** use the test token from your user account:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser@local.dev", "password": "password123"}'
```

---

## 🚀 Step 2: Start the Celery Beat Scheduler

**In a NEW terminal window**, run:

```bash
cd c:/Users/LENOVO/faceless-video-app/backend
.\.venv311\Scripts\python.exe -m celery -A app.worker.celery_app beat --loglevel=info
```

**Expected output:**
```
celery beat v5.x.x is starting.
...
[scheduler] Scheduler: Ticking with max interval->5.00 seconds
```

This scheduler checks **every minute** if it's time to post. When the time matches your `posting_times`, it triggers video generation.

---

## ⚙️ Step 3: Start the Celery Worker

**In ANOTHER NEW terminal window**, run:

```bash
cd c:/Users/LENOVO/faceless-video-app/backend
.\.venv311\Scripts\python.exe -m celery -A app.worker.celery_app worker --loglevel=info
```

**Expected output:**
```
-------------- celery@COMPUTERNAME v5.x.x ...
...
[*] Ready to accept tasks.
```

This worker **executes the video generation pipeline** when triggered by the scheduler.

---

## 🎬 How It Works (Complete Flow)

### Timeline: Video Generation Every Time You Have a Scheduled Post

**Example: You configured `posting_times: "14:30"` and `posts_per_day: 1`**

**At 2:30 PM exactly:**

1. **Celery Beat** checks the database
2. Finds your user with `auto_post_enabled=true` and time matches
3. Triggers `generate_and_post_video` task

**Worker then:**

```
1. 📝 Generate Script
   ↓ Calls OpenAI with your niche
   ↓ Creates a 60-second script about "Hacks with joe"
   
2. 🎙️ Generate Voice-Over
   ↓ Uses ElevenLabs API
   ↓ Creates MP3 audio with your configured voice style
   
3. 🎬 Fetch Stock Footage
   ↓ Searches Pexels API for relevant background video
   ↓ Downloads MP4 file matching your niche
   
4. 📍 Get Word Timestamps
   ↓ Analyzes audio to sync captions with speech
   
5. 🎞️ Render Final Video
   ↓ Uses FFmpeg to overlay audio on footage
   ↓ Adds captions synchronized with words
   ↓ Creates final 60-second short-form video
   
6. ⬆️ Upload to YouTube
   ↓ Posts to your "Hacks with joe" channel
   ↓ Sets as unlisted/public based on config
   ↓ Stores video record in database

✅ Done! Next post scheduled for 2:30 PM tomorrow (if posts_per_day allows)
```

---

## 🧪 Testing (Manual Trigger)

Don't want to wait until scheduled time? **Manually trigger video generation:**

```bash
curl -X POST http://localhost:8000/api/videos/generate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

This **immediately** starts the video generation pipeline.

---

## 📊 Monitoring

### View Video Status
```bash
curl http://localhost:8000/api/videos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### View Logs
- **Beat scheduler**: Check terminal 2 for scheduling decisions
- **Celery worker**: Check terminal 3 for pipeline progress
- **Backend API**: Check terminal 1 for API requests

### Database Query
```bash
cd c:/Users/LENOVO/faceless-video-app/backend
.\.venv311\Scripts\python.exe -c "
import sqlite3
conn = sqlite3.connect('facelessapp.db')
cursor = conn.cursor()
cursor.execute('SELECT id, user_id, status, created_at FROM videos ORDER BY created_at DESC LIMIT 5')
for row in cursor.fetchall():
    print(f'Video {row[0]}: User {row[1]}, Status: {row[2]}, Created: {row[3]}')
conn.close()
"
```

---

## 📁 Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── auth.py              # JWT & password hashing
│   ├── routers/
│   │   ├── auth.py          # Register/login endpoints
│   │   ├── settings.py      # User settings endpoint
│   │   ├── social_connect.py # YouTube/TikTok/Meta OAuth
│   │   └── videos.py        # Video management
│   └── worker/
│       ├── celery_app.py    # Celery configuration
│       ├── beat_schedule.py # Scheduler config
│       ├── scheduler.py     # Main scheduler task
│       ├── pipeline.py      # Video generation pipeline
│       ├── script_gen.py    # OpenAI script generation
│       ├── voice_gen.py     # ElevenLabs voice-over
│       ├── stock_footage.py # Pexels video download
│       ├── video_render.py  # FFmpeg rendering
│       └── captions.py      # Caption synchronization
├── facelessapp.db           # SQLite database
└── storage/                 # Generated videos directory
```

---

## 🐛 Troubleshooting

### Issue: "Redis not available" in Celery logs
**Solution**: This is OK! The app uses in-memory/synchronous execution for development. Videos will still generate but slightly slower.

### Issue: Task not triggering at scheduled time
**Check**:
1. Is `auto_post_enabled: true` in settings?
2. Is time format correct? Use 24-hour format: `"14:30"` not `"2:30 PM"`
3. Is Beat scheduler running? Check terminal 2 for logs
4. Restart scheduler if timestamp changed

### Issue: OpenAI/ElevenLabs API errors
**Check**:
1. API keys in `backend/.env` are valid
2. APIs have remaining quota/balance
3. Add `--loglevel=debug` to see full error

### Issue: FFmpeg errors
**Solution**: Install FFmpeg from https://ffmpeg.org/download.html and add to PATH

---

## 🎯 Next Steps

1. **Configure your settings** (Step 1 above)
2. **Start Beat scheduler** (Step 2 above)
3. **Start Celery worker** (Step 3 above)
4. **Wait for scheduled time** OR manually trigger test
5. **Check YouTube channel** for new video!

---

## 🔗 Useful Commands

```bash
# Check all terminals are running:
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Kill a specific worker if needed:
Stop-Process -Name python -Force

# View real-time logs:
# Keep Step 1, 2, 3 terminals open

# Manually test generation:
curl -X POST http://localhost:8000/api/videos/generate \
  -H "Authorization: Bearer TOKEN"
```

---

## 📞 Support

If you encounter issues:
1. Check backend logs in terminal 1
2. Check Beat scheduler logs in terminal 2  
3. Check Worker logs in terminal 3
4. Run `GET /docs` at `http://localhost:8000/docs` for API reference

Happy automated video generation! 🚀
