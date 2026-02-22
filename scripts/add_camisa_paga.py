"""Script para adicionar a coluna camisa_paga ao banco de dados"""
import sqlite3
import os

db_paths = [
    os.path.join(os.path.dirname(__file__), 'instance', 'turma_unip.db'),
    os.path.join(os.path.dirname(__file__), 'instance', 'users.db'),
    os.path.join(os.path.dirname(__file__), 'database.db'),
]

db_path = None
for p in db_paths:
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("❌ Banco de dados não encontrado! Verifique o caminho.")
    exit(1)

print(f"✅ Banco de dados encontrado: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verifica se a coluna já existe
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]

if 'camisa_paga' in columns:
    print("ℹ️  Coluna 'camisa_paga' já existe. Nenhuma alteração necessária.")
else:
    cursor.execute("ALTER TABLE users ADD COLUMN camisa_paga BOOLEAN DEFAULT 0")
    conn.commit()
    print("✅ Coluna 'camisa_paga' adicionada com sucesso!")

conn.close()
print("✅ Migração concluída!")
