from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .. import models
from ..config import settings


def _get_service(account: models.SocialAccount):
    creds = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.YOUTUBE_CLIENT_ID,
        client_secret=settings.YOUTUBE_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


def upload_short(account: models.SocialAccount, file_path: str, title: str, description: str) -> str:
    youtube = _get_service(account)
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000] + "\n\n#Shorts",
            "categoryId": "22",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
    video_id = response["id"]
    return f"https://youtube.com/shorts/{video_id}"
