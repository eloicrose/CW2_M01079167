import streamlit as st
from app.data.db import connect_database
from app.data.datasets import get_all_datasets

# Role-based access control
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("Unauthorized")
    st.stop()
elif st.session_state["role"] not in ["analyst", "admin", "guest"]:
    st.error("Access denied. You do not have permission to view this page.")
    st.stop()

st.title("📊 Data Science Dashboard")

conn = connect_database()
df = get_all_datasets(conn)
st.dataframe(df, use_container_width=True)

st.subheader("📈 Dataset Size Distribution")
if "rows" in df.columns and "columns" in df.columns:
    st.bar_chart(df[["rows", "columns"]])

conn.close()

