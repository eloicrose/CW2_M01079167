import streamlit as st
from app.services.session_service import validate_session, delete_session
from app.data.db import connect_database
from app.data.tickets import get_all_tickets, insert_ticket
import plotly.express as px
import pandas as pd

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

if st.session_state["role"] not in ["admin", "itoperation"]:
    st.error("Access denied. You do not have permission to view this page.")
    st.stop()

# ---------------- HEADER + LOGOUT ----------------
st.write(f"Logged in as **{st.session_state['username']}** (role: {st.session_state['role']})")

if st.button("Logout"):
    delete_session(st.session_state["token"])
    st.session_state.clear()
    st.success("You have been logged out.")
    st.rerun()

# ---------------- PAGE CONTENT ----------------
st.title("IT Operations Dashboard")

conn = connect_database()
df = get_all_tickets(conn)

st.subheader("All Tickets")
st.dataframe(df, use_container_width=True)

# ---------------- CSV IMPORT ----------------
st.subheader("Import CSV to Database")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], accept_multiple_files=False)

if uploaded_file:
    try:
        df_uploaded = pd.read_csv(uploaded_file)

        # Expected columns for tickets table
        expected_columns = {"ticket_id", "title", "status", "priority", "assigned_to", "description"}
        if not expected_columns.issubset(df_uploaded.columns):
            st.error(f"Invalid CSV format. Required columns: {expected_columns}")
        else:
            inserted_count = 0
            for _, row in df_uploaded.iterrows():
                try:
                    insert_ticket(
                        conn,
                        int(row["ticket_id"]),
                        str(row["title"]),
                        str(row["status"]),
                        str(row["priority"]),
                        str(row["assigned_to"]),
                        str(row["description"])
                    )
                    inserted_count += 1
                except Exception as e:
                    st.warning(f"Row skipped due to error: {e}")
            st.success(f"{inserted_count} tickets imported successfully.")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to read CSV file: {e}")

# ---------------- VISUALIZATIONS ----------------
st.subheader("Ticket Status Distribution (Line Graph)")
if "status" in df.columns:
    status_counts = df["status"].value_counts()
    st.line_chart(status_counts)

st.subheader("Ticket Priority Distribution (Line Graph)")
if "priority" in df.columns:
    priority_counts = df["priority"].value_counts()
    st.line_chart(priority_counts)

st.subheader("Tickets Assigned per Employee")
if "assigned_to" in df.columns:
    assigned_counts = df["assigned_to"].value_counts()
    fig = px.pie(
        names=assigned_counts.index,
        values=assigned_counts.values,
        title="Ticket Distribution by Employee"
    )
    st.plotly_chart(fig, use_container_width=True)
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

# CUSTOM CSS
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

conn.close()

