import random

import requests

from ..config import settings


def fetch_background_video(query: str, output_path: str, min_duration=30) -> str:
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": settings.PEXELS_API_KEY}
    params = {"query": query, "orientation": "portrait", "per_page": 15}
    resp = requests.get(url, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    videos = resp.json().get("videos", [])
    candidates = [v for v in videos if v["duration"] >= min_duration] or videos
    if not candidates:
        raise RuntimeError(f"No Pexels video found for query: {query}")

    chosen = random.choice(candidates)
    file_url = max(chosen["video_files"], key=lambda f: f.get("height", 0))["link"]

    video_resp = requests.get(file_url, timeout=60)
    with open(output_path, "wb") as f:
        f.write(video_resp.content)
    return output_path
