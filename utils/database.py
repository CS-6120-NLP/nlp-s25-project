import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from models.entities import Base, ChatHistory, ChatRecord

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()


def save_chat_message(session_id, role, content):
    db = get_db_session()
    message = ChatHistory(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()


def get_chat_history(session_id):
    db = get_db_session()
    return db.query(ChatHistory).filter_by(session_id=session_id).order_by(ChatHistory.timestamp).all()
