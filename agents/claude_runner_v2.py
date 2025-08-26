"""
ClaudeRunner V2 - Implementação correta seguindo arquitetura real do Google ADK.
O Runner é o ORQUESTRADOR PRINCIPAL, não um componente subordinado.
"""

import asyncio
import uuid
import logging
from typing import AsyncGenerator, Optional, Dict, Any, List
from dataclasses import dataclass, field

from .claude_types import (
    Event, EventActions, Content, Session, 
    InvocationContext, RunConfig
)
from .claude_services import (
    ClaudeSessionService,
    ClaudeMemoryService,
    ClaudeArtifactService
)
from .claude_a2a_agent_v2 import BaseAgent
from a2a.types import Message, Role, TextPart

logger = logging.getLogger(__name__)


@dataclass
class ClaudeRunner:
    """
    Runner correto seguindo padrão ADK - ORQUESTRADOR PRINCIPAL.
    Gerencia conversações, estado, e coordena execução de agentes.
    """
    
    # Configuração obrigatória
    agent: BaseAgent
    app_name: str
    
    # Services obrigatórios
    session_service: ClaudeSessionService = field(default_factory=ClaudeSessionService)
    artifact_service: ClaudeArtifactService = field(default_factory=ClaudeArtifactService)
    
    # Services opcionais
    memory_service: Optional[ClaudeMemoryService] = field(default_factory=ClaudeMemoryService)
    credential_service: Optional[Any] = None
    
    # Estado interno (Runner gerencia conversações!)
    _sessions: Dict[str, Session] = field(default_factory=dict, init=False)
    _conversations: Dict[str, Any] = field(default_factory=dict, init=False)
    
    async def initialize(self):
        """Inicializa o Runner e seus serviços."""
        await self.session_service.initialize()
        await self.artifact_service.initialize()
        if self.memory_service:
            await self.memory_service.initialize()
        
        # Inicializar agente
        await self.agent.initialize()
        
        logger.info(f"✅ ClaudeRunner V2 inicializado para app: {self.app_name}")
    
    async def run_async(
        self,
        user_id: str,
        session_id: str,
        new_message: Content,
        run_config: RunConfig = None
    ) -> AsyncGenerator[Event, None]:
        """
        Método principal do Runner - Orquestra toda execução.
        Segue exatamente o padrão do Google ADK.
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            new_message: Conteúdo da nova mensagem
            run_config: Configuração de execução opcional
            
        Yields:
            Events processados e prontos para UI
        """
        if not run_config:
            run_config = RunConfig()
        
        logger.info(f"🎯 [RUNNER V2] Iniciando run_async para sessão {session_id[:8]}")
        
        # 1. CARREGAR OU CRIAR SESSÃO
        session = await self._get_or_create_session(user_id, session_id)
        
        # 2. ADICIONAR MENSAGEM DO USUÁRIO COMO EVENTO
        user_event = Event(
            author="user",
            invocation_id=str(uuid.uuid4()),
            content=new_message,
            turn_complete=True
        )
        session.add_event(user_event)
        await self.session_service.append_event(session_id, user_event)
        
        # Yield evento do usuário para UI
        yield user_event
        
        # 3. CRIAR INVOCATION CONTEXT
        invocation_id = str(uuid.uuid4())
        ctx = InvocationContext(
            session=session,
            invocation_id=invocation_id,
            agent=self.agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
            memory_service=self.memory_service,
            credential_service=self.credential_service
        )
        
        logger.info(f"📦 [RUNNER V2] Context criado com invocation_id: {invocation_id[:8]}")
        
        # 4. EXECUTAR AGENTE E PROCESSAR EVENTOS
        try:
            event_count = 0
            async for event in self.agent._run_async_impl(ctx):
                event_count += 1
                logger.info(f"📡 [RUNNER V2] Evento {event_count} do agente: author={event.author}, turn_complete={event.turn_complete}")
                
                # PROCESSAR STATE_DELTA (Staging automático!)
                if event.actions and event.actions.state_delta:
                    logger.info(f"🔄 [RUNNER V2] Aplicando state_delta: {event.actions.state_delta}")
                    session.state.update(event.actions.state_delta)
                    # Persistir mudanças
                    await self.session_service.update_session_state(session_id, session.state)
                
                # PROCESSAR ARTIFACT_DELTA
                if event.actions and event.actions.artifact_delta:
                    logger.info(f"📁 [RUNNER V2] Processando artifact_delta")
                    for key, value in event.actions.artifact_delta.items():
                        if value is None:
                            # Deletar artifact
                            await self.artifact_service.delete_artifact(key)
                        else:
                            # Salvar/atualizar artifact
                            await self.artifact_service.save_artifact(key, value)
                
                # PROCESSAR TRANSFER_TO_AGENT
                if event.actions and event.actions.transfer_to_agent:
                    logger.warning(f"🔀 [RUNNER V2] Transfer to agent: {event.actions.transfer_to_agent} (não implementado)")
                    # TODO: Implementar handoff para outro agente
                
                # PROCESSAR ESCALATE
                if event.actions and event.actions.escalate:
                    logger.warning(f"⚠️ [RUNNER V2] Escalate solicitado - encerrando loop")
                    break
                
                # ADICIONAR EVENTO À SESSÃO
                session.add_event(event)
                await self.session_service.append_event(session_id, event)
                
                # YIELD EVENTO PARA UPSTREAM (UI/Application)
                yield event
                
                # VERIFICAR LIMITES
                if run_config.max_events and event_count >= run_config.max_events:
                    logger.info(f"🛑 [RUNNER V2] Limite de eventos atingido: {run_config.max_events}")
                    break
                
                # SE TURN COMPLETE, ENCERRAR
                if event.turn_complete:
                    logger.info(f"✅ [RUNNER V2] Turn complete - encerrando")
                    break
            
            logger.info(f"✅ [RUNNER V2] Execução completa - {event_count} eventos processados")
            
        except Exception as e:
            logger.error(f"❌ [RUNNER V2] Erro durante execução: {e}")
            import traceback
            traceback.print_exc()
            
            # Criar evento de erro
            error_event = Event(
                author="system",
                invocation_id=invocation_id,
                content=Content.from_text(f"Erro: {str(e)}"),
                turn_complete=True
            )
            session.add_event(error_event)
            yield error_event
    
    async def _get_or_create_session(self, user_id: str, session_id: str) -> Session:
        """Obtém ou cria uma sessão."""
        # Verificar cache local primeiro
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # Tentar carregar do SessionService
        session_data = await self.session_service.get_session(session_id)
        
        if session_data:
            # Reconstituir Session a partir dos dados
            session = Session(
                id=session_id,
                state=session_data.get("state", {}),
                events=[]  # TODO: Carregar eventos históricos se necessário
            )
        else:
            # Criar nova sessão
            session = Session(id=session_id)
            await self.session_service.create_session(session_id)
        
        # Cachear localmente
        self._sessions[session_id] = session
        return session
    
    # =========================================================================
    # MÉTODOS DE COMPATIBILIDADE COM INTERFACE ANTERIOR
    # =========================================================================
    
    async def create_conversation(self) -> Dict[str, Any]:
        """Cria uma nova conversação (compatibilidade)."""
        conversation_id = str(uuid.uuid4())
        session_id = conversation_id  # Usar mesmo ID
        
        # Criar sessão
        session = Session(id=session_id)
        self._sessions[session_id] = session
        await self.session_service.create_session(session_id)
        
        # Criar estrutura de conversação para compatibilidade
        conversation = {
            "conversationId": conversation_id,
            "messages": [],
            "status": "active"
        }
        self._conversations[conversation_id] = conversation
        
        logger.info(f"✅ [RUNNER V2] Conversação criada: {conversation_id[:8]}")
        return conversation
    
    async def process_message(self, message: Message) -> Message:
        """
        Processa uma mensagem A2A (compatibilidade com interface anterior).
        """
        conversation_id = message.contextId or str(uuid.uuid4())
        user_id = "default_user"  # TODO: Extrair de algum lugar
        
        # Converter Message A2A para Content
        content = self._message_to_content(message)
        
        # Processar via run_async
        response_text = ""
        async for event in self.run_async(user_id, conversation_id, content):
            if event.turn_complete and event.content:
                # Extrair texto da resposta final
                for part in event.content.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
        
        # Criar mensagem de resposta A2A
        from a2a.types import Message, Role, TextPart
        response_message = Message(
            messageId=str(uuid.uuid4()),
            contextId=conversation_id,
            role=Role.agent,
            parts=[TextPart(text=response_text)]
        )
        
        return response_message
    
    def _message_to_content(self, message: Message) -> Content:
        """Converte Message A2A para Content ADK."""
        parts = []
        for part in message.parts:
            if hasattr(part, 'text'):
                parts.append(part)  # Manter TextPart
            elif hasattr(part, 'file'):
                parts.append(part)  # Manter FilePart
            else:
                parts.append(str(part))  # Converter para string
        
        return Content(parts=parts)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma conversação (compatibilidade)."""
        return self._conversations.get(conversation_id)
    
    @property
    def conversations(self) -> List[Dict[str, Any]]:
        """Lista todas as conversações (compatibilidade)."""
        return list(self._conversations.values())
    
    def close(self):
        """Fecha o Runner e libera recursos."""
        self._sessions.clear()
        self._conversations.clear()
        
        if self.session_service:
            self.session_service.close()
        if self.artifact_service:
            self.artifact_service.close()
        if self.memory_service:
            self.memory_service.close()
        
        logger.info(f"🔒 [RUNNER V2] ClaudeRunner fechado")