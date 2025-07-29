from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime

from app.data.dependencies import get_db
from sqlalchemy.orm import Session
from app.data.models import Category, Transaction as TransactionModel
from app.api.models.models import Transaction, PutTransaction
from app.api.models.models_response import CategoryResponse, TransactionResponse

router = APIRouter()

def validate_transaction(transaction):
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be greater than zero")
    if transaction.type not in ['income', 'expense']:
        raise HTTPException(status_code=400, detail="Transaction type must be 'income' or 'expense'")
    if not transaction.date:
        raise HTTPException(status_code=400, detail="Transaction date is required")
    if not transaction.description:
        raise HTTPException(status_code=400, detail="Transaction description is required")
    return transaction

def to_response(transaction: TransactionModel, category_name: str) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        amount=float(transaction.amount),
        category_name=category_name,
        createdAt=transaction.created_at.isoformat(),
        date=transaction.date.isoformat(),
        description=transaction.description,
        type=transaction.type,
        notes=transaction.notes
    )

def get_category_name(db: Session, category_id: int) -> str:
    category = db.query(Category).filter(Category.id == category_id).first()
    return category.name if category else "Unknown Category"

def build_transaction_model(data: Transaction | PutTransaction) -> TransactionModel:
    return TransactionModel(
        amount=data.amount,
        category_id=data.category_id,
        created_at=datetime.fromisoformat(data.createdAt) if data.createdAt else datetime.utcnow(),
        date=datetime.fromisoformat(data.date),
        description=data.description,
        type=data.type,
        notes=data.notes,
    )

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(db: Session = Depends(get_db)):
    transactions_db = db.query(TransactionModel).all()
    if not transactions_db:
        raise HTTPException(status_code=404, detail="No transactions found")
    categories = {c.id: c.name for c in db.query(Category).all()}
    return [
        to_response(t, categories.get(t.category_id, "Unknown Category"))
        for t in transactions_db
    ]

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    validate_transaction(transaction)
    if not transaction.category_id:
        raise HTTPException(status_code=400, detail="Category ID is required")
    category = db.query(Category).filter(Category.id == transaction.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    new_transaction = build_transaction_model(transaction)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return to_response(new_transaction, category.name)

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction: PutTransaction, transaction_id: int, db: Session = Depends(get_db)):
    existing_transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    if not existing_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    validate_transaction(transaction)
    for attr in ['amount', 'category_id', 'description', 'type', 'notes']:
        setattr(existing_transaction, attr, getattr(transaction, attr))
    existing_transaction.created_at = datetime.fromisoformat(transaction.createdAt) if transaction.createdAt else datetime.utcnow()
    existing_transaction.date = datetime.fromisoformat(transaction.date)
    db.commit()
    db.refresh(existing_transaction)
    category_name = get_category_name(db, existing_transaction.category_id)
    return to_response(existing_transaction, category_name)

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionModel).filter_by(id=transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    category_name = get_category_name(db, transaction.category_id)
    return to_response(transaction, category_name)  

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}

@router.post("/transactions/bulk")
async def save_transactions(transactions_data: List[Transaction], db: Session = Depends(get_db)):
    if not transactions_data:
        raise HTTPException(status_code=400, detail="No transactions provided")
    for transaction in transactions_data:
        validate_transaction(transaction)
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with ID {transaction.category_id} not found")
        new_transaction = build_transaction_model(transaction)
        db.add(new_transaction)
    db.commit()
    return {"message": "Transactions saved successfully"}

@router.get("/categories", response_model=dict[str, List[CategoryResponse]])
async def get_categories(db: Session = Depends(get_db)):
    income = db.query(Category).filter_by(type='income').all()
    expense = db.query(Category).filter_by(type='expense').all()
    return {"income": income, "expense": expense}
