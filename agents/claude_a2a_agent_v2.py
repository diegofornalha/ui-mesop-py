"""
Claude A2A Agent V2 - Implementação correta seguindo padrão Google ADK.
Usa _run_async_impl ao invés de run_iteration (que não existe no ADK).
"""

import logging
from typing import AsyncGenerator, Optional, List, Dict, Any
from abc import ABC, abstractmethod
import uuid

from .claude_types import Event, EventActions, Content, InvocationContext
from .claude_client import ClaudeClientV10
from a2a.types import TextPart

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Classe base para agentes seguindo padrão ADK.
    """
    
    def __init__(self, name: str, instruction: str = "", tools: List[Any] = None):
        self.name = name
        self.instruction = instruction
        self.tools = tools or []
        self._initialized = False
    
    async def initialize(self):
        """Inicializa o agente."""
        if not self._initialized:
            await self._initialize_impl()
            self._initialized = True
    
    async def _initialize_impl(self):
        """Override para inicialização customizada."""
        pass
    
    @abstractmethod
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Método principal do agente - DEVE ser implementado.
        Este é o padrão correto do ADK (não run_iteration!).
        
        Args:
            ctx: InvocationContext com sessão, serviços, etc.
            
        Yields:
            Events durante o processamento
        """
        raise NotImplementedError("Agentes devem implementar _run_async_impl")


class ClaudeA2AAgent(BaseAgent):
    """
    Agente A2A concreto usando Claude.
    Implementa o padrão correto do ADK com _run_async_impl.
    """
    
    def __init__(
        self, 
        name: str = "Claude Agent",
        instruction: str = "Você é um assistente útil.",
        tools: List[Any] = None,
        use_real_sdk: bool = True
    ):
        super().__init__(name, instruction, tools)
        self.llm_client = ClaudeClientV10(use_real_sdk=use_real_sdk)
    
    async def _initialize_impl(self):
        """Inicializa cliente LLM."""
        await self.llm_client.initialize()
        logger.info(f"✅ {self.name} inicializado")
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implementação principal do agente seguindo padrão ADK.
        Observe → Think → Decide → Act através de eventos.
        
        Args:
            ctx: Contexto com sessão, estado, serviços
            
        Yields:
            Events durante o ciclo de processamento
        """
        logger.info(f"🤖 [AGENT V2] {self.name} iniciando _run_async_impl")
        
        # 1. OBSERVE - Acessar estado e histórico
        current_state = ctx.session.state
        history = ctx.session.events
        invocation_id = ctx.invocation_id
        
        logger.info(f"👁️ [OBSERVE] Estado atual: {len(current_state)} items, Histórico: {len(history)} eventos")
        
        # Extrair última mensagem do usuário
        user_message = None
        for event in reversed(history):
            if event.author == "user" and event.content:
                user_message = event.content
                break
        
        if not user_message:
            logger.warning("⚠️ Nenhuma mensagem do usuário encontrada")
            yield Event(
                author=self.name,
                invocation_id=invocation_id,
                content=Content.from_text("Desculpe, não encontrei sua mensagem."),
                turn_complete=True
            )
            return
        
        # 2. THINK - Processar com LLM
        logger.info(f"🤔 [THINK] Processando mensagem com Claude...")
        
        # Extrair texto do Content
        user_text = self._extract_text_from_content(user_message)
        
        # Adicionar contexto da instrução
        prompt = f"{self.instruction}\n\nUsuário: {user_text}\n\nAssistente:"
        
        # Chamar Claude
        try:
            response_text = ""
            partial_count = 0
            
            # Stream de resposta do Claude
            async for chunk in self.llm_client.send_message(prompt):
                if chunk.get("type") == "text":
                    text_chunk = chunk.get("content", "")
                    response_text += text_chunk
                    
                    # Yield evento parcial para streaming (opcional)
                    partial_count += 1
                    if partial_count % 5 == 0:  # A cada 5 chunks
                        yield Event(
                            author=self.name,
                            invocation_id=invocation_id,
                            content=Content.from_text(response_text),
                            partial=True,  # Indica streaming
                            turn_complete=False
                        )
            
            # Se não teve resposta, usar fallback
            if not response_text:
                response_text = f"Entendi sua mensagem: '{user_text[:50]}...'. Como posso ajudar?"
            
        except Exception as e:
            logger.error(f"❌ Erro ao chamar Claude: {e}")
            response_text = f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"
        
        logger.info(f"💡 [THINK] Resposta gerada: {response_text[:100]}...")
        
        # 3. DECIDE - Determinar ações
        logger.info(f"⚖️ [DECIDE] Determinando ações...")
        
        # Verificar se precisa executar ferramentas
        tool_calls = self._check_for_tool_calls(response_text)
        
        if tool_calls:
            logger.info(f"🔧 [DECIDE] {len(tool_calls)} ferramentas a executar")
            
            # 4. ACT - Executar ferramentas
            for tool_call in tool_calls:
                # Yield evento de chamada de ferramenta
                yield Event(
                    author=self.name,
                    invocation_id=invocation_id,
                    content=Content.from_text(f"Executando ferramenta: {tool_call['name']}"),
                    partial=False,
                    turn_complete=False
                )
                
                # Executar ferramenta (simulado)
                tool_result = await self._execute_tool(tool_call)
                
                # Yield resultado da ferramenta
                yield Event(
                    author=self.name,
                    invocation_id=invocation_id,
                    content=Content.from_text(f"Resultado: {tool_result}"),
                    actions=EventActions(
                        state_delta={"last_tool": tool_call['name']}
                    ),
                    partial=False,
                    turn_complete=False
                )
        
        # 5. ACT - Resposta final
        logger.info(f"🎬 [ACT] Enviando resposta final")
        
        # Atualizar estado com informações da interação
        state_updates = {
            "last_response": response_text[:100],
            "interaction_count": current_state.get("interaction_count", 0) + 1,
            "last_agent": self.name
        }
        
        # Yield evento final com resposta completa
        yield Event(
            author=self.name,
            invocation_id=invocation_id,
            content=Content.from_text(response_text),
            actions=EventActions(
                state_delta=state_updates  # Estado será commitado pelo Runner
            ),
            partial=False,
            turn_complete=True  # Marca fim do turno
        )
        
        logger.info(f"✅ [AGENT V2] {self.name} completou _run_async_impl")
    
    def _extract_text_from_content(self, content: Content) -> str:
        """Extrai texto de um Content."""
        text_parts = []
        for part in content.parts:
            if hasattr(part, 'text'):
                text_parts.append(part.text)
            elif isinstance(part, str):
                text_parts.append(part)
        return " ".join(text_parts)
    
    def _check_for_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Verifica se a resposta contém chamadas de ferramentas.
        Por enquanto retorna lista vazia (implementar detecção real depois).
        """
        # TODO: Implementar detecção real de tool calls
        return []
    
    async def _execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """
        Executa uma ferramenta.
        Por enquanto retorna resultado simulado.
        """
        # TODO: Implementar execução real de ferramentas
        return f"Resultado simulado para {tool_call['name']}"


class SimpleTestAgent(BaseAgent):
    """
    Agente de teste simples para validação.
    """
    
    def __init__(self):
        super().__init__(name="TestAgent", instruction="Agente de teste")
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Implementação mínima para teste."""
        # Simplesmente ecoa a mensagem
        last_user_message = "Olá!"
        for event in reversed(ctx.session.events):
            if event.author == "user" and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text'):
                        last_user_message = part.text
                        break
                break
        
        response = f"Echo: {last_user_message}"
        
        yield Event(
            author=self.name,
            invocation_id=ctx.invocation_id,
            content=Content.from_text(response),
            actions=EventActions(
                state_delta={"echo_count": ctx.get_state("echo_count", 0) + 1}
            ),
            turn_complete=True
        )