import streamlit as st
from app.services.session_service import validate_session, delete_session

# ---------------- SECURITY CHECK ----------------
if "token" not in st.session_state or not validate_session(st.session_state["token"]):
    st.error("Session expired or unauthorized.")
    st.session_state.clear()
    st.switch_page("main.py")
    st.stop()

username = st.session_state["username"]
role = st.session_state["role"]

st.title("📊 Intelligence Platform Dashboard")
st.success(f"Welcome {username} ({role})")


# ---------------- NAVIGATION (RBAC) ----------------
if role == "admin":
    st.page_link("pages/2_Cybersecurity.py", label="Cybersecurity")
    st.page_link("pages/3_DataScience.py", label="Data Science")
    st.page_link("pages/4_ITOperations.py", label="IT Operations")

elif role == "analyst":
    st.page_link("pages/2_Cybersecurity.py", label="Cybersecurity")
