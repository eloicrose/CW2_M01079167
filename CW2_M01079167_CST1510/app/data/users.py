import sqlite3
from app.data.db import connect_database

def insert_user(username, password_hash, role):
    """
    Insert a new user into the database.
    Parameters:
        - username: unique identifier for the user (primary key)
        - password_hash: securely stored password (hashed, not plain text)
        - role: defines the user's role (e.g., admin, analyst, operator)
    """
    # Establish a connection to the database
    conn = connect_database()
    cur = conn.cursor()

    # Insert the new user record into the users table
    cur.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role)
    )

    # Commit the transaction to save changes permanently
    conn.commit()   # VERY IMPORTANT to ensure data is written to the DB
    # Close the connection to free resources
    conn.close()


def get_user_by_username(username):
    """
    Retrieve a user record by username.
    Returns a sqlite3.Row object (can be converted to dict for easier use).
    """
    # Establish a connection to the database
    conn = connect_database()
    # row_factory allows accessing columns by name (dict-like behavior)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Query the users table for the given username
    cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    # Fetch the first matching record (None if not found)
    user = cur.fetchone()

    # Close the connection to free resources
    conn.close()
    return user