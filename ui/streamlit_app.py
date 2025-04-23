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

# Document upload
st.sidebar.header("Upload Document")
uploaded_file = st.sidebar.file_uploader("Choose file", type=["pdf", "docx", "txt"])
personas = st.sidebar.multiselect("Tag personas", ["student", "staff"], default=[persona])
if uploaded_file and st.sidebar.button("Upload"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    data = [("personas", p) for p in personas]
    res = requests.post(f"{API_URL}/document", files=files, data=data)
    if res.ok:
        st.sidebar.success("Uploaded!")
    else:
        st.sidebar.error(res.text)

# Query
st.header("Ask a Question")
query = st.text_input("Your question here")
if st.button("Send"):
    payload = {"query": query, "persona": persona, "session_id": session_id}
    res = requests.post(f"{API_URL}/chat", json=payload)
    if res.ok:
        data = res.json()
        st.subheader("Answer")
        st.write(data["answer"])
        st.write(f"Confidence: {data['confidence']:.2f}")
    else:
        st.error(res.text)
