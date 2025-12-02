import pandas as pd
from app.data.db import connect_database

def migrate_datasets_from_csv(file_path="DATA/datasets_metadata.csv", conn=None):
    """
    Load datasets from a CSV file and insert them into the datasets_metadata table.
    Expected columns: dataset_id, name, description, rows, columns, size
    """
    local_conn = False
    if conn is None:
        conn = connect_database()
        local_conn = True

    with conn:  # garantit commit/rollback automatique
        cursor = conn.cursor()

        # 🔍 Vérification préalable : est-ce que la table contient déjà des données ?
        cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
        count = cursor.fetchone()[0]

        if count > 0:
            print("⚠️ Migration ignorée : datasets_metadata contient déjà des données.")
            return  # on sort de la fonction sans ré-importer

        # 👉 Si la table est vide, on charge le CSV et on insère
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO datasets_metadata (dataset_id, name, description, rows, columns, size)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row.get("dataset_id"),
                row.get("name"),
                row.get("description"),
                row.get("rows"),
                row.get("columns"),
                row.get("size"),
            ))

    if local_conn:
        conn.close()

def get_all_datasets(conn=None):
    if conn is None:
        conn = connect_database()

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM datasets_metadata")
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
    return df

def insert_dataset(conn, dataset_id, name, description):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata (dataset_id, name, description)
        VALUES (?, ?, ?)
    """, (dataset_id, name, description))
    conn.commit() 