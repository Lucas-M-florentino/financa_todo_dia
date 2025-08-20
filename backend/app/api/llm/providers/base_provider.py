# backend/app/api/llm/providers/base_provider.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool


class BaseLLMProvider(ABC):
    """Classe base abstrata para provedores de LLM"""
    
    def __init__(self, model_name: str, temperature: float = 0.7, **kwargs):
        self.model_name = model_name
        self.temperature = temperature
        self.extra_params = kwargs
        self._llm_with_tools = None
    
    @abstractmethod
    def _initialize_llm(self, tools: List[BaseTool]) -> Any:
        """
        Inicializa o modelo LLM com as ferramentas.
        Deve ser implementado por cada provider específico.
        """
        pass
    
    @abstractmethod
    async def invoke(self, messages: List[BaseMessage]) -> Any:
        """
        Invoca o modelo LLM com as mensagens.
        Deve ser implementado por cada provider específico.
        """
        pass
    
    def bind_tools(self, tools: List[BaseTool]):
        """Vincula as ferramentas ao modelo LLM"""
        self._llm_with_tools = self._initialize_llm(tools)
        return self
    
    @property
    def provider_name(self) -> str:
        """Retorna o nome do provider"""
        return self.__class__.__name__.replace('Provider', '').lower()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo atual"""
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "temperature": self.temperature,
            "extra_params": self.extra_params
        }