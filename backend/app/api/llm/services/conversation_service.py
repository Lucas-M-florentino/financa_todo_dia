# conversation_service.py 
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.api.llm.infra.redis import RedisClient

redis_client = RedisClient().get_client()  # Instancia o cliente Redis

class ConversationService:
    def __init__(self):
        self.redis_client = redis_client
        self.history_ttl_seconds = 60 * 60 # 1 hora de TTL para o histórico no Redis
        self.max_history_length = 10 # Limite de turnos no histórico do Redis

    async def add_to_conversation_history_redis(self, user_id: str, role: str, message_content: str):
        """
        Adiciona uma mensagem ao histórico da conversa do usuário no Redis.
        O histórico é armazenado como uma lista de JSONs.
        """
        key = f"chat_history:{user_id}"
        turn = {"role": role, "content": message_content, "timestamp": datetime.now().isoformat()}
        
        # Adiciona o novo turno ao início da lista (para manter os mais recentes visíveis)
        self.redis_client.lpush(key, json.dumps(turn))
        
        # Trim the list to max_history_length
        self.redis_client.ltrim(key, 0, self.max_history_length - 1)
        
        # Define um TTL para a chave, para que o histórico expire automaticamente
        self.redis_client.expire(key, self.history_ttl_seconds)
        logging.debug(f"Adicionado turno ao Redis para {user_id}: {role} - '{message_content}'")

    async def get_conversation_history_redis(self, user_id: str) -> List[Dict]:
        """
        Recupera o histórico da conversa do usuário do Redis.
        Retorna uma lista de dicionários no formato Gemini 'parts'.
        """
        key = f"chat_history:{user_id}"
        raw_history = self.redis_client.lrange(key, 0, -1)
        
        history_parts = []
        for item_json in raw_history:
            item = json.loads(item_json)
            # Converte para o formato esperado pelo Gemini para histórico: {"role": "user", "parts": [{"text": "..."}]}
            history_parts.append({
                "role": item["role"],
                "parts": [{"text": item["content"]}]
            })
        
        # O Redis guarda em ordem inversa (lpush adiciona no início), então inverta para cronológica
        return list(reversed(history_parts))

    # Esta função (save_conversation_neo4j) permaneceria no RAGContext
    # ou seria chamada separadamente no final do endpoint
    # async def save_conversation_neo4j(self, user_id: str, pergunta: str, resposta: str, contexto: str):
    #     # Lógica para salvar no Neo4j (já existente no seu RAGContext)
    #     pass

# Exemplo de como obter o serviço Redis (via dependência no FastAPI)
# from app.data.dependencies import get_redis_client # Se você tiver uma
# def get_conversation_service(redis_client: redis.Redis = Depends(get_redis_client)):
#     return ConversationService(redis_client)