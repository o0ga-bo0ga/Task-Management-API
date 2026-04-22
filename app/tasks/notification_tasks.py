from app.worker import celery_app
import structlog
from app.database import SyncSessionLocal as SessionLocal
from app.models.notification import Notification
import time

logger = structlog.get_logger()

@celery_app.task(name="send_notification")
def send_notification(
        user_id: int,
        task_id: int,
        message: str):
    
    log = logger.bind(user_id=user_id,
                      task_id=task_id)
    
    with SessionLocal() as session:
        try:
            time.sleep(1)

            notification = Notification(
                user_id=user_id,
                task_id=task_id,
                message=message
            )
            session.add(notification)
            session.commit()

            log.info("notification_sent_and_saved", message=message)
            return {"user_id": user_id}
        except Exception as e:
            session.rollback()
            log.error("notification_failed", error=str(e))
            raise