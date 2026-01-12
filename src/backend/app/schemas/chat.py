from datetime import datetime

from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    message: str


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    message: str
    action_taken: str | None = None
    action_result: dict | None = None
