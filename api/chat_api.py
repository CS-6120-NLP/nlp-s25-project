from typing import List

from fastapi import APIRouter

from models.request_models import ChatRequest, ChatHistoryRequest
from models.response_models import ChatResponse
from services.chat_service import process_chat, get_chat_history as get_chat_history_service

router = APIRouter()


@router.post("", response_model=ChatResponse)
def initiate_chat(payload: ChatRequest):
    # Process the chat query
    answer, confidence = process_chat(
        session_id=payload.session_id,
        persona=payload.persona,
        raw_query=payload.query
    )

    return ChatResponse(raw_query=payload.query, answer=answer, confidence=confidence)


@router.get("/history", response_model=List[ChatResponse])
def get_chat_history(payload: ChatHistoryRequest):
    chat_history = get_chat_history_service(payload.session_id)
    return [ChatResponse(raw_query=record.raw_query, answer=record.answer, confidence=record.confidence) for record in chat_history]
