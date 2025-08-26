"""
ClaudeA2AAgent - Agente A2A completo usando Claude Code SDK.
Implementa pensamento e ação como um agente real, não apenas LLM.
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum

from .claude_client import ClaudeClientV10

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Estados do ciclo de execução do agente."""
    OBSERVING = "observing"
    THINKING = "thinking"  
    DECIDING = "deciding"
    ACTING = "acting"
    WAITING = "waiting"
    COMPLETED = "completed"


@dataclass 
class ClaudeA2AAgent:
    """
    Agente A2A completo que pode pensar e agir.
    Não é apenas um wrapper de LLM, mas um agente real!
    """
    
    # Configuração
    name: str = "Claude A2A Agent"
    description: str = "Agente inteligente com capacidade de raciocínio e ação"
    
    # Cliente Claude para LLM
    llm_client: ClaudeClientV10 = field(default_factory=ClaudeClientV10)
    
    # Estado do agente
    _initialized: bool = False
    _memory: Dict[str, Any] = field(default_factory=dict)
    _tools: Dict[str, callable] = field(default_factory=dict)
    _state: AgentState = AgentState.WAITING
    _current_context: Dict[str, Any] = field(default_factory=dict)
    _pending_events: List[Dict[str, Any]] = field(default_factory=list)
    
    async def initialize(self):
        """Inicializa o agente A2A."""
        if not self._initialized:
            await self.llm_client.initialize()
            self._register_default_tools()
            self._initialized = True
            logger.info(f"✅ {self.name} inicializado com ferramentas")
    
    def _register_default_tools(self):
        """Registra ferramentas padrão do agente."""
        # Ferramentas básicas que um agente A2A pode ter
        self._tools = {
            "remember": self._tool_remember,
            "recall": self._tool_recall,
            "analyze": self._tool_analyze,
            "plan": self._tool_plan,
        }
    
    async def _think_and_act(self, input_data: str, session_id: str) -> str:
        """
        Processo principal de pensar e agir do agente.
        Este é o coração do agente A2A!
        """
        await self.initialize()
        
        # Etapa 1: Entender a entrada
        understanding = await self._understand(input_data, session_id)
        
        # Etapa 2: Planejar ação
        plan = await self._plan_action(understanding, session_id)
        
        # Etapa 3: Executar ação
        result = await self._execute_action(plan, session_id)
        
        # Etapa 4: Formular resposta
        response = await self._formulate_response(result, session_id)
        
        return response
    
    async def _understand(self, input_data: str, session_id: str) -> Dict:
        """Entende a entrada do usuário."""
        prompt = f"""
        Analise esta entrada do usuário e identifique:
        1. Intenção principal
        2. Entidades mencionadas
        3. Contexto necessário
        
        Entrada: {input_data}
        """
        
        response = ""
        async for part in self.llm_client.send_message(prompt):
            if part.get("type") == "text":
                response += part.get("content", "")
        
        return {
            "input": input_data,
            "understanding": response,
            "session_id": session_id
        }
    
    async def _plan_action(self, understanding: Dict, session_id: str) -> Dict:
        """Planeja a ação baseado no entendimento."""
        prompt = f"""
        Com base neste entendimento: {understanding['understanding']}
        
        Crie um plano de ação simples e direto para responder.
        """
        
        response = ""
        async for part in self.llm_client.send_message(prompt):
            if part.get("type") == "text":
                response += part.get("content", "")
        
        return {
            "understanding": understanding,
            "plan": response,
            "session_id": session_id
        }
    
    async def _execute_action(self, plan: Dict, session_id: str) -> Dict:
        """Executa o plano de ação."""
        # Por agora, apenas processa com o LLM
        # Em um agente real, aqui executaríamos ferramentas, APIs, etc.
        
        original_input = plan['understanding']['input']
        prompt = f"Responda de forma útil e concisa: {original_input}"
        
        response = ""
        async for part in self.llm_client.send_message(prompt):
            if part.get("type") == "text":
                response += part.get("content", "")
        
        return {
            "plan": plan,
            "execution": response,
            "session_id": session_id
        }
    
    async def _formulate_response(self, result: Dict, session_id: str) -> str:
        """Formula a resposta final para o usuário."""
        # Por agora, retorna diretamente a execução
        # Em um agente real, poderia formatar, adicionar contexto, etc.
        return result.get("execution", "Desculpe, não consegui processar sua solicitação.")
    
    # Ferramentas do agente
    async def _tool_remember(self, key: str, value: Any):
        """Ferramenta para lembrar informações."""
        self._memory[key] = value
        return f"Lembrado: {key}"
    
    async def _tool_recall(self, key: str) -> Any:
        """Ferramenta para recuperar informações."""
        return self._memory.get(key, None)
    
    async def _tool_analyze(self, data: Any) -> str:
        """Ferramenta para análise."""
        # Análise simples por agora
        return f"Analisado: {str(data)[:100]}"
    
    async def _tool_plan(self, goal: str) -> List[str]:
        """Ferramenta para planejamento."""
        # Planejamento simples por agora
        return ["Passo 1: Entender", "Passo 2: Processar", "Passo 3: Responder"]
    
    def close(self):
        """Fecha o agente."""
        if self.llm_client:
            asyncio.run(self.llm_client.close())
        self._memory.clear()
        self._tools.clear()
        self._initialized = False
        logger.info(f"✅ {self.name} fechado")

    
    async def run_iteration(self, input_data: str = None, session_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executa uma iteração completa do ciclo do agente.
        Implementa o padrão do ADK: observar → pensar → decidir → agir → yield evento.
        """
        await self.initialize()
        
        # 1. OBSERVAR - Observa o estado atual e entrada
        self._state = AgentState.OBSERVING
        logger.info(f"🔍 [ITERATION] Estado: OBSERVANDO")
        
        observation = {
            "input": input_data,
            "session_id": session_id,
            "memory": self._memory.copy(),
            "timestamp": str(uuid.uuid4())
        }
        
        # YIELD: Evento de observação
        yield self.yield_event("observation", observation)
        
        # 2. PENSAR - Usa LLM para processar observação
        self._state = AgentState.THINKING
        logger.info(f"🤔 [ITERATION] Estado: PENSANDO")
        
        thought = await self._understand(input_data or "", session_id or "")
        
        # YIELD: Evento de pensamento
        yield self.yield_event("thought", thought)
        
        # 3. DECIDIR - Decide ação baseada no pensamento
        self._state = AgentState.DECIDING
        logger.info(f"⚖️ [ITERATION] Estado: DECIDINDO")
        
        decision = await self._plan_action(thought, session_id or "")
        
        # YIELD: Evento de decisão
        yield self.yield_event("decision", decision)
        
        # 4. AGIR - Executa a ação decidida
        self._state = AgentState.ACTING
        logger.info(f"🎬 [ITERATION] Estado: AGINDO")
        
        action_result = await self._execute_action(decision, session_id or "")
        
        # YIELD: Evento de ação
        yield self.yield_event("action", action_result)
        
        # 5. FINALIZAR - Prepara resposta final
        self._state = AgentState.COMPLETED
        logger.info(f"✅ [ITERATION] Estado: COMPLETO")
        
        final_response = await self._formulate_response(action_result, session_id or "")
        
        # YIELD: Evento de conclusão
        yield self.yield_event("completion", {
            "response": final_response,
            "state": "completed",
            "session_id": session_id
        })
        
        # Resetar estado
        self._state = AgentState.WAITING
    
    def yield_event(self, event_type: str, data: Any) -> Dict[str, Any]:
        """
        Cria e retorna um evento para ser yielded.
        Implementa o padrão de eventos do ADK.
        """
        event = {
            "type": f"agent_{event_type}",
            "agent": self.name,
            "state": self._state.value,
            "data": data,
            "timestamp": str(uuid.uuid4())
        }
        
        # Adicionar à lista de eventos pendentes
        self._pending_events.append(event)
        
        logger.info(f"📤 [EVENT] Yielding: {event['type']}")
        return event
    
    async def process_until_yield(self) -> Optional[Dict[str, Any]]:
        """
        Processa até o próximo yield de evento.
        Útil para processamento step-by-step.
        """
        if self._pending_events:
            return self._pending_events.pop(0)
        return None
    
    async def resume(self):
        """
        Retoma o processamento após um yield.
        """
        logger.info(f"▶️ [RESUME] Retomando do estado: {self._state.value}")


# Teste do agente
async def test_agent():
    """Testa o agente A2A."""
    agent = ClaudeA2AAgent(name="TestAgent")
    
    response = await agent._think_and_act(
        "Olá! Como você está?",
        "test-session"
    )
    
    print(f"Agente respondeu: {response}")
    
    agent.close()


if __name__ == "__main__":
    asyncio.run(test_agent())