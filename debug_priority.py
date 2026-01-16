"""Debug priority extraction."""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"
EMAIL = "testuser@example.com"
PASSWORD = "password123"

def get_token():
    """Login and get access token."""
    try:
        requests.post(f"{BASE_URL}/auth/register", json={
            "email": EMAIL, "password": PASSWORD, "full_name": "Test User"
        })
    except:
        pass

    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": EMAIL, "password": PASSWORD
    })

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Login failed:", response.text)
        return None

def debug_one_message():
    print("DEBUGGING PRIORITY EXTRACTION")
    print("=" * 60)

    token = get_token()
    if not token:
        return

    # Test one message with full debug
    message = "Add an urgent task: Fix the bug"
    print(f"\nUser: {message}")
    print("-" * 60)

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message},
        stream=True
    )

    print("Raw stream output:")
    for line in response.iter_lines():
        if line:
            try:
                decoded = line.decode('utf-8', errors='replace')
                data = json.loads(decoded)

                if data["type"] == "tool_call":
                    print(f"\nTOOL_CALL:")
                    print(f"  Name: {data.get('name')}")
                    print(f"  Arguments: {json.dumps(data.get('arguments', {}), indent=4)}")

                    # Check if priority is in arguments
                    args = data.get('arguments', {})
                    if 'priority' in args:
                        print(f"  ✓ Priority found: {args['priority']}")
                    else:
                        print(f"  ✗ Priority NOT in arguments!")
                        print(f"  Arguments keys: {list(args.keys())}")

                elif data["type"] == "action_result":
                    print(f"\nACTION_RESULT:")
                    print(f"  Action: {data.get('action_taken')}")
                    result = data.get('action_result', {})
                    print(f"  Success: {result.get('success')}")
                    if 'task' in result:
                        task = result['task']
                        print(f"  Task ID: {task.get('id')}")
                        print(f"  Task Priority: {task.get('priority')}")
                        print(f"  Task Title: {task.get('title')}")

                elif data["type"] == "token":
                    content = data["content"]
                    safe_content = ''.join(c if ord(c) < 128 else '.' for c in content)
                    print(f"\nTOKEN: {safe_content}")

            except Exception as e:
                print(f"Error: {e}")
                print(f"Raw: {line[:100]}...")

    print("\n" + "="*60)
    print("ANALYSIS:")
    print("The AI should call add_task with arguments including 'priority': 'High'")
    print("Check if the tool_call includes priority in arguments.")

if __name__ == "__main__":
    debug_one_message()