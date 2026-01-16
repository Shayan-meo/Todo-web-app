"""Simple test for priority extraction."""
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

def test_simple():
    print("TESTING PRIORITY EXTRACTION")
    print("=" * 60)

    token = get_token()
    if not token:
        return

    # Wait for backend with new prompts
    print("Waiting for backend...")
    time.sleep(5)

    # Test one simple case
    message = "Add an urgent task: Fix the critical bug"
    print(f"\nUser: {message}")
    print("-" * 60)

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message},
        stream=True
    )

    print("Response events:")
    events = []
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                events.append(data["type"])
                if data["type"] == "action_result":
                    result = data.get('action_result', {})
                    if 'task' in result:
                        task = result['task']
                        print(f"\n✅ Task created:")
                        print(f"  ID: {task.get('id')}")
                        print(f"  Title: {task.get('title')}")
                        print(f"  Priority: {task.get('priority')}")
                        if task.get('priority') == 'High':
                            print("  ✓ CORRECT: Priority is High!")
                        else:
                            print(f"  ✗ WRONG: Priority is {task.get('priority')} (should be High)")
            except:
                pass

    print(f"\nEvent flow: {' → '.join(events)}")
    print("\nExpected: status → action_result → token")
    print("With priority='High' in add_task arguments")

if __name__ == "__main__":
    test_simple()