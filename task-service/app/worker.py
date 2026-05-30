from celery import Celery
from app.config import get_settings

env_settings = get_settings()

celery_app = Celery(
    "worker",
    broker=env_settings.CELERY_BROKER_URL,
    backend=env_settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.notification_tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_persistent=True,
    broker_connection_retry_on_startup=True
)

celery_app.autodiscover_tasks(["app.tasks"])