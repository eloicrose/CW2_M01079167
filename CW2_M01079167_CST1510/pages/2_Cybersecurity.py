import streamlit as st
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# Role-based access control
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Unauthorized")
    st.stop()
elif st.session_state["role"] not in ["analyst", "admin", "guest"]:
    st.error("Access denied. You do not have permission to view this page.")
    st.stop()

st.title("🔐 Cybersecurity Dashboard")

conn = connect_database()
df = get_all_incidents(conn)
st.dataframe(df, use_container_width=True)

st.subheader("➕ Add New Incident")
with st.form("new_incident"):
    incident_id = st.number_input("Incident ID", min_value=1, step=1)
    timestamp = st.text_input("Timestamp (YYYY-MM-DD HH:MM)")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    category = st.text_input("Category")
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Incident")

    if submitted and incident_id and timestamp:
        insert_incident(conn, incident_id, timestamp, severity, category, status, description)
        st.success("Incident added successfully!")
        st.rerun()

conn.close()

