from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    Text,
    Date,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, declarative_base   
from datetime import datetime

Base = declarative_base()
metadata = Base.metadata

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' ou 'expense'

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="check_category_type"),
    )

    # Relacionamento reverso: lista de transações dessa categoria
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(10), nullable=False)  # opcional, pode validar com a categoria
    notes = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="check_transaction_type"),
    )

    # Relacionamento com a categoria
    category = relationship("Category", back_populates="transactions")
