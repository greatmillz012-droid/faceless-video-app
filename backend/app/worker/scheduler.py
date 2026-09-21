from datetime import datetime

from .celery_app import celery_app
from .. import models
from ..database import SessionLocal


@celery_app.task
def dispatch_scheduled_posts():
    from .pipeline import generate_and_post_video

    db = SessionLocal()
    try:
        now = datetime.utcnow().strftime("%H:%M")
        settings_rows = db.query(models.UserSettings).filter_by(auto_post_enabled=True).all()
        for row in settings_rows:
            times = [t.strip() for t in row.posting_times.split(",") if t.strip()]
            if now in times:
                daily_limit = row.posts_per_day
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                videos_today = (
                    db.query(models.Video)
                    .filter(
                        models.Video.user_id == row.user_id,
                        models.Video.created_at >= today_start,
                    )
                    .count()
                )
                if videos_today >= daily_limit:
                    continue
                generate_and_post_video.delay(row.user_id)
    finally:
        db.close()
