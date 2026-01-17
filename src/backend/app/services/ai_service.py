"""
AI Service for Todo Chatbot using Groq API.
This service handles natural language processing, tool calling, 
and context-aware task management for MultiCraft Agency projects.
"""

import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, List, Dict, Optional

from openai import AsyncOpenAI

from app.core.config import settings
from app.models.task import Task
from app.schemas.chat import ChatResponse

# Setup logging for debugging tool calls
logger = logging.getLogger(__name__)

class AIService:
    """
    Service for processing chat messages with Groq API.
    Handles tool calling, language mirroring, and premium task formatting.
    """

    def __init__(self, api_key: str, model: str, base_url: str):
        """
        Initialize the OpenAI client with Groq configuration.
        """
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
        if not message:
            return "english"
            
        words = message.strip().split()[:5] # Checking first 5 words for better accuracy
        urdu_indicators = {
            'ji', 'ek', 'mujhe', 'bana', 'karo', 'kar', 'hai', 'nahi', 
            'zaroori', 'aaram', 'dikhao', 'saaf', 'khelna', 'chai', 'sham',
            'dikha', 'dikhayein', 'kardo', 'shukriya', 'salam'
        }

        # Check if any words contain Urdu indicators
        for word in words:
            if word.lower() in urdu_indicators:
                return "urdu"

        # Default to English if no Urdu indicators found
        return "english"

    def _format_tasks_for_language(self, tasks: List[Task], language: str) -> str:
        """
        Format tasks with language-specific labels and PREMIUM Markdown Icons.
        Ensures the list looks elegant, organized, and follows a strict sequence.
        """
        if not tasks:
            if language == "urdu":
                return "✨ Abhi aapki list khali hai. Koi naya task add karna hai?"
            return "✨ Your task list is currently empty. Ready to add something new?"

        # --- SEQUENCE FIX ---
        # Sorting tasks by ID descending so newest tasks appear at the top
        sorted_tasks = sorted(tasks, key=lambda x: x.id, reverse=True)
        
        formatted_output = []
        
        for task in sorted_tasks:
            # 1. Define Icons based on Status & Priority
            status_icon = "✅" if task.is_completed else "⏳"
            
            # Using getattr for safety in case priority field is missing in some records
            priority = getattr(task, "priority", "Normal")
            
            # Premium Priority Icons
            if priority == "High":
                prio_icon = "🔥" 
                prio_label_en = "URGENT"
                prio_label_ur = "BOHAT ZAROORI"
            elif priority == "Medium":
                prio_icon = "⚡"
                prio_label_en = "MEDIUM"
                prio_label_ur = "DARMIYANI"
            elif priority == "Low":
                prio_icon = "🧊"
                prio_label_en = "LOW"
                prio_label_ur = "KAM ZAROORI"
            else:
                prio_icon = "🟢"
                prio_label_en = "NORMAL"
                prio_label_ur = "NORMAL"

            # 2. Construct the Main Task Line
            if language == "urdu":
                status_text = "Mukammal" if task.is_completed else "Baaki"
                line = f"{status_icon} **ID: {task.id}** | {task.title}\n   └─ {prio_icon} Tarjeeh: {prio_label_ur} | Halat: {status_text}"
            else:
                status_text = "Completed" if task.is_completed else "Pending"
                line = f"{status_icon} **ID: {task.id}** | {task.title}\n   └─ {prio_icon} Priority: {prio_label_en} | Status: {status_text}"

            formatted_output.append(line)

            # 3. Handle Detailed Metadata (Description, Reminders)
            metadata_parts = []
            
            if task.description:
                desc_label = "Tafseel" if language == "urdu" else "Note"
                metadata_parts.append(f"📝 {desc_label}: {task.description}")

            reminder = getattr(task, "reminder_time", None)
            if reminder:
                rem_label = "Yaad dilaana" if language == "urdu" else "Reminder"
                metadata_parts.append(f"🔔 {rem_label}: {reminder}")

            if metadata_parts:
                formatted_output.append(f"      {' | '.join(metadata_parts)}")

        # Joining with double newlines ensures 'whitespace-pre-wrap' in React works perfectly
        return "\n\n".join(formatted_output)

    def _get_system_prompt(self, user_tasks: List[Task], detected_language: str) -> str:
        """
        Generate a comprehensive system prompt with strict identity and logic rules.
        """
        tasks_summary = self._format_tasks_for_language(user_tasks, detected_language)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Define Persona and Tone based on language
        if detected_language == "urdu":
            persona = "Aap Lyvexa AI hain, MultiCraft Agency ka official task manager."
            instructions = """
            - 'Ji' ka istemal har jawab mein karein (e.g., 'Ji bilkul', 'Ji zaroor').
            - Roman Urdu mein hi baat karein.
            - Jawab dene se pehle user ko acknowledge karein, sirf list na dikhayein.
            """
        else:
            persona = "You are Lyvexa AI, a high-end executive task management assistant."
            instructions = """
            - Maintain a professional and sharp English tone.
            - Use bullet points and clean spacing.
            - Greet the user politely before performing actions.
            """

        return f"""{persona}

SYSTEM CORE LOGIC:
1. DETECTED LANGUAGE: {detected_language.upper()} (Stay locked in this language).
2. CURRENT TIMESTAMP: {current_time}
3. CONTEXTUAL AWARENESS: Use the Task List below for IDs and details.

{instructions}

STRICT INTENT RULES:
- GREETING: If user says 'Hi' or 'Salam', reply warmly. DO NOT list tasks automatically.
- TASK REQUEST: If user asks 'tasks dikhao' or 'list tasks', use the FORMATTED CONTEXT.
- THE 'Ji' RULE: Always use 'Ji' instead of 'Zi'. This is non-negotiable for Urdu mode.

FORMATTED TASK CONTEXT (NEWEST FIRST):
--------------------------------------------------
{tasks_summary}
--------------------------------------------------

PRIORITY EXTRACTION SYSTEM:
- Detect 'Urgent', 'ASAP', 'Fori', 'Zaroori' -> set priority="High"
- Detect 'Slow', 'Aaram se', 'Low', 'Baad mein' -> set priority="Low"
- Otherwise -> set priority="Normal"
- ALWAYS pass the 'priority' argument in 'add_task' function calls.

TOOL USAGE:
- Use 'add_task' for new entries.
- Use 'list_tasks' to refresh the view.
- Use 'update_task' to change status (is_completed) or priority using Task ID.
- Use 'delete_task' for permanent removal using Task ID.
"""

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        Detailed JSON Schema for AI Tool calling.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task in the database. Ensure title and priority are captured.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Short summary of the task"},
                            "description": {"type": "string", "description": "Detailed notes about the task"},
                            "priority": {
                                "type": "string", 
                                "enum": ["High", "Normal", "Low"],
                                "description": "Mandatory priority level"
                            },
                            "reminder_time": {"type": "string", "description": "ISO format date string"}
                        },
                        "required": ["title", "priority"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve the current list of tasks for the user.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Modify an existing task status, title, or priority using its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "The unique ID of the task"},
                            "is_completed": {"type": "boolean", "description": "Target completion status"},
                            "title": {"type": "string"},
                            "priority": {"type": "string", "enum": ["High", "Normal", "Low"]},
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently remove a task record by ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "Task ID to delete"}
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

    async def stream_chat(
        self,
        user_message: str,
        user_tasks: List[Task],
        chat_history: List[Dict[str, Any]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Main interface for streaming chat completions with Groq.
        """
        # 1. Detection Phase
        detected_language = self._detect_language(user_message)
        
        # 2. Message Assembly
        messages = [
            {"role": "system", "content": self._get_system_prompt(user_tasks, detected_language)}
        ]
        
        # Add historical context (Last 8 turns for balance)
        if chat_history:
            for msg in chat_history[-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Final user input
        messages.append({"role": "user", "content": user_message})

        try:
            # 3. API Execution (Temperature 0.1 for high precision)
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools(),
                temperature=0.1,
                stream=True,
            )

            tool_calls_buffer = {}

            async for chunk in stream:
                if not chunk.choices:
                    continue
                    
                delta = chunk.choices[0].delta
                
                # Stream content tokens
                if delta.content:
                    yield json.dumps({"type": "token", "content": delta.content}) + "\n"

                # Buffer tool calls
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

            # 4. Finalizing Tool Calls
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
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode tool arguments: {tool_data['arguments']}")

        except Exception as e:
            logger.error(f"Streaming Error: {str(e)}")
            yield json.dumps({"type": "error", "content": "Neural Link reset. Attempting reconnection..."}) + "\n"

def get_ai_service() -> AIService:
    """
    Dependency provider for AI Service.
    """
    return AIService(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        base_url=settings.groq_base_url,
    )