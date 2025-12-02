import sqlite3
import pandas as pd
from app.data.db import connect_database

def get_all_operations(conn=None):
    if conn is None:
        conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM it_operations")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df

def insert_operation(conn, op_id, name, status, notes):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_operations (id, name, status, notes)
        VALUES (?, ?, ?, ?)
    """, (op_id, name, status, notes))
    conn.commit()