# backend/app/api/llm/providers/groq_provider.py

import os
from typing import List, Any
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from .base_provider import BaseLLMProvider

class GroqProvider(BaseLLMProvider):
    """Provider para Groq usando LangChain"""
    
    def __init__(self, 
                 model_name: str = None, 
                 temperature: float = 0.7, 
                 api_key: str = None,
                 **kwargs):
        
        # Define valores padrão
        model_name = model_name or os.getenv("GROQ_MODEL", "groq-1")
        api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY deve ser definido no ambiente ou passado como parâmetro")
        
        super().__init__(model_name, temperature, **kwargs)
        self.api_key = api_key
    
    def _initialize_llm(self, tools: List[BaseTool]) -> ChatGroq:
        """Inicializa o modelo Groq com ferramentas"""
        llm = ChatGroq(
            model=self.model_name,
            temperature=self.temperature,
            groq_api_key=self.api_key,
            **self.extra_params
        )
        
        if tools:
            llm = llm.bind_tools(tools)
        
        return llm
    
    async def invoke(self, messages: List[BaseMessage]) -> Any:
        """Invoca o modelo Groq"""
        if not self._llm_with_tools:
            raise RuntimeError("LLM não foi inicializado. Chame bind_tools() primeiro.")
        
        return await self._llm_with_tools.ainvoke(messages)
    
    @property
    def provider_name(self) -> str:
        return "groq"   