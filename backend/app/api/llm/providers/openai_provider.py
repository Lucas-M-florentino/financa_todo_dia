# backend/app/api/llm/providers/openai_provider.py

import os
from typing import List, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Provider para OpenAI usando LangChain"""
    
    def __init__(self, 
                 model_name: str = None, 
                 temperature: float = 0.7, 
                 api_key: str = None,
                 **kwargs):
        
        # Define valores padrão
        model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY deve ser definido no ambiente ou passado como parâmetro")
        
        super().__init__(model_name, temperature, **kwargs)
        self.api_key = api_key
    
    def _initialize_llm(self, tools: List[BaseTool]) -> ChatOpenAI:
        """Inicializa o modelo OpenAI com ferramentas"""
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
            **self.extra_params
        )
        
        if tools:
            llm = llm.bind_tools(tools)
        
        return llm
    
    async def invoke(self, messages: List[BaseMessage]) -> Any:
        """Invoca o modelo OpenAI"""
        if not self._llm_with_tools:
            raise RuntimeError("LLM não foi inicializado. Chame bind_tools() primeiro.")
        
        return await self._llm_with_tools.ainvoke(messages)
    
    @property
    def provider_name(self) -> str:
        return "openai"