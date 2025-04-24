from typing import List

from fastapi import APIRouter

from models.request_models import SessionRequest, SessionSummaryRequest
from models.response_models import SessionResponse, SessionSummaryResponse
from services.chat_service import get_session_summary as get_session_summary_service
from services.session_service import get_session_history as get_session_history_service
from utils.authentication import get_or_create_session

router = APIRouter()


@router.post("", response_model=SessionResponse)
def initiate_session(payload: SessionRequest):
    session = get_or_create_session(payload.persona, payload.session_id)
    return SessionResponse(session_id=session.session_id, persona=session.persona)


@router.get("/history", response_model=List[SessionResponse])
def get_session_history():
    session_history = get_session_history_service()
    return [SessionResponse(session_id=session.session_id, persona=session.persona) for session in session_history]


@router.get("/summary", response_model=SessionSummaryResponse)
def get_session_summary(payload: SessionSummaryRequest):
    summary = get_session_summary_service(payload.session_id)
    return SessionSummaryResponse(summary=summary)
