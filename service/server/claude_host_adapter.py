"""
Claude Host Adapter - Integração do Claude com o sistema ADK existente.
Implementa a interface ApplicationManager para compatibilidade total.
"""

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from a2a.types import (
    Message,
    Part,
    TextPart,
    Role,
    Task,
    TaskState,
    TaskStatus,
)

from service.types import Conversation, Event, MessageInfo
from service.server.application_manager import ApplicationManager

# Importar o nosso Claude Host Manager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents.claude_host_manager import ClaudeHostManager

logger = logging.getLogger(__name__)


class ClaudeHostAdapter(ApplicationManager):
    """
    Adaptador para integrar Claude Host Manager com o sistema ADK.
    Implementa a mesma interface que ADKHostManager.
    """
    
    def __init__(self, http_client: httpx.AsyncClient):
        """Inicializa o adaptador."""
        self.http_client = http_client
        self.claude_manager = None
        self._conversations: Dict[str, Conversation] = {}
        self._messages: Dict[str, List[Message]] = {}
        self._tasks: Dict[str, Task] = {}
        self._events: List[Event] = []
        
        # Inicializar Claude de forma assíncrona será feito em create_conversation
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Garante que o Claude Manager está inicializado."""
        if not self._initialized:
            self.claude_manager = await ClaudeHostManager().initialize()
            self._initialized = True
            logger.info("✅ Claude Host Adapter inicializado")
    
    def sanitize_message(self, message: Message) -> Message:
        """Sanitiza a mensagem para o formato esperado."""
        # Garantir que a mensagem tem os campos necessários
        if not message.messageId:
            message.messageId = str(uuid.uuid4())
        if not message.contextId:
            message.contextId = 'default'
        if not message.role:
            message.role = Role.user
        return message
    
    async def create_conversation(self) -> Conversation:
        """Cria uma nova conversa."""
        await self._ensure_initialized()
        
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            conversationId=conversation_id,
            name=f"Conversa {len(self._conversations) + 1}",
            isActive=True,
            messages=[]
        )
        
        self._conversations[conversation_id] = conversation
        self._messages[conversation_id] = []
        
        logger.info(f"Nova conversa criada: {conversation_id}")
        return conversation
    
    async def list_conversation(self) -> List[Conversation]:
        """Lista todas as conversas."""
        return list(self._conversations.values())
    
    async def send_message(
        self, 
        message: Message, 
        task_callback=None
    ) -> MessageInfo:
        """Envia mensagem para o Claude."""
        await self._ensure_initialized()
        
        # Sanitizar mensagem
        message = self.sanitize_message(message)
        conversation_id = message.contextId
        
        # Garantir que a conversa existe
        if conversation_id not in self._conversations:
            await self.create_conversation()
        
        # Adicionar mensagem do usuário ao histórico
        if conversation_id not in self._messages:
            self._messages[conversation_id] = []
        self._messages[conversation_id].append(message)
        
        # Extrair texto da mensagem
        user_text = ""
        if message.parts:
            for part in message.parts:
                if isinstance(part, TextPart) or (hasattr(part, 'text')):
                    text_value = part.text if hasattr(part, 'text') else str(part)
                    user_text += text_value + " "
        
        # Criar task para resposta
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            context_id=conversation_id,
            status=TaskStatus(state=TaskState.submitted),
            history=[message]
        )
        self._tasks[task_id] = task
        
        # Processar com Claude de forma assíncrona
        asyncio.create_task(
            self._process_claude_response(
                conversation_id, 
                user_text.strip(), 
                task_id,
                task_callback
            )
        )
        
        # Retornar info da mensagem
        return MessageInfo(
            messageId=message.messageId,
            taskId=task_id
        )
    
    async def _process_claude_response(
        self, 
        conversation_id: str, 
        user_text: str,
        task_id: str,
        task_callback=None
    ):
        """Processa resposta do Claude de forma assíncrona."""
        try:
            # Atualizar estado da task
            if task_id in self._tasks:
                self._tasks[task_id].status.state = TaskState.submitted
            
            # Obter resposta do Claude
            response_text = ""
            async for response_part in self.claude_manager.process_message(
                session_id=conversation_id,
                message=user_text
            ):
                if response_part.get('type') == 'text':
                    response_text += response_part.get('content', '')
            
            # Criar mensagem de resposta
            response_message = Message(
                messageId=str(uuid.uuid4()),
                contextId=conversation_id,
                role=Role.agent,
                parts=[TextPart(text=response_text)] if response_text else []
            )
            
            # Adicionar ao histórico
            self._messages[conversation_id].append(response_message)
            
            # Atualizar task
            if task_id in self._tasks:
                self._tasks[task_id].status.state = TaskState.completed
                self._tasks[task_id].history.append(response_message)
            
            # Chamar callback se fornecido
            if task_callback:
                await task_callback(self._tasks[task_id])
            
            # Adicionar evento
            self._events.append(Event(
                id=str(uuid.uuid4()),
                actor='claude',
                content=response_message
            ))
            
            logger.info(f"Resposta do Claude processada para conversa {conversation_id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta do Claude: {e}")
            if task_id in self._tasks:
                self._tasks[task_id].status.state = TaskState.failed
    
    async def list_messages(self, conversation_id: str) -> List[Message]:
        """Lista mensagens de uma conversa."""
        return self._messages.get(conversation_id, [])
    
    async def get_pending_messages(self) -> Dict[str, str]:
        """Retorna mensagens pendentes."""
        pending = {}
        for task_id, task in self._tasks.items():
            if task.status.state == TaskState.submitted:
                pending[task_id] = "Processando com Claude..."
        return pending
    
    async def list_tasks(self) -> List[Task]:
        """Lista todas as tasks."""
        return list(self._tasks.values())
    
    async def list_agents(self) -> List[str]:
        """Lista agentes disponíveis."""
        return ["Claude (CLI local - sem API key)"]
    
    async def get_events(self) -> List[Event]:
        """Retorna eventos do sistema."""
        return self._events[-100:]  # Últimos 100 eventos
    
    # Implementar métodos abstratos da interface ApplicationManager
    async def process_message(self, message: Message):
        """Processa uma mensagem (compatibilidade com interface)."""
        return await self.send_message(message)
    
    def register_agent(self, url: str):
        """Registra agente (método síncrono para interface)."""
        logger.info(f"Registro de agente ignorado: {url}")
    
    def get_pending_messages(self) -> list[tuple[str, str]]:
        """Retorna mensagens pendentes (formato de tupla)."""
        pending = []
        for task_id, task in self._tasks.items():
            if task.status.state == TaskState.submitted:
                pending.append((task_id, "Processando com Claude..."))
        return pending
    
    def get_conversation(self, conversationid: str | None) -> Conversation | None:
        """Obtém uma conversa específica."""
        if conversationid:
            return self._conversations.get(conversationid)
        return None
    
    @property
    def conversations(self) -> list[Conversation]:
        """Propriedade: lista de conversas."""
        return list(self._conversations.values())
    
    @property
    def tasks(self) -> list[Task]:
        """Propriedade: lista de tasks."""
        return list(self._tasks.values())
    
    @property
    def agents(self) -> list:
        """Propriedade: lista de agentes."""
        # Retornar um AgentCard simulado para Claude
        from a2a.types import AgentCard
        return [AgentCard(
            name="Claude Assistant",
            description="Claude AI via CLI local (sem API key)",
            author="Anthropic",
            version="1.0.0"
        )]
    
    @property  
    def events(self) -> list[Event]:
        """Propriedade: lista de eventos."""
        return self._events[-100:]  # Últimos 100 eventos