"""Quick test to check if priority extraction works."""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"
EMAIL = "testuser@example.com"
PASSWORD = "password123"

def quick_test():
    print("QUICK CHAT TEST - Priority Extraction")
    print("=" * 60)

    # Get token
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": EMAIL, "password": PASSWORD
        })
        token = response.json()["access_token"]
        print("✓ Got auth token")
    except:
        print("✗ Failed to get token")
        return

    # Clear tasks
    print("\nClearing tasks...")
    requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Delete all tasks"},
        stream=True
    )
    time.sleep(1)

    # Test 1: Roman Urdu with priority
    print("\nTest 1: Roman Urdu - 'Ek urgent task add karo: Meeting kal 11 baje'")
    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Ek urgent task add karo: Meeting kal 11 baje"},
        stream=True
    )

    # Just get response
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                if data["type"] == "action_result":
                    print(f"Action: {data.get('action_taken')}")
                    if data.get('action_taken') == 'add_task':
                        result = data.get('action_result', {})
                        if 'task' in result:
                            task = result['task']
                            print(f"  Task Priority: {task.get('priority')}")
                            if task.get('priority') == 'High':
                                print("  ✓ SUCCESS: High priority detected!")
                            else:
                                print(f"  ✗ FAILED: Priority is {task.get('priority')}")
            except:
                pass

    time.sleep(1)

    # Test 2: List tasks to confirm
    print("\nTest 2: Listing tasks...")
    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Mere tasks dikhao"},
        stream=True
    )

    print("Task list:")
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                if data["type"] == "action_result" and data.get('action_taken') == 'list_tasks':
                    result = data.get('action_result', {})
                    tasks = result.get('tasks', [])
                    if tasks:
                        task = tasks[0]
                        print(f"\nLatest task:")
                        print(f"  Title: {task.get('title')}")
                        print(f"  Priority: {task.get('priority')}")
                elif data["type"] == "token":
                    content = data.get('content', '')
                    if content and len(content) < 100:
                        safe = ''.join(c if ord(c) < 128 else '.' for c in content)
                        print(f"AI: {safe}")
            except:
                pass

    print("\n" + "="*60)
    print("Check backend terminal for [DEBUG] logs showing priority parameter!")

if __name__ == "__main__":
    quick_test()