import requests

from ..config import settings

GRAPH = "https://graph.facebook.com/v19.0"


def post_reel(account, file_path: str, caption: str) -> str:
    page_id = account.extra_data["page_id"]
    token = account.access_token
    import os

    filename = os.path.basename(file_path)
    video_url = f"{settings.BASE_URL}/static/videos/{filename}"

    start_resp = requests.post(
        f"{GRAPH}/{page_id}/video_reels",
        data={"upload_phase": "start", "access_token": token},
        timeout=30,
    )
    start_resp.raise_for_status()
    video_id = start_resp.json()["video_id"]

    requests.post(
        f"{GRAPH}/{video_id}",
        data={"file_url": video_url, "access_token": token},
        timeout=30,
    ).raise_for_status()

    publish_resp = requests.post(
        f"{GRAPH}/{page_id}/video_reels",
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "description": caption[:2200],
            "video_state": "PUBLISHED",
            "access_token": token,
        },
        timeout=30,
    )
    publish_resp.raise_for_status()
    return f"https://www.facebook.com/reel/{video_id}"
