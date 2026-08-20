import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .. import auth, models
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/api/social", tags=["social"])


def _resolve_user_from_request(request: Request, db: Session, token: str | None = None):
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth.get_user_from_token(auth_header.replace("Bearer ", "", 1), db)
    if token:
        return auth.get_user_from_token(token, db)
    raise HTTPException(401, "Missing authentication")


def _upsert_account(
    db: Session,
    user_id: int,
    platform: models.SocialPlatform,
    access_token: str,
    refresh_token: str | None,
    account_name: str | None = None,
    extra_data: dict | None = None,
    expires_in: int | None = None,
):
    expires_at = None
    if expires_in is not None:
        expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))

    existing = (
        db.query(models.SocialAccount)
        .filter(models.SocialAccount.user_id == user_id, models.SocialAccount.platform == platform)
        .first()
    )

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.token_expires_at = expires_at
        existing.account_name = account_name or existing.account_name
        existing.extra_data = {**(existing.extra_data or {}), **(extra_data or {})}
        db.commit()
        db.refresh(existing)
        return existing

    account = models.SocialAccount(
        user_id=user_id,
        platform=platform,
        account_name=account_name,
        access_token=access_token,
        refresh_token=refresh_token,
        token_expires_at=expires_at,
        extra_data=extra_data or {},
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/youtube/connect")
def youtube_connect(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    user = _resolve_user_from_request(request, db, token)
    # Use broader scope that includes both read (to get channel info) and write (to upload videos)
    scope = " ".join([
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
    ])
    params = {
        "client_id": settings.YOUTUBE_CLIENT_ID,
        "redirect_uri": settings.YOUTUBE_REDIRECT_URI,
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",
        "prompt": "consent",
        "state": str(user.id),
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(url)


@router.get("/youtube/callback")
def youtube_callback(request: Request, db: Session = Depends(get_db)):
    query = request.query_params
    if "error" in query:
        raise HTTPException(400, f"OAuth failed: {query.get('error')}")

    state = query.get("state")
    code = query.get("code")
    if not state or not code:
        raise HTTPException(400, "Missing OAuth state or code")

    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.YOUTUBE_CLIENT_ID,
            "client_secret": settings.YOUTUBE_CLIENT_SECRET,
            "redirect_uri": settings.YOUTUBE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    token_res.raise_for_status()
    token_data = token_res.json()

    user_id = int(state)
    channel_res = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "snippet", "mine": "true"},
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        timeout=30,
    )
    channel_res.raise_for_status()
    channel = channel_res.json().get("items", [{}])[0]
    channel_name = channel.get("snippet", {}).get("title", "YouTube")

    _upsert_account(
        db,
        user_id,
        models.SocialPlatform.youtube,
        token_data["access_token"],
        token_data.get("refresh_token"),
        account_name=channel_name,
        extra_data={"channel_id": channel.get("id")},
        expires_in=token_data.get("expires_in"),
    )

    return {"status": "connected", "platform": "youtube", "account_name": channel_name}


@router.get("/tiktok/connect")
def tiktok_connect(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    user = _resolve_user_from_request(request, db, token)
    params = {
        "client_key": settings.TIKTOK_CLIENT_KEY,
        "scope": "user.info.basic,video.publish",
        "response_type": "code",
        "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        "state": str(user.id),
    }
    url = "https://www.tiktok.com/v2/auth/authorize/?" + urlencode(params)
    return RedirectResponse(url)


@router.get("/tiktok/callback")
def tiktok_callback(request: Request, db: Session = Depends(get_db)):
    query = request.query_params
    if "error" in query:
        raise HTTPException(400, f"OAuth failed: {query.get('error')}")

    code = query.get("code")
    state = query.get("state")
    if not code or not state:
        raise HTTPException(400, "Missing TikTok code or state")

    token_res = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data={
            "client_key": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.TIKTOK_REDIRECT_URI,
        },
        timeout=30,
    )
    token_res.raise_for_status()
    token_data = token_res.json().get("data", {})

    _upsert_account(
        db,
        int(state),
        models.SocialPlatform.tiktok,
        token_data.get("access_token", ""),
        token_data.get("refresh_token"),
        account_name="TikTok",
        expires_in=token_data.get("expires_in"),
    )
    return {"status": "connected", "platform": "tiktok"}


@router.get("/meta/connect")
def meta_connect(request: Request, token: str | None = None, db: Session = Depends(get_db)):
    user = _resolve_user_from_request(request, db, token)
    params = {
        "client_id": settings.META_APP_ID,
        "redirect_uri": settings.META_REDIRECT_URI,
        "scope": "pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish,business_management,pages_show_list",
        "response_type": "code",
        "state": str(user.id),
    }
    url = "https://www.facebook.com/v19.0/dialog/oauth?" + urlencode(params)
    return RedirectResponse(url)


@router.get("/meta/callback")
def meta_callback(request: Request, db: Session = Depends(get_db)):
    query = request.query_params
    if "error" in query:
        raise HTTPException(400, f"OAuth failed: {query.get('error')}")

    code = query.get("code")
    state = query.get("state")
    if not code or not state:
        raise HTTPException(400, "Missing Meta code or state")

    token_res = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={
            "client_id": settings.META_APP_ID,
            "client_secret": settings.META_APP_SECRET,
            "redirect_uri": settings.META_REDIRECT_URI,
            "code": code,
        },
        timeout=30,
    )
    token_res.raise_for_status()
    token_data = token_res.json()

    accounts_res = requests.get(
        "https://graph.facebook.com/v19.0/me/accounts",
        params={"fields": "id,name,access_token", "access_token": token_data["access_token"]},
        timeout=30,
    )
    accounts_res.raise_for_status()
    account_data = accounts_res.json().get("data", [])
    page = account_data[0] if account_data else {}

    _upsert_account(
        db,
        int(state),
        models.SocialPlatform.facebook,
        page.get("access_token") or token_data["access_token"],
        None,
        account_name=page.get("name", "Facebook Page"),
        extra_data={"page_id": page.get("id")},
        expires_in=token_data.get("expires_in"),
    )

    return {"status": "connected", "platform": "facebook", "account_name": page.get("name", "Facebook Page")}


@router.get("/accounts")
def list_accounts(
    user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(models.SocialAccount).filter(models.SocialAccount.user_id == user.id).all()
