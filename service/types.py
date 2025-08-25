"""
Tipos corrigidos com nomenclatura consistente.
Resolve o problema de messageId vs messageid.
"""

from typing import Annotated, Any, Literal, Optional, Union, List, Tuple
from uuid import uuid4
from pydantic import BaseModel, Field, TypeAdapter, validator

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
    """Representa uma mensagem - padrão A2A Protocol"""
    messageId: str  # Campo principal em camelCase (A2A Protocol)
    content: str = ""  # Valor padrão vazio
    author: str = ""  # Valor padrão vazio
    timestamp: float = 0.0
    contextId: Optional[str] = Field(default=None, alias="context_id")  # Padrão camelCase com alias Python
    parts: List[Any] = Field(default_factory=list)
    
    def __init__(self, **data):
        """Override init para normalizar campos"""
        # Normalizar messageId - aceitar todas as variações
        for key in ['messageid', 'message_id', 'message_Id', 'MessageId', 'id']:
            if key in data and 'messageId' not in data:
                data['messageId'] = data.pop(key)
        
        # Se ainda não tiver messageId, criar um
        if 'messageId' not in data and 'id' not in data:
            data['messageId'] = str(uuid4())
        
        # Normalizar text/content
        for key in ['text', 'message', 'body']:
            if key in data and 'content' not in data:
                data['content'] = data.pop(key)
        
        # Normalizar author
        for key in ['user', 'userId', 'user_id', 'sender']:
            if key in data and 'author' not in data:
                data['author'] = data.pop(key)
        
        # contextId é tratado automaticamente pelo alias Pydantic
        
        # Chamar o init original
        super().__init__(**data)
    
    # Propriedades Python MUTÁVEIS - retornam referências diretas
    @property
    def message_id_python(self) -> str:
        """Propriedade Python - compatibilidade snake_case"""
        return self.messageId
    
    @property
    def context_id_python(self) -> str:
        """Propriedade Python - compatibilidade snake_case"""
        return self.contextId or ""
    
    @property
    def parts_python(self) -> list:
        """Propriedade Python MUTÁVEL - retorna referência direta à lista"""
        return self.parts  # ✅ Retorna referência, permite append/extend


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
    messages: List[Any] = Field(default_factory=list)  # Será List[Message] ou List[MessagePatched]
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
    
    # Propriedades Python MUTÁVEIS - retornam referências diretas
    @property
    def conversation_id_python(self) -> str:
        """Propriedade Python - compatibilidade snake_case"""
        return self.conversationId
    
    @property
    def is_active_python(self) -> bool:
        """Propriedade Python - compatibilidade snake_case"""
        return self.isActive
    
    @property
    def messages_python(self) -> list:
        """Propriedade Python MUTÁVEL - retorna referência direta à lista"""
        return self.messages  # ✅ Retorna referência, permite append/extend


class EventFixed(BaseModel):
    """Event com nomenclatura consistente"""
    id: str
    actor: str = ''
    content: Any  # Será Message ou MessagePatched
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