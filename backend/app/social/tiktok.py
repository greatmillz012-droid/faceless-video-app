import os
import time

import requests


def post_video(account, file_path: str, caption: str) -> str:
    headers = {"Authorization": f"Bearer {account.access_token}"}

    init_resp = requests.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers=headers,
        json={
            "post_info": {
                "title": caption[:150],
                "privacy_level": "SELF_ONLY",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": _file_size(file_path),
                "chunk_size": _file_size(file_path),
                "total_chunk_count": 1,
            },
        },
        timeout=30,
    )
    init_resp.raise_for_status()
    data = init_resp.json()["data"]
    upload_url = data["upload_url"]
    publish_id = data["publish_id"]

    with open(file_path, "rb") as f:
        video_bytes = f.read()

    requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{len(video_bytes) - 1}/{len(video_bytes)}",
        },
        data=video_bytes,
        timeout=60,
    ).raise_for_status()

    for _ in range(10):
        time.sleep(3)
        status_resp = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/status/fetch/",
            headers=headers,
            json={"publish_id": publish_id},
            timeout=30,
        )
        status_data = status_resp.json()["data"]
        if status_data["status"] == "PUBLISH_COMPLETE":
            return f"https://www.tiktok.com/@user/video/{status_data.get('publicaly_available_post_id', ['unknown'])[0]}"
        if status_data["status"] == "FAILED":
            raise RuntimeError(f"TikTok publish failed: {status_data}")
    raise RuntimeError("TikTok publish timed out waiting for status")


def _file_size(path):
    return os.path.getsize(path)
