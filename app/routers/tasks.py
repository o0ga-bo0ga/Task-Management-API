from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PaginatedTaskResponse
from app.services.task_service import create_task as create_task_service, get_tasks_for_user, get_task_by_id, update_task as update_task_service, delete_task as delete_task_service
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.task import Status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/")
async def create_task(task_data: TaskCreate, db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)) -> TaskResponse:
    task = await create_task_service(db, task_data, user.id)
    return task

@router.get("/")
async def get_all_tasks(db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user), page: int = 1, page_size: int = 10, status: Status | None = None) -> PaginatedTaskResponse:
    response = await get_tasks_for_user(db, user.id, status, page, page_size)
    return response

@router.get("/{task_id}")
async def get_task(task_id: int, db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)) -> TaskResponse:
    task = await get_task_by_id(db, task_id)
    if(task is None or user.id != task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}")
async def update_task(task_id: int, update_data: TaskUpdate, db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)) -> TaskResponse:
    old_task = await get_task_by_id(db, task_id)
    if(old_task is None or user.id != old_task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    new_task = await update_task_service(db, old_task, update_data)
    return new_task

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession=Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    task = await get_task_by_id(db, task_id)
    if(task is None or user.id != task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_task_service(db, task)
    return Response(status_code=204)