# ==========================================
# backend/app/api/llm/multiagent/config.py
# ==========================================

from typing import Dict, List
from .models import AgentRole, TaskPriority


class MultiAgentConfig:
    """Configurações do sistema multiagentes"""
    
    # Mapeamento de ferramentas para agentes
    TOOL_TO_AGENT: Dict[str, AgentRole] = {
        # Dados e recuperação
        "get_financial_data": AgentRole.DATA_RETRIEVER,
        "get_market_data": AgentRole.DATA_RETRIEVER,
        "get_company_info": AgentRole.DATA_RETRIEVER,
        "search_transactions": AgentRole.DATA_RETRIEVER,
        
        # Cálculos
        "calculate_metrics": AgentRole.CALCULATOR,
        "calculate_ratios": AgentRole.CALCULATOR,
        "calculate_returns": AgentRole.CALCULATOR,
        "calculate_valuation": AgentRole.CALCULATOR,
        
        # Análises
        "analyze_portfolio": AgentRole.FINANCIAL_ANALYST,
        "analyze_performance": AgentRole.FINANCIAL_ANALYST,
        "generate_insights": AgentRole.FINANCIAL_ANALYST,
        "comparative_analysis": AgentRole.FINANCIAL_ANALYST,
        
        # Riscos
        "risk_assessment": AgentRole.RISK_ASSESSOR,
        "calculate_var": AgentRole.RISK_ASSESSOR,
        "stress_testing": AgentRole.RISK_ASSESSOR,
        
        # Validação e compliance
        "validate_transaction": AgentRole.VALIDATOR,
        "data_quality_check": AgentRole.VALIDATOR,
        "compliance_check": AgentRole.COMPLIANCE_CHECKER,
        "regulatory_validation": AgentRole.COMPLIANCE_CHECKER,
    }
    
    # Prioridades por tipo de agente
    AGENT_PRIORITIES: Dict[AgentRole, TaskPriority] = {
        AgentRole.DATA_RETRIEVER: TaskPriority.HIGH,     # Dados primeiro
        AgentRole.CALCULATOR: TaskPriority.MEDIUM,       # Cálculos após dados
        AgentRole.FINANCIAL_ANALYST: TaskPriority.MEDIUM, # Análises paralelas
        AgentRole.RISK_ASSESSOR: TaskPriority.MEDIUM,    # Riscos após análises
        AgentRole.VALIDATOR: TaskPriority.LOW,           # Validação por último
        AgentRole.COMPLIANCE_CHECKER: TaskPriority.LOW,  # Compliance por último
        AgentRole.COORDINATOR: TaskPriority.HIGH
    }
    
    # Regras de dependência
    DEPENDENCY_RULES: Dict[str, List[str]] = {
        # Cálculos dependem de dados
        "calculate_metrics": ["get_financial_data"],
        "calculate_ratios": ["get_financial_data"],
        "calculate_returns": ["get_financial_data"],
        
        # Análises dependem de dados e/ou cálculos
        "analyze_portfolio": ["get_financial_data", "calculate_metrics"],
        "analyze_performance": ["calculate_returns", "get_market_data"],
        "comparative_analysis": ["get_financial_data", "get_market_data"],
        
        # Riscos dependem de análises
        "risk_assessment": ["analyze_portfolio", "calculate_metrics"],
        "calculate_var": ["get_financial_data", "calculate_returns"],
        "stress_testing": ["analyze_portfolio", "risk_assessment"],
        
        # Validações dependem de cálculos
        "validate_transaction": ["calculate_metrics"],
        "compliance_check": ["analyze_portfolio", "risk_assessment"],
    }
    
    # Configurações de execução
    MAX_PARALLEL_TASKS = 5
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Configurações de validação
    VALIDATION_RULES = {
        AgentRole.FINANCIAL_ANALYST: {
            "required_fields": ["status", "data", "analysis"],
            "numeric_fields": ["value", "percentage", "ratio"],
        },
        AgentRole.CALCULATOR: {
            "required_fields": ["status", "result"],
            "numeric_fields": ["value", "amount", "total"],
        },
        AgentRole.RISK_ASSESSOR: {
            "required_fields": ["status", "risk_level", "metrics"],
            "numeric_fields": ["var", "volatility", "beta"],
        }
    }
