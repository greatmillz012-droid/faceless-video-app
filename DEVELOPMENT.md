# Developer Setup & Quick Start

## Overview

This app now runs **natively on your machine without Docker**. It uses SQLite for the database by default, so no PostgreSQL installation is required. Redis is optional for advanced features like async task queues.

**Quick Start** (5 minutes):
1. Install Python 3.11+ and Node.js 18+
2. Create backend venv and install deps
3. Copy `.env.example` to `.env`
4. Run backend on port 8000
5. Run frontend on port 3000

---

## First Time Setup

### 1. Clone and Environment Setup

```bash
git clone <your-repo-url>
cd faceless-video-app
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API keys for OpenAI, ElevenLabs, Pexels, and OAuth providers (see [OAUTH_SETUP.md](./OAUTH_SETUP.md) for details).

**Database Note:** The `.env` file now defaults to SQLite:
```
DATABASE_URL=sqlite:///./facelessapp.db
```

If you want to use PostgreSQL instead (for production or team development), update `.env`:
```
DATABASE_URL=postgresql://appuser:apppass@localhost:5432/facelessapp
```

### 2. Backend Setup (Python 3.11+)

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start Backend

```bash
cd backend
.venv\Scripts\activate  # or: source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend will:
- Create `facelessapp.db` in the current directory (SQLite)
- Auto-create all database tables on startup
- Serve at http://localhost:8000
- Swagger docs at http://localhost:8000/docs

### 4. Frontend Setup (Node.js 18+)

In a new terminal:

```bash
cd frontend
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

Frontend will serve at http://localhost:3000

### 5. Verify It Works

Open a browser and visit:
- **Frontend**: http://localhost:3000 – You should see the dashboard
- **Backend Health**: http://localhost:8000/health – Should return `{"status":"ok"}`
- **API Docs**: http://localhost:8000/docs – Interactive API documentation

---

## Daily Development Workflow

### Terminal 1: Backend API
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Output should show:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Frontend Dev Server
```bash
cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000
```

**Output should show:**
```
  ▲ Next.js 14.2.15
  - Local:        http://localhost:3000
  - Network:      http://0.0.0.0:3000
 ✓ Ready in 2.5s
```

### Terminal 3: (Optional) Background Workers

For async task processing (video generation, posting), start Celery. **Note:** This requires Redis to be running.

```bash
cd backend
source .venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info --concurrency=2
```

In another terminal:
```bash
cd backend
source .venv/bin/activate
celery -A app.worker.celery_app beat --loglevel=info
```

**Without Redis**, the app still works—video generation tasks will fail, but the API and dashboard are fully functional for testing authentication and OAuth flows.

### Stop Everything
Press `Ctrl+C` in each terminal to stop the processes.

---

## Database

### SQLite (Default)

The database file `facelessapp.db` is created in the `backend/` directory automatically on first startup. No setup needed.

To inspect the database:
```bash
# View tables
sqlite3 backend/facelessapp.db ".tables"

# Query users
sqlite3 backend/facelessapp.db "SELECT * FROM users;"
```

To reset the database, delete the file:
```bash
rm backend/facelessapp.db
```

Next startup will recreate it with fresh tables.

### PostgreSQL (Optional, for Production)

If you prefer PostgreSQL for team development or production:

1. Install PostgreSQL 15+
2. Create a database and user:
   ```bash
   createdb facelessapp
   psql -d facelessapp -c "CREATE USER appuser WITH PASSWORD 'apppass';"
   psql -d facelessapp -c "ALTER USER appuser WITH SUPERUSER;"
   ```
3. Update `backend/.env`:
   ```
   DATABASE_URL=postgresql://appuser:apppass@localhost:5432/facelessapp
   ```
4. Restart the backend

---

## API Endpoints for Testing

### Health Check
```bash
curl http://localhost:8000/health
```
Response: `{"status":"ok"}`

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}'
```
Response includes `access_token` (JWT).

### Get Videos (requires token)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/videos
```

See http://localhost:8000/docs for the full interactive API reference.

---

## Troubleshooting

### Port Already in Use

**Backend port 8000 in use:**
```bash
# Find process
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill it
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Frontend port 3000 in use:**
```bash
# Find process
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill it
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Errors

If you see `psycopg2.OperationalError`:
1. Check `.env` — it should have `sqlite:///` for local dev
2. Or ensure PostgreSQL is running if using PostgreSQL URL
3. Delete `facelessapp.db` and restart to reset SQLite

### Missing Dependencies

If you see `ModuleNotFoundError`:
```bash
cd backend
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Won't Start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev -- --hostname 0.0.0.0 --port 3000
```

---

## Testing OAuth Locally

1. Open http://localhost:3000
2. Register a new account
3. Click "Connect YouTube" (or TikTok/Instagram)
4. You'll be redirected to the provider's OAuth consent screen
5. Grant permissions
6. You'll be redirected back to the app—account is now connected
7. See your connected accounts at http://localhost:3000/dashboard

**Note:** OAuth requires valid Client ID/Secret in `.env`. See [OAUTH_SETUP.md](./OAUTH_SETUP.md) for how to get these.

---

## Environment Variables Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | (required) | JWT signing key |
| `DATABASE_URL` | `sqlite:///./facelessapp.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for task queue (optional) |
| `STORAGE_PATH` | `../storage/videos` | Where videos are saved |
| `BASE_URL` | `http://localhost:8000` | API base URL for OAuth redirects |
| `OPENAI_API_KEY` | (optional) | For script generation |
| `ELEVENLABS_API_KEY` | (optional) | For voiceover synthesis |
| `PEXELS_API_KEY` | (optional) | For stock footage |
| `YOUTUBE_CLIENT_ID` | (optional) | YouTube OAuth |
| `TIKTOK_CLIENT_KEY` | (optional) | TikTok OAuth |
| `META_APP_ID` | (optional) | Meta (Facebook/Instagram) OAuth |

See `backend/.env.example` for a complete template.

---

## Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Settings from environment
│   ├── auth.py              # JWT token creation/verification
│   ├── models.py            # Database models (User, SocialAccount, Video)
│   ├── database.py          # Database connection setup
│   ├── routers/
│   │   ├── auth.py          # Login/register endpoints
│   │   ├── social_connect.py # OAuth flow endpoints
│   │   ├── settings.py      # User settings endpoints
│   │   └── videos.py        # Video list/status endpoints
│   └── worker/
│       ├── __init__.py      # Celery app configuration
│       ├── pipeline.py      # Main task orchestration
│       └── tasks/
│           ├── script.py    # Generate video script
│           ├── voiceover.py # Generate audio
│           ├── captions.py  # Generate captions
│           ├── render.py    # Render final video
│           └── post.py      # Post to social platforms
├── .env.example             # Template for environment variables
└── requirements.txt         # Python dependencies
```

---

## Frontend Structure

```
frontend/
├── app/
│   ├── page.tsx             # Main dashboard
│   ├── layout.tsx           # App layout
│   └── globals.css          # Global styles
├── next.config.js           # Next.js configuration
└── package.json             # Node dependencies
```

---

## Common Commands

### Database Management

```bash
# Access PostgreSQL CLI
psql postgresql://appuser:apppass@localhost:5432/facelessapp

# View all users
SELECT * FROM users;

# View connected social accounts
SELECT * FROM social_accounts;

# View generated videos
SELECT * FROM videos;
```

### Celery Task Queue

```bash
# View active tasks
# Use the worker terminal output or run:
celery -A app.worker.celery_app inspect active

# View scheduled tasks
celery -A app.worker.celery_app inspect scheduled

# Clear Redis cache
redis-cli -u redis://localhost:6379/0 FLUSHALL
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}'

# List connected accounts
curl http://localhost:8000/api/social/accounts \
  -H "Authorization: Bearer <your_jwt_token>"
```

---

## Troubleshooting

### Port Already in Use

If you get "port already in use", kill the existing process:

```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Database Connection Failed

```bash
# Restart the database service
sudo systemctl restart postgresql
# On macOS with Homebrew
brew services restart postgresql
```

### Frontend/Backend Not Communicating

Check that the frontend's `API_URL` env var matches your backend URL.

In `frontend/app/page.tsx`:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

For production, set:
```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | JWT signing key | `your-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@db:5432/dbname` |
| `REDIS_URL` | Redis cache connection | `redis://redis:6379/0` |
| `BASE_URL` | Backend URL for redirects | `http://localhost:8000` |
| `OPENAI_API_KEY` | Script generation | From OpenAI dashboard |
| `ELEVENLABS_API_KEY` | Voiceover generation | From ElevenLabs dashboard |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth | See OAUTH_SETUP.md |
| `TIKTOK_CLIENT_KEY` | TikTok OAuth | See OAUTH_SETUP.md |
| `META_APP_ID` | Meta OAuth | See OAUTH_SETUP.md |

---

## Next Steps

1. ✅ Set up OAuth credentials for YouTube, TikTok, and Meta (see [OAUTH_SETUP.md](./OAUTH_SETUP.md))
2. ✅ Update `.env` with real keys
3. ✅ Test the OAuth flow in the dashboard
4. Create video generation jobs via the dashboard
5. Deploy to production (see [DEPLOYMENT.md](./DEPLOYMENT.md) - coming soon)

