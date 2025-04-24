import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "")
API_URL = BACKEND_URL + st.secrets.get("API_PREFIX", "")

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
        print(selection)
        selected_session = selection.split(" (")[0]
        res = requests.post(f"{API_URL}/session", json={"persona": persona, "session_id": selected_session})
        if res.ok:
            st.sidebar.success("Session loaded!")
            session_id = selected_session
        else:
            st.sidebar.error(res.text)
else:
    st.sidebar.text("(No past sessions available.)")

# Chat summary
st.sidebar.header("Chat Summary")
res = requests.get(f"{API_URL}/session/summary", json={"session_id": session_id})
if res.ok:
    chat_summary = res.json()
    st.sidebar.markdown(chat_summary.get("summary", "N/A"))
else:
    st.sidebar.text("(No summary available.)")

# Chat history
chat_history_panel = st.empty()

res = requests.get(f"{API_URL}/chat/history", json={"session_id": session_id})
if res.ok:
    chat_history = res.json()
    chat_history_content = ""
    for record in chat_history:
        chat_history_content += "**You:** " + record.get("raw_query", "") + "\n\n"
        chat_history_content += "**Assistant:** " + record.get("answer", "") + "\n\n"
    chat_history_panel.markdown(chat_history_content)
else:
    chat_history_panel.write("(No chat history available.)")

# Generate response
def generate_response(user_input):
    st.markdown(f"**You:** {user_input}")
    payload = {
        "query": user_input,
        "persona": persona,
        "session_id": session_id
    }
    res = requests.post(f"{API_URL}/chat", json=payload)
    if res.ok:
        answer = res.json().get("answer", "No response")
        st.markdown(f"**Assistant:** {answer}")
    else:
        st.error(res.text)

# Query
question_input = st.chat_input("Ask a Question")
if question_input:
    generate_response(question_input)