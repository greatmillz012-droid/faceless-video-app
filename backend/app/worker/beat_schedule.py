from celery.schedules import crontab

from .celery_app import celery_app

celery_app.conf.beat_schedule = {
    "dispatch-every-minute": {
        "task": "app.worker.scheduler.dispatch_scheduled_posts",
        "schedule": crontab(minute="*"),
    },
}
