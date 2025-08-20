# ==========================================
# backend/app/api/llm/services/conversation_service.py
# ==========================================

import json
import logging
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

from ..providers.base_provider import BaseLLMProvider
from ..tools.functions import get_tools, set_db_session
from .rag_service import RAGService
from ..multiagent.orchestrator import MultiAgentOrchestrator
from ..multiagent.config import MultiAgentConfig
from ..multiagent.models import ExecutionSummary

logger = logging.getLogger(__name__)


class ConversationService:
    """Serviço principal para processamento de conversas com sistema multiagentes avançado"""
    
    def __init__(self, llm_provider: BaseLLMProvider, rag_service: RAGService):
        self.llm_provider = llm_provider
        self.rag_service = rag_service
        self._tools = get_tools()
        
        # Configura sistema multiagentes
        self.multiagent_config = MultiAgentConfig()
        self.orchestrator = MultiAgentOrchestrator(
            tools=self._tools,
            llm_provider=llm_provider,
            config=self.multiagent_config
        )
        
        # Vincula as ferramentas ao provedor LLM
        self.llm_provider.bind_tools(self._tools)
        
        logger.info(f"ConversationService inicializado com {len(self._tools)} ferramentas")
    
    def _get_tool_by_name(self, tool_name: str):
        """Busca uma ferramenta pelo nome"""
        for tool in self._tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def _create_system_prompt(self, context: str) -> str:
        """Cria o prompt do sistema com o contexto e informações sobre agentes"""
        available_agents = list(self.multiagent_config.TOOL_TO_AGENT.values())
        unique_agents = list(set(agent.value for agent in available_agents))
        
        return f"""
        Você é um assistente financeiro inteligente com acesso a um sistema multiagentes especializado.

        SISTEMA MULTIAGENTES DISPONÍVEL:
        - Recuperador de Dados: busca informações financeiras, dados de mercado, informações de empresas
        - Calculadora Financeira: realiza cálculos de métricas, ratios, retornos e valuations
        - Analista Financeiro: gera análises avançadas, insights estratégicos e análises comparativas
        - Avaliador de Riscos: análises de risco, VaR, stress testing
        - Validador: verifica consistência e qualidade dos dados
        - Verificador de Compliance: validações regulatórias e de conformidade

        CAPACIDADES DO SISTEMA:
        - Execução paralela de múltiplas análises quando possível
        - Detecção automática de dependências entre operações
        - Validação automática de resultados
        - Sistema de retry para operações que falham
        - Consolidação inteligente de resultados de múltiplos agentes

        INSTRUÇÕES:
        - Use o contexto fornecido e o sistema multiagentes para fornecer análises financeiras completas
        - Quando uma pergunta requer múltiplas operações, o sistema executará automaticamente todos os agentes necessários
        - Seja transparente sobre quais agentes foram utilizados e como os resultados foram obtidos
        - Se detectar inconsistências nos resultados, mencione-as explicitamente
        - Forneça recomendações acionáveis baseadas nas análises realizadas
        - Para análises complexas, explique a metodologia utilizada pelos agentes

        CONTEXTO DISPONÍVEL:
        {context or "Nenhum contexto específico encontrado na base de conhecimento."}
        """
    
    async def process_conversation(
        self, 
        message: str, 
        user_id: str, 
        db_session: Session
    ) -> Tuple[str, str]:
        """
        Processa uma conversa completa com sistema multiagentes avançado
        """
        logger.info(f"Processando mensagem do usuário {user_id}: {message}")
        
        try:
            # 1. Configura a sessão do banco para as ferramentas
            set_db_session(db_session)
            
            # 2. Busca contexto relevante
            context = await self.rag_service.get_relevant_context(message)
            logger.info(f"Contexto RAG encontrado: {len(context)} caracteres")
            
            # 3. Cria as mensagens iniciais
            system_prompt = self._create_system_prompt(context)
            messages = [
                HumanMessage(content=system_prompt),
                HumanMessage(content=message),
            ]
            
            # 4. Invoca o LLM para primeira resposta
            logger.info(f"Invocando LLM ({self.llm_provider.provider_name})")
            response = await self.llm_provider.invoke(messages)
            logger.info(f"Resposta inicial recebida: {type(response)}")
            
            final_response_text = ""
            
            # 5. Verifica se há chamadas de ferramentas
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Detectadas {len(response.tool_calls)} tool calls - iniciando sistema multiagentes")
                final_response_text = await self._handle_multiagent_execution(
                    response, messages
                )
            else:
                # Resposta direta sem ferramentas
                final_response_text = response.content
                logger.info("Resposta direta sem uso de ferramentas")
            
            # 6. Salva a conversa no grafo
            await self.rag_service.save_conversation(
                user_id=user_id,
                question=message,
                answer=final_response_text,
                context=context
            )
            
            return final_response_text.strip(), context
            
        except Exception as e:
            logger.error(f"Erro no processamento da conversa: {str(e)}", exc_info=True)
            error_message = "Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente."
            return error_message, ""
    
    async def _handle_multiagent_execution(self, response, messages) -> str:
        """Executa sistema multiagentes e processa resultados"""
        try:
            # 1. Orquestra a execução dos agentes
            logger.info("Iniciando orquestração multiagentes")
            execution_summary = await self.orchestrator.coordinate_agents(response.tool_calls)
            
            # 2. Converte resultados para ToolMessages
            tool_messages = self._create_tool_messages_from_summary(
                execution_summary, response.tool_calls
            )
            
            # 3. Cria relatório de execução para o LLM
            execution_report = self._create_execution_report(execution_summary)
            
            # 4. Atualiza histórico de mensagens
            messages.extend([response] + tool_messages)
            
            # 5. Adiciona relatório de execução se relevante
            if execution_summary.failed_tasks > 0 or len(execution_summary.agents_used) > 1:
                messages.append(
                    HumanMessage(content=f"RELATÓRIO DE EXECUÇÃO DO SISTEMA MULTIAGENTES:\n{execution_report}")
                )
            
            # 6. Solicita resposta final consolidada
            logger.info("Solicitando resposta final do LLM")
            final_response = await self.llm_provider.invoke(messages)
            
            logger.info(f"Sistema multiagentes concluído - Sucesso: {execution_summary.success_rate:.1f}%")
            
            return final_response.content
            
        except Exception as e:
            logger.error(f"Erro no sistema multiagentes: {str(e)}", exc_info=True)
            return f"Ocorreu um erro no processamento multiagentes. Detalhes técnicos foram registrados para análise."
    
    def _create_tool_messages_from_summary(
        self, 
        summary: ExecutionSummary, 
        original_tool_calls: List[dict]
    ) -> List[ToolMessage]:
        """Cria ToolMessages a partir do sumário de execução"""
        tool_messages = []
        
        # Mapeia tool calls para obter IDs corretos
        tool_call_map = {call["name"]: call.get("id", "unknown") for call in original_tool_calls}
        
        # Cria uma mensagem consolidada com todos os resultados
        consolidated_results = {
            "execution_summary": summary.to_dict(),
            "results_by_agent": {},
            "status": "success" if summary.failed_tasks == 0 else "partial_success"
        }
        
        # Para cada tool call original, cria uma mensagem
        for tool_call in original_tool_calls:
            tool_name = tool_call["name"]
            tool_call_id = tool_call_map.get(tool_name, "unknown")
            
            # Simula resultado baseado no sumário
            # (Na implementação real, você manteria os resultados individuais)
            tool_result = {
                "tool_name": tool_name,
                "status": "completed",
                "execution_time": summary.total_execution_time / summary.total_tasks,
                "message": f"Processado pelo sistema multiagentes"
            }
            
            content = json.dumps(tool_result, ensure_ascii=False)
            tool_messages.append(ToolMessage(content=content, tool_call_id=tool_call_id))
        
        return tool_messages
    
    def _create_execution_report(self, summary: ExecutionSummary) -> str:
        """Cria relatório detalhado da execução para o LLM"""
        report_parts = [
            f"EXECUÇÃO MULTIAGENTES CONCLUÍDA:",
            f"- Total de tarefas: {summary.total_tasks}",
            f"- Sucessos: {summary.successful_tasks}",
            f"- Falhas: {summary.failed_tasks}",
            f"- Taxa de sucesso: {summary.success_rate:.1f}%",
            f"- Tempo total: {summary.total_execution_time:.2f}s"
        ]
        
        if summary.agents_used:
            report_parts.append("\nAGENTES UTILIZADOS:")
            for agent_role, count in summary.agents_used.items():
                role_name = agent_role.value if hasattr(agent_role, 'value') else str(agent_role)
                report_parts.append(f"- {role_name}: {count} tarefa(s)")
        
        if summary.performance_metrics:
            metrics = summary.performance_metrics
            report_parts.append(f"\nMÉTRICAS DE PERFORMANCE:")
            report_parts.append(f"- Tempo médio por tarefa: {metrics.get('average_task_time', 0):.2f}s")
            report_parts.append(f"- Tarefa mais rápida: {metrics.get('fastest_task', 0):.2f}s")
            report_parts.append(f"- Tarefa mais lenta: {metrics.get('slowest_task', 0):.2f}s")
            if metrics.get('retry_rate', 0) > 0:
                report_parts.append(f"- Taxa de retry: {metrics.get('retry_rate', 0):.1f}")
        
        if summary.errors:
            report_parts.append(f"\nERROS ENCONTRADOS:")
            for error in summary.errors[:3]:  # Limita a 3 erros
                report_parts.append(f"- {error}")
            if len(summary.errors) > 3:
                report_parts.append(f"- ... e mais {len(summary.errors) - 3} erro(s)")
        
        return "\n".join(report_parts)
    
    def get_provider_info(self) -> dict:
        """Retorna informações sobre o provedor LLM atual"""
        return self.llm_provider.get_model_info()
    
    def get_multiagent_stats(self) -> dict:
        """Retorna estatísticas do sistema multiagentes"""
        return self.orchestrator.get_statistics()
    
    async def health_check(self) -> dict:
        """
        Verifica a saúde do serviço de conversação e sistema multiagentes
        """
        status = {
            "conversation_service": "healthy",
            "llm_provider": self.llm_provider.get_model_info(),
            "tools_count": len(self._tools),
            "tools_available": [tool.name for tool in self._tools],
            "multiagent_system": "enabled",
            "multiagent_config": {
                "max_parallel_tasks": self.multiagent_config.MAX_PARALLEL_TASKS,
                "default_timeout": self.multiagent_config.DEFAULT_TIMEOUT,
                "max_retries": self.multiagent_config.MAX_RETRIES,
                "supported_agents": list(set(role.value for role in self.multiagent_config.TOOL_TO_AGENT.values()))
            }
        }
        
        try:
            # Testa conexão LLM
            test_messages = [HumanMessage(content="Health check test.")]
            await self.llm_provider.invoke(test_messages)
            status["llm_connection"] = "healthy"
            
            # Adiciona estatísticas do multiagente
            status["multiagent_stats"] = self.get_multiagent_stats()
            
        except Exception as e:
            status["llm_connection"] = f"error: {str(e)}"
            status["conversation_service"] = "unhealthy"
        
        return status