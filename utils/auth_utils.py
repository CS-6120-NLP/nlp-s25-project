from fastapi import HTTPException

from models.entities import UserSession
from utils.db_utils import get_db_session


def get_or_create_session(persona: str, session_id: str):
    db = get_db_session()
    session = db.query(UserSession).filter_by(session_id=session_id).first()
    if session and session.persona != persona:
        raise HTTPException(status_code=403, detail="Persona mismatch.")
    if not session:
        session = UserSession(session_id=session_id, persona=persona)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session
