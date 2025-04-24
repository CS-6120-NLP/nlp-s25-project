from typing import List

from fastapi import APIRouter

from models.request_models import SessionRequest
from models.response_models import SessionResponse
from utils.authentication import get_or_create_session
from services.session_service import get_session_history as get_session_history_service

router = APIRouter()


@router.post("", response_model=SessionResponse)
def initiate_session(payload: SessionRequest):
    session = get_or_create_session(payload.persona, payload.session_id)
    return SessionResponse(session_id=session.session_id, persona=session.persona)


@router.get("/history", response_model=List[SessionResponse])
def get_session_history():
    session_history = get_session_history_service()
    return [SessionResponse(session_id=session.session_id, persona=session.persona) for session in session_history]
