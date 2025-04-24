# services/entities.py
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False)
    persona = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    chats = relationship('ChatRecord', back_populates='session')


class ChatRecord(Base):
    __tablename__ = "chat_records"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("user_sessions.id"))
    raw_query = Column(String)
    clarified_query = Column(String)
    answer = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    session = relationship('UserSession', back_populates='chats')


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    persona_tags = Column(JSON, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
