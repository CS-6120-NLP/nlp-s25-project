# Northeastern University (NU) Chatbot

This service provides a RAG-based Q&A for **Northeastern University (NU)**, with:

- Persona-based document filtering (`student` vs `staff`)
- Query enrichment & permission checks
- Conversation memory per session
- Incremental Chroma DB persistence
- Simple Streamlit UI

Backend:

- `uvicorn main:app --reload`

Frontend:

- `cd ui`
- `streamlit run streamlit_app.py`
