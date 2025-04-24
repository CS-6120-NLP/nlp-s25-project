from models.entities import ChatRecord, UserSession
from utils.database import get_db_session


class ChatRepository:
    """Repository for chat-related database operations."""

    def __init__(self):
        self.db = get_db_session()

    def get_chat_history(self, session_id):
        """Retrieve chat records for a given session ID."""
        return self.db.query(ChatRecord).filter(ChatRecord.session_id == session_id).order_by(ChatRecord.created_at.asc()).all()

    def get_chat_summary(self, session_id):
        """Retrieve the latest chat summary for a given session ID."""
        session = self.db.query(UserSession).filter_by(session_id=session_id).first()
        if not session:
            print("Session not found:", session_id)
        return session.chat_summary

    def save_chat_record(self, session_id, raw_query, clarified_query, answer, confidence):
        """Save a chat record to the database."""
        record = ChatRecord(
            session_id=session_id,
            raw_query=raw_query,
            clarified_query=clarified_query,
            answer=answer,
            confidence=confidence
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def save_chat_summary(self, session_id, chat_summary):
        """Save a chat summary to the database."""
        session = self.db.query(UserSession).filter_by(session_id=session_id).first()
        if not session:
            print("Session not found:", session_id)
            return None
        session.chat_summary = chat_summary
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_history(self):
        """Retrieve all user sessions."""
        return self.db.query(UserSession).order_by(UserSession.created_at.desc()).all()