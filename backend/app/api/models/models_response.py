from pydantic import BaseModel
from .models import TransactionType
from typing import Optional


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
    notes: Optional[str] = None