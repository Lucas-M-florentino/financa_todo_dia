from pydantic import BaseModel
from .models import TransactionType
from typing import Optional

class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    cargo: Optional[str] = None
    telefone: Optional[str] = None
    empresa_nome: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    type: TransactionType

class TransactionResponse(BaseModel):
    id: int
    amount: float
    category_name: str
    createdAt: str
    date: str
    description: str
    type: TransactionType
    empresa_id: Optional[int] = None
    usuario_id: Optional[int] = None
    notes: Optional[str] = None