from sqlalchemy.orm import Session

from app.models.chat import ChatMessage


def get_chat_history(db: Session, user_id: int, limit: int = 20) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]  # Return in chronological order
    )


def save_chat_message(
    db: Session,
    user_id: int,
    role: str,
    content: str,
    tool_calls: str | None = None,
) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id, role=role, content=content, tool_calls=tool_calls
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def clear_chat_history(db: Session, user_id: int) -> None:
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
