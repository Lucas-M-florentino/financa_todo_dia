from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import transacao
from app.routers import transacao as transacao_router

# Criar as tabelas no banco de dados
transacao.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finanças API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar para seus domínios específicos em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router de transações
app.include_router(
    transacao_router.router,
    prefix="/transacoes",
    tags=["Transações"]
)

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Finanças"}