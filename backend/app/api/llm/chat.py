# backend/app/api/llm/chat.py

import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

# Dependências locais
from app.data.dependencies import get_db
from .multiagent.hybrid_conversation_service import (
    HybridConversationService,
    MultiAgentBenchmark
)
from .providers.factory import LLMProviderFactory
from .services.rag_service import RAGService
from .services.conversation_service import ConversationService

# Dependências de serviços externos
from neo4j import GraphDatabase
import redis.asyncio as redis

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router FastAPI
router = APIRouter()

# -----------------------------
# MODELOS PYDANTIC
# -----------------------------


class ChatMessage(BaseModel):
    message: str
    user_id: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    context: Optional[str] = None
    provider_info: Optional[dict] = None


class HealthCheckResponse(BaseModel):
    status: str
    details: dict


# -----------------------------
# CONFIGURAÇÃO DE SERVIÇOS
# -----------------------------

# Singleton pattern para serviços
_conversation_service = None
_neo4j_driver = None
_redis_client = None


async def get_neo4j_driver():
    """Dependency para obter driver Neo4j"""
    global _neo4j_driver

    if _neo4j_driver is None:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD")

        if not neo4j_password:
            raise ValueError("NEO4J_PASSWORD deve ser definido no ambiente")

        _neo4j_driver = GraphDatabase.driver(
            neo4j_uri, auth=(neo4j_user, neo4j_password)
        )
        logger.info("Neo4j driver inicializado")

    yield _neo4j_driver


async def get_redis_client():
    """Dependency para obter cliente Redis"""
    global _redis_client

    if _redis_client is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))

        _redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=False,  # Mantém bytes para compatibilidade
        )
        logger.info("Redis client inicializado")

    yield _redis_client


async def get_conversation_service(
    neo4j_driver: GraphDatabase.driver = Depends(get_neo4j_driver),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    """Dependency para obter serviço de conversação"""
    global _conversation_service

    if _conversation_service is None:
        # Cria o provedor LLM baseado no ambiente
        llm_provider = LLMProviderFactory.create_from_env()
        logger.info(f"LLM Provider inicializado: {llm_provider.get_model_info()}")

        # Cria o serviço RAG
        redis_ttl = int(os.getenv("REDIS_TTL", 3600))
        rag_service = RAGService(neo4j_driver, redis_client, redis_ttl)

        # Cria o serviço de conversação
        # _conversation_service = ConversationService(llm_provider, rag_service)
        _conversation_service = HybridConversationService(
            llm_provider=llm_provider, rag_service=rag_service
        )
        logger.info("Conversation Service inicializado")

    yield _conversation_service


# -----------------------------
# ENDPOINTS
# -----------------------------


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    db: Session = Depends(get_db),
    conversation_service: HybridConversationService = Depends(get_conversation_service),
):
    """
    Endpoint principal para chat com IA

    Processa mensagens do usuário usando:
    - RAG (Retrieval-Augmented Generation) com Neo4j + Redis
    - LLM configurável (Gemini, OpenAI, LM Studio)
    - Ferramentas financeiras integradas
    """
    try:
        logger.info(f"Recebida mensagem do usuário {message.user_id}")

        # Processa a conversa
        response_text, context = await conversation_service.process_conversation(
            message=message.message, user_id=message.user_id, db_session=db
        )

        # Informações do provedor (opcional para debug)
        provider_info = conversation_service.get_provider_info()

        return ChatResponse(
            response=response_text, context=context, provider_info=provider_info
        )

    except Exception as e:
        logger.error(f"Erro no endpoint /chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    conversation_service: HybridConversationService = Depends(get_conversation_service),
):
    """
    Endpoint para verificar a saúde do serviço de chat
    """
    try:
        health_details = await conversation_service.health_check()

        # Determina status geral
        is_healthy = health_details.get("conversation_service") == "healthy"
        status = "healthy" if is_healthy else "unhealthy"

        return HealthCheckResponse(status=status, details=health_details)

    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return HealthCheckResponse(status="unhealthy", details={"error": str(e)})


@router.post("/clear-cache")
async def clear_cache(
    conversation_service: HybridConversationService = Depends(get_conversation_service),
):
    """
    Endpoint para limpar o cache Redis
    """
    try:
        await conversation_service.rag_service.clear_cache()
        return {"message": "Cache limpo com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provider-info")
async def get_provider_info(
    conversation_service: HybridConversationService = Depends(get_conversation_service),
):
    """
    Endpoint para obter informações sobre o provedor LLM atual
    """
    return conversation_service.get_provider_info()


@router.get("/available-providers")
async def get_available_providers():
    """
    Endpoint para listar provedores de LLM disponíveis
    """
    return {
        "available_providers": LLMProviderFactory.get_available_providers(),
        "current_provider": os.getenv("LLM_PROVIDER", "gemini"),
        "how_to_change": "Altere a variável de ambiente LLM_PROVIDER e reinicie o serviço",
    }


# -----------------------------
# LIMPEZA DE RECURSOS
# -----------------------------


@router.on_event("shutdown")
async def shutdown_event():
    """Limpa recursos ao desligar"""
    global _neo4j_driver, _redis_client

    if _neo4j_driver:
        _neo4j_driver.close()
        logger.info("Neo4j driver fechado")

    if _redis_client:
        await _redis_client.close()
        logger.info("Redis client fechado")
        # -----------------------------
        # BENCHMARK COMPARATIVO
        # -----------------------------


        @router.post("/benchmark")
        async def run_benchmark(
            conversation_service: HybridConversationService = Depends(get_conversation_service),
        ):
            """
            Endpoint para executar benchmark comparativo entre agentes
            """
            benchmark = MultiAgentBenchmark(conversation_service)
            test_queries = [
                "Calcule as métricas do portfolio ABC",
                "Análise completa de risco e retorno da empresa XYZ",
                "Comparativo de performance entre fundos A, B e C"
            ]
            results = await benchmark.run_benchmark(test_queries, iterations=3)
            return {"recommendation": results.get("recommendation"), "details": results}