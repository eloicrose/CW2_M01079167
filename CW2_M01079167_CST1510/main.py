import streamlit as st
import bcrypt

from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import (
    register_user,
    login_user,
    migrate_users_from_file,
    create_default_admin,
)
from app.services.session_service import validate_session, delete_session

# CSV migrations
from app.data.incidents import migrate_incidents_from_csv
from app.data.datasets import migrate_datasets_from_csv
from app.data.tickets import migrate_tickets_from_csv


# ---------------------------
# AUTHENTICATION SYSTEM
# ---------------------------
def login_page():
    """
    Login page UI and logic.
    - Prompts for username and password.
    - Validates credentials using login_user().
    - If successful, stores session state and redirects user based on role.
    """
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("Username and password are required.")
        else:
            success, msg, token, role = login_user(username, password)
            if success:
                st.success(f"{msg} Welcome, {username}! Your role is: {role}")
                # Save login state in session
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["role"] = role
                st.session_state["token"] = token

                #  Redirect user to correct dashboard based on role
                if role == "admin":
                    st.switch_page("pages/1_Dashboard.py")
                elif role == "cybersecurity":
                    st.switch_page("pages/2_Cybersecurity.py")
                elif role == "datascience":
                    st.switch_page("pages/3_DataScience.py")
                elif role == "itoperation":
                    st.switch_page("pages/4_ITOperations.py")
                else:
                    st.error("⛔ Invalid role.")
            else:
                st.error(msg)


def register_page():
    """
    Registration page UI and logic.
    - Prompts for new username, password, and role.
    - Hashes password securely with bcrypt.
    - Calls register_user() to insert into DB.
    """
    st.title("📝 Register")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")

    #  Only allowed roles
    role = st.selectbox("Role", ["admin", "cybersecurity", "datascience", "itoperation"])

    if st.button("Register"):
        if not username or not password:
            st.error("Username and password are required.")
        else:
            # Securely hash password before storing
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            success, msg = register_user(username, password_hash, role)
            if success:
                st.success(msg)
                st.info("Go to Login tab to sign in.")
            else:
                st.error(msg)


# ---------------------------
# MAIN APPLICATION LOGIC
# ---------------------------
def main():
    """
    Main entry point of the app.
    - Initializes database and performs one-time migrations.
    - Handles authentication (login/register).
    - Validates session tokens.
    - Provides logout functionality.
    - Redirects users to appropriate dashboard based on role.
    """
    st.set_page_config(page_title="Intelligence Platform", layout="wide")

    #  Welcome message at the top
    st.markdown("##  Welcome to Multi-Domain Intelligence Platform")

    # Initialize DB and perform one-time migrations
    if "db_initialized" not in st.session_state:
        conn = connect_database()
        create_all_tables(conn)

        # Create default admin and migrate initial data
        create_default_admin()
        migrate_users_from_file()
        migrate_incidents_from_csv("DATA/cyber_incidents.csv", conn)
        migrate_datasets_from_csv("DATA/datasets_metadata.csv", conn)
        migrate_tickets_from_csv("DATA/it_tickets.csv", conn)

        conn.commit()
        conn.close()

        st.session_state["db_initialized"] = True
        st.success("✅ Database initialized successfully.")

    # Auth state initialization
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["token"] = ""

    # Require login if not authenticated
    if not st.session_state["logged_in"]:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_page()
        with tab2:
            register_page()
        return

    # Validate token
    if not validate_session(st.session_state["token"]):
        st.error("Session expired. Please login again.")
        st.session_state.clear()
        st.stop()

    # ✅ Logout button always visible
    st.write(f"👤 Logged in as **{st.session_state['username']}** (role: {st.session_state['role']})")
    if st.button("🚪 Logout"):
        delete_session(st.session_state["token"])   # Delete session from DB
        st.session_state.clear()                    # Clear session state
        st.success("✅ You have been logged out.")   # Confirmation message
        st.rerun()                                  # Reload app

    # ✅ Redirect according to role
    role = st.session_state.get("role", "")
    if role == "admin":
        st.switch_page("pages/1_Dashboard.py")
    elif role == "cybersecurity":
        st.switch_page("pages/2_Cybersecurity.py")
    elif role == "datascience":
        st.switch_page("pages/3_DataScience.py")
    elif role == "itoperation":
        st.switch_page("pages/4_ITOperations.py")
    else:
        st.error("⛔ Invalid role.")


# Inject custom CSS for gradient background
page_bg_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, red, blue, purple);
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0); /* transparent header */
}
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.2); /* semi-transparent sidebar */
}
</style>
"""

st.markdown(page_bg_css, unsafe_allow_html=True)


if __name__ == "__main__":
    main()