from app.data.db import connect_database
from app.data.schema import create_all_tables

conn = connect_database()
create_all_tables(conn)
conn.close()

print("✅ Base de données initialisée avec toutes les tables.")
from app.data.db import connect_database

conn = connect_database()
cur = conn.cursor()

# Liste toutes les tables présentes dans ta base SQLite
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

print("📋 Tables dans la base :", tables)

conn.close()