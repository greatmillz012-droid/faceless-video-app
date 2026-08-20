import time

import requests

from ..config import settings

GRAPH = "https://graph.facebook.com/v19.0"


def post_reel(account, file_path: str, caption: str) -> str:
    ig_user_id = account.extra_data["ig_business_account_id"]
    token = account.access_token

    import os

    filename = os.path.basename(file_path)
    video_url = f"{settings.BASE_URL}/static/videos/{filename}"

    create_resp = requests.post(
        f"{GRAPH}/{ig_user_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption[:2200],
            "access_token": token,
        },
        timeout=30,
    )
    create_resp.raise_for_status()
    container_id = create_resp.json()["id"]

    for _ in range(20):
        time.sleep(5)
        status_resp = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        code = status_resp.json().get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError(f"IG container failed: {status_resp.json()}")
    else:
        raise RuntimeError("IG container processing timed out")

    publish_resp = requests.post(
        f"{GRAPH}/{ig_user_id}/media_publish",
        data={"creation_id": container_id, "access_token": token},
        timeout=30,
    )
    publish_resp.raise_for_status()
    media_id = publish_resp.json()["id"]
    return f"https://www.instagram.com/reel/{media_id}/"
