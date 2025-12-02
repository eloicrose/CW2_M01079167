import pandas as pd
from app.data.db import connect_database

def migrate_tickets_from_csv(file_path="DATA/it_tickets.csv", conn=None):
    """
    Load IT tickets from a CSV file and insert them into the it_tickets table.
    Expected columns: ticket_id, title, status, priority, assigned_to, created_at
    """
    df = pd.read_csv(file_path)

    local_conn = False
    if conn is None:
        conn = connect_database()
        local_conn = True

    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO it_tickets (ticket_id, title, status, priority, assigned_to, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row.get("ticket_id"),
            row.get("title"),
            row.get("status"),
            row.get("priority"),
            row.get("assigned_to"),
            row.get("created_at")
        ))

    if local_conn:
        conn.commit()
        conn.close()


def get_all_tickets(conn=None):
    if conn is None:
        conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM it_tickets")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df