"""
Tipos corrigidos com nomenclatura consistente.
Resolve o problema de messageId vs messageid.
"""

from typing import Annotated, Any, Literal, Optional, Union, List, Tuple
from uuid import uuid4
from pydantic import BaseModel, Field, TypeAdapter, model_validator

# Importar MessagePatched se disponível
try:
    from message_patch import MessagePatched
    HAS_MESSAGE_PATCHED = True
except ImportError:
    MessagePatched = None
    HAS_MESSAGE_PATCHED = False


# ========== CLASSES BASE NECESSÁRIAS ==========

class AgentCard(BaseModel):
    """Representa um agente"""
    id: str
    name: str
    description: str = ""
    url: str = ""


class Message(BaseModel):
    """Representa uma mensagem - aceita múltiplas variações de campos"""
    messageId: str  # Campo principal em camelCase
    content: str = ""  # Valor padrão vazio
    author: str = ""  # Valor padrão vazio
    timestamp: float = 0.0
    context_id: Optional[str] = None
    parts: List[Any] = Field(default_factory=list)
    
    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, values):
        """Normaliza variações de campos para Message"""
        if isinstance(values, dict):
            # Normalizar messageId - aceitar todas as variações
            for key in ['messageid', 'message_id', 'message_Id', 'MessageId', 'id']:
                if key in values and 'messageId' not in values:
                    values['messageId'] = values.pop(key)
            
            # Se ainda não tiver messageId, criar um
            if 'messageId' not in values and 'id' not in values:
                values['messageId'] = str(uuid4())
            
            # Normalizar text/content
            for key in ['text', 'message', 'body']:
                if key in values and 'content' not in values:
                    values['content'] = values.pop(key)
            
            # Normalizar author
            for key in ['user', 'userId', 'user_id', 'sender']:
                if key in values and 'author' not in values:
                    values['author'] = values.pop(key)
            
            # Normalizar context_id
            for key in ['contextId', 'contextid', 'context_Id']:
                if key in values and 'context_id' not in values:
                    values['context_id'] = values.pop(key)
                    
        return values
    
    # Propriedade para compatibilidade
    @property
    def messageid(self) -> str:
        return self.messageId
    
    @property
    def id(self) -> str:
        return self.messageId


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
    conversationid: str
    isactive: bool
    name: str = ''
    task_ids: List[str] = Field(default_factory=list)
    messages: List[Any] = Field(default_factory=list)  # Será List[Message] ou List[MessagePatched]
    
    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, values):
        """Normaliza variações de campos"""
        if isinstance(values, dict):
            # Aceitar variações de conversationid
            for key in ['conversationId', 'conversation_id', 'conversationID']:
                if key in values and 'conversationid' not in values:
                    values['conversationid'] = values.pop(key)
            
            # Aceitar variações de isactive
            for key in ['isActive', 'is_active', 'active']:
                if key in values and 'isactive' not in values:
                    values['isactive'] = values.pop(key)
        
        return values


class EventFixed(BaseModel):
    """Event com nomenclatura consistente"""
    id: str
    actor: str = ''
    content: Any  # Será Message ou MessagePatched
    timestamp: float
    
    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, values):
        """Normaliza variações de campos"""
        if isinstance(values, dict):
            # Aceitar variações de id
            for key in ['eventId', 'event_id', 'eventID']:
                if key in values and 'id' not in values:
                    values['id'] = values.pop(key)
        
        return values


class MessageInfoFixed(BaseModel):
    """MessageInfo corrigido - ESTE ERA O PROBLEMA!"""
    messageId: str  # CORRIGIDO: era 'messageid', agora é 'messageId'
    contextId: str  # CORRIGIDO: era 'contextid', agora é 'contextId'
    
    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, values):
        """Aceita múltiplas variações dos campos"""
        if isinstance(values, dict):
            # Normalizar messageId
            for key in ['messageid', 'message_id', 'message_Id', 'MessageId']:
                if key in values and 'messageId' not in values:
                    values['messageId'] = values.pop(key)
            
            # Normalizar contextId
            for key in ['contextid', 'context_id', 'context_Id', 'ContextId']:
                if key in values and 'contextId' not in values:
                    values['contextId'] = values.pop(key)
        
        return values


# ========== TIPO DINÂMICO DE MESSAGE ==========

# Criar tipo dinâmico para aceitar ambos Message e MessagePatched
if HAS_MESSAGE_PATCHED and MessagePatched:
    MessageType = Union[Message, MessagePatched]
else:
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


# ========== ALIASES PARA COMPATIBILIDADE ==========

Conversation = ConversationFixed
Event = EventFixed
MessageInfo = MessageInfoFixed