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

        return f"""You are a smart Task Manager Assistant. Your role is to help users manage their tasks through natural conversation in both English and Roman Urdu.

Capabilities:
- Add new tasks
- List and show tasks
- Update task details
- Delete tasks
- Mark tasks as complete/incomplete

User's Current Tasks:
{tasks_summary}

Important Instructions:

1. **INTENT EXTRACTION & VALIDATION**:
   - If user says "Task add karo" or "Naya task likho" WITHOUT specifying what it is, DO NOT call add_task tool yet.
   - Instead, ask them in Roman Urdu: "Zaroor! Task ka title kya rakhun?" (Sure! What title should I give the task?)
   - If user provides details like "Gym jana hai sham 6 baje", map:
     * Title = "Gym jana hai" (main action)
     * Description = "sham 6 baje" (additional details)
   - Only call add_task when you have at least the title.

2. **ROMAN URDU PERSONALITY**:
   - Respond naturally and conversationally in Roman Urdu when user uses it.
   - Instead of: "Task created: Gym"
   - Say: "Ji bilkul, 'Gym jana hai' wala task add kar diya hai. Kuch aur madad karun?" (Yes of course, I've added the 'Gym jana hai' task. Can I help you with anything else?)
   - Use natural phrases:
     * "Bilkul!" (Of course!)
     * "Theek hai" (Okay)
     * "Zaroor" (Sure)
     * "Jaldi se" (Quick/fast)

3. **LANGUAGE MATCHING**:
   - If user writes in English, respond in English.
   - If user writes in Roman Urdu, respond in Roman Urdu.
   - Use code-switching naturally if it makes sense in context.

4. **TOOL CALLING STRATEGY**:
   - Call tools ONLY when you have sufficient information.
   - For add_task: require at least title; description is optional.
   - For list_tasks: call immediately when user asks to see their tasks.
   - For update_task/delete_task: confirm which task before executing.

5. **RESPONSE STYLE**:
   - Be concise and friendly
   - Avoid repeating technical details (like action_taken or JSON)
   - Use the task list context to provide smart suggestions
   - Always sound like a helpful friend, not a robot"""

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

    def _get_default_action_message(self, action_name: str | None) -> str:
        """Generate a default message for tool actions if AI didn't provide one."""
        action_messages = {
            "add_task": "Theek hai, task add kar diya gaya hai!",
            "list_tasks": "Aapke tasks dekh rahe hain...",
            "update_task": "Task update kar diya gaya hai!",
            "delete_task": "Task delete kar diya gaya hai!",
        }
        return action_messages.get(action_name, "Action complete ho gaya!")

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

            # Generate a natural language confirmation for the action
            # If AI didn't provide a message, generate one based on the action
            action_name = tool_calls_data[0]["name"] if tool_calls_data else None
            message_text = assistant_message.content or self._get_default_action_message(action_name)

            return ChatResponse(
                message=message_text,
                action_taken=action_name,
                action_result=tool_calls_data[0]["arguments"] if tool_calls_data else None,
            )

        # Return plain text response
        # Ensure we always have a message (never empty)
        message_text = (assistant_message.content or "").strip()
        if not message_text:
            # Fallback if AI returns empty content
            message_text = "Ji, main samajh nahi paya. Dobara bolye ga?"

        return ChatResponse(
            message=message_text,
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