import os
from celery import Celery
from app.config import settings

celery = Celery(
    "dupeai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_concurrency=int(os.getenv("CELERY_CONCURRENCY", "4")),
    broker_connection_retry_on_startup=True,
)
