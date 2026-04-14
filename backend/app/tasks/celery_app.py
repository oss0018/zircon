"""Celery application configuration."""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "zircon",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.file_tasks",
        "app.tasks.monitoring_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "run-scheduled-searches": {
            "task": "app.tasks.monitoring_tasks.run_scheduled_search",
            "schedule": 3600.0,  # every hour
        },
    },
)
