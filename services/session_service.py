# services/session_service.py
from clients.llm_client import generate_updated_summary
from repositories.session_repository import SessionRepository

def get_session_history():
    """Retrieve all user sessions."""
    repo = SessionRepository()
    return repo.get_session_history()


def get_session_summary(session_id):
    """Retrieve chat summary from the database."""
    repo = SessionRepository()
    summary = repo.get_session_summary(session_id)

    if summary is None:
        summary = ""
        # Imported here to avoid circular import
        from services.chat_service import get_chat_history

        # Retrieve chat history
        chat_history = [{"raw_query": chat_record.raw_query, "clarified_query": chat_record.clarified_query,
                         "answer": chat_record.answer} for chat_record in get_chat_history(session_id)]

        for record in chat_history:
            summary += f"- User: {record['raw_query']}\n- AI: {record['answer']}\n"

    return summary


def update_session_summary(session_id, current_chat_summary, latest_chat_record):
    """Update the session summary with the latest chat record."""
    repo = SessionRepository()
    updated_summary = generate_updated_summary(current_chat_summary, latest_chat_record)
    repo.update_session_summary(session_id, updated_summary)