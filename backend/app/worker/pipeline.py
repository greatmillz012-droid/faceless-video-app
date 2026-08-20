import os
import uuid
from datetime import datetime

from .. import models
from ..config import settings
from ..database import SessionLocal
from ..social import facebook, instagram, tiktok, youtube
from .captions import get_word_timestamps
from .celery_app import celery_app
from .script_gen import generate_script
from .stock_footage import fetch_background_video
from .video_render import render_video
from .voice_gen import generate_voiceover


@celery_app.task(bind=True, max_retries=2)
def generate_and_post_video(self, user_id: int):
    db = SessionLocal()
    try:
        user = db.query(models.User).get(user_id)
        if user is None:
            return {"status": "failed", "error": "user_not_found"}

        user_settings = db.query(models.UserSettings).filter_by(user_id=user_id).first()
        if user_settings is None:
            return {"status": "failed", "error": "settings_not_found"}

        video_row = models.Video(user_id=user_id, status=models.VideoStatus.generating)
        db.add(video_row)
        db.commit()
        db.refresh(video_row)

        work_dir = os.path.join(settings.STORAGE_PATH, f"job_{video_row.id}_{uuid.uuid4().hex[:8]}")
        os.makedirs(work_dir, exist_ok=True)

        script_data = generate_script(user_settings.niche, user_settings.video_length_seconds)
        video_row.script_text = script_data["script"]
        db.commit()

        audio_path = os.path.join(work_dir, "voice.mp3")
        generate_voiceover(script_data["script"], audio_path)

        bg_path = os.path.join(work_dir, "bg.mp4")
        fetch_background_video(user_settings.niche, bg_path)

        words = get_word_timestamps(audio_path)

        final_path = os.path.join(work_dir, "final.mp4")
        render_video(bg_path, audio_path, words, final_path)

        video_row.file_path = final_path
        video_row.status = models.VideoStatus.ready
        db.commit()

        video_row.status = models.VideoStatus.posting
        db.commit()

        results = {}
        accounts = db.query(models.SocialAccount).filter_by(user_id=user_id).all()
        if not accounts:
            video_row.post_results = {
                "system": {
                    "status": "failed",
                    "error": "No social account is connected for this user",
                }
            }
            video_row.status = models.VideoStatus.ready
            db.commit()
            return video_row.post_results

        caption = script_data["caption"] + " " + " ".join(script_data["hashtags"])

        for account in accounts:
            try:
                if account.platform == models.SocialPlatform.youtube:
                    url = youtube.upload_short(account, final_path, script_data["title"], caption)
                elif account.platform == models.SocialPlatform.tiktok:
                    url = tiktok.post_video(account, final_path, caption)
                elif account.platform == models.SocialPlatform.instagram:
                    url = instagram.post_reel(account, final_path, caption)
                elif account.platform == models.SocialPlatform.facebook:
                    url = facebook.post_reel(account, final_path, caption)
                else:
                    continue
                results[account.platform.value] = {"status": "success", "url": url}
            except Exception as exc:
                results[account.platform.value] = {"status": "failed", "error": str(exc)}

        video_row.post_results = results
        successful_posts = [result for result in results.values() if result.get("status") == "success"]
        video_row.status = models.VideoStatus.posted if successful_posts else models.VideoStatus.ready
        db.commit()
        return results

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()
