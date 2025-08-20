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


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False)
    telefone = Column(String(20), nullable=True)
    endereco = Column(Text, nullable=True)

    usuarios = relationship("UserModel", back_populates="empresa")
    transactions = relationship("Transaction", back_populates="empresa")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cargo = Column(String, nullable=True)
    telefone = Column(String, nullable=True)
    password = Column(String, nullable=False)

    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True)
    empresa = relationship("Empresa", back_populates="usuarios")

    transactions = relationship("Transaction", back_populates="usuario")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' ou 'expense'

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="check_category_type"),
    )

    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(10), nullable=False)
    notes = Column(Text, nullable=True)

    usuario_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="check_transaction_type"),
    )

    category = relationship("Category", back_populates="transactions")
    usuario = relationship("UserModel", back_populates="transactions")
    empresa = relationship("Empresa", back_populates="transactions")
