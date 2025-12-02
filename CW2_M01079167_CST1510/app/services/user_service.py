from app.data.db import connect_database
import bcrypt
import csv
from app.services.session_service import create_session

# ---------------------------
# GET USER BY USERNAME
# ---------------------------
def get_user_by_username(username):
    """
    Récupère un utilisateur depuis la base par son username.
    Retourne un tuple (username, password_hash, role) ou None si absent.
    """
    with connect_database() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        return cursor.fetchone()


# ---------------------------
# REGISTER USER
# ---------------------------
def register_user(username, password_hash, role):
    """
    Enregistre un nouvel utilisateur dans la base.
    Retourne (success, message).
    """
    try:
        with connect_database() as conn:
            cursor = conn.cursor()

            # Vérifier si l'utilisateur existe déjà
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                return False, "⚠️ Username already exists."

            # Insérer le nouvel utilisateur
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            conn.commit()
            return True, "✅ User registered successfully."
    except Exception as e:
        return False, f"❌ Error registering user: {e}"


# ---------------------------
# LOGIN USER
# ---------------------------
def login_user(username, password):
    """
    Vérifie les identifiants et crée une session si succès.
    Retourne (success, message, token, role)
    """
    user = get_user_by_username(username)
    if not user:
        return False, "❌ User not found.", None, None

    # Déconstruction correcte du tuple
    username_db, stored_hash, role = user

    # Vérification du mot de passe
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        token = create_session(username_db)
        return True, "✅ Login successful!", token, role

    return False, "❌ Incorrect password.", None, None


# ---------------------------
# CREATE DEFAULT ADMIN
# ---------------------------
def create_default_admin():
    """
    Crée un compte admin par défaut si absent.
    """
    username = "admin"
    password = "admin123"
    role = "admin"

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with connect_database() as conn:
        cursor = conn.cursor()

        # Vérification préalable
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            conn.commit()
            print("✅ Admin créé avec succès.")
        else:
            print("⚠️ Admin déjà présent, aucune insertion faite.")


# ---------------------------
# MIGRATE USERS FROM FILE
# ---------------------------
def migrate_users_from_file(file_path="DATA/users.csv"):
    """
    Migre les utilisateurs depuis un fichier CSV vers la table users.
    CSV attendu : username,password,role
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            with connect_database() as conn:
                cursor = conn.cursor()
                for row in reader:
                    username = row["username"]
                    password = row["password"]
                    role = row["role"]

                    # Hash du mot de passe
                    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

                    # Vérifier si l'utilisateur existe déjà
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, role)
                            VALUES (?, ?, ?)
                        """, (username, password_hash, role))
                conn.commit()
        print("✅ Migration des utilisateurs terminée.")
    except FileNotFoundError:
        print("⚠️ Fichier users.csv introuvable, migration ignorée.")
    except Exception as e:
        print(f"❌ Erreur lors de la migration des utilisateurs : {e}")
