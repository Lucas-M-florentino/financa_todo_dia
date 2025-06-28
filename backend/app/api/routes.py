from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class Transaction(BaseModel):
    id: int
    amount: float
    category: str
    createdAt: str = datetime.now().isoformat()
    date: str
    description: str
    type: str  # 'income' or 'expense'
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    category: str
    createdAt: Optional[datetime] = None
    date: str
    description: str
    type: str  # 'income' or 'expense'
    notes: Optional[str] = None

# In-memory storage for transactions
transactions = []

@router.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    return transactions

@router.post("/transactions")
async def create_transaction(transaction: Transaction):
    print(f"Creating transaction: {transaction}")
    # Generate ID if not provided
    if transaction.amount is None or transaction.amount <= 0 or transaction.type is None:
        raise HTTPException(status_code=400, detail="Invalid transaction data")
    new_transaction = transaction.dict()
    transactions.append(new_transaction)
    return new_transaction

@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: int, transaction: Transaction):
    for i, t in enumerate(transactions):
        if t.id == transaction_id:
            transaction.id = transaction_id
            transactions[i] = transaction
            return transaction
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    for i, t in enumerate(transactions):
        if t['id'] == transaction_id:
            del transactions[i]
            return {"message": "Transaction deleted successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.post("/transactions/bulk")
async def save_transactions(transactions_data: List[Transaction]):
    # Clear existing transactions
    transactions.clear()
    # Add new transactions
    for transaction in transactions_data:
        if transaction.id is None:
            transaction.id = len(transactions) + 1
        transactions.append(transaction)
    return {"message": "Transactions saved successfully"}
