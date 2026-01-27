from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import deps
from app.crud import task as task_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.kafka_producer import publish_task_event

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    return task_crud.get_tasks_for_user(db, current_user.id)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = task_crud.create_task(db, current_user.id, task_in)
    # Publish task creation event to Kafka
    publish_task_event(task_id=task.id, action="create", user_id=current_user.id)
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = task_crud.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    updated_task = task_crud.update_task(db, task, task_in)
    # Publish task update event to Kafka
    publish_task_event(task_id=task_id, action="update", user_id=current_user.id)
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> None:
    task = task_crud.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    # Publish task deletion event to Kafka before deleting
    publish_task_event(task_id=task_id, action="delete", user_id=current_user.id)
    task_crud.delete_task(db, task)


@router.patch("/{task_id}/complete", response_model=TaskRead)
def mark_complete(
    task_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = task_crud.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task.is_completed = True
    db.commit()
    db.refresh(task)
    # Publish task completion (update) event to Kafka
    publish_task_event(task_id=task_id, action="update", user_id=current_user.id)
    return task
