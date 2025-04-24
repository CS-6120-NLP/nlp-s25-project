from models.entities import UserSession
from utils.database import get_db_session


class SessionRepository:
    """Repository for session-related database operations."""

    def __init__(self):
        self.db = get_db_session()

    def get_session_summary(self, session_id):
        """Retrieve the latest chat summary for a given session ID."""
        session = self.db.query(UserSession).filter_by(session_id=session_id).first()
        if not session:
            print("Session not found:", session_id)
        try:
            return session.summary
        except AttributeError:
            print("Chat summary not found for session:", session_id)
            return None

    def save_session_summary(self, session_id, summary):
        """Save a chat summary to the database."""
        session = self.db.query(UserSession).filter_by(session_id=session_id).first()
        if not session:
            print("Session not found:", session_id)
            return None
        session.summary = summary
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_history(self):
        """Retrieve all user sessions."""
        return self.db.query(UserSession).order_by(UserSession.created_at.desc()).all()

    def update_session_summary(self, session_id, updated_summary):
        self.save_session_summary(
            session_id=session_id,
            summary=updated_summary
        )
