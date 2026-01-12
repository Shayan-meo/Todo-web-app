"""AI Service for Todo Chatbot using Groq API."""

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.task import Task
from app.schemas.chat import ChatResponse


class AIService:
    """Service for processing chat messages with Groq API."""

    def __init__(self, api_key: str, model: str, base_url: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

    def _get_system_prompt(self, user_tasks: list[Task]) -> str:
        """Generate system prompt with current task context."""
        tasks_summary = self._format_tasks_for_context(user_tasks)

        return f"""You are a helpful Todo Assistant. Your role is to help users manage their tasks through natural conversation.

Capabilities:
- Add new tasks
- List and show tasks
- Update task details
- Delete tasks
- Mark tasks as complete/incomplete

User's Current Tasks:
{tasks_summary}

Important Instructions:
1. **Language Support**: You understand and respond in both English and Roman Urdu. Respond in the same language/style as the user uses.
2. **Code-Switching**: If the user uses Roman Urdu (Hinglish), respond similarly. Examples:
   - User: "Mere kitne tasks baaki hain?" → AI: "Aap ke 3 tasks baaki hain..."
   - User: "Meeting add karo" → AI: "Theek hai, meeting add kar di gayi hai."
3. **Prefer Tool Calling**: For task-related operations, always call the appropriate tool instead of just explaining.
4. **Be Concise**: Keep responses helpful but brief.
5. **Context**: Use the provided task list to answer questions about existing tasks.
6. **Friendly Tone**: Be helpful, encouraging, and polite."""

    def _format_tasks_for_context(self, tasks: list[Task]) -> str:
        """Format user's tasks as context for the AI."""
        if not tasks:
            return "No tasks yet."

        formatted = []
        for i, task in enumerate(tasks, 1):
            status = "✓" if task.is_completed else "○"
            formatted.append(f"{i}. {status} {task.title}")
            if task.description:
                formatted.append(f"   Description: {task.description}")

        return "\n".join(formatted)

    def _get_tools(self) -> list[dict[str, Any]]:
        """Define available tools for the AI."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the task to add",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description for the task",
                            },
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all of the user's tasks",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task (mark complete, change title, etc.)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update",
                            },
                            "is_completed": {
                                "type": "boolean",
                                "description": "Mark task as completed or not completed",
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the task",
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the task",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task from the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

    async def process_message(
        self,
        user_message: str,
        user_tasks: list[Task],
        chat_history: list[dict[str, Any]] | None = None,
    ) -> ChatResponse:
        """Process user message and return AI response."""
        messages = []

        # Add system prompt
        messages.append(
            {
                "role": "system",
                "content": self._get_system_prompt(user_tasks),
            }
        )

        # Add chat history if available (limit to last 10 exchanges)
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                )

        # Add current user message
        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        # Call Groq API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._get_tools(),
            temperature=0.7,
        )

        assistant_message = response.choices[0].message

        # Check if tool calls were made
        if assistant_message.tool_calls:
            # Return the tool call information for the API layer to execute
            tool_calls_data = [
                {
                    "id": tool.id,
                    "name": tool.function.name,
                    "arguments": json.loads(tool.function.arguments),
                }
                for tool in assistant_message.tool_calls
            ]

            return ChatResponse(
                message=assistant_message.content or "",
                action_taken=tool_calls_data[0]["name"] if tool_calls_data else None,
                action_result=tool_calls_data[0]["arguments"] if tool_calls_data else None,
            )

        # Return plain text response
        return ChatResponse(
            message=assistant_message.content or "",
            action_taken=None,
            action_result=None,
        )


def get_ai_service() -> AIService:
    """Dependency injection for AI Service."""
    return AIService(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        base_url=settings.groq_base_url,
    )