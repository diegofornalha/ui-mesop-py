"""
ClaudeRunner - Implementação compatível com ADKRunner.
Fornece a mesma interface e funcionalidades que o Google ADK Runner.
"""

import asyncio
import uuid
import logging
from typing import Any, Dict, Optional, Callable, List, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

# Importar nossos componentes Claude
from .claude_a2a_agent import ClaudeA2AAgent  # Agente A2A completo
from .claude_services import (
    ClaudeSessionService,
    ClaudeMemoryService,
    ClaudeArtifactService,
    ClaudeEvent,
    ClaudeEventActions
)

logger = logging.getLogger(__name__)


@dataclass
class ClaudeRunner:
    """
    Runner compatível com ADKRunner para integração com Claude.
    Implementa os mesmos métodos: run(), run_async(), run_live(), close()
    """
    
    # Configuração básica
    app_name: str
    agent: Optional[Callable] = None  # Função do agente customizada (opcional)
    
    # Serviços compatíveis com ADK
    session_service: ClaudeSessionService = field(default_factory=ClaudeSessionService)
    memory_service: ClaudeMemoryService = field(default_factory=ClaudeMemoryService)
    artifact_service: ClaudeArtifactService = field(default_factory=ClaudeArtifactService)
    
    # Agente A2A completo (não apenas LLM!)
    claude_agent: ClaudeA2AAgent = field(default_factory=ClaudeA2AAgent)
    
    # Estado interno
    _initialized: bool = False
    _sessions: Dict[str, Any] = field(default_factory=dict)
    _tasks: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialização pós-criação."""
        logger.info(f"Inicializando ClaudeRunner para app: {self.app_name}")
        self._initialized = True
    
    async def initialize(self):
        """Inicialização assíncrona dos serviços."""
        if not self._initialized:
            # Inicializar serviços
            await self.session_service.initialize()
            await self.memory_service.initialize()
            await self.artifact_service.initialize()
            
            # Agente já está inicializado via dataclass
            logger.info("✅ Claude A2A Agent pronto")
            
            self._initialized = True
        return self
    
    def run(self, input_data: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa o runner de forma síncrona (compatível com ADKRunner.run).
        """
        return asyncio.run(self.run_async_simple(input_data, session_id))
    
    async def run_async(self, input_data: str, session_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executa o runner de forma assíncrona com yield/pause/resume (compatível com ADKRunner.run_async).
        
        Este é o método principal que implementa o padrão event-driven do ADK.
        
        Args:
            input_data: Dados de entrada (mensagem do usuário)
            session_id: ID da sessão (cria nova se None)
            
        Yields:
            Dict com eventos durante o processamento
        """
        await self.initialize()
        
        # Criar ou recuperar sessão
        if not session_id:
            session_id = str(uuid.uuid4())
            session = await self.session_service.create_session(session_id)
        else:
            session = await self.session_service.get_session(session_id)
            if not session:
                session = await self.session_service.create_session(session_id)
        
        # 1. YIELD: Evento de início de processamento
        start_event = {
            "type": "processing_start",
            "session_id": session_id,
            "message": "Iniciando processamento da mensagem"
        }
        logger.info(f"🎯 [RUNNER] Yielding start event: {start_event['type']}")
        yield start_event
        
        # 2. Registrar evento de entrada
        input_event = ClaudeEvent.create(
            type="user_input",
            session_id=session_id,
            content=input_data
        )
        await self.session_service.append_event(session_id, input_event)
        
        # 3. YIELD: Evento de entrada registrada
        input_registered_event = {
            "type": "input_registered",
            "session_id": session_id,
            "event_id": input_event.id,
            "content": input_data
        }
        logger.info(f"🎯 [RUNNER] Yielding input registered event")
        yield input_registered_event
        
        # 4. Processar com Claude (aqui ocorre a "pausa" para pensar)
        logger.info(f"🤔 [RUNNER] Processando com Claude...")
        response = await self._process_with_claude(input_data, session_id)
        
        # 5. YIELD: Evento de resposta gerada
        response_generated_event = {
            "type": "response_generated",
            "session_id": session_id,
            "response": response
        }
        logger.info(f"🎯 [RUNNER] Yielding response generated event")
        yield response_generated_event
        
        # 6. Registrar evento de resposta
        response_event = ClaudeEvent.create(
            type="agent_response",
            session_id=session_id,
            content=response
        )
        await self.session_service.append_event(session_id, response_event)
        
        # 7. Salvar na memória
        if self.memory_service:
            await self.memory_service.store(
                key=f"response_{session_id}_{input_event.id}",
                value=response
            )
        
        # 8. YIELD: Evento final com resultado completo
        final_event = {
            "type": "processing_complete",
            "session_id": session_id,
            "response": response,
            "events": [input_event.to_dict(), response_event.to_dict()]
        }
        logger.info(f"🎯 [RUNNER] Yielding final event: {final_event['type']}")
        yield final_event
    
    async def run_async_simple(self, input_data: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Versão simplificada do run_async que retorna diretamente o resultado.
        Útil para casos onde não é necessário o padrão event-driven.
        
        Returns:
            Dict com resposta final e metadados
        """
        # Consumir o generator e retornar apenas o resultado final
        final_result = None
        async for event in self.run_async(input_data, session_id):
            if event.get("type") == "processing_complete":
                final_result = event
        
        return final_result or {
            "session_id": session_id,
            "response": "Erro ao processar",
            "events": []
        }
    
    async def _process_with_claude(self, input_data: str, session_id: str) -> str:
        """
        Processa entrada com o Agente A2A Claude.
        Usa o agente completo, não apenas LLM!
        """
        try:
            # Usar o agente A2A para pensar e agir
            response = await self.claude_agent._think_and_act(input_data, session_id)
            
            # Se tem função de agente customizada adicional, processar
            if self.agent:
                try:
                    # Chamar agente customizado com a resposta
                    session = await self.session_service.get_session(session_id)
                    agent_response = await self._call_agent(
                        input_data=input_data,
                        claude_response=response,
                        session=session
                    )
                    if agent_response:
                        response = agent_response
                except Exception as e:
                    logger.error(f"Erro ao chamar agente customizado: {e}")
            
            return response or "Desculpe, não consegui processar sua mensagem."
            
        except Exception as e:
            logger.error(f"Erro ao processar com Claude: {e}")
            return f"Erro ao processar: {str(e)}"
    
    async def _call_agent(self, input_data: str, claude_response: str, session: Dict) -> Optional[str]:
        """
        Chama o agente customizado se configurado.
        """
        if not self.agent:
            return None
        
        try:
            # Preparar contexto para o agente
            agent_context = {
                "input": input_data,
                "claude_response": claude_response,
                "session": session,
                "services": {
                    "session": self.session_service,
                    "memory": self.memory_service,
                    "artifact": self.artifact_service
                }
            }
            
            # Chamar agente
            if asyncio.iscoroutinefunction(self.agent):
                result = await self.agent(agent_context)
            else:
                result = self.agent(agent_context)
            
            return str(result) if result else None
            
        except Exception as e:
            logger.error(f"Erro ao executar agente: {e}")
            return None
    
    async def run_live(self, session_id: Optional[str] = None):
        """
        Executa o runner em modo live/streaming (compatível com ADKRunner.run_live).
        """
        await self.initialize()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"Iniciando modo live para sessão: {session_id}")
        
        # Loop interativo
        while True:
            try:
                # Aguardar entrada
                user_input = input("\n👤 User: ")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Encerrando sessão...")
                    break
                
                # Processar usando run_async_simple
                result = await self.run_async_simple(user_input, session_id)
                
                # Exibir resposta
                print(f"\n🤖 Claude: {result['response']}")
                
            except KeyboardInterrupt:
                print("\n👋 Sessão interrompida")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def close(self):
        """
        Fecha o runner e libera recursos (compatível com ADKRunner.close).
        """
        logger.info(f"Fechando ClaudeRunner para app: {self.app_name}")
        
        # Limpar sessões
        self._sessions.clear()
        self._tasks.clear()
        
        # Fechar serviços
        if self.session_service:
            self.session_service.close()
        if self.memory_service:
            self.memory_service.close()
        if self.artifact_service:
            self.artifact_service.close()
        
        self._initialized = False
        logger.info("✅ ClaudeRunner fechado")
    
    # Métodos adicionais para compatibilidade
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Obtém dados da sessão."""
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[str]:
        """Lista IDs de sessões ativas."""
        return list(self._sessions.keys())
    
    @property
    def is_initialized(self) -> bool:
        """Verifica se o runner está inicializado."""
        return self._initialized


# Exemplo de uso
async def example_usage():
    """Exemplo de uso do ClaudeRunner."""
    
    # Definir um agente customizado (opcional)
    def my_agent(context):
        """Agente que adiciona contexto específico."""
        response = context["claude_response"]
        # Adicionar lógica customizada aqui
        return f"[Processado pelo agente] {response}"
    
    # Criar runner
    runner = ClaudeRunner(
        app_name="MeuApp",
        agent=my_agent
    )
    
    # Executar de forma assíncrona
    result = await runner.run_async("Olá Claude!")
    print(f"Resposta: {result['response']}")
    
    # Executar de forma síncrona
    result = runner.run("Como você está?")
    print(f"Resposta: {result['response']}")
    
    # Fechar
    runner.close()


if __name__ == "__main__":
    # Testar runner
    asyncio.run(example_usage())