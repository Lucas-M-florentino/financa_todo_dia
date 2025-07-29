# -----------------------------
# MODELOS Pydantic
# -----------------------------
from typing import Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str = "Qual a maior despesa do mês 07/2025?"
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    context: Optional[str] = None