from typing import Literal

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    persona: Literal["student", "staff"]
    session_id: str


class SessionRequest(BaseModel):
    persona: Literal["student", "staff"]
    session_id: str
