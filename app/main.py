from fastapi import FastAPI
from api.db_utils import init_db
from app.routers.query import router as query_router
from app.routers.session import router as session_router
from app.routers.documents import router as docs_router

# Initialize database tables
init_db()

app = FastAPI(title="Northeastern University (NU) Chatbot")

app.include_router(session_router, prefix="/session", tags=["session"])
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(docs_router, prefix="/documents", tags=["documents"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
