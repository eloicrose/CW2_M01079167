import sqlite3
from pathlib import Path

# Always use the absolute path of the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "DATA" / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database using absolute path."""
    try:
        return sqlite3.connect(str(db_path), check_same_thread=False)
    except sqlite3.Error as err:
        print(f"[db] Error connecting to database: {err}")
        raise