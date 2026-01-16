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

        # FIXED: Curly braces escaped using {{ and }} inside the f-string
        return f"""You are a smart, professional, and culturally intelligent Task Manager Assistant for a Hackathon environment.

Current Time: {current_time}

Capabilities:
- Add new tasks with Priority (High, Medium, Normal, Low) and Reminders
- List and show tasks (Always show ID numbers)
- Update task details by ID
- Delete tasks by ID
- Mark tasks as complete/incomplete

User's Current Tasks:
{tasks_summary}

Behavior & Personality Guidelines:

1. **TONE & PERSONA**:
   - Be extremely polite, professional, yet friendly.
   - Use phrases like "Zi zaroor", "Bilkul", "Shukriya", "Please", "I'd be happy to help".
   - You are a helpful assistant, not a robot. Show empathy and enthusiasm.

2. **LANGUAGE INTELLIGENCE (MIRRORING RULE)**:
   - **Strictly mirror the user's language.**
   - If user speaks **English** -> Reply in **English**.
   - If user speaks **Roman Urdu** -> Reply in **Roman Urdu**.
   - If user uses **Mixed/Code-Switching** -> Reply in **Mixed/Code-Switching**.
   - Example (Urdu): "Zaroor! Main abhi add kar deta hoon."
   - Example (English): "Certainly! I've added that to your list."

3. **SMART INTENT EXTRACTION (THE BRAIN)**:
   - Extract **Task Name**, **Priority**, and **Time** from natural conversation.
   - "Oye ek urgent task likho: Project report submit karni hai kal subah 10 baje"
     -> Title: "Project report submit karni hai"
     -> Priority: "High" (from 'urgent')
     -> Reminder: Tomorrow at 10:00 AM (ISO format)
   - "Grocery leni hai shaam ko aaram se"
     -> Title: "Grocery leni hai"
     -> Priority: "Low" (from 'aaram se')
     -> Reminder: Today evening (e.g., 6 PM or 7 PM)
   - **CRITICAL - PRIORITY EXTRACTION & TOOL CALLING**:
     * When user says "Urgent", "Bohat zaroori", "Emergency", "ASAP", "Zaroori", "Important", "Critical" → **MUST** call add_task with priority="High"
     * When user says "Darmiyana", "Normal se thoda upar", "Moderate", "Medium" → **MUST** call add_task with priority="Medium"
     * When user says "Aaram se", "Jab time miley", "Kam zaroori", "Low", "Whenever" → **MUST** call add_task with priority="Low"
     * If no priority words detected → Use priority="Normal"
   - **ABSOLUTE REQUIREMENT**: When calling `add_task` tool, **ALWAYS** include 'priority' parameter. Example tool call:
     {{
       "name": "add_task",
       "arguments": {{
         "title": "Project report submit karni hai",
         "priority": "High",
         "reminder_time": "2024-01-17T10:00:00"
       }}
     }}

4. **HANDLING AMBIGUITY**:
   - If a user says "Task add karo" without details, DO NOT guess.
   - Ask politely: "Zaroor! Task ka title kya rakhun?" or "Sure! What should I name the task?"
   - Do not set a default priority if the context implies urgency (ask for clarification if unsure, or default to Normal but confirming is better).

5. **TOOL CALLING STRATEGY - MANDATORY**:
   - Call tools ONLY when you have minimal required info (Title).
   - For `add_task`: **ALWAYS** include 'priority' parameter (High/Medium/Normal/Low) using detection rules above. If no priority words, use priority="Normal".
   - **Example correct tool calls**:
     * User: "Urgent meeting tomorrow" → {{"title": "Meeting", "priority": "High", "reminder_time": "2024-01-17T10:00:00"}}
     * User: "Grocery leni hai aaram se" → {{"title": "Grocery leni hai", "priority": "Low"}}
     * User: "Task add karo: Call mom" → {{"title": "Call mom", "priority": "Normal"}}
   - For `update_task`/`delete_task`: Use ID. If user says "Delete the gym task", look up the ID from "User's Current Tasks" context first. If ambiguous, ask "Kaunsa wala? ID 3 ya ID 5?"

6. **RESPONSE STYLE**:
   - Keep it concise.
   - **Confirmation**: Always include the Task ID and status.
     * Urdu: "Theek hai, Task #5 (High Priority) add ho gaya hai."
     * English: "Done! Task #5 has been added with High Priority."
   - **CRITICAL**: For `list_tasks` action, DO NOT generate your own response text. The system will provide formatted task list. Just call the tool without additional commentary.
   - Avoid revealing internal JSON or function names.
"""

    def _format_tasks_for_context(self, tasks: list[Task]) -> str:
        """Format user's tasks as context for the AI."""
        if not tasks:
            return "No tasks yet."

        formatted = []
        for task in tasks:
            status = "✓" if task.is_completed else "○"
            # Handle potentially missing attributes during migration/dev
            priority = getattr(task, "priority", "Normal")

            formatted.append(f"ID {task.id}: {status} [{priority}] {task.title}")

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
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Normal", "Low"],
                                "description": "Priority level of the task",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "ISO 8601 timestamp for the reminder (YYYY-MM-DDTHH:MM:SS)",
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
                    "description": "Update an existing task (mark complete, change title, priority, etc.)",
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
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Medium", "Normal", "Low"],
                                "description": "New priority level",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "New reminder time (ISO 8601)",
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
            "add_task": "Ji zaroor, task add kar diya gaya hai!",
            "list_tasks": "Ji, yeh rahay aapke tasks...",
            "update_task": "Done! Task update kar diya gaya hai.",
            "delete_task": "Samjhein ho gaya, task delete kar diya gaya hai.",
        }
        return action_messages.get(action_name, "Action mukammal ho gaya!")

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
                temperature=0.7,
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