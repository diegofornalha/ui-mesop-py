import json
import os
import sys
import traceback
import uuid

from typing import Any

from a2a.types import FileWithBytes, Message, Part, Role, Task, TaskState
from service.client.client import ConversationClient
from service.types import (
    Conversation,
    CreateConversationRequest,
    Event,
    GetEventRequest,
    ListAgentRequest,
    ListConversationRequest,
    ListMessageRequest,
    ListTaskRequest,
    MessageInfo,
    PendingMessageRequest,
    RegisterAgentRequest,
    SendMessageRequest,
)

from .state import (
    AppState,
    SessionTask,
    StateConversation,
    StateEvent,
    StateMessage,
    StateTask,
)


server_url = 'http://localhost:8888'


async def ListConversations() -> list[Conversation]:
    client = ConversationClient(server_url)
    try:
        response = await client.list_conversation(ListConversationRequest())
        return response.result if response.result else []
    except Exception as e:
        print('Failed to list conversations: ', e)
    return []


async def SendMessage(message: Message) -> Message | MessageInfo | None:
    client = ConversationClient(server_url)
    try:
        response = await client.send_message(SendMessageRequest(params=message))
        return response.result
    except Exception as e:
        traceback.print_exc()
        print('Failed to send message: ', e)
    return None


async def CreateConversation() -> Conversation:
    client = ConversationClient(server_url)
    try:
        response = await client.create_conversation(CreateConversationRequest())
        return (
            response.result
            if response.result
            else Conversation(conversationid='', isactive=False)
        )
    except Exception as e:
        print('Failed to create conversation', e)
    return Conversation(conversationid='', isactive=False)


async def ListRemoteAgents():
    client = ConversationClient(server_url)
    try:
        response = await client.list_agents(ListAgentRequest())
        return response.result
    except Exception as e:
        print('Failed to read agents', e)


async def AddRemoteAgent(path: str):
    client = ConversationClient(server_url)
    try:
        await client.register_agent(RegisterAgentRequest(params=path))
    except Exception as e:
        print('Failed to register the agent', e)


async def GetEvents() -> list[Event]:
    client = ConversationClient(server_url)
    try:
        response = await client.get_events(GetEventRequest())
        return response.result if response.result else []
    except Exception as e:
        print('Failed to get events', e)
    return []


async def GetProcessingMessages():
    client = ConversationClient(server_url)
    try:
        response = await client.get_pending_messages(PendingMessageRequest())
        return dict(response.result)
    except Exception as e:
        print('Error getting pending messages', e)


def GetMessageAliases():
    return {}


async def GetTasks():
    client = ConversationClient(server_url)
    try:
        response = await client.list_tasks(ListTaskRequest())
        return response.result
    except Exception as e:
        print('Failed to list tasks ', e)
        return []


async def ListMessages(conversationid: str) -> list[Message]:
    client = ConversationClient(server_url)
    try:
        response = await client.list_messages(
            ListMessageRequest(params=conversationid)
        )
        return response.result if response.result else []
    except Exception as e:
        print('Failed to list messages ', e)
    return []


async def UpdateAppState(state: AppState, conversationid: str):
    """Update the app state."""
    try:
        if conversationid:
            state.current_conversation_id = conversationid
            messages = await ListMessages(conversationid)
            if not messages:
                state.messages = []
            else:
                # Converter mensagens e aplicar lógica alternada para detectar role
                converted_messages = []
                for i, msg in enumerate(messages):
                    # Mensagens ímpares (0, 2, 4...) são do usuário
                    # Mensagens pares (1, 3, 5...) são do agente
                    state_msg = convert_message_to_state(msg)
                    
                    # Se o role não foi detectado corretamente, usar posição
                    if state_msg.role == 'user' and i % 2 == 1:
                        # Posição ímpar deve ser agente
                        state_msg.role = 'agent'
                        print(f"[DEBUG] Corrigido message {state_msg.messageId} para agent pela posição {i}")
                    
                    converted_messages.append(state_msg)
                
                state.messages = converted_messages
        conversations = await ListConversations()
        if not conversations:
            state.conversations = []
        else:
            state.conversations = [
                convert_conversation_to_state(x) for x in conversations
            ]

        state.task_list = []
        for task in await GetTasks():
            state.task_list.append(
                SessionTask(
                    contextId=extract_conversation_id(task),
                    task=convert_task_to_state(task),
                )
            )
        state.background_tasks = await GetProcessingMessages()
        state.message_aliases = GetMessageAliases()
    except Exception as e:
        print('Failed to update state: ', e)
        traceback.print_exc(file=sys.stdout)


async def UpdateApiKey(api_key: str):
    """Update the API key"""
    import httpx

    try:
        # Set the environment variable
        os.environ['GOOGLE_API_KEY'] = api_key

        # Call the update API endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{server_url}/api_key/update', json={'api_key': api_key}
            )
            response.raise_for_status()
        return True
    except Exception as e:
        print('Failed to update API key: ', e)
        return False


def convert_message_to_state(message: Message) -> StateMessage:
    if not message:
        return StateMessage()

    # Estratégia múltipla para detectar role
    role_value = 'user'  # Valor padrão
    
    # 1. Verificar se role existe e é enum ou string
    if hasattr(message, 'role') and message.role is not None:
        if hasattr(message.role, 'name'):
            role_value = message.role.name
            print(f"[DEBUG] Message {message.messageId}: Role enum = {role_value}")
        else:
            role_value = str(message.role)
            print(f"[DEBUG] Message {message.messageId}: Role string = {role_value}")
    
    # 2. Se não tem role, verificar taskId (mensagens com taskId geralmente são do agente)
    elif hasattr(message, 'taskId') and message.taskId:
        role_value = 'agent'
        print(f"[DEBUG] Message {message.messageId}: Detectado como agent pelo taskId: {message.taskId}")
    
    # 3. Verificar se tem author e contém 'agent' ou 'gemini'
    elif hasattr(message, 'author'):
        author_str = str(message.author).lower()
        if 'agent' in author_str or 'gemini' in author_str or 'ai' in author_str:
            role_value = 'agent'
            print(f"[DEBUG] Message {message.messageId}: Detectado como agent pelo author: {message.author}")
        else:
            print(f"[DEBUG] Message {message.messageId}: Author encontrado mas não é agent: {message.author}")
    
    # 4. Verificar conteúdo da mensagem (heurística adicional)
    elif hasattr(message, 'parts') and message.parts:
        # Se a mensagem tem conteúdo complexo ou formatado, pode ser do agente
        content_str = str(message.parts).lower()
        if 'olá' in content_str and 'como posso' in content_str:
            role_value = 'agent'
            print(f"[DEBUG] Message {message.messageId}: Detectado como agent pelo conteúdo")
    else:
        print(f"[DEBUG] Message {message.messageId}: Usando padrão user - nenhuma detecção funcionou")

    # Log final
    print(f"[DEBUG] Final role for message {message.messageId}: {role_value}")

    return StateMessage(
        messageId=message.messageId,  # Usando camelCase padrão
        contextId=message.contextId if message.contextId else '',
        taskId=getattr(message, 'taskId', '') or '',  # Garante string vazia se None
        role=role_value,
        content=extract_content(message.parts),
    )


def convert_conversation_to_state(
    conversation: Conversation,
) -> StateConversation:
    return StateConversation(
        conversationId=conversation.conversationId,  # Usar campo real camelCase
        conversationName=conversation.name,
        isActive=conversation.isActive,  # Usar campo real camelCase
        messageIds=[extract_message_id(x) for x in conversation.messages],
    )


def convert_task_to_state(task: Task) -> StateTask:
    # Get the first message as the description
    output = (
        [extract_content(a.parts) for a in task.artifacts]
        if task.artifacts
        else []
    )
    if not task.history:
        return StateTask(
            taskId=task.id,
            contextId=task.context_id,
            state=TaskState.failed.name,
            message=StateMessage(
                messageId=str(uuid.uuid4()),
                contextId=task.context_id,
                taskId=task.id,
                role='agent',  # Role.agent.name simplificado para evitar erro
                content=[('No history', 'text')],
            ),
            artifacts=output,
        )
    message = task.history[0]
    last_message = task.history[-1]
    if last_message != message:
        output = [extract_content(last_message.parts)] + output
    return StateTask(
        taskId=task.id,
        contextId=task.context_id,
        state=str(task.status.state),
        message=convert_message_to_state(message),
        artifacts=output,
    )


def convert_event_to_state(event: Event) -> StateEvent:
    # Verificar se event.content é dict ou objeto
    if isinstance(event.content, dict):
        # Se content é dict
        content_dict = event.content
        role_value = content_dict.get('role', 'agent')
        if hasattr(role_value, 'name'):  # Se role é enum
            role_value = role_value.name
        else:
            role_value = str(role_value)
        
        # Extrair parts do dict
        parts = content_dict.get('parts', [])
        context_id = content_dict.get('contextId', content_dict.get('context_id', ''))
    else:
        # Se content é objeto
        if hasattr(event.content, 'role'):
            if hasattr(event.content.role, 'name'):
                role_value = event.content.role.name
            else:
                role_value = str(event.content.role)
        else:
            role_value = 'agent'  # Valor padrão para eventos
        
        # Extrair parts do objeto
        parts = getattr(event.content, 'parts', [])
        context_id = extract_message_conversation(event.content)
    
    return StateEvent(
        contextId=context_id,
        actor=getattr(event, 'actor', ''),
        role=role_value,
        id=getattr(event, 'id', ''),
        content=extract_content(parts),
    )


def extract_content(
    message_parts: list[Part],
) -> list[tuple[str | dict[str, Any], str]]:
    parts: list[tuple[str | dict[str, Any], str]] = []
    if not message_parts:
        return []
    for part in message_parts:
        # Handle both dict and object formats
        if isinstance(part, dict):
            if 'root' in part:
                p = part['root']
            else:
                p = part
        elif hasattr(part, 'root'):
            p = part.root
        else:
            p = part
            
        # Get kind attribute safely
        kind = p.get('kind') if isinstance(p, dict) else getattr(p, 'kind', None)
        
        if kind == 'text':
            text = p.get('text') if isinstance(p, dict) else getattr(p, 'text', '')
            parts.append((text, 'text/plain'))
        elif kind == 'file':
            file_obj = p.get('file') if isinstance(p, dict) else getattr(p, 'file', None)
            if file_obj and isinstance(file_obj, FileWithBytes):
                parts.append((file_obj.bytes, file_obj.mime_type or ''))
            elif file_obj:
                parts.append((file_obj.uri, file_obj.mime_type or ''))
        elif kind == 'data':
            data = p.get('data') if isinstance(p, dict) else getattr(p, 'data', None)
            if data:
                try:
                    jsonData = json.dumps(data)
                    if 'type' in data and data['type'] == 'form':
                        parts.append((data, 'form'))
                    else:
                        parts.append((jsonData, 'application/json'))
                except Exception as e:
                    print('Failed to dump data', e)
                    parts.append(('<data>', 'text/plain'))
    return parts


def extract_message_id(message: Message) -> str:
    if isinstance(message, dict):
        return message.get('messageId', message.get('messageid', ''))
    # Tentar primeiro messageId (padrão), depois messageid (compatibilidade)
    return getattr(message, 'messageId', getattr(message, 'messageid', ''))


def extract_message_conversation(message: Message) -> str:
    # Tentar contextId primeiro (padrão), depois context_id (compatibilidade)
    if hasattr(message, 'contextId'):
        return message.contextId if message.contextId else ''
    return message.context_id if hasattr(message, 'context_id') and message.context_id else ''


def extract_conversation_id(task: Task) -> str:
    if task.context_id:
        return task.context_id
    # Tries to find the first conversation id for the message in the task.
    if task.status.message:
        return task.status.message.context_id or ''
    return ''
