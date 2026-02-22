import sqlite3
import os

db_path = os.path.join('instance', 'turma_unip.db')

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    if os.path.exists('turma_unip.db'):
        db_path = 'turma_unip.db'
        print(f"Found database at root: {db_path}")
    else:
        print("Database file missing!")
        exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'apelido' not in columns:
        print("Adding 'apelido' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN apelido TEXT")
        conn.commit()
        print("Column added successfully!")
    else:
        print("'apelido' column already exists.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    conn.close()
