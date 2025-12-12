import pandas as pd
from app.data.db import connect_database

def migrate_datasets_from_csv(file_path="DATA/datasets_metadata.csv", conn=None):
    """
    Load datasets from a CSV file and insert them into the datasets_metadata table.
    Expected columns: dataset_id, name, description, rows, columns, size
    """
    # Flag to know if we created a local connection (so we can close it later)
    local_conn = False
    if conn is None:
        # If no connection is passed, establish a new one
        conn = connect_database()
        local_conn = True

    # Using 'with conn' ensures automatic commit/rollback handling
    with conn:
        cursor = conn.cursor()

        #  Pre-check: verify if the table already contains data
        cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
        count = cursor.fetchone()[0]

        if count > 0:
            # If data already exists, skip migration to avoid duplicates
            print("⚠️ Migration ignored: datasets_metadata already contains data.")
            return  # Exit function without re-importing

        #  If the table is empty, load the CSV file and insert rows
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO datasets_metadata (dataset_id, name, description, rows, columns, size)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row.get("dataset_id"),   # Unique identifier of the dataset
                row.get("name"),         # Dataset name
                row.get("description"),  # Short description of the dataset
                row.get("rows"),         # Number of rows in the dataset
                row.get("columns"),      # Number of columns in the dataset
                row.get("size"),         # Size of the dataset (e.g., MB)
            ))

    # Close the connection if it was created locally
    if local_conn:
        conn.close()


def get_all_datasets(conn=None):
    """
    Retrieve all datasets stored in the datasets_metadata table
    and return them as a pandas DataFrame.
    """
    if conn is None:
        # Create a new connection if none is provided
        conn = connect_database()

    cursor = conn.cursor()
    # Select all rows from the metadata table
    cursor.execute("SELECT * FROM datasets_metadata")
    rows = cursor.fetchall()

    # Convert query results into a DataFrame with proper column names
    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df


def insert_dataset(conn, dataset_id, name, description):
    """
    Insert a new dataset entry into the datasets_metadata table.
    Only dataset_id, name, and description are provided here.
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata (dataset_id, name, description)
        VALUES (?, ?, ?)
    """, (dataset_id, name, description))

    # Commit the transaction to save changes permanently
    conn.commit()