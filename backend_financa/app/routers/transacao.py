from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class TipoTransacao(str, Enum):
    RECEITA = "receita"
    DESPESA = "despesa"

class TransacaoBase(BaseModel):
    descricao: str = Field(..., min_length=3, max_length=255)
    valor: Decimal = Field(..., gt=0)
    tipo: TipoTransacao

    @validator('valor')
    def valor_deve_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError('O valor deve ser maior que zero')
        return v

class TransacaoCreate(TransacaoBase):
    pass

class Transacao(TransacaoBase):
    id: int
    data_criacao: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class TransacaoUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=3, max_length=255)
    valor: Optional[Decimal] = Field(None, gt=0)
    tipo: Optional[TipoTransacao] = None