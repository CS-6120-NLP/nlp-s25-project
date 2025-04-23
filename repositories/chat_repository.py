from models.entities import ChatRecord
from utils.database import get_db_session


class ChatRepository:
    """Repository for chat-related database operations."""

    def __init__(self):
        self.db = get_db_session()

    def save_chat_record(self, session_id: int, raw_query: str, clarified_query: str,
                         answer: str, confidence: float) -> ChatRecord:
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
