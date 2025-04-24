from typing import Literal

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    persona: Literal["student", "staff"]
    session_id: str


class ChatHistoryRequest(BaseModel):
    session_id: str


class SessionRequest(BaseModel):
    persona: Literal["student", "staff"]
    session_id: str
