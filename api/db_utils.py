from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.db_models import Base, ChatHistory, QueryRecord
from config.default_settings import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db_session():
    return SessionLocal()


def save_query_record(session_id, raw_query, clarified_query, answer, confidence):
    db = get_db_session()
    query_record = QueryRecord(
        session_id=session_id,
        raw_query=raw_query,
        clarified_query=clarified_query,
        answer=answer,
        confidence=confidence
    )
    db.add(query_record)
    db.commit()


def save_chat_message(session_id, role, content):
    db = get_db_session()
    message = ChatHistory(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()


def get_chat_history(session_id):
    db = get_db_session()
    return db.query(ChatHistory).filter_by(session_id=session_id).order_by(ChatHistory.timestamp).all()
