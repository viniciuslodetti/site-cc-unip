import sqlite3
import os

db_path = os.path.join('instance', 'turma_unip.db')

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    if os.path.exists('turma_unip.db'):
        db_path = 'turma_unip.db'
    else:
        print("db not found")
        exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column(table, column, definition):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Added column {column}")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f"Column {column} already exists")
        else:
            print(f"Error adding {column}: {e}")

try:
    add_column('users', 'tamanho_camisa', 'TEXT')
    add_column('users', 'quantidade_camisa', 'INTEGER DEFAULT 1')
    conn.commit()
    print("Database updated!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
