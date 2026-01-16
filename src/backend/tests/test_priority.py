from app.crud import task as task_crud
from app.schemas.task import TaskCreate
from app.models.task import Task

def test_priority_sorting(db_session, test_user):
    # Create tasks with different priorities and times
    # We create them in an order that would be wrong if not sorted by priority

    # 1. Low Priority (Created first)
    task1 = task_crud.create_task(
        db_session,
        test_user.id,
        TaskCreate(title="Low Task", priority="Low")
    )

    # 2. High Priority (Created second)
    task2 = task_crud.create_task(
        db_session,
        test_user.id,
        TaskCreate(title="High Task", priority="High")
    )

    # 3. Medium Priority (Created third)
    task3 = task_crud.create_task(
        db_session,
        test_user.id,
        TaskCreate(title="Medium Task", priority="Medium")
    )

    # 4. High Priority (Created fourth - should be above task2 due to date sorting descending? or check code)
    # in CRUD: order_by(priority_order, Task.created_at.desc())
    # So High tasks come first. Among High tasks, newest (task4) comes before older (task2).
    task4 = task_crud.create_task(
        db_session,
        test_user.id,
        TaskCreate(title="High Task Newer", priority="High")
    )

    tasks = task_crud.get_tasks_for_user(db_session, test_user.id)

    # Expected Order:
    # 1. High Task Newer (ID 4)
    # 2. High Task (ID 2)
    # 3. Medium Task (ID 3)
    # 4. Low Task (ID 1)

    assert len(tasks) == 4
    assert tasks[0].id == task4.id
    assert tasks[0].priority == "High"

    assert tasks[1].id == task2.id
    assert tasks[1].priority == "High"

    assert tasks[2].id == task3.id
    assert tasks[2].priority == "Medium"

    assert tasks[3].id == task1.id
    assert tasks[3].priority == "Low"

def test_delete_by_id(db_session, test_user):
    task = task_crud.create_task(
        db_session,
        test_user.id,
        TaskCreate(title="To Delete", priority="Normal")
    )

    # Verify existence
    stored_task = task_crud.get_task(db_session, task.id, test_user.id)
    assert stored_task is not None

    # Delete
    task_crud.delete_task(db_session, stored_task)

    # Verify deletion
    deleted_task = task_crud.get_task(db_session, task.id, test_user.id)
    assert deleted_task is None
