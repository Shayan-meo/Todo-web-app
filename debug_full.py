"""Full debug of AI stream."""
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

def debug_full():
    print("FULL DEBUG OF AI STREAM")
    print("=" * 60)

    token = get_token()
    if not token:
        return

    # Clear tasks first
    print("\nClearing tasks...")
    requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Delete all tasks"},
        stream=True
    )
    time.sleep(1)

    # Test message
    message = "Add an urgent task: Fix the critical bug"
    print(f"\nUser: {message}")
    print("-" * 60)

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message},
        stream=True
    )

    print("\nFull stream events:")
    print("-" * 40)

    events = []
    for i, line in enumerate(response.iter_lines()):
        if line:
            events.append(line)
            try:
                decoded = line.decode('utf-8', errors='replace')
                data = json.loads(decoded)
                print(f"\nEvent {i+1}:")
                print(f"  Type: {data.get('type')}")

                if data["type"] == "status":
                    print(f"  Content: {data.get('content')}")

                elif data["type"] == "tool_call":
                    print(f"  Name: {data.get('name')}")
                    args = data.get('arguments', {})
                    print(f"  Arguments: {json.dumps(args, indent=4)}")
                    print(f"  Has priority: {'priority' in args}")
                    if 'priority' in args:
                        print(f"  Priority value: {args['priority']}")

                elif data["type"] == "action_result":
                    print(f"  Action: {data.get('action_taken')}")
                    result = data.get('action_result', {})
                    print(f"  Success: {result.get('success')}")
                    if 'task' in result:
                        task = result['task']
                        print(f"  Task priority: {task.get('priority')}")

                elif data["type"] == "token":
                    content = data.get('content', '')
                    print(f"  Content length: {len(content)}")
                    if content:
                        safe = ''.join(c if ord(c) < 128 else '.' for c in content[:100])
                        print(f"  First 100 chars: {safe}")

                elif data["type"] == "error":
                    print(f"  Error: {data.get('content')}")

            except Exception as e:
                print(f"  Parse error: {e}")
                print(f"  Raw line: {line[:100]}...")

    print("\n" + "="*60)
    print(f"Total events: {len(events)}")
    print("Event types found:", end=" ")
    for line in events:
        try:
            data = json.loads(line.decode('utf-8', errors='replace'))
            print(data.get('type'), end=" ")
        except:
            print("?", end=" ")

    print("\n\nEXPECTED FLOW:")
    print("1. status: 'Processing...' (optional)")
    print("2. tool_call: add_task with arguments including priority='High'")
    print("3. action_result: add_task with task details")
    print("4. token: AI response or default message")

if __name__ == "__main__":
    debug_full()