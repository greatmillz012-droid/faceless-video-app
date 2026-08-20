import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .routers import auth, settings as settings_router, social_connect, videos

app = FastAPI(title="Faceless Video Automation")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create database tables on startup: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.STORAGE_PATH, exist_ok=True)
app.mount("/static/videos", StaticFiles(directory=settings.STORAGE_PATH), name="videos")

app.include_router(auth.router)
app.include_router(settings_router.router)
app.include_router(videos.router)
app.include_router(social_connect.router)


@app.get("/health")
def health():
    return {"status": "ok"}
