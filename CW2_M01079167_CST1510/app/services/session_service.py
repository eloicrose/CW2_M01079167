import sqlite3
import uuid
from datetime import datetime, timedelta
from app.data.db import connect_database

# ---------------------------
# CREATE SESSION
# ---------------------------
def create_session(username, hours_valid=1):
    """
    Crée une session pour un utilisateur et retourne le token.
    La session expire après `hours_valid` heures.
    """
    token = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(hours=hours_valid)).isoformat()

    with connect_database() as conn:
        cursor = conn.cursor()
        # Création de la table si elle n'existe pas encore
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
        """)
        # Insertion de la session
        cursor.execute("""
        INSERT INTO sessions (token, username, expires_at)
        VALUES (?, ?, ?)
        """, (token, username, expires_at))
        conn.commit()

    return token

# ---------------------------
# VALIDATE SESSION
# ---------------------------
def validate_session(token):
    """
    Vérifie si un token existe et n'est pas expiré.
    Retourne True si valide, False sinon.
    """
    try:
        with connect_database() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT username, expires_at FROM sessions WHERE token = ?
            """, (token,))
            row = cursor.fetchone()
            if row is None:
                return False
            username, expires_at_str = row
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                # Session expirée, on peut la supprimer
                cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
                conn.commit()
                return False
            return True
    except Exception as e:
        print(f"❌ Error validating session: {e}")
        return False

# ---------------------------
# OPTIONAL: DELETE SESSION
# ---------------------------
def delete_session(token):
    """
    Supprime une session manuellement.
    """
    try:
        with connect_database() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Error deleting session: {e}")
        return False
