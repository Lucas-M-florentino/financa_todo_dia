# ==========================================
# backend/app/api/llm/services/hybrid_conversation_service.py
# ==========================================

import logging
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from ..providers.base_provider import BaseLLMProvider
from ..tools.functions import get_tools, set_db_session
from ..services.rag_service import RAGService
from ..multiagent.orchestrator import MultiAgentOrchestrator
from ..multiagent.config import MultiAgentConfig
from ..multiagent.langgraph_implementation import LangGraphFinancialMultiAgent, LANGGRAPH_AVAILABLE

logger = logging.getLogger(__name__)


class HybridConversationService:
    """
    Serviço híbrido que usa LangGraph quando disponível e apropriado,
    ou fallback para implementação customizada
    """
    
    def __init__(self, llm_provider: BaseLLMProvider, rag_service: RAGService):
        self.llm_provider = llm_provider
        self.rag_service = rag_service
        self._tools = get_tools()
        
        # Configuração multiagentes customizada
        self.multiagent_config = MultiAgentConfig()
        self.custom_orchestrator = MultiAgentOrchestrator(
            tools=self._tools,
            llm_provider=llm_provider,
            config=self.multiagent_config
        )
        
        # LangGraph (se disponível)
        self.langgraph_agent = None
        if LANGGRAPH_AVAILABLE:
            try:
                self.langgraph_agent = LangGraphFinancialMultiAgent(llm_provider)
                logger.info("LangGraph MultiAgent inicializado com sucesso")
            except Exception as e:
                logger.warning(f"Falha ao inicializar LangGraph: {str(e)}. Usando implementação customizada.")
        
        # Vincula ferramentas ao LLM
        self.llm_provider.bind_tools(self._tools)
        
        # Estratégias de escolha de implementação
        self.complexity_threshold = 3  # Número de tool_calls para considerar "complexo"
        self.prefer_langgraph = True  # Preferir LangGraph quando disponível
    
    def _should_use_langgraph(self, tool_calls: list, user_query: str) -> bool:
        """Decide se deve usar LangGraph ou implementação customizada"""
        
        if not self.langgraph_agent or not self.prefer_langgraph:
            return False
        
        # Critérios para usar LangGraph:
        
        # 1. Queries complexas com múltiplas ferramentas
        if len(tool_calls) >= self.complexity_threshold:
            logger.info(f"Usando LangGraph: {len(tool_calls)} tool calls (complexidade alta)")
            return True
        
        # 2. Queries que indicam fluxos complexos
        complex_keywords = [
            "análise completa", "relatório detalhado", "avaliação integral",
            "múltiplas análises", "comparativo", "benchmarking",
            "risco e retorno", "análise de cenários"
        ]
        
        if any(keyword in user_query.lower() for keyword in complex_keywords):
            logger.info("Usando LangGraph: query indica análise complexa")
            return True
        
        # 3. Dependências entre ferramentas detectadas
        dependency_patterns = [
            ("get_financial_data", "calculate_metrics"),
            ("calculate_metrics", "analyze_portfolio"),
            ("analyze_portfolio", "risk_assessment")
        ]
        
        tool_names = [call["name"] for call in tool_calls]
        for dep1, dep2 in dependency_patterns:
            if dep1 in tool_names and dep2 in tool_names:
                logger.info("Usando LangGraph: dependências complexas detectadas")
                return True
        
        # 4. Para queries simples, usar implementação customizada (mais rápida)
        logger.info("Usando implementação customizada: query simples")
        return False
    
    async def process_conversation(
        self, 
        message: str, 
        user_id: str, 
        db_session: Session
    ) -> Tuple[str, str]:
        """
        Processa conversa usando estratégia híbrida
        """
        logger.info(f"Processando mensagem híbrida do usuário {user_id}: {message}")
        
        try:
            # 1. Configura sessão do banco
            set_db_session(db_session)
            
            # 2. Busca contexto RAG
            context = await self.rag_service.get_relevant_context(message)
            logger.info(f"Contexto RAG: {len(context)} caracteres")
            
            # 3. Primeira invocação do LLM para identificar ferramentas necessárias
            system_prompt = self._create_hybrid_system_prompt(context)
            messages = [
                HumanMessage(content=system_prompt),
                HumanMessage(content=message),
            ]
            
            response = await self.llm_provider.invoke(messages)
            
            final_response_text = ""
            
            # 4. Processa baseado na presença de tool_calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Decide qual implementação usar
                use_langgraph = self._should_use_langgraph(response.tool_calls, message)
                
                if use_langgraph:
                    final_response_text = await self._process_with_langgraph(
                        message, user_id, context, response, messages
                    )
                else:
                    final_response_text = await self._process_with_custom_orchestrator(
                        response, messages
                    )
            else:
                # Resposta direta
                final_response_text = response.content
                logger.info("Resposta direta sem ferramentas")
            
            # 5. Salva conversa
            await self.rag_service.save_conversation(
                user_id=user_id,
                question=message,
                answer=final_response_text,
                context=context
            )
            
            return final_response_text.strip(), context
            
        except Exception as e:
            logger.error(f"Erro no processamento híbrido: {str(e)}", exc_info=True)
            return "Desculpe, ocorreu um erro ao processar sua solicitação. Tente novamente.", ""
    
    async def _process_with_langgraph(
        self, 
        message: str, 
        user_id: str, 
        context: str,
        response,
        messages
    ) -> str:
        """Processa usando LangGraph"""
        
        logger.info("Processando com LangGraph")
        
        try:
            result = await self.langgraph_agent.process_financial_query(
                user_query=message,
                user_id=user_id,
                context=context
            )
            
            response_text = result.get("response", "")
            execution_summary = result.get("execution_summary", {})
            
            # Log de performance
            if execution_summary:
                success_rate = execution_summary.get("success_rate", 0)
                agents_used = len(result.get("agents_completed", []))
                logger.info(f"LangGraph concluído - Agentes: {agents_used}, Sucesso: {success_rate}%")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Erro no LangGraph, fallback para implementação customizada: {str(e)}")
            # Fallback para implementação customizada
            return await self._process_with_custom_orchestrator(response, messages)
    
    async def _process_with_custom_orchestrator(self, response, messages) -> str:
        """Processa usando orquestrador customizado"""
        
        logger.info("Processando com orquestrador customizado")
        
        try:
            # Usa a implementação original
            execution_summary = await self.custom_orchestrator.coordinate_agents(response.tool_calls)
            
            # Converte para tool messages
            tool_messages = self._create_tool_messages_from_summary(execution_summary, response.tool_calls)
            
            # Atualiza mensagens e solicita resposta final
            messages.extend([response] + tool_messages)
            
            if execution_summary.failed_tasks > 0:
                execution_report = self._create_execution_report(execution_summary)
                messages.append(HumanMessage(content=f"RELATÓRIO: {execution_report}"))
            
            final_response = await self.llm_provider.invoke(messages)
            
            logger.info(f"Orquestrador customizado concluído - Sucesso: {execution_summary.success_rate:.1f}%")
            
            return final_response.content
            
        except Exception as e:
            logger.error(f"Erro no orquestrador customizado: {str(e)}")
            return f"Erro no processamento multiagentes: {str(e)}"
    
    def _create_hybrid_system_prompt(self, context: str) -> str:
        """Cria prompt otimizado para o sistema híbrido"""
        
        system_features = []
        
        if self.langgraph_agent:
            system_features.append("- Sistema LangGraph para análises complexas com fluxos otimizados")
        
        system_features.append("- Orquestrador customizado para operações especializadas")
        system_features.append("- Seleção automática da melhor estratégia de processamento")
        
        return f"""
        Você é um assistente financeiro avançado com sistema multiagentes híbrido.

        CAPACIDADES DO SISTEMA:
        {chr(10).join(system_features)}

        AGENTES ESPECIALIZADOS DISPONÍVEIS:
        - 📊 Recuperador de Dados: informações financeiras, mercado, empresas
        - 🧮 Calculadora: métricas, ratios, retornos, valuations
        - 📈 Analista Financeiro: insights, análises estratégicas, recomendações
        - ⚠️ Avaliador de Riscos: VaR, stress testing, análise de volatilidade
        - ✅ Validador: consistência de dados e resultados
        - 📋 Compliance: verificações regulatórias

        OTIMIZAÇÕES AUTOMÁTICAS:
        - Execução paralela quando possível
        - Detecção inteligente de dependências
        - Validação automática de resultados
        - Retry automático em falhas transitórias
        - Seleção da estratégia mais eficiente

        CONTEXTO:
        {context or "Nenhum contexto específico disponível."}
        """
    
    def _create_tool_messages_from_summary(self, summary, tool_calls):
        """Converte sumário de execução para ToolMessages (implementação simplificada)"""
        # Reutiliza a lógica do ConversationService original
        from langchain_core.messages import ToolMessage
        import json
        
        tool_messages = []
        tool_call_map = {call["name"]: call.get("id", "unknown") for call in tool_calls}
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_call_id = tool_call_map.get(tool_name, "unknown")
            
            content = json.dumps({
                "tool_name": tool_name,
                "status": "processed",
                "execution_summary": summary.to_dict()
            }, ensure_ascii=False)
            
            tool_messages.append(ToolMessage(content=content, tool_call_id=tool_call_id))
        
        return tool_messages
    
    def _create_execution_report(self, summary) -> str:
        """Cria relatório de execução"""
        return f"""
        Execução concluída:
        - Tarefas: {summary.total_tasks}
        - Sucessos: {summary.successful_tasks}  
        - Taxa: {summary.success_rate:.1f}%
        - Tempo: {summary.total_execution_time:.2f}s
        """
    def get_provider_info(self) -> dict:
        """Retorna informações sobre o provedor LLM atual"""
        return self.llm_provider.get_model_info()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o sistema híbrido"""
        info = {
            "type": "hybrid_multiagent_system",
            "langgraph_available": self.langgraph_agent is not None,
            "custom_orchestrator": True,
            "tools_count": len(self._tools),
            "complexity_threshold": self.complexity_threshold,
            "prefer_langgraph": self.prefer_langgraph
        }
        
        if self.langgraph_agent:
            info["langgraph_features"] = [
                "state_management",
                "conditional_routing", 
                "parallel_execution",
                "checkpoints",
                "visual_debugging"
            ]
        
        info["custom_features"] = [
            "specialized_validators",
            "performance_analytics", 
            "retry_mechanisms",
            "dependency_detection",
            "execution_statistics"
        ]
        
        return info
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check do sistema híbrido"""
        status = {
            "service": "hybrid_multiagent_conversation",
            "status": "healthy",
            "llm_provider": self.llm_provider.get_model_info(),
            "tools_available": len(self._tools),
            "implementations": {
                "custom_orchestrator": "available",
                "langgraph": "available" if self.langgraph_agent else "unavailable"
            }
        }
        
        try:
            # Testa LLM
            test_messages = [HumanMessage(content="Health check")]
            await self.llm_provider.invoke(test_messages)
            status["llm_connection"] = "healthy"
            
            # Testa orquestrador customizado
            custom_stats = self.custom_orchestrator.get_statistics()
            status["custom_orchestrator_stats"] = custom_stats
            
            # Informações do sistema
            status["system_info"] = self.get_system_info()
            
        except Exception as e:
            status["status"] = "unhealthy"
            status["error"] = str(e)
        
        return status
    
    def configure_strategy(self, 
                          complexity_threshold: int = None, 
                          prefer_langgraph: bool = None):
        """Permite configurar a estratégia de seleção"""
        if complexity_threshold is not None:
            self.complexity_threshold = complexity_threshold
            
        if prefer_langgraph is not None:
            self.prefer_langgraph = prefer_langgraph
        
        logger.info(f"Estratégia atualizada - Threshold: {self.complexity_threshold}, "
                   f"Preferir LangGraph: {self.prefer_langgraph}")


# ==========================================
# BENCHMARK E COMPARAÇÃO DE PERFORMANCE
# ==========================================

class MultiAgentBenchmark:
    """Classe para benchmark entre diferentes implementações"""
    
    def __init__(self, hybrid_service: HybridConversationService):
        self.hybrid_service = hybrid_service
        self.benchmark_results = []
    
    async def run_benchmark(self, test_queries: list, iterations: int = 3):
        """Executa benchmark comparativo"""
        
        for query in test_queries:
            query_results = {
                "query": query,
                "langgraph_results": [],
                "custom_results": []
            }
            
            for i in range(iterations):
                # Força uso do LangGraph
                original_prefer = self.hybrid_service.prefer_langgraph
                self.hybrid_service.prefer_langgraph = True
                
                try:
                    import time
                    start_time = time.time()
                    
                    # Simula processamento (sem salvar no banco)
                    # Implementar lógica de benchmark aqui
                    
                    execution_time = time.time() - start_time
                    query_results["langgraph_results"].append({
                        "iteration": i + 1,
                        "execution_time": execution_time,
                        "success": True
                    })
                    
                except Exception as e:
                    query_results["langgraph_results"].append({
                        "iteration": i + 1,
                        "execution_time": 0,
                        "success": False,
                        "error": str(e)
                    })
                
                # Força uso do customizado
                self.hybrid_service.prefer_langgraph = False
                
                try:
                    start_time = time.time()
                    
                    # Simula processamento customizado
                    
                    execution_time = time.time() - start_time
                    query_results["custom_results"].append({
                        "iteration": i + 1,
                        "execution_time": execution_time,
                        "success": True
                    })
                    
                except Exception as e:
                    query_results["custom_results"].append({
                        "iteration": i + 1,
                        "execution_time": 0,
                        "success": False,
                        "error": str(e)
                    })
                
                # Restaura configuração original
                self.hybrid_service.prefer_langgraph = original_prefer
            
            self.benchmark_results.append(query_results)
        
        return self.analyze_benchmark_results()
    
    def analyze_benchmark_results(self):
        """Analisa resultados do benchmark"""
        if not self.benchmark_results:
            return {"message": "Nenhum benchmark executado"}
        
        analysis = {
            "total_queries": len(self.benchmark_results),
            "langgraph_performance": {
                "average_time": 0,
                "success_rate": 0,
                "total_executions": 0
            },
            "custom_performance": {
                "average_time": 0,
                "success_rate": 0,
                "total_executions": 0
            },
            "recommendation": ""
        }
        
        # Calcula estatísticas
        lg_times = []
        lg_successes = 0
        custom_times = []
        custom_successes = 0
        
        for result in self.benchmark_results:
            for lg_result in result["langgraph_results"]:
                if lg_result["success"]:
                    lg_times.append(lg_result["execution_time"])
                    lg_successes += 1
            
            for custom_result in result["custom_results"]:
                if custom_result["success"]:
                    custom_times.append(custom_result["execution_time"])
                    custom_successes += 1
        
        # Análise LangGraph
        if lg_times:
            analysis["langgraph_performance"]["average_time"] = sum(lg_times) / len(lg_times)
        analysis["langgraph_performance"]["success_rate"] = (lg_successes / (len(self.benchmark_results) * 3)) * 100
        analysis["langgraph_performance"]["total_executions"] = len(self.benchmark_results) * 3
        
        # Análise Custom
        if custom_times:
            analysis["custom_performance"]["average_time"] = sum(custom_times) / len(custom_times)
        analysis["custom_performance"]["success_rate"] = (custom_successes / (len(self.benchmark_results) * 3)) * 100
        analysis["custom_performance"]["total_executions"] = len(self.benchmark_results) * 3
        
        # Recomendação
        lg_avg = analysis["langgraph_performance"]["average_time"]
        custom_avg = analysis["custom_performance"]["average_time"]
        lg_success = analysis["langgraph_performance"]["success_rate"]
        custom_success = analysis["custom_performance"]["success_rate"]
        
        if lg_success > custom_success and lg_avg < custom_avg * 1.5:
            analysis["recommendation"] = "LangGraph recomendado - melhor sucesso e performance aceitável"
        elif custom_avg < lg_avg * 0.7:
            analysis["recommendation"] = "Implementação customizada recomendada - significativamente mais rápida"
        else:
            analysis["recommendation"] = "Estratégia híbrida recomendada - usar baseado na complexidade"
        
        return analysis


# ==========================================
# EXEMPLO DE USO
# ==========================================

"""
# Exemplo de configuração e uso:

# Inicialização
llm_provider = SeuLLMProvider()
rag_service = SeuRAGService()

# Serviço híbrido
hybrid_service = HybridConversationService(llm_provider, rag_service)

# Processamento automático (escolhe a melhor estratégia)
response, context = await hybrid_service.process_conversation(
    message="Faça uma análise completa do portfólio XYZ incluindo riscos e recomendações",
    user_id="user_123",
    db_session=session
)

# Configuração manual da estratégia
hybrid_service.configure_strategy(
    complexity_threshold=2,  # Usar LangGraph com 2+ ferramentas
    prefer_langgraph=True    # Preferir LangGraph quando disponível
)

# Benchmark comparativo
benchmark = MultiAgentBenchmark(hybrid_service)
test_queries = [
    "Calcule as métricas do portfolio ABC",
    "Análise completa de risco e retorno da empresa XYZ",
    "Comparativo de performance entre fundos A, B e C"
]

results = await benchmark.run_benchmark(test_queries, iterations=3)
print(f"Recomendação: {results['recommendation']}")
"""