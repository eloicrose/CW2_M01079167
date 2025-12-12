import streamlit as st
from google import genai
from google.genai import types

# Initialize Gemini client using API key stored securely in Streamlit secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Configure the Streamlit page layout and appearance
st.set_page_config(
    page_title="Multi-Domain AI Assistant (Gemini)",
    page_icon="🤖",
    layout="wide"
)

# Main page title
st.title("🤖 Multi-Domain AI Assistant (Gemini API)")
st.caption("Cybersecurity • Data Science • IT Operations")


# -----------------------------------------------------
# INITIALIZE SESSION STATE (Stores chat history)
# -----------------------------------------------------
# If messages list does not exist yet, create it
if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------------------------------
# SIDEBAR SETTINGS (Model controls + Domain selection)
# -----------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    # Allow user to choose what type of expert the AI should be
    domain = st.selectbox(
        "Choose AI Domain",
        ["Cybersecurity", "Data Science", "IT Operations"]
    )

    # Domain-specific system instructions to guide Gemini's behavior
    SYSTEM_PROMPTS = {
        "Cybersecurity": "You are a cybersecurity expert. Analyze threats, incidents and provide expert guidance.",
        "Data Science": "You are a data science expert. Help with statistics, ML, visualization and analysis.",
        "IT Operations": "You are an IT Operations expert. Help with troubleshooting, optimization and tickets."
    }

    # Button to clear all chat messages
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# -----------------------------------------------------
# DISPLAY CHAT HISTORY (Shows all previous messages)
# -----------------------------------------------------
for msg in st.session_state.messages:
    # Convert Google's "model" role into Streamlit's "assistant"
    role = "assistant" if msg["role"] == "model" else "user"

    # Display message in the chat UI
    with st.chat_message(role):
        st.markdown(msg["parts"][0]["text"])


# -----------------------------------------------------
# USER INPUT (Where user types a message)
# -----------------------------------------------------
prompt = st.chat_input("Ask something...")

if prompt:

    # Immediately show user's message on screen
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save the user message to session state (conversation history)
    st.session_state.messages.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })


    # -----------------------------------------------------
    # GEMINI STREAMING RESPONSE (Word-by-word generation)
    # -----------------------------------------------------
    # Send conversation context + system instruction + user message
    response = client.models.generate_content_stream(
        model="gemini-3-pro-preview",
        config=types.GenerateContentConfig(
            # Tells the AI what "expert role" it should follow
            system_instruction=SYSTEM_PROMPTS[domain]
        ),
        contents=st.session_state.messages
    )

    # Prepare to display the streaming answer
    with st.chat_message("assistant"):
        container = st.empty()      # Placeholder that updates live
        full_reply = ""             # Stores streaming output

        # Loop through each streamed chunk of text
        for chunk in response:
            full_reply += chunk.text            # Add new text
            container.markdown(full_reply + "▌")  # Display with a typing cursor

        # Replace final output (remove the cursor)
        container.markdown(full_reply)


    # -----------------------------------------------------
    # SAVE ASSISTANT MESSAGE TO HISTORY
    # -----------------------------------------------------
    st.session_state.messages.append({
        "role": "model",
        "parts": [{"text": full_reply}]
    })

    # Refresh the page to load new chat state
    st.rerun()
