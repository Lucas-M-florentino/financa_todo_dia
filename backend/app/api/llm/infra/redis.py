import redis
import os
from dotenv import load_dotenv
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialização Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        self.client.ping()  # Verifica se a conexão com o Redis está funcionando

    def get_client(self):
        return self.client

    def close(self):
        self.client.close()