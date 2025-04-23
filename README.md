# Northeastern University (NU) Chatbot

This service provides a RAG-based Q&A for **Northeastern University (NU)**, with:
- Persona-based document filtering (`student` vs `staff`)
- Query enrichment & permission checks
- Conversation memory per session
- Incremental Chroma DB persistence
- Simple Streamlit UI

## Run Locally
### Without Docker

Set up environmental variables:
```python
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.abspath(".env"))
```

Backend:
```bash
uvicorn main:app --reload
```

Frontend:
```bash
cd ui
streamlit run streamlit_app.py
```
