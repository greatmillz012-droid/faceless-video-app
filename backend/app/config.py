from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Falls back to a development-only default so the app can start locally
    # without a .env file. Railway (and any production deployment) should
    # always override this via an environment variable with a secure value.
    SECRET_KEY: str = "dev-secret-key-change-me"
    DATABASE_URL: str = "sqlite:///./facelessapp.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    STORAGE_PATH: str = "/app/storage/videos"
    BASE_URL: str = "http://localhost:8000"

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
