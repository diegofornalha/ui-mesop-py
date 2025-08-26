import asyncio
import base64
import os
import threading
import uuid

from typing import cast

import httpx

from a2a.types import FilePart, FileWithUri, Message, Part
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

# from .adk_host_manager import ADKHostManager  # Não usado - sempre Claude
from .claude_adk_host_manager import get_message_id
from .application_manager import ApplicationManager
# from .in_memory_manager import InMemoryFakeAgentManager  # Não usado - sempre Claude


class ConversationServer:
    """ConversationServer is the backend to serve the agent interactions in the UI

    This defines the interface that is used by the Mesop system to interact with
    agents and provide details about the executions.
    """

    def __init__(self, app: FastAPI, http_client: httpx.AsyncClient):
        agent_manager = os.environ.get('A2A_HOST', 'ADK')
        self.manager: ApplicationManager

        # Sempre usar Claude - sem necessidade de API key
        from .claude_adk_host_manager import ClaudeADKHostManager
        self.manager = ClaudeADKHostManager(http_client)
        # Inicialização assíncrona será feita automaticamente quando necessário
        self._file_cache = {}  # dict[str, FilePart] maps file id to message data
        self._message_to_cache = {}  # dict[str, str] maps message id to cache id

        app.add_api_route(
            '/conversation/create', self._create_conversation, methods=['POST']
        )
        app.add_api_route(
            '/conversation/list', self._list_conversation, methods=['POST']
        )
        app.add_api_route('/message/send', self._send_message, methods=['POST'])
        app.add_api_route('/events/get', self._get_events, methods=['POST'])
        app.add_api_route(
            '/message/list', self._list_messages, methods=['POST']
        )
        app.add_api_route(
            '/message/pending', self._pending_messages, methods=['POST']
        )
        app.add_api_route('/task/list', self._list_tasks, methods=['POST'])
        app.add_api_route(
            '/agent/register', self._register_agent, methods=['POST']
        )
        app.add_api_route('/agent/list', self._list_agents, methods=['POST'])
        app.add_api_route(
            '/message/file/{file_id}', self._files, methods=['GET']
        )
        # Endpoint mantido para compatibilidade, mas não faz nada
        app.add_api_route(
            '/api_key/update', self._update_api_key, methods=['POST']
        )

    # Método mantido para compatibilidade, mas não faz nada com Claude
    def update_api_key(self, api_key: str):
        pass  # Claude não precisa de API key

    async def _create_conversation(self):
        c = await self.manager.create_conversation()
        return CreateConversationResponse(result=c)

    async def _send_message(self, request: Request):
        message_data = await request.json()
        message = Message(**message_data['params'])
        message = self.manager.sanitize_message(message)
        loop = asyncio.get_event_loop()
        
        # Import para verificar tipo
        from .claude_adk_host_manager import ClaudeADKHostManager
        
        print(f"🔍 [SEND_MESSAGE] Manager type: {type(self.manager).__name__}")
        print(f"   Message ID: {message.messageId[:8]}...")
        print(f"   Context ID: {message.contextId[:8]}...")
        
        if isinstance(self.manager, ClaudeADKHostManager):
            # Ambos têm process_message_threadsafe
            print(f"✅ Usando process_message_threadsafe")
            t = threading.Thread(
                target=lambda: self.manager.process_message_threadsafe(message, loop)
            )
        else:
            print(f"⚠️ Usando asyncio.run diretamente")
            t = threading.Thread(
                target=lambda: asyncio.run(
                    self.manager.process_message(message)
                )
            )
        t.start()
        print(f"🚀 Thread iniciada para processar mensagem")
        return SendMessageResponse(
            result=MessageInfo(
                messageid=message.messageId,
                contextid=message.contextId if message.contextId else '',
            )
        )

    async def _list_messages(self, request: Request):
        message_data = await request.json()
        conversationid = message_data['params']
        conversation = self.manager.get_conversation(conversationid)
        if conversation:
            messages = conversation.messages
            print(f"🔍 [SERVER] Listando {len(messages)} mensagens da conversa {conversationid[:8]}")
            for i, msg in enumerate(messages):
                role = getattr(msg, 'role', 'NO_ROLE')
                print(f"   [SERVER] Msg {i}: role={role}, type={type(role)}")
            
            cached_messages = self.cache_content(messages)
            
            print(f"📤 [SERVER] Retornando mensagens após cache:")
            for i, msg in enumerate(cached_messages):
                role = getattr(msg, 'role', 'NO_ROLE')
                print(f"   [CACHED] Msg {i}: role={role}")
            
            return ListMessageResponse(result=cached_messages)
        return ListMessageResponse(result=[])

    def cache_content(self, messages: list[Message]):
        rval = []
        for m in messages:
            messageid = get_message_id(m)
            if not messageid:
                rval.append(m)
                continue
            new_parts: list[Part] = []
            for i, p in enumerate(m.parts):
                # Handle both dict and object formats for part
                if isinstance(p, dict):
                    if 'root' in p:
                        part = p['root']
                    else:
                        part = p
                elif hasattr(p, 'root'):
                    part = p.root
                else:
                    part = p
                    
                # Get kind attribute safely
                kind = part.get('kind') if isinstance(part, dict) else getattr(part, 'kind', None)
                if kind != 'file':
                    new_parts.append(p)
                    continue
                message_part_id = f'{messageid}:{i}'
                if message_part_id in self._message_to_cache:
                    cache_id = self._message_to_cache[message_part_id]
                else:
                    cache_id = str(uuid.uuid4())
                    self._message_to_cache[message_part_id] = cache_id
                # Replace the part data with a url reference
                file_obj = part.get('file') if isinstance(part, dict) else getattr(part, 'file', None)
                mime_type = file_obj.mime_type if file_obj and hasattr(file_obj, 'mime_type') else ''
                new_parts.append(
                    FilePart(
                        file=FileWithUri(
                            mime_type=mime_type,
                            uri=f'/message/file/{cache_id}',
                        )
                    )
                )
                if cache_id not in self._file_cache:
                    self._file_cache[cache_id] = part
            m.parts = new_parts
            rval.append(m)
        return rval

    async def _pending_messages(self):
        return PendingMessageResponse(
            result=self.manager.get_pending_messages()
        )

    def _list_conversation(self):
        return ListConversationResponse(result=self.manager.conversations)

    def _get_events(self):
        return GetEventResponse(result=self.manager.events)

    def _list_tasks(self):
        # Por enquanto, retornar lista vazia para evitar erro de validação
        # TODO: Converter dataclass Task para Pydantic Task
        return ListTaskResponse(result=[])

    async def _register_agent(self, request: Request):
        message_data = await request.json()
        url = message_data['params']
        self.manager.register_agent(url)
        return RegisterAgentResponse()

    async def _list_agents(self):
        return ListAgentResponse(result=self.manager.agents)

    def _files(self, file_id):
        if file_id not in self._file_cache:
            raise Exception('file not found')
        part = self._file_cache[file_id]
        if 'image' in part.file.mime_type:
            return Response(
                content=base64.b64decode(part.file.bytes),
                media_type=part.file.mime_type,
            )
        return Response(content=part.file.bytes, media_type=part.file.mime_type)

    async def _update_api_key(self, request: Request):
        """Endpoint mantido para compatibilidade - Claude não precisa de API key"""
        return {'status': 'success', 'message': 'Claude não precisa de API key'}
