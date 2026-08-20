from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db
from ..worker.pipeline import generate_and_post_video

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("")
def list_videos(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Video)
        .filter_by(user_id=user.id)
        .order_by(models.Video.created_at.desc())
        .all()
    )


@router.post("/generate-now")
def generate_now(user: models.User = Depends(auth.get_current_user)):
    task = generate_and_post_video.delay(user.id)
    return {"task_id": task.id, "status": "queued"}
