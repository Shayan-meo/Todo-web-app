"""AI Service for Todo Chatbot using Groq API."""

import json
from datetime import datetime
from typing import Any, AsyncGenerator

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
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # FIXED: Language mirroring, Spelling (Ji), and Extraction logic improved
        return f"""You are a professional and culturally intelligent Task Manager Assistant for a Hackathon environment.

Current Time: {current_time}

STRICT LANGUAGE MIRRORING RULES:
1. If the user speaks English -> Respond ONLY in English.
2. If the user speaks Roman Urdu -> Respond ONLY in Roman Urdu.
3. NEVER mix languages in a single response. Use the user's exact language choice.
4. Use "Ji" instead of "Zi" (e.g., "Ji zaroor", "Ji bilkul", "Ji shukriya").

TASK MANAGEMENT CAPABILITIES:
- Add tasks: Extract Title, Description, Priority (High/Medium/Normal/Low), and Time.
- List tasks: Show pending or completed tasks as requested.
- Update/Delete: Use Task ID from the context below.

USER TASK LIST CATEGORIES:
- If user asks for "complete", "done", or "mukammal" tasks -> ONLY list tasks marked with ✓.
- If user asks for "pending", "remaining", or "baaki" tasks -> ONLY list tasks marked with ○.
- "Show all tasks" or "saare tasks" -> List everything.

Current User Tasks Context:
{tasks_summary}

TOOL CALLING GUIDELINES:
- For 'add_task': ALWAYS extract 'priority', 'description', and 'reminder_time' if mentioned.
- Priority extraction: "Urgent/Zaroori/Bohat ahem" -> High, "Aaram se/Kam zaroori" -> Low, "Normal/Medium" -> Medium.
- Example JSON:
  {{
    "name": "add_task",
    "arguments": {{
      "title": "Project report",
      "priority": "High",
      "description": "Submit to manager",
      "reminder_time": "2026-01-20T10:00:00"
    }}
  }}
"""

    def _format_tasks_for_context(self, tasks: list[Task]) -> str:
        """Format user's tasks as context for the AI."""
        if not tasks:
            return "No tasks yet."

        formatted = []
        for task in tasks:
            # FIXED: Ensuring status and priority are accurately reflected
            status = "✓ (Completed)" if task.is_completed else "○ (Pending)"
            priority = getattr(task, "priority", "Normal")

            formatted.append(f"ID {task.id}: {status} [Priority: {priority}] {task.title}")

            details = []
            if task.description:
                details.append(f"Desc: {task.description}")

            reminder = getattr(task, "reminder_time", None)
            if reminder:
                details.append(f"Reminder: {reminder}")

            if details:
                formatted.append(f"   {' | '.join(details)}")

        return "\n".join(formatted)

    def _get_tools(self) -> list[dict[str, Any]]:
        """Define available tools for the AI."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task with details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the task",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Normal", "Low"],
                                "description": "Priority level",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "ISO 8601 timestamp",
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
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task",
                            },
                            "is_completed": {
                                "type": "boolean",
                                "description": "Mark as completed",
                            },
                            "title": {
                                "type": "string",
                                "description": "New title",
                            },
                            "description": {
                                "type": "string",
                                "description": "New description",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Normal", "Low"],
                                "description": "New priority",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "New reminder time",
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
                    "description": "Delete a task from the list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID to delete",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

    def _get_default_action_message(self, action_name: str | None) -> str:
        """Generate a default message for tool actions."""
        # FIXED: Spelling Zi -> Ji
        action_messages = {
            "add_task": "Ji zaroor, task add kar diya gaya hai!",
            "list_tasks": "Ji, yeh rahay aapke tasks...",
            "update_task": "Ji, task update ho gaya hai.",
            "delete_task": "Ji, task delete kar diya gaya hai.",
        }
        return action_messages.get(action_name, "Ji, kaam mukammal ho gaya!")

    async def stream_chat(
        self,
        user_message: str,
        user_tasks: list[Task],
        chat_history: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat tokens and tool calls."""
        messages = []
        messages.append({"role": "system", "content": self._get_system_prompt(user_tasks)})
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools(),
                temperature=0.3, # Low temperature for strict language mirroring
                stream=True,
            )

            tool_calls_buffer = {}

            async for chunk in stream:
                delta = chunk.choices[0].delta

                if delta.content:
                    yield json.dumps({"type": "token", "content": delta.content}) + "\n"

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_buffer:
                            tool_calls_buffer[idx] = {"id": "", "name": "", "arguments": ""}

                        if tc.id:
                            tool_calls_buffer[idx]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_buffer[idx]["name"] = tc.function.name
                            if tc.function.arguments:
                                tool_calls_buffer[idx]["arguments"] += tc.function.arguments

            for idx, tool_data in tool_calls_buffer.items():
                if tool_data["name"]:
                    try:
                        args = json.loads(tool_data["arguments"])
                        yield json.dumps({
                            "type": "tool_call",
                            "id": tool_data["id"],
                            "name": tool_data["name"],
                            "arguments": args
                        }) + "\n"
                    except Exception:
                        yield json.dumps({"type": "error", "content": "Failed to parse tool arguments."}) + "\n"

        except Exception as e:
            print(f"[ERROR] Stream failed: {str(e)}")
            yield json.dumps({"type": "error", "content": "Failed to stream response."}) + "\n"


def get_ai_service() -> AIService:
    """Dependency injection for AI Service."""
    return AIService(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        base_url=settings.groq_base_url,
    )