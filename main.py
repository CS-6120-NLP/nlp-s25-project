from fastapi import FastAPI

from api.chat_api import router as chat_router
from api.document_api import router as doc_router
from api.session_api import router as session_router
from config import API_PREFIX
from utils.db_utils import init_db

# Initialize database tables
init_db()

app = FastAPI(title="Northeastern University (NU) Chatbot")

app.include_router(session_router, prefix=API_PREFIX + "/session", tags=["session"])
app.include_router(chat_router, prefix=API_PREFIX + "/chat", tags=["query"])
app.include_router(doc_router, prefix=API_PREFIX + "/document", tags=["document"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
