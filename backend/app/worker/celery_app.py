from celery import Celery
import os

from ..config import settings

# For development without Redis: use in-memory broker
# In production, uses real Redis
REDIS_URL = settings.REDIS_URL
IS_DEV = os.getenv("ENVIRONMENT") == "development"
REDIS_CONNECTION_URL = REDIS_URL

# Use memory broker for development (executes tasks immediately/synchronously)
if IS_DEV or not REDIS_URL or REDIS_URL.startswith("redis://localhost"):
    try:
        import redis
        # Try to connect to Redis - if it fails, use synchronous mode
        r = redis.from_url(REDIS_CONNECTION_URL, socket_connect_timeout=1)
        r.ping()
        broker_url = REDIS_CONNECTION_URL
        backend_url = REDIS_CONNECTION_URL
    except:
        # Redis not available - use synchronous/immediate execution for development
        print("[CELERY] Redis not available - using synchronous task execution (development mode)")
        broker_url = "memory://"
        backend_url = "cache+memory://"
else:
    broker_url = REDIS_URL
    backend_url = REDIS_URL

celery_app = Celery("faceless_app", broker=broker_url, backend=backend_url)
celery_app.conf.update(
    include=["app.worker.scheduler", "app.worker.pipeline"],
    task_track_started=True,
    timezone="UTC",
    task_always_eager=broker_url.startswith("memory://"),
    task_eager_propagates=True,
    broker_connection_retry_on_startup=False,
)

from . import beat_schedule, pipeline, scheduler  # noqa: E402,F401
