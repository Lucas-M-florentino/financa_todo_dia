from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example":{
                "fullname": "Lucas Florentino",
                "email": "lucasflorentino@teste.com.br",
                "password": "weakpassword"
            }
        }

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "lucasflorentino@teste.com.br",
                "password": "weakpassword"
            }
        }

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class Transaction(BaseModel):
    amount: float = Field(..., description="Valor da transação")
    category_id: int = Field(..., description="ID da categoria da transação")
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Data de criação da transação")
    date: str = Field(..., description="Data da transação no formato ISO 8601")
    description: str = Field(..., description="Descrição da transação")
    type: TransactionType = Field(..., description="Tipo da transação (income ou expense)")
    notes: Optional[str] = Field(None, description="Notas adicionais sobre a transação")
    


class Category(BaseModel):
    id: int = Field(..., description="ID da categoria")
    name: str = Field(..., description="Nome da categoria")
    type: str = Field(..., description="Tipo da categoria (income ou expense)")


class PutTransaction(BaseModel):
    id: int = Field(..., description="ID da transação")
    amount: Optional[float] = Field(None, description="Valor da transação")
    category_id: Optional[int] = Field(None, description="ID da categoria da transação")
    createdAt: Optional[str] = Field(None, description="Data de criação da transação")
    date: Optional[str] = Field(None, description="Data da transação no formato ISO 8601")
    description: Optional[str] = Field(None, description="Descrição da transação")
    type: Optional[TransactionType] = Field(None, description="Tipo da transação (income ou expense)")
    notes: Optional[str] = Field(None, description="Notas adicionais sobre a transação")

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
    transactions: List[Transaction] = Field(..., description="Lista de transações a serem criadas")
    
    """Modelo para transações em lote"""
    def __init__(self, **data):
        super().__init__(**data)
        if not self.transactions:
            raise ValueError("A lista de transações não pode estar vazia")
        

    def to_models(self):
        return [transaction.to_model() for transaction in self.transactions]
    
    
