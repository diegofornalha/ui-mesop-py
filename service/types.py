"""
Tipos consolidados - fonte única de verdade.
Conformidade total com A2A Protocol, Google ADK e Pydantic.
"""

from typing import Annotated, Any, Literal, Optional, Union, List, Tuple, Dict
from uuid import uuid4
from pydantic import BaseModel, Field, TypeAdapter, validator
import sys

# Tentar importar Role do a2a se disponível
try:
    from a2a.types import Role, Message as A2AMessage
    HAS_A2A = True
except ImportError:
    Role = None
    A2AMessage = None
    HAS_A2A = False


# ========== CLASSES BASE NECESSÁRIAS ==========

class AgentCard(BaseModel):
    """Representa um agente"""
    id: str
    name: str
    description: str = ""
    url: str = ""


class Message(BaseModel):
    """
    Mensagem consolidada - conformidade total com A2A Protocol.
    Aceita apenas formatos oficiais: camelCase (A2A) e snake_case (Python).
    """
    # Configuração Pydantic para aceitar aliases
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = 'allow'
        validate_assignment = True
    
    # Campos principais - camelCase (A2A Protocol) com aliases snake_case
    messageId: str = Field(default="", alias="message_id")
    content: str = Field(default="")
    author: str = Field(default="")
    timestamp: float = Field(default=0.0)
    contextId: Optional[str] = Field(default=None, alias="context_id")
    taskId: Optional[str] = Field(default=None, alias="task_id")
    conversationId: Optional[str] = Field(default=None, alias="conversation_id")
    parts: List[Any] = Field(default_factory=list)
    role: Optional[Any] = Field(default="user")
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    def __init__(self, **data):
        """
        Inicialização simplificada - aceita APENAS 2-3 formatos por campo.
        Conformidade com Python 3: "Simple is better than complex"
        """
        # messageId: aceitar apenas 2 formatos (camelCase e snake_case)
        if 'message_id' in data:
            data['messageId'] = data.pop('message_id')
        elif 'messageid' in data:  # Compatibilidade mínima
            data['messageId'] = data.pop('messageid')
        
        # Gerar messageId se não existir
        if 'messageId' not in data:
            data['messageId'] = str(uuid4())
        
        # content: aceitar apenas 'text' como alternativa
        if 'text' in data and 'content' not in data:
            data['content'] = data.pop('text')
        
        # author: aceitar apenas 'user' como alternativa
        if 'user' in data and 'author' not in data:
            data['author'] = data.pop('user')
        
        # contextId: já tratado pelo Field alias
        if 'context_id' in data:
            data['contextId'] = data.pop('context_id')
        
        # taskId: já tratado pelo Field alias
        if 'task_id' in data:
            data['taskId'] = data.pop('task_id')
        
        # conversationId: já tratado pelo Field alias
        if 'conversation_id' in data:
            data['conversationId'] = data.pop('conversation_id')
        
        # Converter role para enum se disponível
        if 'role' in data and HAS_A2A and Role:
            role_value = data['role']
            if isinstance(role_value, str):
                try:
                    if role_value.lower() == 'user':
                        data['role'] = Role.user
                    elif role_value.lower() == 'agent':
                        data['role'] = Role.agent
                except:
                    pass  # Manter como string se falhar
        
        # Chamar init do BaseModel
        super().__init__(**data)


class Task(BaseModel):
    """Representa uma tarefa"""
    id: str
    title: str
    description: str = ""
    status: str = "pending"


# ========== CLASSES JSON-RPC ==========

class JSONRPCMessage(BaseModel):
    jsonrpc: Literal['2.0'] = '2.0'
    id: Union[int, str, None] = Field(default_factory=lambda: uuid4().hex)


class JSONRPCRequest(JSONRPCMessage):
    method: str
    params: Union[Any, None] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Union[Any, None] = None


class JSONRPCResponse(JSONRPCMessage):
    result: Union[Any, None] = None
    error: Union[JSONRPCError, None] = None


# ========== CLASSES CORRIGIDAS ==========

class ConversationFixed(BaseModel):
    """Conversation com nomenclatura consistente"""
    conversationId: str = Field(alias="conversationid")  # Campo em camelCase com alias
    isActive: bool = Field(alias="isactive")
    name: str = ''
    task_ids: List[str] = Field(default_factory=list)
    messages: List[Any] = Field(default_factory=list)  # Lista de mensagens
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True


class EventFixed(BaseModel):
    """Event com nomenclatura consistente"""
    id: str
    actor: str = ''
    content: Any  # Conteúdo do evento (Message)
    timestamp: float
    
    def __init__(self, **data):
        """Override init para normalizar campos"""
        # Aceitar variações de id
        for key in ['eventId', 'event_id', 'eventID']:
            if key in data and 'id' not in data:
                data['id'] = data.pop(key)
        
        # Chamar o init original
        super().__init__(**data)


class MessageInfoFixed(BaseModel):
    """MessageInfo corrigido - ESTE ERA O PROBLEMA!"""
    messageId: str  # CORRIGIDO: era 'messageid', agora é 'messageId'
    contextId: str  # CORRIGIDO: era 'contextid', agora é 'contextId'
    
    def __init__(self, **data):
        """Override init para normalizar campos"""
        # Normalizar messageId
        for key in ['messageid', 'message_id', 'message_Id', 'MessageId']:
            if key in data and 'messageId' not in data:
                data['messageId'] = data.pop(key)
        
        # Normalizar contextId
        for key in ['contextid', 'context_id', 'context_Id', 'ContextId']:
            if key in data and 'contextId' not in data:
                data['contextId'] = data.pop(key)
        
        # Chamar o init original
        super().__init__(**data)


# ========== TIPO DINÂMICO DE MESSAGE ==========

# Tipo de mensagem consolidado
MessageType = Message

# Atualizar campos dinâmicos para usar MessageType
if 'EventFixed' in locals():
    EventFixed.model_fields['content'].annotation = MessageType
if 'ConversationFixed' in locals():
    ConversationFixed.model_fields['messages'].annotation = List[MessageType]

# ========== REQUESTS E RESPONSES ==========

class SendMessageRequest(JSONRPCRequest):
    method: Literal['message/send'] = 'message/send'
    params: MessageType


class ListMessageRequest(JSONRPCRequest):
    method: Literal['message/list'] = 'message/list'
    params: str


class ListMessageResponse(JSONRPCResponse):
    result: Union[List[MessageType], None] = None


class SendMessageResponse(JSONRPCResponse):
    result: Union[MessageType, MessageInfoFixed, None] = None  # Usando MessageInfoFixed


class GetEventRequest(JSONRPCRequest):
    method: Literal['events/get'] = 'events/get'


class GetEventResponse(JSONRPCResponse):
    result: Union[List[EventFixed], None] = None  # Usando EventFixed


class ListConversationRequest(JSONRPCRequest):
    method: Literal['conversation/list'] = 'conversation/list'


class ListConversationResponse(JSONRPCResponse):
    result: Union[List[ConversationFixed], None] = None  # Usando ConversationFixed


class PendingMessageRequest(JSONRPCRequest):
    method: Literal['message/pending'] = 'message/pending'


class PendingMessageResponse(JSONRPCResponse):
    result: Union[List[Tuple[str, str]], None] = None


class CreateConversationRequest(JSONRPCRequest):
    method: Literal['conversation/create'] = 'conversation/create'


class CreateConversationResponse(JSONRPCResponse):
    result: Union[ConversationFixed, None] = None  # Usando ConversationFixed


class ListTaskRequest(JSONRPCRequest):
    method: Literal['task/list'] = 'task/list'


class ListTaskResponse(JSONRPCResponse):
    result: Union[List[Task], None] = None


class RegisterAgentRequest(JSONRPCRequest):
    method: Literal['agent/register'] = 'agent/register'
    params: Union[str, None] = None


class RegisterAgentResponse(JSONRPCResponse):
    result: Union[str, None] = None


class ListAgentRequest(JSONRPCRequest):
    method: Literal['agent/list'] = 'agent/list'


class ListAgentResponse(JSONRPCResponse):
    result: Union[List[AgentCard], None] = None


# ========== ADAPTERS E EXCEPTIONS ==========

AgentRequest = TypeAdapter(
    Annotated[
        Union[SendMessageRequest, ListConversationRequest],
        Field(discriminator='method'),
    ]
)


class AgentClientError(Exception):
    pass


class AgentClientHTTPError(AgentClientError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f'HTTP Error {status_code}: {message}')


class AgentClientJSONError(AgentClientError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(f'JSON Error: {message}')


# ========== PATCH A2A.TYPES SE DISPONÍVEL ==========

def patch_a2a_message():
    """
    Aplica o patch no módulo a2a.types para usar nossa versão consolidada de Message.
    Garante conformidade total com A2A Protocol.
    """
    if HAS_A2A:
        import a2a.types
        
        # Substituir a classe Message no módulo a2a.types
        a2a.types.Message = Message
        
        # Também atualizar no cache de módulos
        if 'a2a.types' in sys.modules:
            sys.modules['a2a.types'].Message = Message
        
        print("[TYPES] a2a.types.Message patchado - conformidade total com A2A Protocol")
        return True
    return False


# Aplicar patch automaticamente ao importar este módulo
if HAS_A2A:
    patch_a2a_message()


# ========== ALIASES PARA COMPATIBILIDADE ==========

Conversation = ConversationFixed
Event = EventFixed
MessageInfo = MessageInfoFixed