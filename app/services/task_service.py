from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from sqlalchemy.orm import Session
from sqlalchemy import select

def create_task(db: Session, task_data: TaskCreate, owner_id: int) -> Task:
    new_task = Task(title=task_data.title,
                    description=task_data.description,
                    owner_id = owner_id,
                    status = task_data.status
                    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

def get_task_by_id(db: Session, task_id: int) -> Task | None:
    select_query = select(Task).where(Task.id == task_id)
    task = db.execute(select_query).scalar_one_or_none()

    return task

def get_tasks_for_user(db: Session, owner_id: int) -> list[Task]:
    select_query = select(Task).where(Task.owner_id == owner_id)
    tasks = db.execute(select_query).scalars().all()

    return tasks

def update_task(db: Session, task: Task, update_data: TaskUpdate) -> Task:
    update_data = update_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)

    return task
    

def delete_task(db: Session, task: Task):
    db.delete(task)
    db.commit()    