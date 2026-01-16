import asyncio
from app.models.task import Task
from app.services.ai_service import AIService

# Create a mock task
class MockTask:
    def __init__(self):
        self.id = 1
        self.title = "Test Task"
        self.description = "Test Description"
        self.is_completed = False

async def test():
    service = AIService(
        api_key="test",
        model="test",
        base_url="http://localhost:8000"
    )
    
    # Test the default action message
    msg = service._get_default_action_message("list_tasks")
    print(f"Default message for list_tasks: '{msg}' (len={len(msg)})")
    
    msg = service._get_default_action_message("add_task")
    print(f"Default message for add_task: '{msg}' (len={len(msg)})")

asyncio.run(test())
