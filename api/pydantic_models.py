from pydantic import BaseModel
from typing import Literal

class QueryRequest(BaseModel):
    query: str
    persona: Literal["student", "staff"]
    session_id: str

class QueryResponse(BaseModel):
    answer: str
    confidence: float

class SessionRequest(BaseModel):
    persona: Literal["student", "staff"]
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    persona: Literal["student", "staff"]
