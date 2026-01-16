"""Quick curl test for priority extraction."""
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

def quick_test():
    print("QUICK PRIORITY TEST")
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

    # Test 1: Urgent task
    print("\nTest 1: Urgent task")
    print("Message: 'Add an urgent task: Fix critical bug'")

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Add an urgent task: Fix critical bug"},
        stream=True
    )

    tool_called = False
    priority_found = False

    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                if data["type"] == "tool_call":
                    tool_called = True
                    args = data.get('arguments', {})
                    print(f"Tool call: {data.get('name')}")
                    print(f"Arguments: {args}")
                    if 'priority' in args:
                        priority_found = True
                        print(f"✓ Priority in args: {args['priority']}")
                    else:
                        print(f"✗ NO priority in args!")
                        print(f"Args keys: {list(args.keys())}")

            except Exception as e:
                print(f"Parse error: {e}")

    if not tool_called:
        print("✗ No tool_call event received!")

    # Wait a moment
    time.sleep(1)

    # Test 2: Check task list
    print("\nTest 2: List tasks")
    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "List my tasks"},
        stream=True
    )

    print("Task list response:")
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                if data["type"] == "action_result" and data.get('action_taken') == "list_tasks":
                    result = data.get('action_result', {})
                    tasks = result.get('tasks', [])
                    if tasks:
                        task = tasks[0]
                        print(f"\nTask created:")
                        print(f"  Title: {task.get('title')}")
                        print(f"  Priority: {task.get('priority')}")
                        if task.get('priority') == 'High':
                            print("  ✓ SUCCESS: Priority extracted correctly!")
                        else:
                            print(f"  ✗ FAILED: Priority is {task.get('priority')} (should be High)")
            except:
                pass

if __name__ == "__main__":
    quick_test()