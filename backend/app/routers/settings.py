import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])

VALID_VOICE_EFFECTS = {
    "natural",
    "robotic",
    "slow_and_clear",
    "fast_and_energetic",
    "whispering",
    "cheerful",
    "deep_and_resonant",
}


class SettingsIn(BaseModel):
    niche: str
    posts_per_day: int = Field(..., ge=1, le=10)
    posting_times: str
    video_length_seconds: int
    voice_style: str
    auto_post_enabled: bool


class PreferencesIn(BaseModel):
    daily_videos: int = Field(..., ge=1, le=10)
    post_times: list[str] = Field(default_factory=list)
    voice_effect: str = "natural"

    @field_validator("voice_effect")
    @classmethod
    def validate_voice_effect(cls, value: str) -> str:
        if value not in VALID_VOICE_EFFECTS:
            raise ValueError(f"voice_effect must be one of {sorted(VALID_VOICE_EFFECTS)}")
        return value


def normalize_post_times(times: list[str] | None) -> list[str]:
    values = [time.strip() for time in (times or []) if isinstance(time, str) and time.strip()]
    normalized = values[:10] + [""] * 10
    return normalized[:10]


def normalize_legacy_posting_times(value: str | None) -> str:
    items = [time.strip() for time in (value or "").split(",") if time and time.strip()]
    padded = items[:10] + [""] * 10
    return ",".join(padded[:10])

    @field_validator("post_times")
    @classmethod
    def validate_post_times(cls, value: list[str]) -> list[str]:
        pattern = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
        for entry in value:
            if not pattern.match(entry):
                raise ValueError(f"Invalid time format: {entry}. Expected HH:MM")
        return value


@router.get("")
def get_settings(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(models.UserSettings).filter(models.UserSettings.user_id == user.id).first()
    if not row:
        return None
    row.posting_times = normalize_legacy_posting_times(row.posting_times)
    return row


@router.put("")
def update_settings(
    payload: SettingsIn,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(models.UserSettings).filter(models.UserSettings.user_id == user.id).first()
    data = payload.model_dump()
    data["posting_times"] = normalize_legacy_posting_times(data.get("posting_times"))
    for field, value in data.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


@router.get("/preferences")
def get_preferences(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        row = (
            db.query(models.UserPreferences)
            .filter(models.UserPreferences.user_id == user.id)
            .first()
        )
    except SQLAlchemyError:
        raise HTTPException(500, "Failed to load preferences")

    if not row:
        return {"daily_videos": 1, "post_times": ["", "", ""], "voice_effect": "natural"}

    return {
        "daily_videos": row.daily_videos,
        "post_times": normalize_post_times(row.post_times or []),
        "voice_effect": row.voice_effect,
    }


@router.post("/preferences")
def save_preferences(
    payload: PreferencesIn,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        row = (
            db.query(models.UserPreferences)
            .filter(models.UserPreferences.user_id == user.id)
            .first()
        )

        normalized_times = normalize_post_times(payload.post_times)

        if row:
            row.daily_videos = payload.daily_videos
            row.post_times = normalized_times
            row.voice_effect = payload.voice_effect
        else:
            row = models.UserPreferences(
                user_id=user.id,
                daily_videos=payload.daily_videos,
                post_times=normalized_times,
                voice_effect=payload.voice_effect,
            )
            db.add(row)

        db.commit()
        db.refresh(row)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Failed to save preferences")

    return {
        "daily_videos": row.daily_videos,
        "post_times": normalize_post_times(row.post_times or []),
        "voice_effect": row.voice_effect,
    }
