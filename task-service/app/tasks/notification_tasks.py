from app.worker import celery_app
import structlog
from app.database import SyncSessionLocal as SessionLocal
from app.models.notification import Notification
import time
import httpx

logger = structlog.get_logger()

@celery_app.task(name="send_notification")
def send_notification(
        user_id: int,
        task_id: int,
        message: str,
        callback_url: str | None = None):
    
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
    
            if callback_url:
                try:
                    response = httpx.post(
                        callback_url, 
                        json={"job_id": task_id,
                              "status": "SUCCESS",
                              "user_id": user_id}, 
                        timeout=10.0
                    )
                    response.raise_for_status() 
                    logger.info("webhook_sent", status_code = response.status_code)
                    
                except httpx.RequestError as exc:
                    logger.warning("webhook_connection_failed", error = str(exc))
                except httpx.HTTPStatusError as exc:
                    logger.warning("webhook_http_error", status_code = exc.response.status_code)
            

            log.info("notification_sent_and_saved", message=message)
            return {"user_id": user_id}
        except Exception as e:
            session.rollback()
            log.error("notification_failed", error=str(e))
            raise