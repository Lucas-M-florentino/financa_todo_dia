
# backend/app/api/llm/tools/__init__.py (atualizado)

from .functions import get_tools, set_db_session, get_db_session

def get_function_by_name(name: str):
    """
    Obtém a função de ferramenta pelo nome.
    
    :param name: Nome da função.
    :return: Função correspondente ou None se não for encontrada.
    """
    tools = get_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    return None

__all__ = [
    "get_tools",
    "set_db_session", 
    "get_db_session",
    "get_function_by_name"
]