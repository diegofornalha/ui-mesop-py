"""
Claude ADK Host Manager - Substitui completamente o ADKHostManager usando ClaudeRunner.
Implementação completa com todos os serviços e conversores.
"""

import asyncio
import base64
import datetime
import json
import os
import uuid
import logging
from typing import Dict, List, Optional, Any

import httpx
from a2a.types import (
    AgentCard,
    Artifact,
    Message,
    Part,
    Role,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
    FilePart,
    DataPart
)

# Importar nossos componentes Claude
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.claude_runner import ClaudeRunner
from agents.claude_services import (
    ClaudeSessionService,
    ClaudeMemoryService,
    ClaudeArtifactService,
    ClaudeEvent,
    ClaudeEventActions,
    ClaudeArtifact
)
from agents.claude_callbacks import (
    ClaudeCallbackManager,
    TaskStatusUpdateEvent as CTaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    get_callback_manager
)
from agents.claude_artifacts import (
    ClaudeArtifactManager,
    ArtifactChunk,
    get_artifact_manager
)
from agents.claude_converters import (
    claude_content_from_message,
    claude_content_to_message,
    build_claude_context,
    extract_text_from_message
)

from service.server.application_manager import ApplicationManager
from service.types import Conversation, Event
from service.server.claude_task_manager import ClaudeTaskManager, get_task_manager

logger = logging.getLogger(__name__)


def get_message_id(message: Message) -> str:
    """Extrai ID da mensagem."""
    return message.messageId if hasattr(message, 'messageId') else str(uuid.uuid4())


class ClaudeADKHostManager(ApplicationManager):
    """
    Substitui ADKHostManager usando ClaudeRunner e serviços compatíveis.
    Implementação completa da interface ApplicationManager.
    """
    
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_key: str = "",  # Não usado para Claude
        uses_vertex_ai: bool = False  # Não usado para Claude
    ):
        """Inicializa o Claude ADK Host Manager."""
        self.http_client = http_client
        
        # Criar ClaudeRunner com serviços
        self.runner = ClaudeRunner(
            app_name="ClaudeADKHost",
            session_service=ClaudeSessionService(),
            memory_service=ClaudeMemoryService(),
            artifact_service=ClaudeArtifactService()
        )
        
        # Inicializar gerenciadores de callbacks e artifacts
        self.callback_manager = get_callback_manager()
        self.artifact_manager = get_artifact_manager()
        self.task_manager = get_task_manager()  # Gerenciador de tasks com conversão
        
        # Estado interno
        self._conversations: Dict[str, Conversation] = {}
        self._messages: Dict[str, List[Message]] = {}
        self._tasks: Dict[str, Task] = {}  # Mantém tasks A2A originais
        self._events: List[Event] = []
        self._agents: List[AgentCard] = []
        self._pending_messages: Dict[str, str] = {}
        
        # Configurar agente padrão
        self._setup_default_agent()
        
        logger.info("✅ ClaudeADKHostManager inicializado (sem API key necessária!)")
    
    def _setup_default_agent(self):
        """Configura o agente Claude padrão."""
        from a2a.types import AgentCapabilities
        
        self._agents.append(AgentCard(
            name="Claude Assistant",
            description="Claude AI via CLI local - Sem necessidade de API key",
            author="Anthropic",
            version="1.0.0",
            url="http://localhost:8888",
            capabilities=AgentCapabilities(),  # Usar objeto vazio ao invés de lista
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            skills=[]  # Lista vazia de skills
        ))
    
    async def initialize(self):
        """Inicializa o manager de forma assíncrona."""
        await self.runner.initialize()
        logger.info("Claude ADK Host Manager pronto para uso")
        return self
    
    # ========================================================================
    # IMPLEMENTAÇÃO DA INTERFACE ApplicationManager
    # ========================================================================
    
    async def create_conversation(self) -> Conversation:
        """Cria uma nova conversa."""
        # Garantir que o runner está inicializado
        try:
            if not self.runner.is_initialized:
                logger.info("🔧 Inicializando runner...")
                await self.runner.initialize()
                logger.info("✅ Runner inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar runner: {e}")
            # Continuar sem runner por enquanto
        
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            conversationId=conversation_id,
            name=f"Conversa {len(self._conversations) + 1}",
            isActive=True,
            messages=[]
        )
        
        self._conversations[conversation_id] = conversation
        self._messages[conversation_id] = []
        
        # Criar sessão no runner de forma assíncrona (se disponível)
        try:
            if self.runner and self.runner.session_service:
                await self.runner.session_service.create_session(conversation_id)
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível criar sessão no runner: {e}")
        
        logger.info(f"Nova conversa criada: {conversation_id}")
        return conversation
    
    def sanitize_message(self, message: Message) -> Message:
        """Sanitiza mensagem para processamento."""
        # Garantir campos necessários
        if not hasattr(message, 'messageId') or not message.messageId:
            message.messageId = str(uuid.uuid4())
        
        if not hasattr(message, 'contextId') or not message.contextId:
            message.contextId = 'default'
        
        if not hasattr(message, 'role'):
            message.role = Role.user
        
        if not hasattr(message, 'parts') or not message.parts:
            message.parts = [TextPart(text="")]
        
        return message
    
    async def process_message(self, message: Message):
        """Processa uma mensagem usando ClaudeRunner."""
        logger.info(f"🔵 [process_message] Iniciando processamento")
        message = self.sanitize_message(message)
        conversation_id = message.contextId
        
        logger.info(f"📝 [process_message] Conversa: {conversation_id[:8]}, Role: {message.role}")
        
        # Garantir que conversa existe
        if conversation_id not in self._conversations:
            logger.info(f"⚠️ Conversa {conversation_id[:8]} não existe, criando com ID específico...")
            # Criar conversa com o ID específico fornecido
            self._conversations[conversation_id] = Conversation(
                conversationId=conversation_id,  # USAR O ID CORRETO
                messages=[],
                status="active"
            )
            logger.info(f"✅ Conversa criada com ID: {conversation_id[:8]}...")
        
        # Adicionar mensagem ao histórico
        if conversation_id not in self._messages:
            self._messages[conversation_id] = []
        self._messages[conversation_id].append(message)
        logger.info(f"✅ Mensagem do usuário adicionada ao histórico")
        
        # Extrair texto da mensagem
        user_text = extract_text_from_message(message)
        logger.info(f"💬 Texto extraído: {user_text[:50]}...")
        
        # Criar task
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            context_id=conversation_id,
            status=TaskStatus(state=TaskState.submitted),
            history=[message]
        )
        self._tasks[task_id] = task
        # Adicionar ao gerenciador de tasks para conversão automática
        self.task_manager.add_a2a_task(task)
        self._pending_messages[task_id] = "Processando com Claude..."
        logger.info(f"📌 Task criada: {task_id[:8]}")
        
        # Emitir evento de status inicial
        await self.callback_manager.emit_event(
            CTaskStatusUpdateEvent(
                task_id=task_id,
                status=task.status,
                context_id=conversation_id,
                message=message
            ),
            self._agents[0] if self._agents else None
        )
        
        try:
            # Verificar se runner está inicializado
            if not self.runner.is_initialized:
                logger.warning("⚠️ Runner não inicializado, inicializando...")
                await self.runner.initialize()
            
            # Processar com ClaudeRunner real
            logger.info(f"🚀 Chamando ClaudeRunner.run_async('{user_text[:30]}...', '{conversation_id[:8]}...')")
            
            try:
                # Consumir o AsyncGenerator do ClaudeRunner
                response_text = ""
                events_received = []
                
                logger.info(f"🔄 Consumindo eventos do ClaudeRunner (padrão yield/pause/resume)...")
                async for event in self.runner.run_async(user_text, conversation_id):
                    logger.info(f"📡 Evento: {event.get('type', 'unknown')}")
                    events_received.append(event)
                    
                    # Processar diferentes tipos de eventos (yield/pause/resume pattern)
                    if event.get("type") == "processing_start":
                        logger.info("⏳ YIELD: Iniciando processamento")
                        # PAUSE: Aqui o runner pausa para processar o evento
                        
                    elif event.get("type") == "input_registered":
                        logger.info("📝 YIELD: Entrada registrada")
                        # PAUSE: Aqui o runner pausa novamente
                        
                    elif event.get("type") == "response_generated":
                        response_text = event.get("response", "")
                        logger.info(f"💡 YIELD: Resposta gerada: {response_text[:50]}...")
                        # PAUSE: Runner pausa para processar resposta
                        
                    elif event.get("type") == "processing_complete":
                        # Evento final - RESUME completo
                        if not response_text:
                            response_text = event.get("response", "")
                        logger.info(f"✅ RESUME: Processamento completo")
                
                # Se não houver resposta, usar fallback
                if not response_text:
                    response_text = f"[Sistema] Processando: {user_text[:50]}..."
                    logger.warning("⚠️ Claude não retornou resposta, usando fallback")
                    
            except Exception as e:
                # Em caso de erro, usar resposta de fallback
                logger.warning(f"⚠️ Erro ao consumir eventos do ClaudeRunner: {e}")
                import traceback
                logger.error(traceback.format_exc())
                response_text = f"[Sistema] Echo: {user_text} (Claude temporariamente indisponível)"
            
            logger.info(f"✅ Resposta obtida: {response_text[:100]}...")
            
            # Verificar se resposta é grande para usar artifacts
            if len(response_text) > 10000:  # Resposta maior que 10KB
                # Criar artifact para conteúdo grande
                artifact = Artifact(
                    id=str(uuid.uuid4()),
                    name="response_content",
                    type="text",
                    content=response_text,
                    metadata={"size": len(response_text)}
                )
                
                # Criar chunks se necessário
                chunks = self.artifact_manager.chunk_artifact(artifact)
                if chunks:
                    logger.info(f"📦 Resposta dividida em {len(chunks)} chunks")
                    # Emitir eventos de artifact para cada chunk
                    for chunk in chunks:
                        await self.callback_manager.emit_event(
                            TaskArtifactUpdateEvent(
                                task_id=task_id,
                                artifact=artifact,
                                context_id=conversation_id,
                                append=True  # Adicionar ao artifact existente
                            ),
                            self._agents[0] if self._agents else None
                        )
                
                # Criar mensagem com referência ao artifact
                response_message = Message(
                    messageId=str(uuid.uuid4()),
                    contextId=conversation_id,
                    role=Role.agent,
                    parts=[
                        TextPart(text=f"[Resposta grande armazenada como artifact {artifact.id}]"),
                        DataPart(data={"artifact_id": artifact.id, "size": len(response_text)})
                    ]
                )
            else:
                # Resposta normal em texto
                response_message = Message(
                    messageId=str(uuid.uuid4()),
                    contextId=conversation_id,
                    role=Role.agent,
                    parts=[TextPart(text=response_text)]
                )
            
            # Log de debug para verificar role
            logger.info(f"✅ Criando resposta do Claude com role={response_message.role}")
            logger.info(f"   Role type: {type(response_message.role)}, value: {response_message.role}")
            
            # Adicionar ao histórico
            self._messages[conversation_id].append(response_message)
            
            # Verificar se foi salvo corretamente
            saved_msg = self._messages[conversation_id][-1]
            logger.info(f"📝 Mensagem salva com role={saved_msg.role}")
            
            # Atualizar task
            task.status.state = TaskState.completed
            task.history.append(response_message)
            # Atualizar no gerenciador de tasks
            self.task_manager.update_task_status(task_id, TaskState.completed)
            
            # Emitir evento de conclusão
            await self.callback_manager.emit_event(
                CTaskStatusUpdateEvent(
                    task_id=task_id,
                    status=task.status,
                    context_id=conversation_id,
                    message=response_message
                ),
                self._agents[0] if self._agents else None
            )
            
            # Criar evento com timestamp
            import time
            self._events.append(Event(
                id=str(uuid.uuid4()),
                actor='claude',
                content=response_message,
                timestamp=time.time()  # Adicionar timestamp obrigatório
            ))
            
            # Remover de pendentes
            if task_id in self._pending_messages:
                del self._pending_messages[task_id]
            
            logger.info(f"Mensagem processada com sucesso: {conversation_id}")
            return response_message
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
            logger.error(f"   Tipo do erro: {type(e).__name__}")
            import traceback
            logger.error(f"   Stack trace:\n{traceback.format_exc()}")
            
            task.status.state = TaskState.failed
            # Atualizar no gerenciador de tasks
            self.task_manager.update_task_status(task_id, TaskState.failed)
            
            # Emitir evento de falha
            await self.callback_manager.emit_event(
                CTaskStatusUpdateEvent(
                    task_id=task_id,
                    status=task.status,
                    context_id=conversation_id,
                    message=None
                ),
                self._agents[0] if self._agents else None
            )
            
            if task_id in self._pending_messages:
                del self._pending_messages[task_id]
            raise
    
    def process_message_threadsafe(self, message: Message, loop: asyncio.AbstractEventLoop):
        """Safely run process_message from a thread using the given event loop."""
        logger.info(f"🔷 [process_message_threadsafe] Iniciando com message_id={message.messageId[:8]}")
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.process_message(message), loop
            )
            logger.info(f"🔷 [process_message_threadsafe] Future criado: {future}")
            # Não bloquear aqui - deixar a thread continuar
            return future
        except Exception as e:
            logger.error(f"❌ [process_message_threadsafe] Erro: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def register_agent(self, url: str):
        """Registra um agente (não aplicável para Claude)."""
        logger.info(f"Registro de agente ignorado (Claude usa CLI local): {url}")
    
    def get_pending_messages(self) -> list[tuple[str, str]]:
        """Retorna mensagens pendentes."""
        return list(self._pending_messages.items())
    
    def get_conversation(self, conversationid: str | None) -> Conversation | None:
        """Obtém uma conversa específica."""
        if conversationid:
            conv = self._conversations.get(conversationid)
            if conv and conversationid in self._messages:
                conv.messages = self._messages[conversationid]
                logger.info(f"🔍 Retornando conversa {conversationid[:8]} com {len(conv.messages)} mensagens")
                for i, msg in enumerate(conv.messages):
                    logger.info(f"   Msg {i}: role={getattr(msg, 'role', 'NO_ROLE')}")
            return conv
        return None
    
    @property
    def conversations(self) -> list[Conversation]:
        """Lista todas as conversas."""
        # Atualizar mensagens nas conversas
        for conv_id, conv in self._conversations.items():
            if conv_id in self._messages:
                conv.messages = self._messages[conv_id]
        return list(self._conversations.values())
    
    @property
    def tasks(self) -> list[Task]:
        """Lista todas as tasks."""
        return list(self._tasks.values())
    
    @property
    def agents(self) -> list[AgentCard]:
        """Lista agentes disponíveis."""
        return self._agents
    
    @property
    def events(self) -> list[Event]:
        """Lista eventos do sistema."""
        return self._events[-100:]  # Últimos 100 eventos
    
    # ========================================================================
    # MÉTODOS ADICIONAIS PARA COMPATIBILIDADE TOTAL
    # ========================================================================
    
    async def send_message(
        self,
        message: Message,
        task_callback=None
    ) -> Dict[str, Any]:
        """
        Envia mensagem e processa resposta (compatível com ADKHostManager).
        """
        # Processar mensagem
        response = await self.process_message(message)
        
        # Chamar callback se fornecido
        if task_callback:
            # Encontrar task correspondente
            for task in self._tasks.values():
                if task.history and task.history[-1].messageId == response.messageId:
                    await task_callback(task)
                    break
        
        return {
            "message": response,
            "task_id": task.id if task else None
        }
    
    def update_api_key(self, api_key: str):
        """
        Atualiza API key (não usado para Claude).
        Claude usa CLI local e não precisa de API key.
        """
        logger.info("Claude não usa API key - usando CLI local")
    
    async def list_messages(self, conversation_id: str) -> List[Message]:
        """Lista mensagens de uma conversa."""
        return self._messages.get(conversation_id, [])
    
    async def list_conversations(self) -> List[Conversation]:
        """Lista todas as conversas."""
        return self.conversations
    
    async def list_tasks(self) -> List[Task]:
        """Lista todas as tasks."""
        return self.tasks
    
    async def get_events(self) -> List[Event]:
        """Obtém eventos do sistema."""
        return self.events
    
    def close(self):
        """Fecha o manager e libera recursos."""
        if self.runner:
            self.runner.close()
        
        self._conversations.clear()
        self._messages.clear()
        self._tasks.clear()
        self._events.clear()
        self._pending_messages.clear()
        
        logger.info("Claude ADK Host Manager fechado")


# ============================================================================
# TESTE DO MANAGER
# ============================================================================

async def test_claude_adk_manager():
    """Testa o Claude ADK Host Manager."""
    print("🧪 Testando Claude ADK Host Manager...")
    
    # Criar cliente HTTP mock
    http_client = httpx.AsyncClient()
    
    # Criar manager
    manager = ClaudeADKHostManager(http_client)
    await manager.initialize()
    
    print("✅ Manager inicializado")
    
    # Criar conversa
    conversation = manager.create_conversation()
    print(f"✅ Conversa criada: {conversation.conversationId}")
    
    # Criar mensagem de teste
    test_message = Message(
        messageId=str(uuid.uuid4()),
        contextId=conversation.conversationId,
        role=Role.user,
        parts=[TextPart(text="Olá Claude! Responda apenas: TESTE OK")]
    )
    
    print("📤 Enviando mensagem de teste...")
    
    try:
        # Processar mensagem
        response = await manager.process_message(test_message)
        
        if response:
            response_text = extract_text_from_message(response)
            print(f"📥 Resposta: {response_text[:100]}...")
            print("✅ Teste passou!")
        else:
            print("❌ Sem resposta")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Verificar estado
    print(f"\n📊 Estado do sistema:")
    print(f"  Conversas: {len(manager.conversations)}")
    print(f"  Tasks: {len(manager.tasks)}")
    print(f"  Eventos: {len(manager.events)}")
    print(f"  Agentes: {len(manager.agents)}")
    
    # Fechar
    manager.close()
    await http_client.aclose()
    
    print("\n✅ Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_claude_adk_manager())