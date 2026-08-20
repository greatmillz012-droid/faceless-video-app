from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
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
