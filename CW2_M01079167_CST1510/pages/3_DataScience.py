import streamlit as st
from app.services.session_service import validate_session, delete_session
from app.data.db import connect_database
from app.data.datasets import get_all_datasets, insert_dataset

# ---------------- SECURITY CHECK ----------------
# Initialize session state variables with default values if not already set
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("role", "")
st.session_state.setdefault("token", "")

# Verify if the user is logged in and the session token is valid
if not st.session_state["logged_in"] or not validate_session(st.session_state["token"]):
    st.error("Session expired or unauthorized.")  # Show error message
    st.session_state.clear()  # Clear all session state values
    st.switch_page("main.py")  # Redirect to login/main page
    st.stop()  # Stop execution of the current page

# Role-based access control: only admin or datascience roles can view this page
if st.session_state["role"] not in ["admin", "datascience"]:
    st.error("Access denied. You do not have permission to view this page.")
    st.stop()

# ---------------- HEADER + LOGOUT ----------------
# Display logged-in user information
st.write(f"Logged in as **{st.session_state['username']}** (role: {st.session_state['role']})")

# Logout button: deletes session, clears state, and refreshes the app
if st.button("Logout"):
    delete_session(st.session_state["token"])  # Remove session from DB
    st.session_state.clear()  # Clear session state
    st.success("You have been logged out.")  # Confirmation message
    st.rerun()  # Reload the app to reset state

# ---------------- PAGE CONTENT ----------------
# Data Science dashboard title
st.title("Data Science Dashboard")

# Connect to database and display all datasets in a table
conn = connect_database()
df = get_all_datasets(conn)
st.dataframe(df, use_container_width=True)

# Section: Import CSV to populate the datasets table
st.subheader("Import CSV to Database")

# File uploader restricted to CSV files only
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], accept_multiple_files=False)

if uploaded_file:
    try:
        import pandas as pd

        # Read the uploaded CSV file into a DataFrame
        df_uploaded = pd.read_csv(uploaded_file)

        # Define the expected columns for the datasets table
        expected_columns = {"dataset_id", "name", "rows", "columns", "description"}

        # Validate that the uploaded CSV contains all required columns
        if not expected_columns.issubset(df_uploaded.columns):
            st.error(f"Invalid CSV format. Required columns: {expected_columns}")
        else:
            # Insert each row into the database using the secure insert_dataset function
            inserted_count = 0
            for _, row in df_uploaded.iterrows():
                try:
                    insert_dataset(
                        conn,
                        int(row["dataset_id"]),
                        str(row["name"]),
                        int(row["rows"]),
                        int(row["columns"]),
                        str(row["description"])
                    )
                    inserted_count += 1
                except Exception as e:
                    # Skip rows that cause errors during insertion
                    st.warning(f"Row skipped due to error: {e}")
            st.success(f"{inserted_count} datasets imported successfully.")
            st.rerun()
    except Exception as e:
        # Handle errors during CSV reading
        st.error(f"Failed to read CSV file: {e}")

# Visualize dataset size distribution using rows and columns
st.subheader("Dataset Size Distribution (Line Graph)")
if "rows" in df.columns and "columns" in df.columns:
    st.line_chart(df[["rows", "columns"]])

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
    background: rgba(0,0,0,0); /* transparent header */
}
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.2); /* semi-transparent sidebar */
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# Close DB connection at the end
conn.close()

