import streamlit as st
import requests

API_URL = "http://localhost:8000"

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

# Document upload
st.sidebar.header("Upload Document")
uploaded_file = st.sidebar.file_uploader("Choose file", type=["pdf","docx","txt"])
personas = st.sidebar.multiselect("Tag personas", ["student","staff"], default=[persona])
if uploaded_file and st.sidebar.button("Upload"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    data = [("personas", p) for p in personas]
    res = requests.post(f"{API_URL}/documents", files=files, data=data)
    if res.ok:
        st.sidebar.success("Uploaded!")
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

if st.session_state["chat_history"]:
    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Assistant:** {message['content']}")
else:
    st.write("(No chat history yet)")

if response:
    if query.strip():
        # Add user message to chat history
        st.session_state["chat_history"].append({"role": "user", "content": query})
        st.write("**You:**", query)

        # Send message to API
        payload = {
            "query": query,
            "persona": persona,
            "session_id": session_id
        }
        res = requests.post(f"{API_URL}/query", json=payload)
        if res.ok:
            data = res.json()
            bot_response = data.get("answer", "No response")
            st.session_state["chat_history"].append({"role": "assistant", "content": bot_response})
            st.write(bot_response)
            st.write(f"Confidence: {data['confidence']:.2f}")
        else:
            st.error(res.text)