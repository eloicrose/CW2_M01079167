import sqlite3
from app.data.db import connect_database

def insert_user(username, password_hash, role):
    """Insert a new user into the database."""
    conn = connect_database()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, role)
    )

    conn.commit()   # VERY IMPORTANT
    conn.close()


def get_user_by_username(username):
    """Retrieve a user record by username."""
    conn = connect_database()
    conn.row_factory = sqlite3.Row  # pour pouvoir faire dict(user) si besoin
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cur.fetchone()
    conn.close()
    return user 