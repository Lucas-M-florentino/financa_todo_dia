# ==========================================
# backend/app/api/llm/multiagent/langgraph_implementation.py
# ==========================================

import json
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from datetime import datetime
import asyncio

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.prebuilt import create_react_agent
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    from langchain_core.tools import tool
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph não disponível. Usando implementação customizada.")

from ..providers.base_provider import BaseLLMProvider
from ..tools.functions import get_tools
from .models import AgentRole, ExecutionSummary

logger = logging.getLogger(__name__)


class FinancialAgentState(TypedDict):
    """Estado compartilhado entre agentes financeiros"""
    messages: List[Any]
    user_query: str
    context: str
    user_id: str
    
    # Dados coletados
    financial_data: Optional[Dict[str, Any]]
    market_data: Optional[Dict[str, Any]]
    company_info: Optional[Dict[str, Any]]
    
    # Resultados de cálculos
    calculated_metrics: Optional[Dict[str, Any]]
    ratios: Optional[Dict[str, Any]]
    returns: Optional[Dict[str, Any]]
    
    # Análises realizadas
    portfolio_analysis: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    performance_analysis: Optional[Dict[str, Any]]
    
    # Validações
    data_validation: Optional[Dict[str, Any]]
    compliance_check: Optional[Dict[str, Any]]
    
    # Controle de execução
    agents_completed: List[str]
    current_agent: str
    execution_metadata: Dict[str, Any]
    errors: List[str]
    next_action: Optional[str]


class LangGraphFinancialMultiAgent:
    """Implementação de sistema multiagentes usando LangGraph"""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph não disponível. Instale com: pip install langgraph")
        
        self.llm_provider = llm_provider
        self.tools = get_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Configuração de checkpoint para persistência
        self.checkpointer = MemorySaver()
        
        # Cria o grafo
        self.graph = self._create_financial_graph()
        
        # Compila o grafo
        self.compiled_graph = self.graph.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["risk_assessor"]  # Permite intervenção manual se necessário
        )
    
    def _create_financial_graph(self) -> StateGraph:
        """Cria o grafo de agentes financeiros"""
        
        # Define o grafo
        graph = StateGraph(FinancialAgentState)
        
        # Adiciona nós (agentes)
        graph.add_node("coordinator", self._coordinator_agent)
        graph.add_node("data_retriever", self._data_retriever_agent)
        graph.add_node("calculator", self._calculator_agent)
        graph.add_node("financial_analyst", self._financial_analyst_agent)
        graph.add_node("risk_assessor", self._risk_assessor_agent)
        graph.add_node("validator", self._validator_agent)
        graph.add_node("consolidator", self._consolidator_agent)
        
        # Define fluxo principal
        graph.add_edge(START, "coordinator")
        
        # Rotas condicionais baseadas na decisão do coordinator
        graph.add_conditional_edges(
            "coordinator",
            self._should_route_to_data_retriever,
            {
                "data_retriever": "data_retriever",
                "calculator": "calculator",
                "analyst": "financial_analyst",
                "validator": "validator",
                "end": "consolidator"
            }
        )
        
        # Fluxos de dados
        graph.add_conditional_edges(
            "data_retriever",
            self._after_data_retrieval,
            {
                "calculator": "calculator",
                "analyst": "financial_analyst",
                "coordinator": "coordinator"
            }
        )
        
        graph.add_conditional_edges(
            "calculator",
            self._after_calculation,
            {
                "analyst": "financial_analyst",
                "risk_assessor": "risk_assessor",
                "coordinator": "coordinator"
            }
        )
        
        graph.add_conditional_edges(
            "financial_analyst",
            self._after_analysis,
            {
                "risk_assessor": "risk_assessor",
                "validator": "validator",
                "coordinator": "coordinator"
            }
        )
        
        graph.add_conditional_edges(
            "risk_assessor",
            self._after_risk_assessment,
            {
                "validator": "validator",
                "coordinator": "coordinator"
            }
        )
        
        graph.add_conditional_edges(
            "validator",
            self._after_validation,
            {
                "consolidator": "consolidator",
                "data_retriever": "data_retriever",  # Re-executar se dados inválidos
                "coordinator": "coordinator"
            }
        )
        
        graph.add_edge("consolidator", END)
        
        return graph
    
    # ==========================================
    # AGENTES ESPECIALIZADOS
    # ==========================================
    
    async def _coordinator_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente coordenador que decide próximos passos"""
        
        logger.info("Executando agente coordenador")
        
        # Analisa o estado atual e decide próxima ação
        completed_agents = state.get("agents_completed", [])
        query = state.get("user_query", "")
        
        # Lógica de decisão baseada no estado atual
        if "data_retriever" not in completed_agents and self._needs_data_retrieval(query):
            next_action = "data_retriever"
        elif "calculator" not in completed_agents and self._needs_calculations(query, state):
            next_action = "calculator"
        elif "financial_analyst" not in completed_agents and self._needs_analysis(query, state):
            next_action = "analyst"
        elif "risk_assessor" not in completed_agents and self._needs_risk_assessment(query, state):
            next_action = "risk_assessor"
        elif "validator" not in completed_agents:
            next_action = "validator"
        else:
            next_action = "end"
        
        state["next_action"] = next_action
        state["current_agent"] = "coordinator"
        
        if "coordinator" not in completed_agents:
            state["agents_completed"].append("coordinator")
        
        logger.info(f"Coordenador decidiu próxima ação: {next_action}")
        
        return state
    
    async def _data_retriever_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente especializado em recuperação de dados"""
        
        logger.info("Executando agente recuperador de dados")
        
        try:
            # Identifica quais dados são necessários
            needed_data = self._identify_needed_data(state["user_query"])
            
            results = {}
            
            # Executa ferramentas de dados em paralelo
            data_tasks = []
            for data_type, tool_name in needed_data.items():
                if tool_name in self.tool_map:
                    task = self._execute_tool_async(tool_name, self._extract_args_for_tool(tool_name, state))
                    data_tasks.append((data_type, task))
            
            # Aguarda todos os resultados
            for data_type, task in data_tasks:
                try:
                    result = await task
                    results[data_type] = result
                except Exception as e:
                    logger.error(f"Erro ao buscar {data_type}: {str(e)}")
                    state["errors"].append(f"Falha na busca de {data_type}: {str(e)}")
            
            # Atualiza estado com os dados
            state["financial_data"] = results.get("financial_data")
            state["market_data"] = results.get("market_data")
            state["company_info"] = results.get("company_info")
            
            state["agents_completed"].append("data_retriever")
            state["current_agent"] = "data_retriever"
            
            logger.info(f"Dados recuperados: {list(results.keys())}")
            
        except Exception as e:
            logger.error(f"Erro no agente de dados: {str(e)}")
            state["errors"].append(f"Erro no recuperador de dados: {str(e)}")
        
        return state
    
    async def _calculator_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente especializado em cálculos financeiros"""
        
        logger.info("Executando agente calculadora")
        
        try:
            # Identifica cálculos necessários
            needed_calculations = self._identify_needed_calculations(state["user_query"], state)
            
            results = {}
            
            # Executa cálculos
            for calc_type, tool_name in needed_calculations.items():
                if tool_name in self.tool_map:
                    try:
                        args = self._extract_args_for_tool(tool_name, state)
                        result = await self._execute_tool_async(tool_name, args)
                        results[calc_type] = result
                    except Exception as e:
                        logger.error(f"Erro no cálculo {calc_type}: {str(e)}")
                        state["errors"].append(f"Falha no cálculo {calc_type}: {str(e)}")
            
            # Atualiza estado
            state["calculated_metrics"] = results.get("metrics")
            state["ratios"] = results.get("ratios")
            state["returns"] = results.get("returns")
            
            state["agents_completed"].append("calculator")
            state["current_agent"] = "calculator"
            
            logger.info(f"Cálculos realizados: {list(results.keys())}")
            
        except Exception as e:
            logger.error(f"Erro no agente calculadora: {str(e)}")
            state["errors"].append(f"Erro na calculadora: {str(e)}")
        
        return state
    
    async def _financial_analyst_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente especializado em análises financeiras"""
        
        logger.info("Executando agente analista financeiro")
        
        try:
            # Identifica análises necessárias
            needed_analyses = self._identify_needed_analyses(state["user_query"], state)
            
            results = {}
            
            # Executa análises
            for analysis_type, tool_name in needed_analyses.items():
                if tool_name in self.tool_map:
                    try:
                        args = self._extract_args_for_tool(tool_name, state)
                        result = await self._execute_tool_async(tool_name, args)
                        results[analysis_type] = result
                    except Exception as e:
                        logger.error(f"Erro na análise {analysis_type}: {str(e)}")
                        state["errors"].append(f"Falha na análise {analysis_type}: {str(e)}")
            
            # Atualiza estado
            state["portfolio_analysis"] = results.get("portfolio")
            state["performance_analysis"] = results.get("performance")
            
            state["agents_completed"].append("financial_analyst")
            state["current_agent"] = "financial_analyst"
            
            logger.info(f"Análises realizadas: {list(results.keys())}")
            
        except Exception as e:
            logger.error(f"Erro no agente analista: {str(e)}")
            state["errors"].append(f"Erro no analista: {str(e)}")
        
        return state
    
    async def _risk_assessor_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente especializado em avaliação de riscos"""
        
        logger.info("Executando agente avaliador de riscos")
        
        try:
            # Avaliações de risco
            risk_tools = ["risk_assessment", "calculate_var", "stress_testing"]
            
            results = {}
            
            for tool_name in risk_tools:
                if tool_name in self.tool_map:
                    try:
                        args = self._extract_args_for_tool(tool_name, state)
                        result = await self._execute_tool_async(tool_name, args)
                        results[tool_name] = result
                    except Exception as e:
                        logger.error(f"Erro na avaliação {tool_name}: {str(e)}")
                        state["errors"].append(f"Falha em {tool_name}: {str(e)}")
            
            # Consolida avaliação de risco
            state["risk_assessment"] = {
                "overall_assessment": results.get("risk_assessment"),
                "var_analysis": results.get("calculate_var"),
                "stress_test": results.get("stress_testing")
            }
            
            state["agents_completed"].append("risk_assessor")
            state["current_agent"] = "risk_assessor"
            
            logger.info("Avaliação de riscos concluída")
            
        except Exception as e:
            logger.error(f"Erro no agente de riscos: {str(e)}")
            state["errors"].append(f"Erro no avaliador de riscos: {str(e)}")
        
        return state
    
    async def _validator_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente especializado em validação"""
        
        logger.info("Executando agente validador")
        
        try:
            validation_results = {}
            
            # Valida dados
            if state.get("financial_data"):
                validation_results["data_quality"] = self._validate_data_quality(state["financial_data"])
            
            # Valida cálculos
            if state.get("calculated_metrics"):
                validation_results["calculation_validity"] = self._validate_calculations(state["calculated_metrics"])
            
            # Valida consistência
            validation_results["cross_validation"] = self._cross_validate_results(state)
            
            state["data_validation"] = validation_results
            
            state["agents_completed"].append("validator")
            state["current_agent"] = "validator"
            
            logger.info("Validação concluída")
            
        except Exception as e:
            logger.error(f"Erro no agente validador: {str(e)}")
            state["errors"].append(f"Erro no validador: {str(e)}")
        
        return state
    
    async def _consolidator_agent(self, state: FinancialAgentState) -> FinancialAgentState:
        """Agente que consolida todos os resultados"""
        
        logger.info("Executando agente consolidador")
        
        # Cria resposta consolidada
        consolidated_response = self._create_consolidated_response(state)
        
        # Adiciona resposta final às mensagens
        state["messages"].append(AIMessage(content=consolidated_response))
        
        state["agents_completed"].append("consolidator")
        state["current_agent"] = "consolidator"
        
        # Atualiza metadados de execução
        state["execution_metadata"]["completed_at"] = datetime.now().isoformat()
        state["execution_metadata"]["total_agents"] = len(state["agents_completed"])
        
        logger.info("Consolidação concluída")
        
        return state
    
    # ==========================================
    # FUNÇÕES DE ROTEAMENTO CONDICIONAL
    # ==========================================
    
    def _should_route_to_data_retriever(self, state: FinancialAgentState) -> str:
        """Decide se deve ir para recuperação de dados"""
        next_action = state.get("next_action", "")
        if next_action == "data_retriever":
            return "data_retriever"
        elif next_action == "calculator":
            return "calculator"
        elif next_action == "analyst":
            return "analyst"
        elif next_action == "validator":
            return "validator"
        else:
            return "end"
    
    def _after_data_retrieval(self, state: FinancialAgentState) -> str:
        """Decide próximo passo após recuperação de dados"""
        query = state.get("user_query", "").lower()
        
        if "calcul" in query or "métrica" in query or "ratio" in query:
            return "calculator"
        elif "analis" in query or "insight" in query:
            return "analyst"
        else:
            return "coordinator"
    
    def _after_calculation(self, state: FinancialAgentState) -> str:
        """Decide próximo passo após cálculos"""
        query = state.get("user_query", "").lower()
        
        if "risco" in query or "var" in query:
            return "risk_assessor"
        elif "analis" in query:
            return "analyst"
        else:
            return "coordinator"
    
    def _after_analysis(self, state: FinancialAgentState) -> str:
        """Decide próximo passo após análise"""
        query = state.get("user_query", "").lower()
        
        if "risco" in query and "risk_assessor" not in state.get("agents_completed", []):
            return "risk_assessor"
        else:
            return "validator"
    
    def _after_risk_assessment(self, state: FinancialAgentState) -> str:
        """Decide próximo passo após avaliação de risco"""
        return "validator"
    
    def _after_validation(self, state: FinancialAgentState) -> str:
        """Decide próximo passo após validação"""
        validation_results = state.get("data_validation", {})
        
        # Se validação falhou, pode ser necessário re-executar
        if validation_results.get("data_quality", {}).get("status") == "invalid":
            return "data_retriever"
        
        return "consolidator"
    
    # ==========================================
    # FUNÇÕES AUXILIARES
    # ==========================================
    
    def _needs_data_retrieval(self, query: str) -> bool:
        """Verifica se a query precisa de recuperação de dados"""
        data_keywords = ["dados", "informações", "empresa", "mercado", "ação", "preço"]
        return any(keyword in query.lower() for keyword in data_keywords)
    
    def _needs_calculations(self, query: str, state: FinancialAgentState) -> bool:
        """Verifica se precisa de cálculos"""
        calc_keywords = ["calcul", "métrica", "ratio", "retorno", "performance"]
        has_data = state.get("financial_data") is not None
        return any(keyword in query.lower() for keyword in calc_keywords) and has_data
    
    def _needs_analysis(self, query: str, state: FinancialAgentState) -> bool:
        """Verifica se precisa de análises"""
        analysis_keywords = ["analis", "insight", "recomendação", "estratégia"]
        has_prerequisites = (
            state.get("financial_data") is not None or 
            state.get("calculated_metrics") is not None
        )
        return any(keyword in query.lower() for keyword in analysis_keywords) and has_prerequisites
    
    def _needs_risk_assessment(self, query: str, state: FinancialAgentState) -> bool:
        """Verifica se precisa de avaliação de risco"""
        risk_keywords = ["risco", "var", "volatilidade", "stress"]
        has_analysis = state.get("portfolio_analysis") is not None
        return any(keyword in query.lower() for keyword in risk_keywords) and has_analysis
    
    async def _execute_tool_async(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Executa ferramenta de forma assíncrona"""
        tool = self.tool_map[tool_name]
        
        if asyncio.iscoroutinefunction(tool.invoke):
            return await tool.invoke(args)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool.invoke, args)
    
    def _identify_needed_data(self, query: str) -> Dict[str, str]:
        """Identifica que tipos de dados são necessários"""
        needed = {}
        
        if any(word in query.lower() for word in ["empresa", "companhia", "ação"]):
            needed["financial_data"] = "get_financial_data"
        
        if any(word in query.lower() for word in ["mercado", "índice", "benchmark"]):
            needed["market_data"] = "get_market_data"
        
        if any(word in query.lower() for word in ["informações", "dados", "perfil"]):
            needed["company_info"] = "get_company_info"
        
        return needed
    
    def _identify_needed_calculations(self, query: str, state: FinancialAgentState) -> Dict[str, str]:
        """Identifica cálculos necessários"""
        needed = {}
        
        if any(word in query.lower() for word in ["métrica", "indicador"]):
            needed["metrics"] = "calculate_metrics"
        
        if any(word in query.lower() for word in ["ratio", "índice"]):
            needed["ratios"] = "calculate_ratios"
        
        if any(word in query.lower() for word in ["retorno", "performance"]):
            needed["returns"] = "calculate_returns"
        
        return needed
    
    def _identify_needed_analyses(self, query: str, state: FinancialAgentState) -> Dict[str, str]:
        """Identifica análises necessárias"""
        needed = {}
        
        if any(word in query.lower() for word in ["portfolio", "carteira"]):
            needed["portfolio"] = "analyze_portfolio"
        
        if any(word in query.lower() for word in ["performance", "desempenho"]):
            needed["performance"] = "analyze_performance"
        
        return needed
    
    def _extract_args_for_tool(self, tool_name: str, state: FinancialAgentState) -> Dict[str, Any]:
        """Extrai argumentos necessários para uma ferramenta baseado no estado"""
        base_args = {"user_id": state.get("user_id", "")}
        
        # Adiciona dados relevantes do estado como contexto
        if state.get("financial_data"):
            base_args["financial_data"] = state["financial_data"]
        
        if state.get("market_data"):
            base_args["market_data"] = state["market_data"]
        
        if state.get("calculated_metrics"):
            base_args["calculated_metrics"] = state["calculated_metrics"]
        
        # Argumentos específicos baseados na query
        # (Esta lógica pode ser mais sofisticada baseada nas suas ferramentas específicas)
        
        return base_args
    
    def _validate_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida qualidade dos dados"""
        if not data:
            return {"status": "invalid", "reason": "Dados vazios"}
        
        # Implementar validações específicas
        return {"status": "valid"}
    
    def _validate_calculations(self, calculations: Dict[str, Any]) -> Dict[str, Any]:
        """Valida cálculos"""
        if not calculations:
            return {"status": "invalid", "reason": "Cálculos vazios"}
        
        # Implementar validações específicas
        return {"status": "valid"}
    
    def _cross_validate_results(self, state: FinancialAgentState) -> Dict[str, Any]:
        """Validação cruzada de resultados"""
        # Implementar validações cruzadas entre diferentes resultados
        return {"status": "consistent"}
    
    def _create_consolidated_response(self, state: FinancialAgentState) -> str:
        """Cria resposta final consolidada"""
        
        response_parts = []
        
        # Resumo da execução
        completed_agents = state.get("agents_completed", [])
        response_parts.append(f"✅ Análise concluída com {len(completed_agents)} agentes especializados:")
        
        # Resultados por seção
        if state.get("financial_data"):
            response_parts.append("\n📊 **Dados Financeiros Coletados**")
            # Adicionar resumo dos dados
        
        if state.get("calculated_metrics"):
            response_parts.append("\n🧮 **Métricas Calculadas**")
            # Adicionar resumo dos cálculos
        
        if state.get("portfolio_analysis"):
            response_parts.append("\n📈 **Análise de Portfolio**")
            # Adicionar insights da análise
        
        if state.get("risk_assessment"):
            response_parts.append("\n⚠️ **Avaliação de Riscos**")
            # Adicionar avaliação de riscos
        
        # Erros, se houver
        if state.get("errors"):
            response_parts.append(f"\n⚠️ **Alertas**: {len(state['errors'])} problema(s) detectado(s)")
        
        return "\n".join(response_parts)
    
    # ==========================================
    # INTERFACE PÚBLICA
    # ==========================================
    
    async def process_financial_query(
        self, 
        user_query: str, 
        user_id: str, 
        context: str = ""
    ) -> Dict[str, Any]:
        """Processa uma consulta financeira usando o sistema LangGraph"""
        
        # Estado inicial
        initial_state = FinancialAgentState(
            messages=[HumanMessage(content=user_query)],
            user_query=user_query,
            context=context,
            user_id=user_id,
            financial_data=None,
            market_data=None,
            company_info=None,
            calculated_metrics=None,
            ratios=None,
            returns=None,
            portfolio_analysis=None,
            risk_assessment=None,
            performance_analysis=None,
            data_validation=None,
            compliance_check=None,
            agents_completed=[],
            current_agent="",
            execution_metadata={
                "started_at": datetime.now().isoformat(),
                "query": user_query,
                "user_id": user_id
            },
            errors=[],
            next_action=None
        )
        
        try:
            # Executa o grafo
            config = {"configurable": {"thread_id": f"user_{user_id}_{int(datetime.now().timestamp())}"}}
            
            final_state = await self.compiled_graph.ainvoke(initial_state, config)
            
            # Extrai resposta final
            final_messages = final_state.get("messages", [])
            final_response = ""
            
            for msg in reversed(final_messages):
                if isinstance(msg, AIMessage):
                    final_response = msg.content
                    break
            
            # Cria sumário de execução
            execution_summary = ExecutionSummary(
                total_tasks=len(final_state.get("agents_completed", [])),
                successful_tasks=len([a for a in final_state.get("agents_completed", []) if a != "coordinator"]),
                failed_tasks=len(final_state.get("errors", [])),
                total_execution_time=0.0,  # LangGraph gerencia isso internamente
                agents_used={},  # Pode ser extraído do estado
                errors=final_state.get("errors", [])
            )
            
            return {
                "response": final_response,
                "execution_summary": execution_summary.to_dict(),
                "agents_completed": final_state.get("agents_completed", []),
                "state": final_state,
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Erro na execução do grafo LangGraph: {str(e)}")
            return {
                "response": f"Erro no processamento: {str(e)}",
                "execution_summary": {"error": str(e)},
                "agents_completed": [],
                "state": initial_state,
                "errors": [str(e)]
            }
