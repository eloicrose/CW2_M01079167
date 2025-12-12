import sqlite3
import pandas as pd
from app.data.db import connect_database

def get_all_operations(conn=None):
    """
    Retrieve all IT operations stored in the it_operations table
    and return them as a pandas DataFrame.
    """
    if conn is None:
        # Create a new database connection if none is provided
        conn = connect_database()

    cursor = conn.cursor()
    # Select all rows from the it_operations table
    cursor.execute("SELECT * FROM it_operations")
    rows = cursor.fetchall()

    # Convert query results into a DataFrame with proper column names
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df


def insert_operation(conn, op_id, name, status, notes):
    """
    Insert a new IT operation entry into the it_operations table.
    Parameters:
        - op_id: unique identifier for the operation
        - name: name of the operation
        - status: current status (e.g., active, completed, pending)
        - notes: additional notes or comments about the operation
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_operations (id, name, status, notes)
        VALUES (?, ?, ?, ?)
    """, (op_id, name, status, notes))

    # Commit the transaction to save changes permanently
    conn.commit()
