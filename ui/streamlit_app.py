import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
API_URL = BACKEND_URL + st.secrets.get("API_PREFIX", "/api/v1")

st.title("Northeastern University (NU) Chatbot")

# Session
st.sidebar.header("Session")
persona = st.sidebar.selectbox("Persona", ["student", "staff"])
session_id = st.sidebar.text_input("Session ID", value="session-1")
if st.sidebar.button("Start Session"):
    res = requests.post(f"{API_URL}/session", json={"persona": persona, "session_id": session_id})
    if res.ok:
        st.sidebar.success("Session started!")
    else:
        st.sidebar.error(res.text)

# Past Sessions
st.sidebar.header("Past Sessions")
res = requests.get(f"{API_URL}/session/history")
if res.ok:
    session_history = res.json()
    session_list = []
    for session in session_history:
        session_list.append(session["session_id"] + " (" + session["persona"] + ")")

    selection = st.sidebar.pills("Select a past session:", session_list)
    if selection:
        selected_session = selection.split(" (")[0]
        res = requests.post(f"{API_URL}/session", json={"persona": persona, "session_id": selected_session})
        if res.ok:
            st.sidebar.success("Session loaded!")
            session_id = selected_session
        else:
            st.sidebar.error(res.text)
else:
    st.sidebar.text("(No past sessions available.)")

# Query
st.header("Ask a Question")
question_input = st.text_input("Your question here:")
send_button_event = st.button("Send")

# Chat history
st.header("Chat History")
chat_history_panel = st.empty()

res = requests.get(f"{API_URL}/chat/history", json={"session_id": session_id})
if res.ok:
    chat_history = res.json()
    chat_history_content = ""
    for record in chat_history:
        chat_history_content += "**You:** " + record.get("raw_query", "") + "\n\n"
        chat_history_content += "**Assistant:** " + record.get("answer", "") + " [Confidence: {}]".format(record.get("confidence", "N/A")) + "\n\n"
    chat_history_panel.markdown(chat_history_content)
else:
    chat_history_panel.write("(No chat history available.)")

if send_button_event:
    if question_input.strip():
        st.markdown("**You:** " + question_input)

        # Send message to API
        payload = {
            "query": question_input,
            "persona": persona,
            "session_id": session_id
        }
        res = requests.post(f"{API_URL}/chat", json=payload)
        if res.ok:
            data = res.json()
            bot_response = data.get("answer", "No response")
            st.markdown("**Assistant:** " + bot_response)
        else:
            st.error(res.text)