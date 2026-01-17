from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def get_tasks_for_user(db: Session, user_id: int) -> list[Task]:
    # Custom sort order for priority
    priority_order = case(
        (Task.priority == "High", 1),
        (Task.priority == "Medium", 2),
        (Task.priority == "Normal", 3),
        (Task.priority == "Low", 4),
        else_=5
    )

    return db.query(Task).filter(Task.user_id == user_id).order_by(priority_order, Task.created_at.desc()).all()


def get_task(db: Session, task_id: int, user_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()


def create_task(db: Session, user_id: int, task_in: TaskCreate) -> Task:
    task = Task(
        user_id=user_id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        reminder_time=task_in.reminder_time
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    if task_in.title is not None:
        task.title = task_in.title
    if task_in.description is not None:
        task.description = task_in.description
    if task_in.is_completed is not None:
        task.is_completed = task_in.is_completed
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()
