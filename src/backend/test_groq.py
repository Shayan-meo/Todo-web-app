"""Test script for Groq AI API connection."""

import asyncio
import os

from openai import AsyncOpenAI

# Get API key from environment
api_key = os.getenv("GROQ_API_KEY", "")

if not api_key:
    print("[X] GROQ_API_KEY not set in environment variables.")
    print("Please set it like: export GROQ_API_KEY=your_key_here")
    exit(1)

print(f"[+] Using API key (first 10 chars): {api_key[:10]}...")

# Initialize client
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

print("[*] Testing Groq API connection...")


async def test_chat():
    """Test basic chat completion."""
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that responds in English and Roman Urdu.",
                },
                {"role": "user", "content": "Hello! Please say hello in Roman Urdu."},
            ],
            temperature=0.7,
        )

        ai_response = response.choices[0].message.content
        print(f"\n[OK] API Connection Successful!")
        print(f"\n[*] AI Response:\n{ai_response}\n")
        return True
    except Exception as e:
        print(f"\n[FAIL] API Connection Failed: {e}\n")
        return False


async def test_tool_calling():
    """Test tool calling capability."""
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a todo assistant. Use tools when appropriate.",
                },
                {"role": "user", "content": "Add a task called 'Test task'"},
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Add a new task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Task title"}
                            },
                            "required": ["title"],
                        },
                    },
                }
            ],
            tool_choice="auto",
            temperature=0.7,
        )

        assistant_message = response.choices[0].message
        has_tool_calls = assistant_message.tool_calls is not None

        if has_tool_calls:
            print(f"[OK] Tool Calling Works!")
            for tool in assistant_message.tool_calls:
                print(f"   Tool: {tool.function.name}")
                print(f"   Args: {tool.function.arguments}")
        else:
            print(f"[WARN] Tool Calling - AI chose not to use tool")
            print(f"   Response: {assistant_message.content}")

        return has_tool_calls
    except Exception as e:
        print(f"[FAIL] Tool Calling Test Failed: {e}")
        return False


async def test_roman_urdu():
    """Test Roman Urdu understanding."""
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You understand English and Roman Urdu. Respond in the same language as the user.",
                },
                {"role": "user", "content": "Mere kitne tasks baaki hain?"},
            ],
            temperature=0.7,
        )

        ai_response = response.choices[0].message.content
        print(f"\n[OK] Roman Urdu Test Passed!")
        print(f"\n[*] Response: {ai_response}\n")
        return True
    except Exception as e:
        print(f"\n[FAIL] Roman Urdu Test Failed: {e}\n")
        return False


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Groq API Test Suite")
    print("=" * 50)
    print()

    # Run tests
    chat_ok = await test_chat()
    tool_ok = await test_tool_calling()
    urdu_ok = await test_roman_urdu()

    # Summary
    print("=" * 50)
    print("Test Summary:")
    print("=" * 50)
    print(f"Basic Chat:      [{'OK' if chat_ok else 'FAIL'}]")
    print(f"Tool Calling:    [{'OK' if tool_ok else 'FAIL'}]")
    print(f"Roman Urdu:      [{'OK' if urdu_ok else 'FAIL'}]")
    print()

    if chat_ok and tool_ok and urdu_ok:
        print("[SUCCESS] All tests passed! Groq API is ready for production.")
        exit(0)
    else:
        print("[WARNING] Some tests failed. Please review the errors above.")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())