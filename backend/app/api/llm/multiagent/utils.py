# ==========================================
# backend/app/api/llm/multiagent/utils.py
# ==========================================

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .models import AgentResult, ExecutionSummary, AgentRole

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analisador de performance do sistema multiagentes"""
    
    def __init__(self):
        self.execution_history: List[ExecutionSummary] = []
        self.max_history = 100  # Manter últimas 100 execuções
    
    def add_execution(self, summary: ExecutionSummary):
        """Adiciona uma execução ao histórico"""
        self.execution_history.append(summary)
        
        # Limita o tamanho do histórico
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history:]
    
    def get_performance_report(self, last_n: int = 10) -> Dict[str, Any]:
        """Gera relatório de performance das últimas N execuções"""
        if not self.execution_history:
            return {"message": "Nenhuma execução registrada"}
        
        recent_executions = self.execution_history[-last_n:]
        
        return {
            "total_executions_analyzed": len(recent_executions),
            "average_success_rate": sum(e.success_rate for e in recent_executions) / len(recent_executions),
            "average_execution_time": sum(e.total_execution_time for e in recent_executions) / len(recent_executions),
            "average_tasks_per_execution": sum(e.total_tasks for e in recent_executions) / len(recent_executions),
            "most_used_agents": self._get_most_used_agents(recent_executions),
            "common_errors": self._get_common_errors(recent_executions),
            "performance_trend": self._analyze_trend(recent_executions)
        }
    
    def _get_most_used_agents(self, executions: List[ExecutionSummary]) -> Dict[str, int]:
        """Identifica os agentes mais utilizados"""
        agent_usage = {}
        
        for execution in executions:
            for agent_role, count in execution.agents_used.items():
                role_name = agent_role.value if hasattr(agent_role, 'value') else str(agent_role)
                agent_usage[role_name] = agent_usage.get(role_name, 0) + count
        
        # Ordena por uso
        return dict(sorted(agent_usage.items(), key=lambda x: x[1], reverse=True))
    
    def _get_common_errors(self, executions: List[ExecutionSummary]) -> List[str]:
        """Identifica erros mais comuns"""
        error_counts = {}
        
        for execution in executions:
            for error in execution.errors:
                # Simplifica erro para contagem
                simplified_error = error.split(':')[0] if ':' in error else error
                error_counts[simplified_error] = error_counts.get(simplified_error, 0) + 1
        
        # Retorna os 5 mais comuns
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [error for error, count in sorted_errors[:5]]
    
    def _analyze_trend(self, executions: List[ExecutionSummary]) -> str:
        """Analisa tendência de performance"""
        if len(executions) < 3:
            return "Dados insuficientes para análise de tendência"
        
        # Compara primeiras e últimas execuções
        first_half = executions[:len(executions)//2]
        second_half = executions[len(executions)//2:]
        
        first_avg_time = sum(e.total_execution_time for e in first_half) / len(first_half)
        second_avg_time = sum(e.total_execution_time for e in second_half) / len(second_half)
        
        first_avg_success = sum(e.success_rate for e in first_half) / len(first_half)
        second_avg_success = sum(e.success_rate for e in second_half) / len(second_half)
        
        if second_avg_time < first_avg_time and second_avg_success > first_avg_success:
            return "Melhorando - tempo reduzindo e sucesso aumentando"
        elif second_avg_time > first_avg_time and second_avg_success < first_avg_success:
            return "Piorando - tempo aumentando e sucesso reduzindo"
        elif second_avg_success > first_avg_success:
            return "Estável com melhoria na taxa de sucesso"
        elif second_avg_time < first_avg_time:
            return "Estável com melhoria no tempo de execução"
        else:
            return "Estável"


class AgentMetrics:
    """Coleta e analisa métricas específicas por agente"""
    
    def __init__(self):
        self.agent_performances: Dict[AgentRole, List[Dict]] = {}
    
    def record_agent_performance(self, result: AgentResult):
        """Registra performance de um agente"""
        if result.agent_role not in self.agent_performances:
            self.agent_performances[result.agent_role] = []
        
        performance_data = {
            "tool_name": result.tool_name,
            "success": result.success,
            "execution_time": result.execution_time,
            "retry_count": result.retry_count,
            "timestamp": result.completed_at,
            "error": result.error_message if not result.success else None
        }
        
        self.agent_performances[result.agent_role].append(performance_data)
        
        # Limita histórico por agente
        if len(self.agent_performances[result.agent_role]) > 50:
            self.agent_performances[result.agent_role] = self.agent_performances[result.agent_role][-50:]
    
    def get_agent_report(self, agent_role: AgentRole) -> Dict[str, Any]:
        """Gera relatório para um agente específico"""
        if agent_role not in self.agent_performances:
            return {"message": "Nenhuma performance registrada para este agente"}
        
        performances = self.agent_performances[agent_role]
        successful_perf = [p for p in performances if p["success"]]
        
        
        return {
            "total_executions": len(performances),
            "successful_executions": len(successful_perf)
        }
    
    