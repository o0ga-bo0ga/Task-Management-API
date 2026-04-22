from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PaginatedTaskResponse
from app.schemas.notification import NotificationResponse
from app.services.task_service import create_task as create_task_service, get_tasks_for_user, get_task_by_id, update_task as update_task_service, delete_task as delete_task_service
from app.services.notification_service import get_notifications_for_user
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.task import Status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.cache import get_cache
from redis.asyncio import Redis
import json
import structlog
from app.tasks.notification_tasks import send_notification

log = structlog.get_logger()

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/")
async def create_task(task_data: TaskCreate,
                      db: AsyncSession=Depends(get_db),
                      user: User = Depends(get_current_user)) -> TaskResponse:
    
    task = await create_task_service(db, task_data, user.id)
    
    send_notification.delay(user.id, task.id, f"Task created: {task.title}")

    return task

@router.get("/")
async def get_all_tasks(db: AsyncSession=Depends(get_db),
                        user: User = Depends(get_current_user),
                        page: int = 1,
                        page_size: int = 10,
                        status: Status | None = None) -> PaginatedTaskResponse:
    
    response = await get_tasks_for_user(db, user.id, status, page, page_size)
    
    return response

@router.get("/notifications")
async def get_all_notifications(db: AsyncSession = Depends(get_db),
                                user: User = Depends(get_current_user)) -> list[NotificationResponse]:
    response = await get_notifications_for_user(db, user.id)

    return response

@router.get("/{task_id}")
async def get_task(task_id: int,
                   db: AsyncSession=Depends(get_db),
                   user: User = Depends(get_current_user),
                   cache: Redis = Depends(get_cache)) -> TaskResponse:
    
    cached_task = await cache.get(f"task:{task_id}")
    if cached_task:
        task = TaskResponse(**json.loads(cached_task))
        if(user.id != task.owner_id):
            raise HTTPException(status_code=404, detail="Task not found")
        else:
            log.info("cache_hit", task_id=task_id)
            return task

    log.info("cache_miss", task_id=task_id)
    task = await get_task_by_id(db, task_id)
    
    if(task is None or user.id != task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    else:
        log.info("cache_set", task_id=task_id)
        await cache.set(f"task:{task_id}", TaskResponse.model_validate(task).model_dump_json(), ex=300)
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}")
async def update_task(task_id: int,
                      update_data: TaskUpdate,
                      db: AsyncSession=Depends(get_db),
                      user: User = Depends(get_current_user),
                      cache: Redis = Depends(get_cache)) -> TaskResponse:
    
    old_task = await get_task_by_id(db, task_id)
    
    if(old_task is None or user.id != old_task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_task = await update_task_service(db, old_task, update_data)
    await cache.delete(f"task:{task_id}")
    
    return new_task

@router.delete("/{task_id}")
async def delete_task(task_id: int,
                      db: AsyncSession=Depends(get_db),
                      user: User = Depends(get_current_user),
                      cache: Redis = Depends(get_cache)) -> Response:
    
    task = await get_task_by_id(db, task_id)

    if(task is None or user.id != task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    await delete_task_service(db, task)
    await cache.delete(f"task:{task_id}")

    return Response(status_code=204)