from typing import Literal

from pydantic import BaseModel


class QueryResponse(BaseModel):
    answer: str
    confidence: float


class SessionResponse(BaseModel):
    session_id: str
    persona: Literal["student", "staff"]
