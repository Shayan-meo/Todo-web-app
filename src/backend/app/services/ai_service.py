"""AI Service for Todo Chatbot using Groq API."""

import json
from datetime import datetime
from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.task import Task
from app.schemas.chat import ChatResponse


class AIService:
    """
    Service for processing chat messages with Groq API.
    Handles tool calling, language mirroring, and task context.
    """

    def __init__(self, api_key: str, model: str, base_url: str):
        """Initialize the OpenAI client with Groq configuration."""
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

    def _detect_language(self, message: str) -> str:
        """
        Neural Language Detection based on first 3 words.
        Returns 'urdu' for Roman Urdu, 'english' for English.
        """
        words = message.strip().split()[:3]
        urdu_indicators = {'ji', 'ek', 'mujhe', 'bana', 'karo', 'kar', 'hai', 'nahi', 'zaroori', 'aaram'}

        # Check if any of the first 3 words contain Urdu indicators
        for word in words:
            if word.lower() in urdu_indicators:
                return "urdu"

        # Default to English if no Urdu indicators found
        return "english"

    def _format_tasks_for_language(self, tasks: list[Task], language: str) -> str:
        """
        Format tasks with language-specific labels.
        """
        if not tasks:
            return "No tasks yet." if language == "english" else "Koi task nahi hai."

        formatted = []
        for task in tasks:
            status = "[STATUS: COMPLETED]" if task.is_completed else "[STATUS: PENDING]"
            priority = getattr(task, "priority", "Normal")

            if language == "urdu":
                status_display = "Mukammal" if task.is_completed else "Baaki"
                priority_display = {
                    "High": "Bohat Zaroori",
                    "Medium": "Darmiyani",
                    "Normal": "Normal",
                    "Low": "Kam Zaroori"
                }.get(priority, "Normal")
                line = f"ID: {task.id} | Halat: {status_display} | Tarjeeh: {priority_display} | {task.title}"
            else:
                status_display = "Completed" if task.is_completed else "Pending"
                line = f"ID: {task.id} | Status: {status_display} | Priority: {priority} | {task.title}"

            formatted.append(line)

            details = []
            if task.description:
                if language == "urdu":
                    details.append(f"Tafseel: {task.description}")
                else:
                    details.append(f"Description: {task.description}")

            reminder = getattr(task, "reminder_time", None)
            if reminder:
                if language == "urdu":
                    details.append(f"Yaad dilaany ka waqt: {reminder}")
                else:
                    details.append(f"Reminder: {reminder}")

            if details:
                formatted.append(f"   {' | '.join(details)}")

        return "\n".join(formatted)

    def _get_system_prompt(self, user_tasks: list[Task], detected_language: str) -> str:
        """
        Generate a detailed system prompt with strict language locking rules.
        """
        tasks_summary = self._format_tasks_for_language(user_tasks, detected_language)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Language-specific opening based on detection
        if detected_language == "urdu":
            opening = "Ji, mein aik professional Urdu-speaking Task Manager Hoon. Mai bilkul aapki bhasha mein jawab doonga."
            tone_instruction = "Tahzeeb se jawab dein lekin professional tareeqe se. 'Ji' istemal karein."
            format_instruction = "ID: 33 | Halat: Baaki | Tarjeeh: Bohat Zaroori | Meeting"
        else:
            opening = "You are a professional, executive-grade Task Manager Assistant."
            tone_instruction = "Use a professional, executive tone. DO NOT mix in any Urdu words."
            format_instruction = "ID: 33 | Status: Pending | Priority: High | Meeting"

        return f"""{opening}

Current Time: {current_time}

STRICT LANGUAGE LOCKING SYSTEM:
1. ANALYSIS PHASE: Detected user language is {detected_language.upper()}.
2. NEURAL LOCK: You are now LOCKED into {detected_language.upper()} mode.
3. THE 'Ji' RULE: Always use 'Ji' instead of 'Zi' (e.g., 'Ji zaroor', 'Ji bilkul', 'Ji shukriya').
4. ZERO MIXING: Under NO circumstances mix languages in a single sentence.
5. {tone_instruction}

TASK MANAGEMENT CAPABILITIES:
- Add tasks: Extract Title, Description, Priority (High/Normal/Low), and Time.
- List tasks: Show pending or completed tasks as requested.
- Update/Delete: Use Task ID from the context below.

USER TASK LIST CATEGORIES (STRICT FILTERING):
- If user asks for 'complete', 'done', or 'mukammal' tasks -> FILTER to ONLY show COMPLETED tasks.
- If user asks for 'pending', 'remaining', 'baaki', or 'incomplete' tasks -> FILTER to ONLY show PENDING tasks.
- 'Show all' or 'saare' -> List everything.

TASK FORMATTING ({detected_language.upper()} MODE):
{tasks_summary}
Example: {format_instruction}

PRIORITY EXTRACTION RULES:
- 'Urgent', 'Zaroori', 'ASAP', 'Emergency' -> priority="High"
- 'Aaram se', 'Low priority', 'Kam zaroori' -> priority="Low"
- Everything else -> priority="Normal"
- ALWAYS provide priority argument in add_task tool call.

CONTEXT-AWARE RESPONSE:
- Maintain language lock throughout conversation
- If user switches languages, adapt immediately but stay consistent in each response
- NEVER use mixed-language labels or formatting

Example JSON Tool Call:
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
        """
        DEPRECATED: Use _format_tasks_for_language instead.
        Kept for backward compatibility.
        """
        return self._format_tasks_for_language(tasks, "english")

    def _get_tools(self) -> list[dict[str, Any]]:
        """
        Define the JSON schema for tools available to the AI.
        Includes add, list, update, and delete functions.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task with details to the todo list. MUST always include priority argument.",
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
                                "enum": ["High", "Normal", "Low"],
                                "description": "MANDATORY: Priority level based on urgency detection",
                            },
                            "reminder_time": {
                                "type": "string",
                                "description": "ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS)",
                            },
                        },
                        "required": ["title", "priority"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all of the user's tasks from the database",
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
                    "description": "Update an existing task's status or details",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The unique ID of the task",
                            },
                            "is_completed": {
                                "type": "boolean",
                                "description": "Mark as completed or pending",
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the task",
                            },
                            "description": {
                                "type": "string",
                                "description": "New description",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["High", "Normal", "Low"],
                                "description": "New priority level",
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
                    "description": "Delete a task from the user's list permanently",
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

    def _get_default_action_message(self, action_name: str | None, language: str = "english") -> str:
        """
        Provide a fallback message if the AI tool call succeeds but
        no specific content is generated.
        """
        if language == "urdu":
            action_messages = {
                "add_task": "Ji zaroor, task add kar diya gaya hai!",
                "list_tasks": "Ji, yeh rahay aapke tasks...",
                "update_task": "Ji, task update ho gaya hai.",
                "delete_task": "Ji, task delete kar diya gaya hai.",
            }
            return action_messages.get(action_name, "Ji, kaam mukammal ho gaya!")
        else:
            action_messages = {
                "add_task": "Task has been added successfully.",
                "list_tasks": "Here are your tasks...",
                "update_task": "Task has been updated.",
                "delete_task": "Task has been deleted.",
            }
            return action_messages.get(action_name, "Operation completed successfully.")

    async def stream_chat(
        self,
        user_message: str,
        user_tasks: list[Task],
        chat_history: list[dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Main method to stream chat tokens and handle asynchronous tool calls.
        Sets temperature to 0.1 for maximum adherence to system rules.
        """
        messages = []
        # Detect language from first 3 words
        detected_language = self._detect_language(user_message)

        # Add system prompt with current context and language detection
        messages.append({"role": "system", "content": self._get_system_prompt(user_tasks, detected_language)})
        
        # Add limited chat history for continuity
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the latest user message
        messages.append({"role": "user", "content": user_message})

        try:
            # Call Groq API with low temperature to avoid hallucination and language mixing
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools(),
                temperature=0.1,  
                stream=True,
            )

            tool_calls_buffer = {}

            async for chunk in stream:
                delta = chunk.choices[0].delta

                # Yield text tokens directly
                if delta.content:
                    yield json.dumps({"type": "token", "content": delta.content}) + "\n"

                # Buffer tool call chunks
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

            # Process completed tool calls from buffer
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
                    except Exception as e:
                        print(f"[ERROR] Tool parsing error: {str(e)}")
                        yield json.dumps({"type": "error", "content": "Failed to parse tool arguments."}) + "\n"

        except Exception as e:
            print(f"[ERROR] Stream failed: {str(e)}")
            yield json.dumps({"type": "error", "content": "Failed to stream response."}) + "\n"


def get_ai_service() -> AIService:
    """
    Dependency injection provider for the AI Service.
    Uses settings from the application core config.
    """
    return AIService(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        base_url=settings.groq_base_url,
    )