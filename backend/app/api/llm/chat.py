from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from typing import Optional
import os
import hashlib
from datetime import datetime
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
import redis.asyncio as redis
from google import genai
import logging
from sqlalchemy.orm import Session as pg_session
from app.data.dependencies import get_db as pg_get_db

from app.api.llm.tools import get_function_by_name
from app.api.llm.tools.tools import Tools  # Importa as ferramentas definidas

load_dotenv()

# Logger configurado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

_neo4j_driver = None

# Inicialização Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL = int(os.getenv("REDIS_TTL", 60 * 60))  # 1 hora

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def hash_query(query: str) -> str:
    """Gera uma hash única para a consulta"""
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()


# -----------------------------
# MODELOS Pydantic
# -----------------------------
class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    context: Optional[str] = None


# -----------------------------
# INICIALIZAÇÃO do GEMINI
# -----------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in environment")

client = genai.Client(api_key=GOOGLE_API_KEY)


class RAGContext:
    def __init__(self, driver: GraphDatabase.driver):  # Recebe o driver já criado
        self.driver = driver

    async def save_conversation(
        self, user_id: str, pergunta: str, resposta: str, contexto: str
    ):
        context_hash = hashlib.sha256(contexto.encode()).hexdigest()
        now = datetime.utcnow().isoformat()

        with self.driver.session() as session:
            result = session.run(
                "MATCH (p:Pergunta {text: $text}) RETURN p", text=pergunta
            )
            if not result.peek():
                logger.info("Pergunta não encontrada, criando nova.")
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
            else:
                logger.info("Pergunta já existe, atualizando resposta.")
                session.run(
                    """
                    MERGE (u:User {id: $user_id})
                    MERGE (p:Pergunta {text: $pergunta}) SET p.createdAt = $now
                    MERGE (r:Resposta {text: $resposta, createdAt: $now})
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


# Função para obter o driver Neo4j (dependência FastAPI)
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
# ENDPOINT de chat
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    user_id: str = "lucas",
    driver: GraphDatabase.driver = Depends(get_neo4j_driver),
    tools: Tools = Depends(Tools.get_tools),
):
    """
    Endpoint que responde perguntas com base em contexto vindo do Neo4j (Graph RAG) + Gemini.
    """
    try:
        logger.info("Recebida pergunta: %s", message.message)

        # Coleta de contexto relevante do grafo
        rag_context = RAGContext(driver)
        context = await rag_context.get_relevant_context(message.message)

        # Prompt final para o LLM
        full_prompt = f"""
        Você é um assistente financeiro. Use o contexto abaixo para responder de forma clara e objetiva.

        Contexto:
        {context or "Nenhum contexto encontrado."}

        Pergunta:
        {message.message}
        """
        # Definição das ferramentas disponíveis
        tools = Tools.get_tools()
        tools_objs = genai.types.Tool(function_declarations=tools)
        config = genai.types.GenerateContentConfig(
            tools=[tools_objs],
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(
                disable=False
            ),
        )

        chat = client.chats.create(model="gemini-2.5-flash", config=config)
        # Geração da resposta inicial
        response = chat.send_message(full_prompt)
        # Verifica se houve function_call
        if (
            hasattr(response.candidates[0].content.parts[0], "function_call")
            and response.candidates[0].content.parts[0].function_call
        ):
            call = response.candidates[0].content.parts[0].function_call
            logger.info("Function Call detectada: %s", call)
            function_name = call.name
            args = call.args

            tool_func = get_function_by_name(function_name)

            
            if tool_func:
                # Executa a função passando o args
                try:
                    tool_response = tool_func(**args)
                except Exception as e:
                    logger.error(
                        "Erro executando a função %s: %s", function_name, str(e)
                    )
                    tool_response = {"error": f"Erro ao executar a função: {str(e)}"}
            else:
                tool_response = {"error": f"Função '{function_name}' não implementada."}
            logger.info("Resposta da ferramenta: %s", tool_response)

            # Envia a resposta da ferramenta de volta para o Gemini para gerar a resposta final ao usuário
            final_gemini_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    full_prompt,
                    response.candidates[0].content,  # Inclui o Function Call original
                    {
                        "role": "function",
                        "name": function_name,
                        "parts": [{"text": json.dumps(tool_response)}],
                    },
                ],
            )

            # Salva no grafo
            await rag_context.save_conversation(
                user_id=user_id,
                pergunta=message.message,
                resposta=final_gemini_response.text,
                contexto=context,
            )

            return ChatResponse(
                response=final_gemini_response.text.strip(), context=context
            )

        else:
            # Se não houver Function Call, retorne a resposta normal do Gemini
            await rag_context.save_conversation(
                user_id=user_id,
                pergunta=message.message,
                resposta=response.text,
                contexto=context,
            )
            return ChatResponse(response=response.text.strip(), context=context)

    except Exception as e:
        logger.error("Erro no endpoint /chat: %s", str(e))
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")


# Adicione eventos de startup/shutdown no seu arquivo principal do FastAPI (onde você define `app = FastAPI()`)
@router.on_event("shutdown")
async def shutdown_event():
    global _neo4j_driver
    if _neo4j_driver:
        _neo4j_driver.close()
        logger.info("Neo4j driver closed.")
