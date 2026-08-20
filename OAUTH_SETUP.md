# OAuth Account Connection Setup Guide

This guide walks you through connecting real social media accounts to the Faceless Video App for live publishing.

---

## Overview

The app uses OAuth 2.0 to securely connect user accounts for:
- **YouTube** – Upload Shorts to a channel
- **TikTok** – Publish videos to account
- **Meta (Facebook/Instagram)** – Post to business pages

Each platform requires you to create a developer app, get credentials, and configure redirect URIs.

---

## YouTube Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a Project** → **New Project**
3. Name: `faceless-video-app`
4. Click **Create**

### Step 2: Enable YouTube Data API v3

1. In the left sidebar, click **APIs & Services** → **Library**
2. Search for `YouTube Data API v3`
3. Click it, then click **Enable**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. If prompted, click **Configure Consent Screen** first:
   - User Type: **External**
   - Fill in App name: `Faceless Video App`
   - User support email: your email
   - Developer contact: your email
   - Scopes to add: `YouTube Data API v3` → scope `youtube.upload`
   - Save and continue
4. Back to Credentials:
   - Application type: **Web application**
   - Name: `Faceless Video App`
   - Authorized JavaScript origins: `http://localhost:8000`
   - Authorized redirect URIs: `http://localhost:8000/api/social/youtube/callback`
   - Click **Create**

### Step 4: Copy Your Credentials

1. A popup shows your Client ID and Client Secret
2. Copy both values
3. In your `.env` file, update:
   ```
   YOUTUBE_CLIENT_ID=<your_client_id>
   YOUTUBE_CLIENT_SECRET=<your_client_secret>
   ```

---

## TikTok Setup

### Step 1: Create a TikTok Developer Account

1. Go to [TikTok Developer Portal](https://developer.tiktok.com/)
2. Sign in or create a TikTok account
3. Go to **Apps** → **Create an app**
4. App name: `faceless-video-app`
5. App category: **Video Platform** or **Content Platform**

### Step 2: Configure OAuth Scopes

1. In your app settings, go to **Server-to-Server** or **Client Credentials**
2. Add these scopes:
   - `user.info.basic`
   - `video.publish`
3. Save

### Step 3: Set Redirect URI

1. Go to **Redirect URLs** in app settings
2. Add: `http://localhost:8000/api/social/tiktok/callback`
3. Save

### Step 4: Get Your Credentials

1. In app settings, find **Client Key** and **Client Secret**
2. Copy both
3. In your `.env` file, update:
   ```
   TIKTOK_CLIENT_KEY=<your_client_key>
   TIKTOK_CLIENT_SECRET=<your_client_secret>
   ```

---

## Meta (Facebook/Instagram) Setup

### Step 1: Create a Facebook App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. App type: **Business**
4. App name: `faceless-video-app`
5. App contact email: your email
6. Fill in details and create

### Step 2: Add Products

1. In your app dashboard, go to **Add Product**
2. Add:
   - **Facebook Login**
   - **Instagram Graph API**
3. For each, configure settings

### Step 3: Configure OAuth Scopes and Redirect URI

1. Go to **Facebook Login** → **Settings**
2. Valid OAuth Redirect URIs: `http://localhost:8000/api/social/meta/callback`
3. Allowed Domains: `localhost:8000`
4. Save

### Step 4: Request Required Permissions

1. Go to **Apps & Roles** section
2. Request these permissions from Meta (they may require review):
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
   - `business_management`
   - `pages_show_list`

### Step 5: Get Your Credentials

1. Go to **Settings** → **Basic**
2. Copy:
   - **App ID**
   - **App Secret**
3. In your `.env` file, update:
   ```
   META_APP_ID=<your_app_id>
   META_APP_SECRET=<your_app_secret>
   ```

---

## Environment File Update

After collecting all credentials, update your `backend/.env`:

```bash
# YouTube
YOUTUBE_CLIENT_ID=<your_client_id>
YOUTUBE_CLIENT_SECRET=<your_client_secret>
YOUTUBE_REDIRECT_URI=http://localhost:8000/api/social/youtube/callback

# TikTok
TIKTOK_CLIENT_KEY=<your_client_key>
TIKTOK_CLIENT_SECRET=<your_client_secret>
TIKTOK_REDIRECT_URI=http://localhost:8000/api/social/tiktok/callback

# Meta
META_APP_ID=<your_app_id>
META_APP_SECRET=<your_app_secret>
META_REDIRECT_URI=http://localhost:8000/api/social/meta/callback
```

Then restart the backend and frontend processes:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

cd frontend
npm run dev -- --hostname 0.0.0.0 --port 3000
```

---

## Testing OAuth Flow

1. Open http://localhost:3000 in your browser
2. Register/login with an account
3. Click **Connect** on any platform
4. You should be redirected to the provider's OAuth consent screen
5. Grant permission
6. You'll be redirected back and your account will appear as connected

---

## Production Deployment

When deploying to production:

1. Update `BASE_URL` in `.env` to your actual domain
2. Update all redirect URIs in both `.env` and provider dashboards:
   - `https://yourdomain.com/api/social/youtube/callback`
   - `https://yourdomain.com/api/social/tiktok/callback`
   - `https://yourdomain.com/api/social/meta/callback`
3. Use environment variables in your hosting platform (DO NOT commit secrets to Git)
4. Store secrets in a secret manager (AWS Secrets Manager, HashiCorp Vault, etc.)

---

## Troubleshooting

### "Invalid redirect URI" Error
- Ensure the redirect URI in each platform's dashboard **exactly** matches your `.env` setting
- Check for trailing slashes or typos
- In production, use HTTPS

### "Missing scopes" Error
- Some platforms require app review before scopes are available
- Request the scopes, wait for approval, then test again

### Token Expiration
- YouTube access tokens expire in ~1 hour; refresh tokens are handled automatically
- TikTok and Meta tokens may have different expiration windows
- The app stores refresh tokens for automatic renewal

---

## Security Best Practices

✅ **DO:**
- Store secrets in environment variables, never commit to Git
- Use `.gitignore` to exclude `.env` files
- Rotate credentials periodically
- Use HTTPS in production
- Validate all OAuth state parameters

❌ **DON'T:**
- Commit `.env` with real credentials to version control
- Share client secrets via email or chat
- Use development credentials in production
- Trust OAuth tokens indefinitely; refresh when needed

