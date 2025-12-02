import sqlite3

def create_all_tables(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # ---------------------------
    # USERS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # ---------------------------
    # CYBER INCIDENTS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            incident_id TEXT PRIMARY KEY,
            timestamp TEXT,
            severity TEXT,
            category TEXT,
            status TEXT,
            description TEXT
        )
    """)

    # ---------------------------
    # DATASETS METADATA TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            rows INTEGER,
            columns INTEGER,
            size INTEGER
        )
    """)

    # ---------------------------
    # IT TICKETS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            priority TEXT,
            assigned_to TEXT,
            created_at TEXT
        )
    """)

    # ---------------------------
    # SESSIONS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)
    # ---------------------------
    # IT OPERATIONS TABLE
    # ---------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_operations (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT,
            notes TEXT
        )
    """)
    conn.commit()