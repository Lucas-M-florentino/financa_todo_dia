from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.models.transacao import Transacao as TransacaoModel
from app.schemas.transacao import (
    Transacao as TransacaoSchema,
    TransacaoCreate,
    TransacaoUpdate,
    TipoTransacao
)

router = APIRouter()

@router.post("/", response_model=TransacaoSchema)
def criar_transacao(transacao: TransacaoCreate, db: Session = Depends(get_db)):
    """Cria uma nova transação"""
    db_transacao = TransacaoModel(**transacao.model_dump())
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@router.get("/", response_model=List[TransacaoSchema])
def listar_transacoes(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoTransacao] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as transações com opção de filtro por tipo"""
    query = db.query(TransacaoModel)
    
    if tipo:
        query = query.filter(TransacaoModel.tipo == tipo)
    
    return query.offset(skip).limit(limit).all()

@router.get("/resumo")
def obter_resumo(db: Session = Depends(get_db)):
    """Obtém um resumo das transações com total de receitas, despesas e saldo"""
    receitas = db.query(TransacaoModel).filter(
        TransacaoModel.tipo == TipoTransacao.RECEITA
    ).with_entities(
        db.func.coalesce(db.func.sum(TransacaoModel.valor), 0)
    ).scalar()

    despesas = db.query(TransacaoModel).filter(
        TransacaoModel.tipo == TipoTransacao.DESPESA
    ).with_entities(
        db.func.coalesce(db.func.sum(TransacaoModel.valor), 0)
    ).scalar()

    return {
        "total_receitas": float(receitas or 0),
        "total_despesas": float(despesas or 0),
        "saldo": float((receitas or 0) - (despesas or 0))
    }

@router.get("/{transacao_id}", response_model=TransacaoSchema)
def obter_transacao(transacao_id: int, db: Session = Depends(get_db)):
    """Obtém uma transação específica pelo ID"""
    transacao = db.query(TransacaoModel).filter(TransacaoModel.id == transacao_id).first()
    if transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao

@router.put("/{transacao_id}", response_model=TransacaoSchema)
def atualizar_transacao(
    transacao_id: int,
    transacao_update: TransacaoUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma transação existente"""
    db_transacao = db.query(TransacaoModel).filter(TransacaoModel.id == transacao_id).first()
    if db_transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    update_data = transacao_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transacao, field, value)

    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@router.delete("/{transacao_id}")
def deletar_transacao(transacao_id: int, db: Session = Depends(get_db)):
    """Deleta uma transação"""
    transacao = db.query(TransacaoModel).filter(TransacaoModel.id == transacao_id).first()
    if transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    db.delete(transacao)
    db.commit()
    return {"message": "Transação deletada com sucesso"}