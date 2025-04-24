from repositories.session_repository import SessionRepository


def get_session_history():
    """Retrieve all user sessions."""
    repo = SessionRepository()
    return repo.get_session_history()


def get_session_summary(session_id):
    """Retrieve chat summary from the database."""
    repo = SessionRepository()
    return repo.get_session_summary(session_id)