"""
Server V2 - Usando ClaudeRunner como orquestrador principal (arquitetura correta do ADK).
"""

import asyncio
import base64
import os
import uuid
from typing import cast, Dict, Any, List

import httpx
from a2a.types import FilePart, FileWithUri, Message, Part, TextPart, Role
from fastapi import FastAPI, Request, Response

from service.types import (
    CreateConversationResponse,
    GetEventResponse,
    ListAgentResponse,
    ListConversationResponse,
    ListMessageResponse,
    ListTaskResponse,
    MessageInfo,
    PendingMessageResponse,
    RegisterAgentResponse,
    SendMessageResponse,
)

# Importar nova arquitetura
from agents.claude_runner_v2 import ClaudeRunner
from agents.claude_a2a_agent_v2 import ClaudeA2AAgent
from agents.claude_types import Content, Event

import logging
logger = logging.getLogger(__name__)


class ConversationServerV2:
    """
    Server V2 usando arquitetura correta do ADK.
    Runner é o orquestrador principal.
    """
    
    def __init__(self, app: FastAPI, http_client: httpx.AsyncClient):
        # Criar agente com SDK real
        self.agent = ClaudeA2AAgent(
            name="Claude Assistant",
            instruction="Você é um assistente útil que responde em português.",
            use_real_sdk=True  # Usar SDK real do Claude!
        )
        
        # Criar Runner (ORQUESTRADOR PRINCIPAL)
        self.runner = ClaudeRunner(
            agent=self.agent,
            app_name="mesop_ui"
        )
        
        # Estado para compatibilidade com UI existente
        self._messages: Dict[str, List[Message]] = {}  # conversation_id -> messages
        self._events: List[Event] = []
        self._tasks: Dict[str, Any] = {}
        self._pending_messages_dict: Dict[str, str] = {}  # Renomeado para evitar conflito
        self._file_cache = {}
        self._message_to_cache = {}
        
        # Configurar rotas
        self._setup_routes(app)
        
        # Inicialização assíncrona
        asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """Inicializa Runner e agente."""
        await self.runner.initialize()
        logger.info("✅ ConversationServerV2 inicializado")
    
    def _setup_routes(self, app: FastAPI):
        """Configura as rotas da API."""
        app.add_api_route('/conversation/create', self._create_conversation, methods=['POST'])
        app.add_api_route('/conversation/list', self._list_conversation, methods=['POST'])
        app.add_api_route('/message/send', self._send_message, methods=['POST'])
        app.add_api_route('/events/get', self._get_events, methods=['POST'])
        app.add_api_route('/message/list', self._list_messages, methods=['POST'])
        app.add_api_route('/message/pending', self._pending_messages, methods=['POST'])
        app.add_api_route('/task/list', self._list_tasks, methods=['POST'])
        app.add_api_route('/agent/register', self._register_agent, methods=['POST'])
        app.add_api_route('/agent/list', self._list_agents, methods=['POST'])
        app.add_api_route('/message/file/{file_id}', self._files, methods=['GET'])
        app.add_api_route('/api_key/update', self._update_api_key, methods=['POST'])
    
    async def _create_conversation(self):
        """Cria uma nova conversação."""
        conversation = await self.runner.create_conversation()
        conversation_id = conversation["conversationId"]
        self._messages[conversation_id] = []
        
        logger.info(f"✅ [SERVER V2] Conversação criada: {conversation_id[:8]}")
        return CreateConversationResponse(result=conversation)
    
    async def _send_message(self, request: Request):
        """Envia uma mensagem e processa com Runner."""
        message_data = await request.json()
        message = Message(**message_data['params'])
        
        # Garantir campos essenciais
        if not message.messageId:
            message.messageId = str(uuid.uuid4())
        if not message.contextId:
            message.contextId = str(uuid.uuid4())
        if not hasattr(message, 'role'):
            message.role = Role.user
        
        conversation_id = message.contextId
        logger.info(f"📨 [SERVER V2] Mensagem recebida: {message.messageId[:8]} para conversa {conversation_id[:8]}")
        
        # Adicionar mensagem do usuário ao histórico
        if conversation_id not in self._messages:
            self._messages[conversation_id] = []
        self._messages[conversation_id].append(message)
        
        # Processar assincronamente
        asyncio.create_task(self._process_message_async(message))
        
        return SendMessageResponse(
            result=MessageInfo(
                messageid=message.messageId,
                contextid=conversation_id
            )
        )
    
    async def _process_message_async(self, message: Message):
        """Processa mensagem usando Runner V2."""
        try:
            conversation_id = message.contextId
            logger.info(f"🔄 [SERVER V2] Processando mensagem com Runner")
            
            # Converter Message para Content
            content = self._message_to_content(message)
            
            # Processar com Runner (arquitetura correta!)
            response_text = ""
            async for event in self.runner.run_async(
                user_id="default_user",
                session_id=conversation_id,
                new_message=content
            ):
                logger.info(f"📡 [SERVER V2] Evento recebido: author={event.author}, complete={event.turn_complete}")
                
                # Capturar resposta do agente
                if event.author != "user" and event.content and event.turn_complete:
                    for part in event.content.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text
            
            # Criar mensagem de resposta
            if response_text:
                response_message = Message(
                    messageId=str(uuid.uuid4()),
                    contextId=conversation_id,
                    role=Role.agent,
                    parts=[TextPart(text=response_text)]
                )
                
                # Adicionar ao histórico
                self._messages[conversation_id].append(response_message)
                logger.info(f"✅ [SERVER V2] Resposta adicionada: {response_message.messageId[:8]}")
            
        except Exception as e:
            logger.error(f"❌ [SERVER V2] Erro ao processar: {e}")
            import traceback
            traceback.print_exc()
    
    def _message_to_content(self, message: Message) -> Content:
        """Converte Message A2A para Content ADK."""
        from agents.claude_types import Content
        parts = []
        
        for part in message.parts:
            if hasattr(part, 'text'):
                parts.append(part)  # Manter TextPart
            elif hasattr(part, 'file'):
                parts.append(part)  # Manter FilePart
            else:
                parts.append(str(part))
        
        return Content(parts=parts)
    
    async def _list_messages(self, request: Request):
        """Lista mensagens de uma conversação."""
        message_data = await request.json()
        conversation_id = message_data['params']
        
        messages = self._messages.get(conversation_id, [])
        logger.info(f"📋 [SERVER V2] Listando {len(messages)} mensagens da conversa {conversation_id[:8]}")
        
        # Converter para formato da API preservando messageId
        converted_messages = []
        for msg in messages:
            msg_dict = {
                "messageId": msg.messageId,  # PRESERVAR messageId!
                "contextId": msg.contextId or conversation_id,
                "role": str(msg.role.value if hasattr(msg.role, 'value') else msg.role),
                "parts": []
            }
            
            # Converter parts
            for part in msg.parts:
                if hasattr(part, 'text'):
                    msg_dict["parts"].append({
                        "text": part.text,
                        "kind": "text"
                    })
                elif hasattr(part, 'file'):
                    msg_dict["parts"].append({
                        "file": {
                            "uri": part.file.uri,
                            "mime_type": part.file.mime_type
                        },
                        "kind": "file"
                    })
            
            converted_messages.append(msg_dict)
        
        return ListMessageResponse(result=converted_messages)
    
    async def _pending_messages(self):
        """Retorna mensagens pendentes."""
        return PendingMessageResponse(
            result=list(self._pending_messages_dict.items())
        )
    
    async def _list_conversation(self):
        """Lista conversações."""
        conversations = self.runner.conversations
        return ListConversationResponse(result=conversations)
    
    async def _get_events(self):
        """Retorna eventos."""
        # Converter Events para formato esperado
        converted_events = []
        for event in self._events[-100:]:  # Últimos 100
            converted_events.append({
                "id": event.id,
                "actor": event.author,
                "content": str(event.content) if event.content else "",
                "timestamp": event.timestamp
            })
        return GetEventResponse(result=converted_events)
    
    async def _list_tasks(self):
        """Lista tasks."""
        # Por enquanto retornar lista vazia
        return ListTaskResponse(result=[])
    
    async def _register_agent(self, request: Request):
        """Registra agente (não usado com Claude)."""
        return RegisterAgentResponse()
    
    async def _list_agents(self):
        """Lista agentes."""
        # Retornar agente atual
        agents = [{
            "name": self.agent.name,
            "instruction": self.agent.instruction
        }]
        return ListAgentResponse(result=agents)
    
    def _files(self, file_id: str):
        """Serve arquivos."""
        if file_id not in self._file_cache:
            raise Exception('File not found')
        
        part = self._file_cache[file_id]
        if hasattr(part, 'file'):
            if 'image' in part.file.mime_type:
                return Response(
                    content=base64.b64decode(part.file.bytes),
                    media_type=part.file.mime_type
                )
            return Response(
                content=part.file.bytes,
                media_type=part.file.mime_type
            )
        return Response(content="", media_type="text/plain")
    
    async def _update_api_key(self, request: Request):
        """Atualiza API key (não usado com Claude)."""
        return {'status': 'success', 'message': 'Claude não precisa de API key'}