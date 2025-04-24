from typing import Literal

from pydantic import BaseModel


class ChatResponse(BaseModel):
    raw_query: str
    answer: str
    confidence: float


class SessionResponse(BaseModel):
    session_id: str


class SummaryResponse(BaseModel):
    summary: str