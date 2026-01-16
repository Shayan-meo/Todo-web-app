"""Test priority extraction with updated prompts."""
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

def test_priority_extraction():
    print("\nTESTING PRIORITY EXTRACTION")
    print("=" * 60)

    token = get_token()
    if not token:
        print("Failed to get token")
        return

    # Wait for backend to reload with new prompts
    print("Waiting for backend to reload...")
    time.sleep(3)

    # Clear existing tasks
    print("\nClearing tasks...")
    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Delete all my tasks"},
        stream=True
    )
    for _ in response.iter_lines():
        pass
    time.sleep(1)

    # Test cases with expected priorities
    test_cases = [
        ("Urgent Roman Urdu", "Salam! Ek bohat zaroori task add karo: Project report submit karni hai", "High"),
        ("Zaroori keyword", "Ek zaroori task: Meeting kal 11 baje", "High"),
        ("Urgent English", "Add an urgent task: Fix the bug", "High"),
        ("Darmiyana Roman Urdu", "Ek darmiyana task: Grocery leni hai", "Medium"),
        ("Medium English", "Add a medium priority task: Write documentation", "Medium"),
        ("Aaram se Roman Urdu", "Aaram se ek task: Book padhna hai", "Low"),
        ("Low English", "Add a low priority task: Clean desk", "Low"),
        ("No priority specified", "Task add karo: Call mom", "Normal"),
    ]

    for description, message, expected_priority in test_cases:
        print(f"\n{'='*40}")
        print(f"Test: {description}")
        print(f"Expected Priority: {expected_priority}")
        print('='*40)

        print(f"User: {message}")
        print("AI: ", end="", flush=True)

        response = requests.post(
            f"{BASE_URL}/ai/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": message},
            stream=True
        )

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8', errors='replace'))
                    if data["type"] == "token":
                        content = data["content"]
                        safe_content = ''.join(c if ord(c) < 128 else '.' for c in content)
                        print(safe_content, end="", flush=True)
                    elif data["type"] == "action_result":
                        action = data.get('action_taken', 'unknown')
                        if action == "add_task":
                            result = data.get('action_result', {})
                            task = result.get('task', {})
                            actual_priority = task.get('priority', 'Normal')
                            print(f"\n[Action: {action}, Priority: {actual_priority}]", end="", flush=True)
                            if actual_priority == expected_priority:
                                print(" ✅", end="")
                            else:
                                print(f" ❌ (expected {expected_priority})", end="")
                except:
                    pass

        print("\n")
        time.sleep(1)

    # Now list all tasks to see priorities
    print("\n" + "="*60)
    print("LISTING ALL TASKS TO VERIFY PRIORITIES")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Mere sarae tasks dikhao with priorities"},
        stream=True
    )

    print("\nUser: Mere sarae tasks dikhao with priorities")
    print("AI: ", end="", flush=True)

    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8', errors='replace'))
                if data["type"] == "token":
                    content = data["content"]
                    safe_content = ''.join(c if ord(c) < 128 else '.' for c in content)
                    print(safe_content, end="", flush=True)
            except:
                pass

    print("\n\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("The AI should now correctly extract and set priorities:")
    print("- 'Urgent', 'Bohat zaroori', 'Zaroori' → High")
    print("- 'Darmiyana', 'Medium' → Medium")
    print("- 'Aaram se', 'Low' → Low")
    print("- No priority mentioned → Normal")

if __name__ == "__main__":
    test_priority_extraction()