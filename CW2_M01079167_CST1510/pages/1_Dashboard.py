import streamlit as st
from app.services.session_service import validate_session, delete_session

# ---------------- SECURITY CHECK ----------------
# Initialize session state variables with default values if not already set
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("role", "")
st.session_state.setdefault("token", "")

# Verify if the user is logged in and the session token is valid
if not st.session_state["logged_in"] or not validate_session(st.session_state["token"]):
    st.error("Session expired or unauthorized.")   # Show error message
    st.session_state.clear()                       # Clear all session state values
    st.switch_page("main.py")                      # Redirect to login/main page
    st.stop()                                      # Stop execution of the current page

# Retrieve username and role from session state for display and access control
username = st.session_state["username"]
role = st.session_state["role"]

# ---------------- HEADER + LOGOUT ----------------
# Display logged-in user information
st.write(f"👤 Logged in as **{username}** (role: {role})")

# Logout button: deletes session, clears state, and refreshes the app
if st.button("🚪 Logout"):
    delete_session(st.session_state["token"])      # Remove session from DB
    st.session_state.clear()                       # Clear session state
    st.success("✅ You have been logged out.")      # Confirmation message
    st.rerun()                                     # Reload the app to reset state

# ---------------- DASHBOARD ----------------
# Main dashboard title and welcome message
st.title("📊 Intelligence Platform Dashboard")
st.success(f"Welcome {username} ({role})")

# Navigation links (only visible to admin users)
if role == "admin":
    st.page_link("pages/2_Cybersecurity.py", label="Cybersecurity")
    st.page_link("pages/3_DataScience.py", label="Data Science")
    st.page_link("pages/4_ITOperations.py", label="IT Operations")

# Inject custom CSS for purple gradient background
page_bg_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #4B0082, #8A2BE2, #DA70D6);
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

