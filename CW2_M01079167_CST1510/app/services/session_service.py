import sqlite3
import uuid
from datetime import datetime, timedelta
from app.data.db import connect_database

# ---------------------------
# CREATE SESSION
# ---------------------------
def create_session(username, hours_valid=1):
    """
    Create a session for a user and return the session token.
    The session expires after `hours_valid` hours.
    """
    # Generate a unique session token using UUID
    token = str(uuid.uuid4())
    # Calculate expiration time based on current time + validity period
    expires_at = (datetime.now() + timedelta(hours=hours_valid)).isoformat()

    # Open a database connection (context manager ensures proper closing)
    with connect_database() as conn:
        cursor = conn.cursor()
        # Ensure the sessions table exists (create if not)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
        """)
        # Insert the new session record
        cursor.execute("""
        INSERT INTO sessions (token, username, expires_at)
        VALUES (?, ?, ?)
        """, (token, username, expires_at))
        # Commit changes to save the session
        conn.commit()

    # Return the generated session token
    return token


# ---------------------------
# VALIDATE SESSION
# ---------------------------
def validate_session(token):
    """
    Check if a session token exists and is not expired.
    Returns True if valid, False otherwise.
    """
    try:
        with connect_database() as conn:
            cursor = conn.cursor()
            # Look up the session by token
            cursor.execute("""
            SELECT username, expires_at FROM sessions WHERE token = ?
            """, (token,))
            row = cursor.fetchone()

            # If no session found, token is invalid
            if row is None:
                return False

            username, expires_at_str = row
            # Convert expiration string back to datetime
            expires_at = datetime.fromisoformat(expires_at_str)

            # If current time is past expiration, session is invalid
            if datetime.now() > expires_at:
                # Delete expired session from DB
                cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
                conn.commit()
                return False

            # Otherwise, session is still valid
            return True
    except Exception as e:
        # Handle unexpected errors gracefully
        print(f"❌ Error validating session: {e}")
        return False


# ---------------------------
# OPTIONAL: DELETE SESSION
# ---------------------------
def delete_session(token):
    """
    Manually delete a session by its token.
    Returns True if deletion succeeded, False otherwise.
    """
    try:
        with connect_database() as conn:
            cursor = conn.cursor()
            # Delete the session record
            cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
            return True
    except Exception as e:
        # Handle unexpected errors gracefully
        print(f"❌ Error deleting session: {e}")
        return False
