from fastapi import HTTPException
from api.db_utils import get_db_session
from api.db_models import UserSession

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
