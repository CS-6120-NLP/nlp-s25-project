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

# Query
st.header("Ask a Question")
query = st.text_input("Your question here:")
response = st.button("Send")

# Chat history
st.header("Chat History")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

placeholder = st.empty()
if st.session_state["chat_history"]:
    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Assistant:** {message['content']}")
else:
    placeholder.text("(No chat history yet.)")

if response:
    if query.strip():
        # Clear the placeholder
        placeholder.empty()

        # Add user message to chat history
        st.session_state["chat_history"].append({"role": "user", "content": query})
        st.write("**You:**", query)

        # Send message to API
        payload = {
            "query": query,
            "persona": persona,
            "session_id": session_id
        }
        res = requests.post(f"{API_URL}/chat", json=payload)
        if res.ok:
            data = res.json()
            bot_response = data.get("answer", "No response")
            st.session_state["chat_history"].append({"role": "assistant", "content": bot_response})
            st.markdown(f"**Assistant:** {bot_response} [Confidence: {data.get('confidence', 'N/A')}]")
        else:
            st.error(res.text)
