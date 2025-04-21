import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.default_settings import DATABASE_URL
from api.db_models import Base

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()
