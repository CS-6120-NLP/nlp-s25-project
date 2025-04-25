import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "")
API_URL = BACKEND_URL + st.secrets.get("API_PREFIX", "")

# Initialize session state variables
if "processing" not in st.session_state:
    st.session_state.processing = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_history" not in st.session_state:
    st.session_state.session_history = []
if "chat_summary" not in st.session_state:
    st.session_state.chat_summary = "N/A"
if "persona" not in st.session_state:
    st.session_state.persona = "student"
if "session_id" not in st.session_state:
    st.session_state.session_id = "session-1"


# Load data functions
def load_session_history():
    res = requests.get(f"{API_URL}/session/history")
    if res.ok:
        st.session_state.session_history = res.json()
    else:
        st.session_state.session_history = []


def load_chat_history():
    res = requests.get(f"{API_URL}/chat/history", json={"session_id": st.session_state.session_id})
    if res.ok:
        st.session_state.chat_history = res.json()
    else:
        st.session_state.chat_history = []


def load_chat_summary():
    res = requests.get(f"{API_URL}/session/summary", json={"session_id": st.session_state.session_id})
    if res.ok:
        chat_summary = res.json()
        st.session_state.chat_summary = chat_summary.get("summary", "N/A")
    else:
        st.session_state.chat_summary = "N/A"


# Initial data load
if "initialized" not in st.session_state:
    load_session_history()
    load_chat_history()
    load_chat_summary()
    st.session_state.initialized = True

st.title("Northeastern University (NU) Chatbot")

# Session
st.sidebar.header("Session")
persona = st.sidebar.selectbox("Persona", ["student", "staff"],
                               index=["student", "staff"].index(st.session_state.persona))
session_id = st.sidebar.text_input("Session ID", value=st.session_state.session_id)

# Update session state
st.session_state.persona = persona
st.session_state.session_id = session_id


def start_session():
    res = requests.post(f"{API_URL}/session", json={"persona": persona, "session_id": session_id})
    if res.ok:
        st.sidebar.success("Session started!")
        # Refresh data for new session
        load_chat_history()
        load_chat_summary()
    else:
        st.sidebar.error(res.text)


if st.sidebar.button("Start Session"):
    start_session()

# Past Sessions
st.sidebar.header("Past Sessions")
col1, col2 = st.sidebar.columns([4, 1])
with col2:
    if st.button("🔄", key="refresh_sessions"):
        load_session_history()

if st.session_state.session_history:
    session_list = [f"{session['session_id']} ({session['persona']})" for session in st.session_state.session_history]
    selection = st.sidebar.pills("Select a past session:", session_list)
    if selection:
        selected_session = selection.split(" (")[0]
        res = requests.post(f"{API_URL}/session", json={"persona": persona, "session_id": selected_session})
        if res.ok:
            st.session_state.session_id = selected_session
            st.sidebar.success("Session loaded!")
            load_chat_history()
            load_chat_summary()
        else:
            st.sidebar.error(res.text)
else:
    st.sidebar.text("(No past sessions available.)")

# Chat summary
st.sidebar.header("Chat Summary")
col1, col2 = st.sidebar.columns([4, 1])
with col2:
    if st.button("🔄", key="refresh_summary"):
        load_chat_summary()
st.sidebar.markdown(st.session_state.chat_summary)

# Chat history
chat_history_container = st.container()
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🔄", key="refresh_chat"):
        load_chat_history()

# Display chat history from session state
with chat_history_container:
    chat_history_content = ""
    for record in st.session_state.chat_history:
        chat_history_content += f"**You:** {record.get('raw_query', '')}\n\n"
        chat_history_content += f"**Assistant:** {record.get('answer', '')}\n\n"
    st.markdown(chat_history_content)


# Handle user input
def handle_user_input():
    user_input = st.session_state.user_question
    if user_input:
        st.session_state.processing = True
        st.session_state.current_question = user_input
        st.rerun()


# Process the question if we're in processing state
if st.session_state.processing and "current_question" in st.session_state:
    user_input = st.session_state.current_question

    # Display user message
    st.markdown(f"**You:** {user_input}")

    # Send request to backend
    with st.spinner("Generating response..."):
        payload = {
            "query": user_input,
            "persona": st.session_state.persona,
            "session_id": st.session_state.session_id
        }
        res = requests.post(f"{API_URL}/chat", json=payload)

        if res.ok:
            answer = res.json().get("answer", "No response")
            st.markdown(f"**Assistant:** {answer}")
        else:
            st.error(res.text)

    # Update chat history
    load_chat_history()
    load_chat_summary()

    # Reset processing state
    st.session_state.processing = False
    del st.session_state.current_question

# Query input
st.chat_input(
    "Ask a Question",
    key="user_question",
    on_submit=handle_user_input,
    disabled=st.session_state.processing
)
