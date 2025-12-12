import streamlit as st
from app.services.session_service import validate_session, delete_session
from app.data.db import connect_database
from app.data.incidents import get_all_incidents, insert_incident

# ---------------- SECURITY CHECK ----------------
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("role", "")
st.session_state.setdefault("token", "")

if not st.session_state["logged_in"] or not validate_session(st.session_state["token"]):
    st.error("Session expired or unauthorized.")
    st.session_state.clear()
    st.switch_page("main.py")
    st.stop()

if st.session_state["role"] not in ["admin", "cybersecurity"]:
    st.error("⛔ Access denied. You do not have permission to view this page.")
    st.stop()

# ---------------- HEADER + LOGOUT ----------------
st.write(f"👤 Logged in as **{st.session_state['username']}** (role: {st.session_state['role']})")

if st.button("🚪 Logout"):
    delete_session(st.session_state["token"])
    st.session_state.clear()
    st.success("✅ You have been logged out.")
    st.rerun()

# ---------------- PAGE CONTENT ----------------
st.title("🔐 Cybersecurity Dashboard")

conn = connect_database()
df = get_all_incidents(conn)

import pandas as pd
# ✅ Handle mixed timestamp formats and display only date + hour:minute
df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce").dt.strftime("%Y-%m-%d %H:%M")

st.dataframe(df, use_container_width=True)

# ---------------- ADD NEW INCIDENT FORM ----------------
st.subheader("➕ Add New Incident")
with st.form("new_incident"):
    incident_id = st.number_input("Incident ID", min_value=1, step=1)

    date = st.date_input("Date")
    hour = st.selectbox("Hour", [f"{h:02d}" for h in range(0, 24)], index=12)
    timestamp = f"{date} {hour}:00"

    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
    category = st.selectbox("Category", ["malware", "misconfiguration", "phishing", "unauthorized access", "ddos"])
    status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Incident")

    if submitted and incident_id:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
        if cursor.fetchone():
            st.error(f"⚠️ Incident ID {incident_id} already exists. Please choose another ID.")
        else:
            insert_incident(conn, incident_id, timestamp, severity, category, status, description)
            st.success("Incident added successfully!")
            st.rerun()

# ---------------- IMPORT CSV TO DATABASE ----------------
st.subheader("Import CSV to Database")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], accept_multiple_files=False)

if uploaded_file:
    try:
        import pandas as pd
        df_uploaded = pd.read_csv(uploaded_file)

        expected_columns = {"incident_id", "timestamp", "severity", "category", "status", "description"}

        if not expected_columns.issubset(df_uploaded.columns):
            st.error(f"Invalid CSV format. Required columns: {expected_columns}")
        else:
            inserted_count = 0
            for _, row in df_uploaded.iterrows():
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM cyber_incidents WHERE incident_id = ?", (int(row["incident_id"]),))
                    if cursor.fetchone():
                        st.warning(f"Row skipped: Incident ID {row['incident_id']} already exists.")
                        continue

                    insert_incident(
                        conn,
                        int(row["incident_id"]),
                        str(row["timestamp"]),
                        str(row["severity"]),
                        str(row["category"]),
                        str(row["status"]),
                        str(row["description"])
                    )
                    inserted_count += 1
                except Exception as e:
                    st.warning(f"Row skipped due to error: {e}")
            st.success(f"{inserted_count} incidents imported successfully.")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to read CSV file: {e}")

  # AI CHAT BOX

import streamlit as st
import google.generativeai as genai

# Configure Gemini with your API key stored securely in Streamlit secrets.toml
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize the Gemini model (fast/free version)
model = genai.GenerativeModel("models/gemini-2.5-flash")

st.subheader("Gemini Cybersecurity Assistant")

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages in the chat interface
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# Sidebar with controls
with st.sidebar:
    st.title("💬 Chat Controls")
    message_count = len(st.session_state.get("messages", []))
    st.metric("Messages", message_count)

    #  Clear Chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Input box for the user to type a new question
prompt = st.chat_input("Pose ta question...")

if prompt:
    # Save the user message into session state
    st.session_state.messages.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    try:
        # Send the full conversation history to Gemini for response generation
        response = model.generate_content(
            contents=st.session_state.messages,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,        # Controls creativity (higher = more creative)
                max_output_tokens=512   # Limits the length of the response
            )
        )

        # Extract the text reply from Gemini's response object
        reply = response.text

        # Display Gemini's reply in the chat interface
        with st.chat_message("assistant"):
            st.markdown(reply)

        # Save Gemini's reply into session state for future context
        st.session_state.messages.append({
            "role": "model",
            "parts": [{"text": reply}]
        })

        # Rerun the app to refresh the chat interface with the new message
        st.rerun()

    except Exception as e:
        # Display any error that occurs during the API call
        st.error(f"Erreur Gemini: {e}")

# Inject custom CSS for purple gradient background
# References:
# - Streamlit Docs – Colors and borders customization
# - YouTube – Custom Streamlit Background Image/Color Gradient through CSS
# - GitHub – streamlit-css-styling-demo
page_bg_css = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #4B0082, #8A2BE2, #DA70D6);
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.2);
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

import sqlite3

#  DELETE INCIDENT BY ID
st.subheader("Delete Incident by ID")

with st.form("delete_incident"):
    delete_id = st.number_input("Enter Incident ID to delete", min_value=1, step=1)
    confirm_delete = st.form_submit_button("Delete Incident")

    if confirm_delete:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM cyber_incidents WHERE incident_id = ? AND created_by = ?",
                (delete_id, st.session_state["username"])
            )
            if cursor.fetchone():
                cursor.execute(
                    "DELETE FROM cyber_incidents WHERE incident_id = ? AND created_by = ?",
                    (delete_id, st.session_state["username"])
                )
                conn.commit()
                st.success(f"Incident ID {delete_id} has been deleted.")
                st.rerun()
            else:
                st.error(" You can’t delete this incident.")
        except sqlite3.OperationalError:
            st.error(" You can’t delete this incident.")

conn.close()



