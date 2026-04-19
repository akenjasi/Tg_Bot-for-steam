import sqlite3
import sys
from pathlib import Path

db_path = Path("data/database.db")
if not db_path.exists():
    print(f"локальная база не найдена: {db_path}")
    print("если сервис запущен в Docker с volume, данные находятся внутри Docker volume, а не в локальном файле")
    sys.exit(0)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print(f"база: {db_path}")
print("таблица link:")
print("-" * 50)

c.execute("SELECT * FROM link")
rows = c.fetchall()

if not rows:
    print("пусто")
else:
    for row in rows:
        print(f"id: {row[0]}, telegram: {row[1]}, steam: {row[2]}")

conn.close()
