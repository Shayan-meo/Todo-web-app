import sqlite3
from pathlib import Path

# Find the database file
db_file = Path(".") / "test.db"
if not db_file.exists():
    print("Database not found")
    exit(1)

conn = sqlite3.connect(str(db_file))
cursor = conn.cursor()

# Get latest assistant messages
cursor.execute("SELECT id, role, content FROM chat_messages ORDER BY created_at DESC LIMIT 10")
rows = cursor.fetchall()

print("Recent chat messages:")
for row_id, role, content in rows:
    print(f"  ID={row_id}, role={role}, len={len(content) if content else 0}, content='{(content or '')[:50]}'")

conn.close()
