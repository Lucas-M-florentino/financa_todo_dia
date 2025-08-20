# backend/app/api/llm/providers/factory.py

import os
from typing import Dict, Type
from .base_provider import BaseLLMProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .lmstudio_provider import LMStudioProvider
from .groq_provider import GroqProvider


class LLMProviderFactory:
    """Factory para criar instâncias de provedores de LLM"""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "lmstudio": LMStudioProvider,
        "groq": GroqProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str = None, **kwargs) -> BaseLLMProvider:
        """
        Cria um provedor de LLM baseado no nome do provedor.
        
        Args:
            provider_name: Nome do provedor (gemini, openai, lmstudio)
                          Se não especificado, usa a variável de ambiente LLM_PROVIDER
            **kwargs: Argumentos adicionais para o provedor
        
        Returns:
            Instância do provedor de LLM
        
        Raises:
            ValueError: Se o provedor não for encontrado
        """
        
        # Usa provider do ambiente se não especificado
        if not provider_name:
            provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
        
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available_providers = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Provedor '{provider_name}' não encontrado. "
                f"Provedores disponíveis: {available_providers}"
            )
        
        # Adiciona configurações padrão do ambiente se não especificadas
        if "temperature" not in kwargs:
            kwargs["temperature"] = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]):
        """
        Registra um novo provedor na factory.
        
        Args:
            name: Nome do provedor
            provider_class: Classe do provedor que herda de BaseLLMProvider
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ValueError("Provider deve herdar de BaseLLMProvider")
        
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Retorna lista de provedores disponíveis"""
        return list(cls._providers.keys())
    
    @classmethod
    def create_from_env(cls) -> BaseLLMProvider:
        """
        Cria um provedor baseado inteiramente nas variáveis de ambiente.
        Conveniente para usar em produção.
        """
        return cls.create_provider()