"""Test priority extraction manually."""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"
EMAIL = "testuser@example.com"
PASSWORD = "password123"

def test_priority():
    print("TESTING PRIORITY EXTRACTION MANUALLY")
    print("=" * 60)

    # First get auth token
    print("Getting auth token...")
    try:
        # Try to register/login
        try:
            requests.post(f"{BASE_URL}/auth/register", json={
                "email": EMAIL, "password": PASSWORD, "full_name": "Test User"
            })
        except:
            pass

        login_resp = requests.post(f"{BASE_URL}/auth/login", data={
            "username": EMAIL, "password": PASSWORD
        })

        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.text}")
            return None

        token = login_resp.json()["access_token"]
        print("✓ Got token")

    except Exception as e:
        print(f"Auth failed: {e}")
        return None

    # Clear any existing tasks
    print("\nClearing tasks...")
    requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Delete all tasks"},
        stream=True
    )
    time.sleep(1)

    # Test 1: Add urgent task
    print("\nTest 1: Adding urgent task...")
    print("Message: 'Add an urgent task: Fix critical bug'")

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Add an urgent task: Fix critical bug"},
        stream=True
    )

    # Check what priority was used
    print("\nChecking backend logs for debug output...")
    print("(Check the backend terminal for [DEBUG] messages)")

    # Now list tasks to see priority
    print("\nTest 2: Listing tasks to check priority...")
    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "List my tasks"},
        stream=True
    )

    print("\nTask list response:")
    tasks_found = []
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                if data["type"] == "action_result" and data.get('action_taken') == "list_tasks":
                    result = data.get('action_result', {})
                    tasks = result.get('tasks', [])
                    if tasks:
                        print("\n✓ Tasks found:")
                        for task in tasks:
                            print(f"  - Task: {task.get('title')}")
                            print(f"    Priority: {task.get('priority')}")
                            print(f"    ID: {task.get('id')}")
                            tasks_found.append(task)
            except:
                pass

    if not tasks_found:
        print("No tasks found or error reading response")

    return token

if __name__ == "__main__":
    test_priority()