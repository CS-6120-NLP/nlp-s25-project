from typing import Literal, Optional, List, Dict

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    persona: Literal["student", "staff"]
    session_id: str
    chat_history: Optional[List[Dict[str, str]]] = None


class QueryResponse(BaseModel):
    answer: str
    confidence: float


class SessionRequest(BaseModel):
    persona: Literal["student", "staff"]
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    persona: Literal["student", "staff"]
