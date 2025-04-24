from models.entities import ChatRecord
from utils.database import get_db_session


class ChatRepository:
    """Repository for chat-related database operations."""

    def __init__(self):
        self.db = get_db_session()

    def get_chat_history(self, session_id):
        """Retrieve chat records for a given session ID."""
        return self.db.query(ChatRecord).filter(ChatRecord.session_id == session_id).all()

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
