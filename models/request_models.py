from typing import Literal, Optional, List, Dict

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    persona: Literal["student", "staff"]
    session_id: str
    chat_history: Optional[List[Dict[str, str]]] = None

class SessionRequest(BaseModel):
    persona: Literal["student", "staff"]
    session_id: str

class ChatHistoryRequest(BaseModel):
    session_id: str
    persona: Literal["student", "staff"]
