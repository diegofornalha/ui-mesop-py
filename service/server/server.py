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
        
        print(f"🔍 [SEND_MESSAGE] Manager type: {type(self.manager).__name__}")
        print(f"   Message ID: {message.messageId[:8]}...")
        print(f"   Context ID: {message.contextId[:8]}...")
        
        # Processar mensagem de forma assíncrona
        # Usar create_task para não bloquear mas garantir execução
        task = asyncio.create_task(self._process_message_async(message))
        
        # Aguardar um pouco para garantir que começou
        await asyncio.sleep(0.1)
        
        print(f"✅ Mensagem sendo processada em background")
        
        return SendMessageResponse(
            result=MessageInfo(
                messageid=message.messageId,
                contextid=message.contextId if message.contextId else '',
            )
        )
    
    async def _process_message_async(self, message: Message):
        """Processa mensagem de forma assíncrona em background."""
        try:
            print(f"🔄 [ASYNC] Processando mensagem {message.messageId[:8]}...")
            print(f"   [ASYNC] Manager: {type(self.manager).__name__}")
            print(f"   [ASYNC] Tem process_message? {hasattr(self.manager, 'process_message')}")
            
            # Verificar se é ClaudeADKHostManager
            from .claude_adk_host_manager import ClaudeADKHostManager
            if isinstance(self.manager, ClaudeADKHostManager):
                print(f"   [ASYNC] É ClaudeADKHostManager, chamando process_message...")
                result = await self.manager.process_message(message)
                print(f"   [ASYNC] Resultado retornado: {result}")
                
                # Verificar se a mensagem foi salva
                if hasattr(result, 'contextId') and result.contextId:
                    conv = self.manager.get_conversation(result.contextId)
                    if conv:
                        print(f"   [ASYNC] Conversa tem {len(conv.messages)} mensagens")
                        # Verificar última mensagem
                        if conv.messages:
                            last_msg = conv.messages[-1]
                            print(f"   [ASYNC] Última mensagem: role={getattr(last_msg, 'role', 'NO_ROLE')}")
                            if hasattr(last_msg, 'parts') and last_msg.parts:
                                content_preview = str(last_msg.parts[0])[:50] if last_msg.parts else "SEM_CONTEUDO"
                                print(f"   [ASYNC] Preview: {content_preview}...")
            else:
                print(f"   [ASYNC] Manager tipo: {type(self.manager)}")
            
            print(f"✅ [ASYNC] Mensagem processada com sucesso")
            return True  # Retornar sucesso
        except Exception as e:
            print(f"❌ [ASYNC] Erro ao processar mensagem: {e}")
            import traceback
            traceback.print_exc()
            return False  # Retornar falha

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
            
            # Converter mensagens a2a para formato compatível
            from .message_converter import convert_messages_for_api
            converted_messages = convert_messages_for_api(messages)
            
            # PATCH: Garantir messageId e preparar para UI
            for msg_dict in converted_messages:
                # Garantir que messageId existe
                if not msg_dict.get('messageId'):
                    import uuid
                    msg_dict['messageId'] = str(uuid.uuid4())
                
                # NÃO adicionar content aqui - será processado pela UI via extract_content
                # O campo content no modelo Message é string, não lista!
            
            print(f"📤 [SERVER] Retornando {len(converted_messages)} mensagens convertidas")
            
            return ListMessageResponse(result=converted_messages)
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
        # Usar ClaudeTaskManager para obter tasks convertidas
        from .claude_adk_host_manager import ClaudeADKHostManager
        
        if isinstance(self.manager, ClaudeADKHostManager):
            # Obter tasks Service do gerenciador
            service_tasks = self.manager.task_manager.get_service_tasks()
            return ListTaskResponse(result=service_tasks)
        else:
            # Fallback para outros managers
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
