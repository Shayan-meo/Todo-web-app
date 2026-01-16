"""Clean test to check list_tasks response."""
import requests
import json

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

def test_clean():
    token = get_token()
    if not token:
        return

    print("Testing list_tasks...")
    print("-" * 50)

    response = requests.post(
        f"{BASE_URL}/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Mere tasks dikhao"},
        stream=True
    )

    for line in response.iter_lines():
        if line:
            try:
                # Decode with utf-8 to handle emojis
                decoded = line.decode('utf-8')
                data = json.loads(decoded)

                if data['type'] == 'action_result':
                    print(f"ACTION_RESULT:")
                    print(f"  Action: {data.get('action_taken')}")
                    result = data.get('action_result', {})
                    print(f"  Success: {result.get('success')}")
                    print(f"  Count: {result.get('count')}")
                    print(f"  Keys in result: {list(result.keys())}")

                    if 'formatted_tasks' in result:
                        formatted = result['formatted_tasks']
                        print(f"  Formatted tasks: {formatted}")
                    else:
                        print(f"  NO formatted_tasks key!")

                        # Check if tasks array exists
                        if 'tasks' in result:
                            tasks = result['tasks']
                            print(f"  Tasks array length: {len(tasks)}")
                            if tasks:
                                print(f"  First task: {tasks[0]}")

                elif data['type'] == 'token':
                    content = data['content']
                    print(f"TOKEN: {repr(content)}")

            except Exception as e:
                print(f"Error: {e}")
                print(f"Raw line (hex): {line.hex()[:50]}...")

    print("-" * 50)

if __name__ == "__main__":
    test_clean()