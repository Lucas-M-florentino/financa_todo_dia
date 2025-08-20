# backend/app/api/llm/providers/gemini_provider.py

import os
from typing import List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Provider para Google Gemini usando LangChain"""
    
    def __init__(self, 
                 model_name: str = None, 
                 temperature: float = 0.7, 
                 api_key: str = None,
                 **kwargs):
        
        # Define valores padrão
        model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY deve ser definido no ambiente ou passado como parâmetro")
        
        super().__init__(model_name, temperature, **kwargs)
        self.api_key = api_key
    
    def _initialize_llm(self, tools: List[BaseTool]) -> ChatGoogleGenerativeAI:
        """Inicializa o modelo Gemini com ferramentas"""
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key,
            **self.extra_params
        )
        
        if tools:
            llm = llm.bind_tools(tools)
        
        return llm
    
    async def invoke(self, messages: List[BaseMessage]) -> Any:
        """Invoca o modelo Gemini"""
        if not self._llm_with_tools:
            raise RuntimeError("LLM não foi inicializado. Chame bind_tools() primeiro.")
        
        return await self._llm_with_tools.ainvoke(messages)
    
    @property
    def provider_name(self) -> str:
        return "gemini"