import os

from pydantic_settings import BaseSettings


def _get_base_url() -> str:
    """Resolve the public base URL for the app.

    Resolution order:
    1. An explicit BASE_URL environment variable (highest priority).
    2. Railway's automatically-provided RAILWAY_PUBLIC_DOMAIN, which does not
       include a scheme, so https:// is prepended.
    3. localhost fallback for local development.
    """
    if explicit_base_url := os.getenv("BASE_URL"):
        return explicit_base_url

    if railway_domain := os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        return f"https://{railway_domain}"

    return "http://localhost:8000"


class Settings(BaseSettings):
    # Falls back to a development-only default so the app can start locally
    # without a .env file. Railway (and any production deployment) should
    # always override this via an environment variable with a secure value.
    SECRET_KEY: str = "dev-secret-key-change-me"
    DATABASE_URL: str = "sqlite:///./facelessapp.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    STORAGE_PATH: str = "/app/storage/videos"
    BASE_URL: str = _get_base_url()

    # Comma-separated list of allowed CORS origins. Defaults to common local
    # development origins; production deployments should override this via
    # the CORS_ORIGINS environment variable with the frontend's domain(s).
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = ""
    PEXELS_API_KEY: str = ""

    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REDIRECT_URI: str = ""

    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    TIKTOK_REDIRECT_URI: str = ""

    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_REDIRECT_URI: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
