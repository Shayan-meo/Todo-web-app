from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: str = "Normal"
    reminder_time: datetime | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None
    priority: str | None = None
    reminder_time: datetime | None = None


class TaskRead(TaskBase):
    id: int
    is_completed: bool
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
