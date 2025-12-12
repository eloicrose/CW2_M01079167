from app.data.db import connect_database
import bcrypt
import csv
from app.services.session_service import create_session

# ---------------------------
# GET USER BY USERNAME
# ---------------------------
def get_user_by_username(username):
    """
    Retrieve a user from the database by their username.
    Returns a tuple (username, password_hash, role) or None if not found.
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
    Register a new user in the database.
    Returns (success, message).
    """
    try:
        with connect_database() as conn:
            cursor = conn.cursor()

            # Check if the username already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                return False, "⚠️ Username already exists."

            # Insert the new user record
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            conn.commit()
            return True, "✅ User registered successfully."
    except Exception as e:
        # Handle unexpected errors gracefully
        return False, f"❌ Error registering user: {e}"


# ---------------------------
# LOGIN USER
# ---------------------------
def login_user(username, password):
    """
    Verify credentials and create a session if successful.
    Returns (success, message, token, role).
    """
    user = get_user_by_username(username)
    if not user:
        return False, "❌ User not found.", None, None

    # Properly unpack the tuple returned from DB
    username_db, stored_hash, role = user

    # Verify the password against the stored hash
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        # Create a session and return the token
        token = create_session(username_db)
        return True, " Login successful!", token, role

    return False, " Incorrect password.", None, None


# ---------------------------
# CREATE DEFAULT ADMIN
# ---------------------------
def create_default_admin():
    """
    Create a default admin account if it does not already exist.
    """
    username = "admin"
    password = "admin123"
    role = "admin"

    # Hash the default password securely
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with connect_database() as conn:
        cursor = conn.cursor()

        # Check if the admin account already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        count = cursor.fetchone()[0]

        if count == 0:
            # Insert the default admin account
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            conn.commit()
            print("✅ Admin created successfully.")
        else:
            print("⚠️ Admin already exists, no insertion performed.")


# ---------------------------
# MIGRATE USERS FROM FILE
# ---------------------------
def migrate_users_from_file(file_path="DATA/users.csv"):
    """
    Migrate users from a CSV file into the users table.
    Expected CSV format: username,password,role
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

                    # Hash the password before storing
                    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

                    # Check if the user already exists
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                    if cursor.fetchone()[0] == 0:
                        # Insert the new user record
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, role)
                            VALUES (?, ?, ?)
                        """, (username, password_hash, role))
                conn.commit()
        print("✅ User migration completed.")
    except FileNotFoundError:
        print("⚠️ users.csv file not found, migration skipped.")
    except Exception as e:
        print(f"❌ Error during user migration: {e}")
