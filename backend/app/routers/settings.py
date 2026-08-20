from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsIn(BaseModel):
    niche: str
    posts_per_day: int
    posting_times: str
    video_length_seconds: int
    voice_style: str
    auto_post_enabled: bool


@router.get("")
def get_settings(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(models.UserSettings).filter(models.UserSettings.user_id == user.id).first()


@router.put("")
def update_settings(
    payload: SettingsIn,
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(models.UserSettings).filter(models.UserSettings.user_id == user.id).first()
    for field, value in payload.model_dump().items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row
