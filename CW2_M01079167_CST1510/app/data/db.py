import sqlite3
from pathlib import Path

# Always use the absolute path of the project root
# BASE_DIR points to the root directory of the project (3 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# DB_PATH builds the full path to the SQLite database file inside the DATA folder
DB_PATH = BASE_DIR / "DATA" / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """
    Connect to SQLite database using absolute path.
    Returns a connection object that can be used to interact with the database.
    """
    try:
        # Establish connection to the SQLite database
        # check_same_thread=False allows the connection to be shared across threads
        return sqlite3.connect(str(db_path), check_same_thread=False)
    except sqlite3.Error as err:
        # If connection fails, print an error message for debugging
        print(f"[db] Error connecting to database: {err}")
        # Re-raise the exception so the calling code knows something went wrong
        raise
