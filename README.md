# Faceless Video App

A **full-stack AI-powered short-form video automation platform** that generates scripts, voiceovers, captions, and renders videos—then publishes them directly to YouTube, TikTok, and Instagram.

---

## 📋 Quick Links

- 🚀 **[Getting Started](./DEVELOPMENT.md)** – Local development setup and daily workflow
- 🔐 **[OAuth Setup](./OAUTH_SETUP.md)** – Connect YouTube, TikTok, and Meta accounts
- 🌐 **[Deployment](./DEPLOYMENT.md)** – Production deployment guide

---

## ✨ Features

- ✅ **AI Video Generation** – Auto-generate scripts via OpenAI
- ✅ **Voiceover Synthesis** – Text-to-speech via ElevenLabs
- ✅ **Caption Generation** – Auto-generated captions
- ✅ **Video Rendering** – Produce final short-form videos
- ✅ **Multi-Platform Publishing** – YouTube Shorts, TikTok, Instagram
- ✅ **User Accounts** – JWT authentication with PostgreSQL
- ✅ **OAuth Integration** – Secure account connection to platforms
- ✅ **Async Task Queue** – Celery + Redis for background processing
- ✅ **Dashboard UI** – Next.js frontend for account management

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend API** | FastAPI (Python) | REST API, OAuth flows, task orchestration |
| **Frontend** | Next.js 14 + React + Tailwind | Dashboard, account connect buttons |
| **Database** | PostgreSQL 15 | User accounts, social connections, video metadata |
| **Cache/Queue** | Redis 7 | Celery task queue, caching |
| **Workers** | Celery | Async task execution (script, voiceover, captions, render, post) |
| **Scheduler** | Celery Beat | Scheduled tasks |
| **Deployment** | Native local services + cloud hosting | Local dev and production |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

**That's it!** No Docker, PostgreSQL, Redis, or FFmpeg required for basic local development.

### Setup (5 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd faceless-video-app

# Copy environment template
cp backend/.env.example backend/.env

# Backend setup
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In a new terminal:

```bash
# Frontend setup
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Open your browser:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

👉 See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed setup and troubleshooting.

---

## 🔐 Setting Up Social Account Connections

The app uses OAuth 2.0 to securely connect user accounts for publishing. You'll need to:

1. **Create developer apps** on YouTube, TikTok, and Meta
2. **Get OAuth credentials** (Client ID, Client Secret, etc.)
3. **Add credentials to `.env`**
4. **Test the connect flow** in the dashboard

👉 **See [OAUTH_SETUP.md](./OAUTH_SETUP.md) for step-by-step instructions**

---

## 📁 Project Structure

```
faceless-video-app/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # App initialization & routes
│   │   ├── auth.py            # JWT token handling
│   │   ├── models.py          # Database models
│   │   ├── config.py          # Settings from env vars
│   │   ├── routers/
│   │   │   ├── auth.py        # Login/register endpoints
│   │   │   ├── social_connect.py # OAuth flow endpoints
│   │   │   ├── settings.py    # User settings
│   │   │   └── videos.py      # Video list/status
│   │   └── worker/
│   │       ├── pipeline.py    # Main task orchestration
│   │       └── tasks/         # Individual worker tasks
│   ├── .env.example           # Template (copy to .env)
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── page.tsx           # Main dashboard
│   │   ├── layout.tsx         # App layout
│   │   └── globals.css
│   ├── next.config.js
│   └── package.json
│
├── docker-compose.yml         # Full stack definition
├── .gitignore                 # Excludes .env and secrets
├── DEVELOPMENT.md             # Developer guide
├── DEPLOYMENT.md              # Production deployment
└── OAUTH_SETUP.md             # OAuth credential setup

```

---

## 🔄 Data Flow

```
User Dashboard
    ↓
[Click "Generate Video"]
    ↓
FastAPI POST /api/videos/generate
    ↓
Celery Task Queue (Redis)
    ↓
Workers Execute:
  1. Generate Script (OpenAI)
  2. Generate Voiceover (ElevenLabs)
  3. Generate Captions
  4. Render Video
  5. Post to Platforms (YouTube/TikTok/Meta)
    ↓
Video Published + Status Updated in DB
    ↓
Dashboard Shows Completed Video
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` – Create account
- `POST /api/auth/login` – Login & get JWT token

### Social Accounts
- `GET /api/social/youtube/connect` – Start YouTube OAuth
- `GET /api/social/tiktok/connect` – Start TikTok OAuth
- `GET /api/social/meta/connect` – Start Meta OAuth
- `GET /api/social/accounts` – List user's connected accounts

### Videos
- `GET /api/videos` – List user's generated videos
- `POST /api/videos/generate` – Start video generation
- `GET /api/videos/{id}` – Get video details

### Health
- `GET /health` – API health check

Full API docs available at: http://localhost:8000/docs

---

## 🛠️ Common Development Commands

```bash
# Start the backend API
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start Celery worker
cd backend
celery -A app.worker.celery_app worker --loglevel=info --concurrency=2

# Start Celery beat scheduler
cd backend
celery -A app.worker.celery_app beat --loglevel=info

# Start the frontend
cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000

# Database access
psql postgresql://appuser:apppass@localhost:5432/facelessapp

# Clear Redis cache
redis-cli -u redis://localhost:6379/0 FLUSHALL
```

See [DEVELOPMENT.md](./DEVELOPMENT.md) for more commands and troubleshooting.

---

## 🔒 Security

- ✅ **Secrets Management** – All API keys in `.env` (excluded from Git)
- ✅ **JWT Authentication** – Secure token-based API access
- ✅ **OAuth 2.0** – Secure platform connections (no passwords stored)
- ✅ **Environment Isolation** – Production credentials separate from dev
- ✅ **HTTPS Ready** – Deployment guides cover SSL/TLS setup

**DO NOT:**
- Commit `.env` with real credentials to Git
- Share API keys via email/chat
- Use development keys in production

---

## 🚀 Deployment

Ready to go live? See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- Docker deployment to Linux servers
- Heroku one-click deployment
- AWS ECS/Fargate setup
- Database backups and disaster recovery
- Monitoring and alerting
- Zero-downtime updates

---

## 🐛 Troubleshooting

### Stack won't start
```bash
# Stop the API and workers manually in each terminal with Ctrl+C
# Then restart them in order:
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

cd backend
celery -A app.worker.celery_app worker --loglevel=info --concurrency=2

cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000
```

### Port conflicts
```bash
# Find process using port 8000
lsof -i :8000

# Kill it or change the port in the run command
```

### OAuth redirect not working
- Check `.env` values match provider dashboard settings
- Verify `BASE_URL` is correct
- Ensure redirect URI has no typos
- Check browser console for error details

See [DEVELOPMENT.md](./DEVELOPMENT.md#troubleshooting) for more solutions.

---

## 📊 Architecture

### Sync API (FastAPI)
- Handles HTTP requests
- Validates JWT tokens
- Manages OAuth flows
- Stores data in PostgreSQL

### Async Workers (Celery)
- Script generation
- Voiceover synthesis
- Caption generation
- Video rendering
- Platform publishing

### Message Broker (Redis)
- Task queue
- Result storage
- Caching layer

### Database (PostgreSQL)
```sql
users              -- App users
social_account     -- Connected platform accounts
video              -- Generated videos & metadata
settings           -- User settings
```

---

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/my-feature`)
2. Make your changes
3. Test locally using the native backend/frontend commands in [DEVELOPMENT.md](./DEVELOPMENT.md)
4. Commit and push
5. Create a pull request

---

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing secret | Use `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/dbname` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `BASE_URL` | App base URL | `http://localhost:8000` or `https://example.com` |
| `OPENAI_API_KEY` | OpenAI API key | Get from [platform.openai.com](https://platform.openai.com) |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | See [OAUTH_SETUP.md](./OAUTH_SETUP.md) |
| `TIKTOK_CLIENT_KEY` | TikTok OAuth client key | See [OAUTH_SETUP.md](./OAUTH_SETUP.md) |
| `META_APP_ID` | Meta app ID | See [OAUTH_SETUP.md](./OAUTH_SETUP.md) |

Copy [backend/.env.example](./backend/.env.example) to `backend/.env` and fill in actual values.

---

## 📖 Documentation

- **[DEVELOPMENT.md](./DEVELOPMENT.md)** – Setup, daily workflow, debugging
- **[OAUTH_SETUP.md](./OAUTH_SETUP.md)** – Connect YouTube, TikTok, Meta
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** – Production deployment & monitoring

---

## 📄 License

MIT License – See LICENSE file for details

---

## 🎯 Roadmap

- [ ] Real-time video processing status updates (WebSocket)
- [ ] Batch video generation
- [ ] Custom branding/watermarks
- [ ] Analytics dashboard
- [ ] Team collaboration
- [ ] Video template library
- [ ] Automatic posting schedules

---

## 💬 Support

For issues or questions:
1. Check [DEVELOPMENT.md](./DEVELOPMENT.md#troubleshooting)
2. Review [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting-production-issues)
3. Create an issue in the repository

---

## ✅ Status

| Component | Status |
|-----------|--------|
| Backend API | ✅ Running |
| Frontend Dashboard | ✅ Running |
| Database | ✅ PostgreSQL 15 |
| Cache/Queue | ✅ Redis 7 |
| Docker Compose | ✅ Configured |
| OAuth Flow | ✅ Implemented |
| Video Pipeline | ✅ Ready |

**All systems operational. Ready for OAuth credential setup and deployment.**

---

**Last Updated:** 2026-08-16

