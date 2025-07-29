

# Função para obter o driver Neo4j (dependência FastAPI)
from datetime import datetime
import hashlib
import logging
import os

from neo4j import GraphDatabase

from app.api.llm.infra.redis import RedisClient

# Logger configurado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Configuração do Redis
# -----------------------------
redis_client = RedisClient().get_client()  # Instancia o cliente Redis
REDIS_TTL = int(os.getenv("REDIS_TTL", 60 * 60))  # 1 hora

_neo4j_driver = None

# -----------------------------
# Funções auxiliares
# -----------------------------
def hash_query(query: str) -> str:
    """Gera uma hash única para a consulta"""
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()

async def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        if not neo4j_user or not neo4j_password:
            raise ValueError(
                "NEO4J_USER and NEO4J_PASSWORD must be set in the environment"
            )
        _neo4j_driver = GraphDatabase.driver(
            neo4j_uri, auth=(neo4j_user, neo4j_password)
        )
        logger.info("Neo4j driver initialized.")
    yield _neo4j_driver
    # O driver pode ser fechado no evento de shutdown da aplicação, não por requisição.

# -----------------------------
# CONTEXTO RAG (Graph RAG)
# -----------------------------
class RAGContext:
    def __init__(self, driver: GraphDatabase.driver):  # Recebe o driver já criado
        self.driver = driver

    async def save_conversation(
        self, user_id: str, pergunta: str, resposta: str, contexto: str
    ):
        context_hash = hashlib.sha256(contexto.encode()).hexdigest()
        now = datetime.utcnow().isoformat()


        with self.driver.session() as session:
            session.run(
                """
                MERGE (u:User {id: $user_id})
                CREATE (p:Pergunta {text: $pergunta, createdAt: $now})
                CREATE (r:Resposta {text: $resposta, createdAt: $now})
                MERGE (c:Contexto {hash: $context_hash, text: $contexto, fonte: "neo4j"})

                MERGE (u)-[:ENVIOU]->(p)
                MERGE (p)-[:GEROU]->(r)
                MERGE (p)-[:COM_BASE_EM]->(c)
                """,
                user_id=user_id,
                pergunta=pergunta,
                resposta=resposta,
                contexto=contexto,
                context_hash=context_hash,
                now=now,
            )

        logger.info("Conversa salva no Neo4j.")

    async def get_relevant_context(self, search_query: str) -> str:
        key = f"context:{hash_query(search_query)}"
        logger.info("Buscando contexto para a consulta: %s", search_query)

        cached = await redis_client.get(key)
        if cached:
            logger.info("Contexto carregado do Redis")
            return cached.decode("utf-8")

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE n.text IS NOT NULL AND toLower(n.text) CONTAINS toLower($search_query)
                RETURN n.text LIMIT 5
                """,
                {"search_query": search_query},
            )
            texts = [record["n.text"] for record in result]
            context = "\n".join(texts)

        await redis_client.set(key, context, ex=REDIS_TTL)
        logger.info("Contexto salvo no Redis")
        return context

    def close(self):
        self.driver.close()
