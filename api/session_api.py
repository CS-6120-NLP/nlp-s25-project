from fastapi import APIRouter

from models.request_models import SessionRequest
from models.response_models import SessionResponse
from utils.auth_utils import get_or_create_session

router = APIRouter()


@router.post("", response_model=SessionResponse)
def session_endpoint(payload: SessionRequest):
    session = get_or_create_session(payload.persona, payload.session_id)
    return SessionResponse(session_id=session.session_id, persona=session.persona)
