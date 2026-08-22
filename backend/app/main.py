import os
import sys

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .routers import auth, settings as settings_router, social_connect, videos

app = FastAPI(title="Faceless Video Automation")

try:

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables on startup: {e}")

    def _get_cors_origins() -> list[str]:
        """Parse the CORS_ORIGINS setting into a list of origins.

        CORS_ORIGINS is expected to be a comma-separated string, e.g.
        "https://frontend-domain.com,http://localhost:3000". Whitespace around
        each origin is stripped and empty entries are dropped. Localhost origins
        are always included as a fallback so local development keeps working
        even if CORS_ORIGINS is overridden without them.
        """
        raw_origins = settings.CORS_ORIGINS or ""
        origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

        dev_fallbacks = ["http://localhost:3000", "http://127.0.0.1:3000"]
        for fallback in dev_fallbacks:
            if fallback not in origins:
                origins.append(fallback)

        return origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    app.mount("/static/videos", StaticFiles(directory=settings.STORAGE_PATH), name="videos")

    app.include_router(auth.router)
    app.include_router(settings_router.router)
    app.include_router(videos.router)
    app.include_router(social_connect.router)
except Exception as e:
    import traceback

    print(f"CRITICAL ERROR DURING APP INITIALIZATION: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise


@app.get("/health")
def health():
    return {"status": "ok"}
