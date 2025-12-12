import pandas as pd  # Import pandas for data manipulation and CSV handling
from app.data.db import connect_database  # Import the database connection function

def migrate_incidents_from_csv(file_path="DATA/cyber_incidents.csv", conn=None):
    """
    Load incidents from a CSV file and insert them into the cyber_incidents table.
    Expected columns: incident_id, timestamp, severity, category, status, description
    Duplicate incident_id values will be ignored.
    """
    df = pd.read_csv(file_path)  # Load the CSV file into a pandas DataFrame

    local_conn = False  # Track whether we need to close the connection later
    if conn is None:
        conn = connect_database()  # Create a new database connection if none is provided
        local_conn = True  # Mark that we created the connection locally

    cursor = conn.cursor()  # Create a cursor to execute SQL commands

    for _, row in df.iterrows():  # Loop through each row in the DataFrame
        cursor.execute("""
            INSERT OR IGNORE INTO cyber_incidents (incident_id, timestamp, severity, category, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row.get("incident_id"),   # Incident ID (must be unique)
            row.get("timestamp"),     # Timestamp of the incident
            row.get("severity"),      # Severity level (e.g., High, Medium, Low)
            row.get("category"),      # Type of incident (e.g., Phishing, Malware)
            row.get("status"),        # Current status (e.g., Open, In Progress)
            row.get("description"),   # Description of the incident
        ))

    if local_conn:
        conn.commit()  # Save changes to the database if we opened the connection
        conn.close()   # Close the connection to free resources

def get_all_incidents(conn=None):
    """
    Retrieve all incidents stored in the cyber_incidents table
    and return them as a pandas DataFrame.
    """
    if conn is None:
        conn = connect_database()  # Create a new database connection if none is provided

    cursor = conn.cursor()  # Create a cursor to execute SQL commands
    cursor.execute("SELECT * FROM cyber_incidents")  # Fetch all incident records
    rows = cursor.fetchall()  # Retrieve all rows from the query result

    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])  # Convert rows to DataFrame with column names
    return df  # Return the DataFrame containing all incidents

def insert_incident(conn, incident_id, timestamp, severity, category, status, description):
    """
    Insert a single new incident entry into the cyber_incidents table.
    Returns the ID of the newly inserted row.
    """
    cursor = conn.cursor()  # Create a cursor to execute SQL commands
    cursor.execute("""
        INSERT INTO cyber_incidents (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (incident_id, timestamp, severity, category, status, description))  # Insert the new incident into the table

    conn.commit()  # Save the changes to the database

    return cursor.lastrowid  # Return the ID of the inserted row for confirmation or logging
