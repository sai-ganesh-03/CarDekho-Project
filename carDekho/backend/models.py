from typing import Any, Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    type: str  # "question" | "cars" | "no_results" | "message"
    message: str
    cars: Optional[list[dict[str, Any]]] = None
