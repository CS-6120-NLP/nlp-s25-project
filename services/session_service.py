from repositories.chat_repository import ChatRepository


def get_session_history():
    """Retrieve all user sessions."""
    repo = ChatRepository()
    return repo.get_session_history()