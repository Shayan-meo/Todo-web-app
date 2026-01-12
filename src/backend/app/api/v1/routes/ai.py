"""AI Chatbot endpoints for Todo app."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import deps
from app.crud import chat as chat_crud
from app.crud import task as task_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatMessageRead, ChatResponse
from app.services.ai_service import AIService, get_ai_service

router = APIRouter(tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message_in: ChatMessageCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> ChatResponse:
    """Send a message to the AI chatbot."""
    # Get user's current tasks for context
    user_tasks = task_crud.get_tasks_for_user(db, current_user.id)

    # Get chat history for context
    chat_history = chat_crud.get_chat_history(db, current_user.id, limit=10)

    # Save user message
    chat_crud.save_chat_message(db, current_user.id, "user", message_in.message)

    # Process with AI
    ai_response = await ai_service.process_message(
        user_message=message_in.message,
        user_tasks=user_tasks,
        chat_history=[
            {"role": msg.role, "content": msg.content} for msg in chat_history
        ],
    )

    # Execute tool calls if any
    if ai_response.action_taken:
        action_result = await _execute_tool_action(
            ai_response.action_taken,
            ai_response.action_result,
            current_user.id,
            db,
        )
        ai_response.action_result = action_result

    # Save assistant message
    chat_crud.save_chat_message(db, current_user.id, "assistant", ai_response.message)

    return ai_response


async def _execute_tool_action(
    action: str, arguments: dict, user_id: int, db: Session
) -> dict:
    """Execute the tool action based on AI decision."""
    try:
        if action == "add_task":
            from app.schemas.task import TaskCreate

            task = task_crud.create_task(
                db,
                user_id,
                TaskCreate(
                    title=arguments.get("title", ""),
                    description=arguments.get("description"),
                ),
            )
            return {
                "success": True,
                "task_id": task.id,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                },
            }

        elif action == "list_tasks":
            tasks = task_crud.get_tasks_for_user(db, user_id)
            return {
                "success": True,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "is_completed": t.is_completed,
                    }
                    for t in tasks
                ],
            }

        elif action == "update_task":
            from app.schemas.task import TaskUpdate

            task = task_crud.get_task(db, arguments["task_id"], user_id)
            if not task:
                return {"success": False, "error": "Task not found"}

            updated_task = task_crud.update_task(
                db, task, TaskUpdate(**{k: v for k, v in arguments.items() if k != "task_id"})
            )
            return {
                "success": True,
                "task_id": updated_task.id,
                "task": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "is_completed": updated_task.is_completed,
                },
            }

        elif action == "delete_task":
            task = task_crud.get_task(db, arguments["task_id"], user_id)
            if not task:
                return {"success": False, "error": "Task not found"}

            task_crud.delete_task(db, task)
            return {"success": True, "deleted_task_id": arguments["task_id"]}

        return {"success": False, "error": f"Unknown action: {action}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/chat/history", response_model=list[ChatMessageRead])
async def get_chat_history(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessageRead]:
    """Get the chat history for the current user."""
    return chat_crud.get_chat_history(db, current_user.id, limit=50)


@router.delete("/chat/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Clear the chat history for the current user."""
    chat_crud.clear_chat_history(db, current_user.id)
