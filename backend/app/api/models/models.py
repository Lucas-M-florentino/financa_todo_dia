from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class Transaction(BaseModel):
    amount: float
    category_id: int
    createdAt: str = datetime.now().isoformat()
    date: str
    description: str
    type: TransactionType
    notes: Optional[str] = None

class Category(BaseModel):
    id: int
    name: str
    type: str  # 'income' or 'expense'

    class Config:
        orm_mode = True

class PutTransaction(BaseModel):
    id: int
    amount: Optional[float] = None
    category_id: Optional[int] = None
    createdAt: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    type: Optional[TransactionType] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True
    def to_model(self):
        return Transaction(
            amount=self.amount,
            category_id=self.category_id,
            createdAt=self.createdAt,
            date=self.date,
            description=self.description,
            type=self.type,
            notes=self.notes
        )
        
class BulkTransaction(BaseModel):
    transactions: List[Transaction]

    class Config:
        orm_mode = True

    def to_models(self):
        return [transaction.to_model() for transaction in self.transactions]
