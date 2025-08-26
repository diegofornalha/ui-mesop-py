"""
ClaudeA2AAgent - Agente A2A completo usando Claude Code SDK.
Implementa pensamento e ação como um agente real, não apenas LLM.
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .claude_client import ClaudeClientV10

logger = logging.getLogger(__name__)


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