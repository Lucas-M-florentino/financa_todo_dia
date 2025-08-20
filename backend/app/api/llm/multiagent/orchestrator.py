# ==========================================
# backend/app/api/llm/multiagent/orchestrator.py
# ==========================================

import json
import logging
import asyncio
import time
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session

from .models import (
    AgentTask, AgentResult, ExecutionPlan, ExecutionSummary,
    TaskStatus, AgentRole
)
from .config import MultiAgentConfig
from .validators import ValidatorFactory
from .task_manager import TaskManager
from ..providers.base_provider import BaseLLMProvider

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """Orquestrador principal do sistema multiagentes"""
    
    def __init__(self, tools: List, llm_provider: BaseLLMProvider, config: MultiAgentConfig = None):
        self.tools = {tool.name: tool for tool in tools}
        self.llm_provider = llm_provider
        self.config = config or MultiAgentConfig()
        self.task_manager = TaskManager(self.config)
        self.validator_factory = ValidatorFactory()
        
        # Estatísticas de execução
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'total_tasks_executed': 0,
            'average_execution_time': 0.0
        }
    
    async def coordinate_agents(self, tool_calls: List[Dict]) -> ExecutionSummary:
        """Coordena a execução de múltiplos agentes"""
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando coordenação de {len(tool_calls)} tool calls")
            
            # 1. Criar tarefas a partir dos tool calls
            tasks = self.task_manager.create_tasks_from_tool_calls(tool_calls)
            logger.info(f"Criadas {len(tasks)} tarefas")
            
            # 2. Criar plano de execução
            execution_plan = self.task_manager.create_execution_plan(tasks)
            
            # 3. Validar plano
            plan_warnings = self.task_manager.validate_execution_plan(execution_plan)
            if plan_warnings:
                logger.warning(f"Warnings no plano: {plan_warnings}")
            
            # 4. Executar tarefas
            results = await self._execute_plan(execution_plan)
            
            # 5. Validar resultados
            validated_results = await self._validate_results(results)
            
            # 6. Criar sumário
            execution_time = time.time() - start_time
            summary = self._create_execution_summary(validated_results, execution_time)
            
            # 7. Atualizar estatísticas
            self._update_stats(summary, execution_time)
            
            logger.info(f"Coordenação concluída em {execution_time:.2f}s - "
                       f"Sucesso: {summary.success_rate:.1f}%")
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro na coordenação de agentes: {str(e)}")
            execution_time = time.time() - start_time
            
            # Retorna sumário de erro
            return ExecutionSummary(
                total_tasks=len(tool_calls),
                successful_tasks=0,
                failed_tasks=len(tool_calls),
                total_execution_time=execution_time,
                agents_used={},
                errors=[str(e)]
            )
    
    async def _execute_plan(self, plan: ExecutionPlan) -> List[AgentResult]:
        """Executa o plano de execução"""
        all_results = []
        completed_tasks = set()
        
        logger.info(f"Executando plano com {len(plan.levels)} níveis")
        
        for priority_level in sorted(plan.levels.keys()):
            level_tasks = plan.levels[priority_level]
            
            # Filtra tarefas prontas para execução
            ready_tasks = plan.get_ready_tasks(priority_level, completed_tasks)
            
            if not ready_tasks:
                logger.warning(f"Nenhuma tarefa pronta no nível {priority_level}")
                continue
            
            logger.info(f"Executando {len(ready_tasks)} tarefas no nível {priority_level}")
            
            # Executa tarefas do nível em paralelo (com limite)
            level_results = await self._execute_level_tasks(ready_tasks, all_results)
            
            # Processa resultados do nível
            for result in level_results:
                all_results.append(result)
                if result.success:
                    completed_tasks.add(result.task_id)
                    logger.debug(f"Tarefa {result.task_id} concluída com sucesso")
                else:
                    logger.warning(f"Tarefa {result.task_id} falhou: {result.error_message}")
        
        return all_results
    
    async def _execute_level_tasks(
        self, 
        tasks: List[AgentTask], 
        previous_results: List[AgentResult]
    ) -> List[AgentResult]:
        """Executa tarefas de um nível em paralelo"""
        
        # Limita paralelização conforme configuração
        semaphore = asyncio.Semaphore(self.config.MAX_PARALLEL_TASKS)
        
        async def execute_with_semaphore(task: AgentTask):
            async with semaphore:
                return await self._execute_single_task(task, previous_results)
        
        # Executa tarefas
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Processa exceções
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exceção na execução: {result}")
                processed_results.append(
                    AgentResult(
                        task_id=tasks[i].task_id,
                        agent_role=tasks[i].agent_role,
                        tool_name=tasks[i].tool_name,
                        success=False,
                        result=None,
                        error_message=str(result),
                        status=TaskStatus.FAILED
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_task(
        self, 
        task: AgentTask, 
        previous_results: List[AgentResult]
    ) -> AgentResult:
        """Executa uma única tarefa"""
        start_time = time.time()
        retry_count = 0
        
        task.status = TaskStatus.RUNNING
        
        while retry_count <= task.max_retries:
            try:
                logger.debug(f"Executando {task.agent_role.value}: {task.tool_name} (tentativa {retry_count + 1})")
                
                # Enriquece argumentos com resultados de dependências
                enriched_args = self._enrich_task_arguments(task, previous_results)
                
                # Busca e executa a ferramenta
                tool = self.tools.get(task.tool_name)
                if not tool:
                    raise Exception(f"Ferramenta '{task.tool_name}' não encontrada")
                
                # Executa com timeout
                result = await asyncio.wait_for(
                    asyncio.create_task(self._invoke_tool_async(tool, enriched_args)),
                    timeout=task.timeout_seconds
                )
                
                execution_time = time.time() - start_time
                
                return AgentResult(
                    task_id=task.task_id,
                    agent_role=task.agent_role,
                    tool_name=task.tool_name,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    retry_count=retry_count,
                    status=TaskStatus.COMPLETED,
                    metadata={
                        "enriched_args_count": len(enriched_args),
                        "dependencies_used": len(task.dependencies)
                    }
                )
                
            except asyncio.TimeoutError:
                retry_count += 1
                if retry_count > task.max_retries:
                    execution_time = time.time() - start_time
                    logger.error(f"Timeout na execução de {task.tool_name} após {task.max_retries} tentativas")
                    
                    return AgentResult(
                        task_id=task.task_id,
                        agent_role=task.agent_role,
                        tool_name=task.tool_name,
                        success=False,
                        result=None,
                        error_message=f"Timeout após {task.timeout_seconds}s",
                        execution_time=execution_time,
                        retry_count=retry_count - 1,
                        status=TaskStatus.FAILED
                    )
                
                logger.warning(f"Timeout em {task.tool_name}, tentando novamente...")
                await asyncio.sleep(1)  # Pausa antes da próxima tentativa
                
            except Exception as e:
                retry_count += 1
                if retry_count > task.max_retries:
                    execution_time = time.time() - start_time
                    logger.error(f"Erro na execução de {task.tool_name}: {str(e)}")
                    
                    return AgentResult(
                        task_id=task.task_id,
                        agent_role=task.agent_role,
                        tool_name=task.tool_name,
                        success=False,
                        result=None,
                        error_message=str(e),
                        execution_time=execution_time,
                        retry_count=retry_count - 1,
                        status=TaskStatus.FAILED
                    )
                
                logger.warning(f"Erro em {task.tool_name}, tentando novamente: {str(e)}")
                await asyncio.sleep(1)
        
        # Não deveria chegar aqui, mas por segurança
        execution_time = time.time() - start_time
        return AgentResult(
            task_id=task.task_id,
            agent_role=task.agent_role,
            tool_name=task.tool_name,
            success=False,
            result=None,
            error_message="Máximo de tentativas excedido",
            execution_time=execution_time,
            retry_count=task.max_retries,
            status=TaskStatus.FAILED
        )
    
    async def _invoke_tool_async(self, tool, args):
        """Invoca ferramenta de forma assíncrona"""
        # Se a ferramenta for assíncrona, chama diretamente
        if asyncio.iscoroutinefunction(tool.invoke):
            return await tool.invoke(args)
        else:
            # Executa em thread pool para não bloquear
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool.invoke, args)
    
    def _enrich_task_arguments(
        self, 
        task: AgentTask, 
        previous_results: List[AgentResult]
    ) -> Dict[str, Any]:
        """Enriquece argumentos da tarefa com resultados de dependências"""
        enriched_args = task.arguments.copy()
        
        # Mapeia dependências para resultados
        dependency_results = {}
        for result in previous_results:
            if result.task_id in task.dependencies and result.success:
                dependency_results[result.task_id] = result.result
        
        # Adiciona resultados de dependências aos argumentos
        if dependency_results:
            enriched_args["dependency_results"] = dependency_results
            
            # Para compatibilidade, também adiciona individualmente
            for dep_id, dep_result in dependency_results.items():
                # Encontra o nome da ferramenta pela task_id
                dep_tool_name = None
                for result in previous_results:
                    if result.task_id == dep_id:
                        dep_tool_name = result.tool_name
                        break
                
                if dep_tool_name:
                    enriched_args[f"dependency_{dep_tool_name}_result"] = dep_result
        
        return enriched_args
    
    async def _validate_results(self, results: List[AgentResult]) -> List[AgentResult]:
        """Valida resultados dos agentes"""
        validated_results = []
        
        for result in results:
            if result.success:
                validator = self.validator_factory.get_validator(result.agent_role)
                try:
                    is_valid = await validator.validate(result)
                    if not is_valid:
                        logger.warning(f"Resultado de {result.tool_name} não passou na validação")
                        result.success = False
                        result.error_message = "Falha na validação do resultado"
                        result.status = TaskStatus.FAILED
                except Exception as e:
                    logger.error(f"Erro durante validação: {str(e)}")
                    # Mantém o resultado como válido se houve erro na validação
            
            validated_results.append(result)
        
        return validated_results
    
    def _create_execution_summary(
        self, 
        results: List[AgentResult], 
        total_time: float
    ) -> ExecutionSummary:
        """Cria sumário da execução"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        # Conta agentes utilizados
        agents_used = {}
        for result in results:
            role = result.agent_role
            agents_used[role] = agents_used.get(role, 0) + 1
        
        # Coleta erros
        errors = [r.error_message for r in failed_results if r.error_message]
        
        # Métricas de performance
        performance_metrics = {
            "average_task_time": total_time / len(results) if results else 0,
            "fastest_task": min(r.execution_time for r in results) if results else 0,
            "slowest_task": max(r.execution_time for r in results) if results else 0,
            "retry_rate": sum(r.retry_count for r in results) / len(results) if results else 0,
        }
        
        return ExecutionSummary(
            total_tasks=len(results),
            successful_tasks=len(successful_results),
            failed_tasks=len(failed_results),
            total_execution_time=total_time,
            agents_used=agents_used,
            errors=errors,
            performance_metrics=performance_metrics
        )
    
    def _update_stats(self, summary: ExecutionSummary, execution_time: float):
        """Atualiza estatísticas de execução"""
        self.execution_stats['total_executions'] += 1
        if summary.failed_tasks == 0:
            self.execution_stats['successful_executions'] += 1
        
        self.execution_stats['total_tasks_executed'] += summary.total_tasks
        
        # Atualiza média de tempo
        total_execs = self.execution_stats['total_executions']
        current_avg = self.execution_stats['average_execution_time']
        self.execution_stats['average_execution_time'] = (
            (current_avg * (total_execs - 1) + execution_time) / total_execs
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do orquestrador"""
        stats = self.execution_stats.copy()
        if stats['total_executions'] > 0:
            stats['success_rate'] = (
                stats['successful_executions'] / stats['total_executions'] * 100
            )
            stats['average_tasks_per_execution'] = (
                stats['total_tasks_executed'] / stats['total_executions']
            )
        else:
            stats['success_rate'] = 0.0
            stats['average_tasks_per_execution'] = 0.0
        
        return stats