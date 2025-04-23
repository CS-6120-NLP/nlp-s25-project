from fastapi import APIRouter

from models.request_models import ChatRequest
from models.response_models import ChatResponse
from services.chat_service import process_chat
from utils.authentication import get_or_create_session

router = APIRouter()


@router.post("", response_model=ChatResponse)
def initiate_chat(payload: ChatRequest):
    # Initialize session
    session = get_or_create_session(payload.persona, payload.session_id)

    # Process the chat query
    answer, confidence = process_chat(
        session_id=session.id,
        raw_query=payload.query,
        session=session,
    )

    return ChatResponse(answer=answer, confidence=confidence)
