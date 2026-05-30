from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.task import Status

class TaskCreate(BaseModel):
    title: str
    description: str
    status: Optional[Status] = Status.PENDING
    callback_url: str | None = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    owner_id: int
    created_at: datetime
    status: Status
    updated_at: datetime

class TaskCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    owner_id: int
    created_at: datetime
    status: Status
    updated_at: datetime
    job_id: Optional[str] | None = None

class PaginatedTaskResponse(BaseModel):
    total: int
    items: list[TaskResponse]