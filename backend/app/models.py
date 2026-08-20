import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    settings = relationship("UserSettings", back_populates="user", uselist=False)
    social_accounts = relationship("SocialAccount", back_populates="user")
    videos = relationship("Video", back_populates="user")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    niche = Column(String, default="motivational quotes")
    posts_per_day = Column(Integer, default=3)
    posting_times = Column(String, default="09:00,14:00,20:00")
    video_length_seconds = Column(Integer, default=30)
    voice_style = Column(String, default="energetic")
    auto_post_enabled = Column(Boolean, default=False)

    user = relationship("User", back_populates="settings")


class SocialPlatform(str, enum.Enum):
    youtube = "youtube"
    tiktok = "tiktok"
    instagram = "instagram"
    facebook = "facebook"


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(Enum(SocialPlatform), nullable=False)
    account_name = Column(String)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, default={})
    connected_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="social_accounts")


class VideoStatus(str, enum.Enum):
    queued = "queued"
    generating = "generating"
    ready = "ready"
    posting = "posting"
    posted = "posted"
    failed = "failed"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    script_text = Column(Text)
    file_path = Column(String, nullable=True)
    status = Column(Enum(VideoStatus), default=VideoStatus.queued)
    scheduled_for = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    post_results = Column(JSON, default={})

    user = relationship("User", back_populates="videos")
