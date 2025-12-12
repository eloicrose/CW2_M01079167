import sqlite3

def create_all_tables(conn: sqlite3.Connection):
    """
    Create all required tables for the application if they do not already exist.
    This ensures the database schema is initialized and ready to store data.
    """
    cursor = conn.cursor()

    # ---------------------------
    # USERS TABLE
    # ---------------------------
    # Stores user accounts with:
    # - username: unique identifier (primary key)
    # - password_hash: securely stored password (hashed)
    # - role: defines user role (e.g., admin, analyst, operator)
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
    # Stores cybersecurity incidents with details:
    # - incident_id: unique identifier (primary key)
    # - timestamp: when the incident occurred
    # - severity: level of impact (low/medium/high)
    # - category: type of incident (e.g., malware, phishing)
    # - status: current state (open, resolved, in-progress)
    # - description: textual explanation of the incident
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
    # Stores metadata about datasets:
    # - dataset_id: unique identifier (primary key)
    # - name: dataset name
    # - description: short description
    # - rows: number of rows in dataset
    # - columns: number of columns in dataset
    # - size: dataset size (e.g., MB)
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
    # Stores IT support tickets:
    # - ticket_id: unique identifier (primary key)
    # - title: short title of the issue
    # - status: current state (open, closed, pending)
    # - priority: urgency level (low, medium, high)
    # - assigned_to: user responsible for handling the ticket
    # - created_at: timestamp when the ticket was created
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
    # Stores active user sessions:
    # - token: unique session token (primary key)
    # - username: user associated with the session
    # - expires_at: expiration timestamp for session validity
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
    # Stores IT operations records:
    # - id: unique identifier (primary key, auto-increment integer)
    # - name: name of the operation
    # - status: current state (e.g., running, completed)
    # - notes: additional comments or details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS it_operations (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT,
            notes TEXT
        )
    """)

    # Commit all table creation statements to the database
    conn.commit()
