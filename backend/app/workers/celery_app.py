"""Celery App Configuration"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "srp_marketing_os",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.social_worker",
        "app.workers.email_worker",
        "app.workers.ai_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Beat schedule for periodic tasks
    beat_schedule={
        "publish-scheduled-posts": {
            "task": "app.workers.social_worker.check_and_publish_posts",
            "schedule": 60.0,  # every 60 seconds
        },
        "process-email-sequences": {
            "task": "app.workers.email_worker.process_email_sequences",
            "schedule": 3600.0,  # every hour
        },
    },
)
