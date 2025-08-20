
# ==========================================
# backend/app/api/llm/multiagent/validators.py
# ==========================================

import logging
from typing import Any, Dict, List
from abc import ABC, abstractmethod
from .models import AgentResult, AgentRole
from .config import MultiAgentConfig

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """Validador base para resultados de agentes"""
    
    @abstractmethod
    async def validate(self, result: AgentResult) -> bool:
        """Valida um resultado de agente"""
        pass


class FinancialAnalystValidator(BaseValidator):
    """Validador para resultados de análise financeira"""
    
    async def validate(self, result: AgentResult) -> bool:
        """Valida análises financeiras"""
        try:
            if not result.success or not result.result:
                return False
            
            data = result.result
            if not isinstance(data, dict):
                return False
            
            # Verifica campos obrigatórios
            config = MultiAgentConfig.VALIDATION_RULES.get(AgentRole.FINANCIAL_ANALYST, {})
            required_fields = config.get("required_fields", [])
            
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Campo obrigatório '{field}' ausente no resultado")
                    return False
            
            # Valida campos numéricos
            numeric_fields = config.get("numeric_fields", [])
            for field in numeric_fields:
                if field in data:
                    if not self._is_valid_number(data[field]):
                        logger.warning(f"Campo numérico '{field}' inválido: {data[field]}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de análise financeira: {str(e)}")
            return False
    
    def _is_valid_number(self, value: Any) -> bool:
        """Verifica se um valor é um número válido"""
        try:
            num_value = float(value)
            return not (num_value != num_value or  # NaN
                       num_value == float('inf') or  # +Inf
                       num_value == float('-inf'))   # -Inf
        except (ValueError, TypeError):
            return False


class CalculatorValidator(BaseValidator):
    """Validador para resultados de cálculos"""
    
    async def validate(self, result: AgentResult) -> bool:
        """Valida cálculos financeiros"""
        try:
            if not result.success or not result.result:
                return False
            
            data = result.result
            if not isinstance(data, dict):
                return False
            
            # Verifica se há resultado numérico
            if 'result' in data or 'value' in data:
                value = data.get('result') or data.get('value')
                if not self._is_valid_financial_number(value):
                    return False
            
            # Validações específicas por tipo de cálculo
            return self._validate_calculation_type(result.tool_name, data)
            
        except Exception as e:
            logger.error(f"Erro na validação de cálculo: {str(e)}")
            return False
    
    def _is_valid_financial_number(self, value: Any) -> bool:
        """Valida números financeiros"""
        try:
            num_value = float(value)
            # Verifica NaN/Inf
            if num_value != num_value or abs(num_value) == float('inf'):
                return False
            # Valores extremamente grandes podem indicar erro
            if abs(num_value) > 1e15:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def _validate_calculation_type(self, tool_name: str, data: Dict) -> bool:
        """Validações específicas por tipo de cálculo"""
        if "ratio" in tool_name.lower():
            # Ratios geralmente devem ser positivos
            value = data.get('result', data.get('value', 0))
            return float(value) >= 0
        
        if "return" in tool_name.lower():
            # Retornos podem ser negativos, mas dentro de limites razoáveis
            value = data.get('result', data.get('value', 0))
            return -1.0 <= float(value) <= 10.0  # -100% a 1000%
        
        return True


class RiskAssessorValidator(BaseValidator):
    """Validador para análises de risco"""
    
    async def validate(self, result: AgentResult) -> bool:
        """Valida análises de risco"""
        try:
            if not result.success or not result.result:
                return False
            
            data = result.result
            if not isinstance(data, dict):
                return False
            
            # Verifica nível de risco
            if 'risk_level' in data:
                risk_level = data['risk_level']
                valid_levels = ['low', 'medium', 'high', 'very_high']
                if risk_level.lower() not in valid_levels:
                    return False
            
            # Valida métricas de risco
            if 'var' in data:  # Value at Risk
                var_value = float(data['var'])
                if var_value < 0 or var_value > 1:  # VaR deve ser entre 0 e 1
                    return False
            
            if 'volatility' in data:
                vol_value = float(data['volatility'])
                if vol_value < 0 or vol_value > 2:  # Volatilidade razoável
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de risco: {str(e)}")
            return False


class ValidatorFactory:
    """Factory para criar validadores específicos"""
    
    _validators = {
        AgentRole.FINANCIAL_ANALYST: FinancialAnalystValidator,
        AgentRole.CALCULATOR: CalculatorValidator,
        AgentRole.RISK_ASSESSOR: RiskAssessorValidator,
    }
    
    @classmethod
    def get_validator(cls, agent_role: AgentRole) -> BaseValidator:
        """Retorna o validador apropriado para o tipo de agente"""
        validator_class = cls._validators.get(agent_role)
        if validator_class:
            return validator_class()
        
        # Validador genérico para tipos não específicos
        return GenericValidator()


class GenericValidator(BaseValidator):
    """Validador genérico para agentes sem validação específica"""
    
    async def validate(self, result: AgentResult) -> bool:
        """Validação básica"""
        return result.success and result.result is not None
