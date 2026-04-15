from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PaginatedTaskResponse
from app.services.task_service import create_task as create_task_service, get_tasks_for_user, get_task_by_id, update_task as update_task_service, delete_task as delete_task_service
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.task import Status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Annotated

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/")
def create_task(task_data: TaskCreate, db: Session=Depends(get_db), user: User = Depends(get_current_user)) -> TaskResponse:
    task = create_task_service(db, task_data, user.id)
    return task

@router.get("/")
def get_all_tasks(db: Session=Depends(get_db), user: User = Depends(get_current_user), page: int = 1, page_size: int = 10, status: Status | None = None) -> PaginatedTaskResponse:
    response = get_tasks_for_user(db, user.id, status, page, page_size)
    return response

@router.get("/{task_id}")
def get_task(task_id: int, db: Session=Depends(get_db), user: User = Depends(get_current_user)) -> TaskResponse:
    task = get_task_by_id(db, task_id)
    if(task is None or user.id != task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}")
def update_task(task_id: int, update_data: TaskUpdate, db: Session=Depends(get_db), user: User = Depends(get_current_user)) -> TaskResponse:
    old_task = get_task_by_id(db, task_id)
    if(old_task is None or user.id != old_task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    new_task = update_task_service(db, old_task, update_data)
    return new_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session=Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    task = get_task_by_id(db, task_id)
    if(task is None or user.id != task.owner_id):
        raise HTTPException(status_code=404, detail="Task not found")
    delete_task_service(db, task)
    return Response(status_code=204)