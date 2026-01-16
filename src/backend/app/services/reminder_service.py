import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.task import Task
from app.crud.chat import save_chat_message

async def start_reminder_loop():
    """Background task to check for reminders every minute."""
    print("[SCHEDULER] Starting reminder loop...")
    while True:
        try:
            await check_reminders()
        except Exception as e:
            print(f"[SCHEDULER ERROR] {str(e)}")

        # Wait for 60 seconds before next check
        await asyncio.sleep(60)

async def check_reminders():
    """Check for due reminders and send notifications."""
    db = SessionLocal()
    try:
        # Use simple naive comparison if TZ handling is complex, assume server UTC
        # Or better, check what is stored. Assuming UTC.
        now = datetime.utcnow()

        # Find tasks:
        # 1. Has reminder_time set
        # 2. reminder_time is in the past (<= now)
        # 3. reminder_sent is False
        # 4. is_completed is False (don't remind for completed tasks)
        tasks = db.query(Task).filter(
            Task.reminder_time.isnot(None),
            Task.reminder_time <= now,
            Task.reminder_sent == False,
            Task.is_completed == False
        ).all()

        if tasks:
            print(f"[SCHEDULER] Found {len(tasks)} due reminders")

        for task in tasks:
            # Send notification based on priority
            if task.priority == "High":
                message = f"Suno! Aapka zaroori kaam '{task.title}' ka waqt ho gaya hai. Foran check karein! 🚩"
            else:
                message = f"Ek reminder hai: Aapne kaha tha ke '{task.title}' abhi karna hai."

            # Save message to chat history so user sees it next time they open chat
            # (or if using polling/WS, immediately)
            print(f"[SCHEDULER] Sending reminder for task {task.id}: {task.title}")
            save_chat_message(db, task.user_id, "assistant", message)

            # Mark as sent
            task.reminder_sent = True
            db.commit()

    except Exception as e:
        print(f"[SCHEDULER ERROR] Database error: {str(e)}")
        db.rollback()
    finally:
        db.close()
