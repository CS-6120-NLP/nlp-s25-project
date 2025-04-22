# api/db_models.py

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, nullable=False)
    persona = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    chat_summary = Column(Text, nullable=True)
    queries = relationship('QueryRecord', back_populates='session')


class QueryRecord(Base):
    __tablename__ = 'query_records'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('user_sessions.id'))
    raw_query = Column(String, nullable=False)
    clarified_query = Column(String)
    answer = Column(String)
    confidence = Column(String)
    timestamp = Column(DateTime, server_default=func.now())
    session = relationship('UserSession', back_populates='queries')


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    persona_tags = Column(JSON, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())


class UnpermittedQuery(Base):
    __tablename__ = 'unpermitted_queries'
    id = Column(Integer, primary_key=True)
    pattern = Column(String, nullable=False)


class PermittedQuery(Base):
    __tablename__ = 'permitted_queries'
    id = Column(Integer, primary_key=True)
    pattern = Column(String, nullable=False)
