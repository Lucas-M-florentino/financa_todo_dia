import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.data.models import Base  # todas suas tabelas
from app.data.dependencies import get_db

# Banco de dados em memória (isolado)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas antes dos testes
Base.metadata.create_all(bind=engine)

# Função que substitui o get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Substituir a dependência do app
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_get_transactions_vazio():
    response = client.get("/transactions")
    assert response.status_code == 404  # Vazio retorna 404, como você definiu

def test_create_transaction_com_categoria():
    # Primeiro, criamos uma categoria no banco
    db = next(override_get_db())
    from app.data.models import Category
    nova_categoria = Category(name="Salário", type="income")
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)

    # Agora criamos uma transação usando a categoria
    response = client.post("/transactions", json={
        "amount": 100.0,
        "category_id": nova_categoria.id,
        "createdAt": "2025-07-21T10:00:00",
        "date": "2025-07-21T10:00:00",
        "description": "Pagamento mensal",
        "type": "income",
        "notes": "Referente a Julho"
    })
    assert response.status_code == 200
    assert response.json()["description"] == "Pagamento mensal"


def test_bulk_transactions():
    payload = [
        {
            "amount": 50.0,
            "category_id": 1,
            "createdAt": "2025-07-21T10:00:00",
            "date": "2025-07-21T10:00:00",
            "description": "Venda A",
            "type": "income",
            "notes": ""
        },
        {
            "amount": 75.0,
            "category_id": 1,
            "createdAt": "2025-07-21T10:00:00",
            "date": "2025-07-21T10:00:00",
            "description": "Venda B",
            "type": "income",
            "notes": ""
        }
    ]
    response = client.post("/transactions/bulk", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Transactions saved successfully"
