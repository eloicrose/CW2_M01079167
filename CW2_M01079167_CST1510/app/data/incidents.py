import pandas as pd
from app.data.db import connect_database

def migrate_incidents_from_csv(file_path="DATA/cyber_incidents.csv", conn=None):
    """
    Load incidents from a CSV file and insert them into the cyber_incidents table.
    Expected columns: incident_id, timestamp, severity, category, status, description
    Duplicate incident_id values will be ignored.
    """
    df = pd.read_csv(file_path)

    local_conn = False
    if conn is None:
        conn = connect_database()
        local_conn = True

    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO cyber_incidents (incident_id, timestamp, severity, category, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row.get("incident_id"),
            row.get("timestamp"),
            row.get("severity"),
            row.get("category"),
            row.get("status"),
            row.get("description"),
        ))

    if local_conn:
        conn.commit()
        conn.close()


def get_all_incidents(conn=None):
    if conn is None:
        conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cyber_incidents")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df


def insert_incident(conn, incident_id, timestamp, severity, category, status, description):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (incident_id, timestamp, severity, category, status, description))
    conn.commit()
    return cursor.lastrowid