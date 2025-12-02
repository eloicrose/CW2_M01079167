import streamlit as st
import pandas as pd
from app.data.db import connect_database
from app.data.tickets import get_all_tickets

# ---------------------------
# Role-based access control
# ---------------------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("Unauthorized")
    st.stop()
elif st.session_state["role"] not in ["analyst", "admin", "guest"]:
    st.error("Access denied. You do not have permission to view this page.")
    st.stop()

st.title("⚙️ IT Operations Dashboard")

# ---------------------------
# Load tickets
# ---------------------------
conn = connect_database()
df = get_all_tickets(conn)
conn.close()

st.subheader("📋 All Tickets")
st.dataframe(df, use_container_width=True)

# ---------------------------
# Ticket Status Distribution
# ---------------------------
st.subheader("📊 Ticket Status Distribution")
if "status" in df.columns:
    status_counts = df["status"].value_counts()
    st.bar_chart(status_counts)

# ---------------------------
# Ticket Priority Distribution
# ---------------------------
st.subheader("📊 Ticket Priority Distribution")
if "priority" in df.columns:
    priority_counts = df["priority"].value_counts()
    st.bar_chart(priority_counts)

# ---------------------------
# Average Resolution Time by Priority
# ---------------------------
st.subheader("⏱ Average Resolution Time by Priority")
if "priority" in df.columns and "resolution_time_hour" in df.columns:
    avg_resolution = df.groupby("priority")["resolution_time_hour"].mean()
    st.bar_chart(avg_resolution)

# ---------------------------
# Tickets Assigned per Employee
# ---------------------------
st.subheader("👤 Tickets Assigned per Employee")
if "assigned_to" in df.columns:
    assigned_counts = df["assigned_to"].value_counts()
    st.bar_chart(assigned_counts)
