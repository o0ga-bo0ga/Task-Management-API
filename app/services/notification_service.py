from app.schemas.notification import NotificationResponse
from app.models.notification import Notification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

async def get_notifications_for_user(db: AsyncSession,
                             user_id: int) -> list:
    select_query = select(Notification).where(Notification.user_id == user_id)
    
    result = await db.execute(select_query)
    tasks = result.scalars().all()

    return list(tasks)