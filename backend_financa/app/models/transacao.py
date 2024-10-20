from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    tipo = Column(String, nullable=False)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Transacao(id={self.id}, descricao={self.descricao}, valor={self.valor}, tipo={self.tipo})>"