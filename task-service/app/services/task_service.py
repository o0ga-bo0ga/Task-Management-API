from app.schemas.task import TaskCreate, TaskUpdate, PaginatedTaskResponse
from app.models.task import Task, Status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

async def create_task(db: AsyncSession, task_data: TaskCreate, owner_id: int) -> Task:
    new_task = Task(title=task_data.title,
                    description=task_data.description,
                    owner_id = owner_id,
                    status = task_data.status
                    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task

async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
    select_query = select(Task).where(Task.id == task_id)
    result = await db.execute(select_query)
    task = result.scalar_one_or_none()

    return task

async def get_tasks_for_user(db: AsyncSession, owner_id: int, status: Status | None, page: int, page_size: int) -> dict:
    select_query = select(Task).where(Task.owner_id == owner_id)

    if(status is not None): 
        select_query = select_query.where(Task.status == status)

    count_query = select(func.count()).select_from(select_query.subquery())
    count_result = await db.execute(count_query)
    count = count_result.scalar()

    select_query = select_query.offset((page-1)*page_size).limit(page_size)
    
    result = await db.execute(select_query)
    tasks = result.scalars().all()

    return {"total": count, "items": list(tasks)}

async def update_task(db: AsyncSession, task: Task, update_data: TaskUpdate) -> Task:
    update_data = update_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)

    return task
    

async def delete_task(db: AsyncSession, task: Task):

    await db.delete(task)
    await db.commit()    