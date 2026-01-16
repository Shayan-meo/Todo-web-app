"""AI Chatbot endpoints for Todo app."""

import json
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import deps
from app.crud import chat as chat_crud
from app.crud import task as task_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import ChatMessageCreate, ChatMessageRead
from app.services.ai_service import AIService, get_ai_service

router = APIRouter(tags=["ai"])


@router.post("/chat")
async def chat(
    message_in: ChatMessageCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
):
    """Send a message to the AI chatbot (Standard JSON Response)."""
    # Get user's current tasks for context
    user_tasks = task_crud.get_tasks_for_user(db, current_user.id)

    # Get chat history for context
    chat_history = chat_crud.get_chat_history(db, current_user.id, limit=10)

    # Save user message
    chat_crud.save_chat_message(db, current_user.id, "user", message_in.message)

    # Variables to collect stream data internally
    full_content = ""
    action_name = None
    action_data = None

    # Prepare history format
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in chat_history]

    # Process AI stream internally to avoid blank bubbles on frontend
    async for event_str in ai_service.stream_chat(
        user_message=message_in.message,
        user_tasks=user_tasks,
        chat_history=history_dicts,
    ):
        try:
            event = json.loads(event_str)

            if event["type"] == "token":
                full_content += event["content"]

            elif event["type"] == "tool_call":
                action_name = event["name"]
                
                # Debug log for priority extraction
                if action_name == "add_task":
                    print(f"[DEBUG] add_task arguments: {event['arguments']}")
                    print(f"[DEBUG] Priority in args: {event['arguments'].get('priority', 'NOT FOUND')}")

                action_result = await _execute_tool_action(
                    event["name"],
                    event["arguments"],
                    current_user.id,
                    db,
                )
                action_data = action_result

                # For list_tasks, send the formatted tasks as content
                if event["name"] == "list_tasks" and action_result.get("formatted_tasks"):
                    full_content += "\n" + action_result["formatted_tasks"]

            elif event["type"] == "error":
                print(f"[AI ERROR] {event.get('content')}")

        except Exception as e:
            print(f"[STREAM ERROR] {str(e)}")

    # Save assistant message to DB after processing finishes
    final_msg = full_content.strip()
    if not final_msg and action_name:
        final_msg = ai_service._get_default_action_message(action_name)

    if final_msg:
        chat_crud.save_chat_message(db, current_user.id, "assistant", final_msg)

    # Return standard JSON instead of StreamingResponse
    return {"role": "assistant", "content": final_msg, "action_taken": action_name}


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
                    priority=arguments.get("priority", "Normal"),
                    reminder_time=arguments.get("reminder_time"),
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
                    "priority": getattr(task, "priority", "Normal"),
                    "reminder_time": getattr(task, "reminder_time", None),
                },
            }

        elif action == "list_tasks":
            tasks = task_crud.get_tasks_for_user(db, user_id)

            # Format tasks as readable list
            if not tasks:
                formatted_tasks = "Aapki list abhi khali hai. Koi naya kaam add karna hai?"
            else:
                task_lines = []
                for i, task in enumerate(tasks, 1):
                    status_symbol = "[Done]" if task.is_completed else "[Pending]"
                    priority_text = ""
                    if hasattr(task, 'priority'):
                        if task.priority == "High":
                            priority_text = "[Urgent]"
                        elif task.priority == "Medium":
                            priority_text = "[Medium]"
                        elif task.priority == "Low":
                            priority_text = "[Low]"
                        elif task.priority == "Normal":
                            priority_text = "[Normal]"

                    line = f"{i}. ID {task.id}: {task.title} {priority_text} {status_symbol}"
                    if task.description:
                        line += f"\n   Description: {task.description}"
                    
                    if hasattr(task, 'reminder_time') and task.reminder_time and not task.is_completed:
                        from datetime import datetime
                        reminder_str = task.reminder_time.strftime("%b %d, %I:%M %p") if isinstance(task.reminder_time, datetime) else str(task.reminder_time)
                        line += f"\n   Reminder: {reminder_str}"
                    task_lines.append(line)

                formatted_tasks = "\n".join(task_lines)

            return {
                "success": True,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "is_completed": t.is_completed,
                        "priority": getattr(t, "priority", "Normal"),
                        "reminder_time": getattr(t, "reminder_time", None),
                    }
                    for t in tasks
                ],
                "formatted_tasks": formatted_tasks,
                "count": len(tasks)
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
                    "priority": getattr(updated_task, "priority", "Normal"),
                    "reminder_time": getattr(updated_task, "reminder_time", None),
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
        print(f"[TOOL ERROR] {str(e)}")
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