# backend/app/api/llm/providers/lmstudio_provider.py

import os
from typing import List, Any
from langchain_openai import ChatOpenAI  # LM Studio usa API compatível com OpenAI
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from .base_provider import BaseLLMProvider


class LMStudioProvider(BaseLLMProvider):
    """Provider para LM Studio (modelos locais) usando API compatível com OpenAI"""
    
    def __init__(self, 
                 model_name: str = None, 
                 temperature: float = 0.7, 
                 base_url: str = None,
                 api_key: str = None,
                 **kwargs):
        
        # Define valores padrão
        model_name = model_name or os.getenv("LMSTUDIO_MODEL", "local-model")
        base_url = base_url or os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        api_key = api_key or os.getenv("LMSTUDIO_API_KEY", "lm-studio")  # LM Studio aceita qualquer key
        
        super().__init__(model_name, temperature, **kwargs)
        self.base_url = base_url
        self.api_key = api_key
    
    def _initialize_llm(self, tools: List[BaseTool]) -> ChatOpenAI:
        """Inicializa o modelo LM Studio com ferramentas"""
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.base_url,
            api_key=self.api_key,
            **self.extra_params
        )
        
        # Nota: Nem todos os modelos locais suportam function calling
        # Verifique se seu modelo suporta antes de usar ferramentas
        if tools:
            try:
                llm = llm.bind_tools(tools)
            except Exception as e:
                print(f"Aviso: Modelo local pode não suportar function calling: {e}")
                # Continue sem ferramentas se necessário
        
        return llm
    
    async def invoke(self, messages: List[BaseMessage]) -> Any:
        """Invoca o modelo LM Studio local"""
        if not self._llm_with_tools:
            raise RuntimeError("LLM não foi inicializado. Chame bind_tools() primeiro.")
        
        return await self._llm_with_tools.ainvoke(messages)
    
    @property
    def provider_name(self) -> str:
        return "lmstudio"
    
    def get_model_info(self) -> dict:
        """Retorna informações específicas do LM Studio"""
        info = super().get_model_info()
        info["base_url"] = self.base_url
        return info