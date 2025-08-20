# backend/app/api/llm/services/rag_service.py

import hashlib
import logging
from datetime import datetime
from typing import Optional
from neo4j import GraphDatabase
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RAGService:
    """Serviço de Retrieval-Augmented Generation usando Neo4j e Redis"""
    
    def __init__(self, neo4j_driver: GraphDatabase.driver, redis_client: redis.Redis, redis_ttl: int = 3600):
        self.neo4j_driver = neo4j_driver
        self.redis_client = redis_client
        self.redis_ttl = redis_ttl
    
    def _hash_query(self, query: str) -> str:
        """Gera uma hash única para a consulta"""
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()
    
    async def get_relevant_context(self, search_query: str) -> str:
        """
        Busca contexto relevante no Neo4j com cache no Redis
        
        Args:
            search_query: Consulta de busca
            
        Returns:
            Contexto relevante encontrado
        """
        # Tenta buscar no cache Redis primeiro
        cache_key = f"context:{self._hash_query(search_query)}"
        
        try:
            cached_context = await self.redis_client.get(cache_key)
            if cached_context:
                logger.info("Contexto carregado do Redis (cache)")
                return cached_context.decode("utf-8")
        except Exception as e:
            logger.warning(f"Erro ao acessar cache Redis: {e}")
        
        # Se não encontrado no cache, busca no Neo4j
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(
                    """
                    MATCH (n)
                    WHERE n.text IS NOT NULL 
                    AND toLower(n.text) CONTAINS toLower($search_query)
                    RETURN n.text 
                    ORDER BY size(n.text) DESC
                    LIMIT 5
                    """,
                    {"search_query": search_query},
                )
                
                texts = [record["n.text"] for record in result]
                context = "\n---\n".join(texts) if texts else ""
                
                # Salva no cache Redis
                try:
                    await self.redis_client.set(cache_key, context, ex=self.redis_ttl)
                    logger.info("Contexto salvo no Redis (cache)")
                except Exception as e:
                    logger.warning(f"Erro ao salvar no cache Redis: {e}")
                
                return context
                
        except Exception as e:
            logger.error(f"Erro ao buscar contexto no Neo4j: {e}")
            return ""
    
    async def save_conversation(self, user_id: str, question: str, answer: str, context: str):
        """
        Salva uma conversa no grafo Neo4j
        
        Args:
            user_id: ID do usuário
            question: Pergunta feita
            answer: Resposta gerada
            context: Contexto usado
        """
        try:
            context_hash = hashlib.sha256(context.encode()).hexdigest()
            now = datetime.utcnow().isoformat()
            
            with self.neo4j_driver.session() as session:
                session.run(
                    """
                    MERGE (u:User {id: $user_id})
                    CREATE (q:Question {text: $question, createdAt: $now})
                    CREATE (a:Answer {text: $answer, createdAt: $now})
                    MERGE (c:Context {hash: $context_hash, text: $context})
                    
                    MERGE (u)-[:ASKED]->(q)
                    MERGE (q)-[:GENERATED]->(a)
                    MERGE (q)-[:USED_CONTEXT]->(c)
                    """,
                    user_id=user_id,
                    question=question,
                    answer=answer,
                    context=context,
                    context_hash=context_hash,
                    now=now,
                )
            
            logger.info(f"Conversa salva no Neo4j para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar conversa no Neo4j: {e}")
    
    async def get_user_conversation_history(self, user_id: str, limit: int = 10) -> list:
        """
        Busca histórico de conversas do usuário
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de conversas a retornar
            
        Returns:
            Lista com histórico de conversas
        """
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(
                    """
                    MATCH (u:User {id: $user_id})-[:ASKED]->(q:Question)-[:GENERATED]->(a:Answer)
                    RETURN q.text as question, a.text as answer, q.createdAt as timestamp
                    ORDER BY q.createdAt DESC
                    LIMIT $limit
                    """,
                    {"user_id": user_id, "limit": limit}
                )
                
                history = []
                for record in result:
                    history.append({
                        "question": record["question"],
                        "answer": record["answer"],
                        "timestamp": record["timestamp"]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Erro ao buscar histórico de conversas: {e}")
            return []
    
    async def clear_cache(self, pattern: str = "context:*"):
        """
        Limpa o cache Redis baseado em um pattern
        
        Args:
            pattern: Pattern para buscar chaves a serem removidas
        """
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Cache limpo: {len(keys)} chaves removidas")
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")