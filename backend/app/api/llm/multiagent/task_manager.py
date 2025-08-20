# ==========================================
# backend/app/api/llm/multiagent/task_manager.py
# ==========================================

import logging
from typing import List, Dict, Set
from .models import AgentTask, ExecutionPlan, TaskPriority, AgentRole
from .config import MultiAgentConfig

logger = logging.getLogger(__name__)


class TaskManager:
    """Gerenciador de tarefas do sistema multiagentes"""
    
    def __init__(self, config: MultiAgentConfig = None):
        self.config = config or MultiAgentConfig()
    
    def create_tasks_from_tool_calls(self, tool_calls: List[Dict]) -> List[AgentTask]:
        """Converte tool calls em tarefas estruturadas"""
        tasks = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            args = tool_call["args"]
            
            # Determina o agente responsável
            agent_role = self._get_agent_for_tool(tool_name)
            
            # Determina prioridade
            priority = self._get_task_priority(agent_role)
            
            task = AgentTask(
                agent_role=agent_role,
                tool_name=tool_name,
                arguments=args,
                priority=priority
            )
            
            tasks.append(task)
        
        # Detecta dependências após criar todas as tarefas
        self._detect_dependencies(tasks)
        
        return tasks
    
    def _get_agent_for_tool(self, tool_name: str) -> AgentRole:
        """Determina qual agente deve executar a ferramenta"""
        return self.config.TOOL_TO_AGENT.get(tool_name, AgentRole.DATA_RETRIEVER)
    
    def _get_task_priority(self, agent_role: AgentRole) -> TaskPriority:
        """Determina a prioridade da tarefa baseada no agente"""
        return self.config.AGENT_PRIORITIES.get(agent_role, TaskPriority.MEDIUM)
    
    def _detect_dependencies(self, tasks: List[AgentTask]):
        """Detecta e configura dependências entre tarefas"""
        task_map = {task.tool_name: task.task_id for task in tasks}
        
        for task in tasks:
            required_tools = self.config.DEPENDENCY_RULES.get(task.tool_name, [])
            
            for required_tool in required_tools:
                if required_tool in task_map:
                    task.dependencies.append(task_map[required_tool])
    
    def create_execution_plan(self, tasks: List[AgentTask]) -> ExecutionPlan:
        """Cria plano de execução otimizado"""
        plan = ExecutionPlan()
        
        # Agrupa tarefas por prioridade
        tasks_by_priority = {}
        for task in tasks:
            priority_value = task.priority.value
            if priority_value not in tasks_by_priority:
                tasks_by_priority[priority_value] = []
            tasks_by_priority[priority_value].append(task)
        
        # Ordena por prioridade e adiciona ao plano
        for priority in sorted(tasks_by_priority.keys()):
            plan.add_level(priority, tasks_by_priority[priority])
        
        # Estima tempo total
        plan.estimated_time = self._estimate_execution_time(tasks)
        
        return plan
    
    def _estimate_execution_time(self, tasks: List[AgentTask]) -> float:
        """Estima tempo total de execução"""
        # Estimativas baseadas no tipo de agente (em segundos)
        time_estimates = {
            AgentRole.DATA_RETRIEVER: 2.0,
            AgentRole.CALCULATOR: 1.0,
            AgentRole.FINANCIAL_ANALYST: 3.0,
            AgentRole.RISK_ASSESSOR: 4.0,
            AgentRole.VALIDATOR: 1.5,
            AgentRole.COMPLIANCE_CHECKER: 2.5,
        }
        
        total_time = 0.0
        for task in tasks:
            total_time += time_estimates.get(task.agent_role, 2.0)
        
        # Considera paralelização (estimativa conservadora)
        parallel_factor = min(len(tasks), self.config.MAX_PARALLEL_TASKS)
        if parallel_factor > 1:
            total_time *= 0.7  # 30% de redução por paralelização
        
        return total_time
    
    def validate_execution_plan(self, plan: ExecutionPlan) -> List[str]:
        """Valida o plano de execução e retorna warnings/erros"""
        warnings = []
        
        # Verifica dependências circulares
        if self._has_circular_dependencies(plan):
            warnings.append("Dependências circulares detectadas")
        
        # Verifica se há tarefas órfãs
        orphaned_tasks = self._find_orphaned_tasks(plan)
        if orphaned_tasks:
            warnings.append(f"Tarefas órfãs encontradas: {orphaned_tasks}")
        
        # Verifica sobrecarga
        if plan.total_tasks > 20:
            warnings.append(f"Muitas tarefas ({plan.total_tasks}). Considere otimizar.")
        
        return warnings
    
    def _has_circular_dependencies(self, plan: ExecutionPlan) -> bool:
        """Verifica se há dependências circulares"""
        all_tasks = []
        for level_tasks in plan.levels.values():
            all_tasks.extend(level_tasks)
        
        # Implementação simples de detecção de ciclos
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str, task_deps: Dict[str, List[str]]) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep in task_deps.get(task_id, []):
                if has_cycle(dep, task_deps):
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        task_deps = {task.task_id: task.dependencies for task in all_tasks}
        
        for task in all_tasks:
            if has_cycle(task.task_id, task_deps):
                return True
        
        return False
    
    def _find_orphaned_tasks(self, plan: ExecutionPlan) -> List[str]:
        """Encontra tarefas sem dependências que deveriam ter"""
        orphaned = []
        
        for level_tasks in plan.levels.values():
            for task in level_tasks:
                expected_deps = self.config.DEPENDENCY_RULES.get(task.tool_name, [])
                if expected_deps and not task.dependencies:
                    orphaned.append(task.tool_name)
        
        return orphaned
