# ==========================================
# backend/app/api/llm/multiagent/models.py
# ==========================================

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class AgentRole(Enum):
    """Tipos de agentes especializados"""
    COORDINATOR = "coordinator"
    FINANCIAL_ANALYST = "financial_analyst"
    DATA_RETRIEVER = "data_retriever"
    CALCULATOR = "calculator"
    VALIDATOR = "validator"
    RISK_ASSESSOR = "risk_assessor"
    COMPLIANCE_CHECKER = "compliance_checker"


class TaskStatus(Enum):
    """Status das tarefas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Prioridades das tarefas"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class AgentTask:
    """Representa uma tarefa para um agente"""
    agent_role: AgentRole
    tool_name: str
    arguments: Dict[str, Any]
    task_id: str = field(default_factory=lambda: f"task_{id(object())}")
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    max_retries: int = 3
    timeout_seconds: int = 30
    
    def __post_init__(self):
        if not self.task_id.startswith('task_'):
            self.task_id = f"task_{self.agent_role.value}_{self.tool_name}_{id(self)}"


@dataclass
class AgentResult:
    """Resultado da execução de um agente"""
    task_id: str
    agent_role: AgentRole
    tool_name: str
    success: bool
    result: Any
    status: TaskStatus = TaskStatus.COMPLETED
    error_message: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    completed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Plano de execução de tarefas"""
    levels: Dict[int, List[AgentTask]] = field(default_factory=dict)
    total_tasks: int = 0
    estimated_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_level(self, priority: int, tasks: List[AgentTask]):
        """Adiciona um nível de execução"""
        self.levels[priority] = tasks
        self.total_tasks += len(tasks)
    
    def get_ready_tasks(self, priority: int, completed_tasks: set) -> List[AgentTask]:
        """Retorna tarefas prontas para execução no nível especificado"""
        if priority not in self.levels:
            return []
        
        return [
            task for task in self.levels[priority]
            if all(dep_id in completed_tasks for dep_id in task.dependencies)
            and task.status == TaskStatus.PENDING
        ]


@dataclass
class ExecutionSummary:
    """Sumário da execução dos agentes"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_execution_time: float
    agents_used: Dict[AgentRole, int]
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso das tarefas"""
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.success_rate,
            "total_execution_time": self.total_execution_time,
            "agents_used": {role.value: count for role, count in self.agents_used.items()},
            "errors": self.errors,
            "performance_metrics": self.performance_metrics
        }