"""
Modelos refatorados com nomenclatura única e sem ambiguidades.
Sistema de nomes que elimina conflitos entre messageId, message_id, etc.
"""

from typing import Annotated, Any, Literal, Optional, Dict, List
from uuid import uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ========== ENUMS PARA VALORES PADRONIZADOS ==========

class TransmissionStatus(str, Enum):
    """Status de transmissão sem ambiguidade"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"
    PROCESSING = "processing"


class ParticipantRole(str, Enum):
    """Papéis dos participantes"""
    SENDER = "sender"
    RECEIVER = "receiver"
    OBSERVER = "observer"
    MODERATOR = "moderator"


class DialogueType(str, Enum):
    """Tipos de diálogo"""
    TEXT = "text"
    SYSTEM = "system"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    ERROR = "error"


# ========== MODELOS BASE COM NOMES ÚNICOS ==========

class DialogueUnit(BaseModel):
    """
    Unidade básica de diálogo - substitui 'Message'
    Nomenclatura única: sem messageId, message_id, etc.
    """
    unit_ref: str = Field(
        default_factory=lambda: f"dlu_{uuid4().hex[:12]}",
        description="Referência única da unidade de diálogo"
    )
    author_tag: str = Field(
        ...,
        description="Tag identificadora do autor (não usar user_id)"
    )
    dialogue_body: str = Field(
        ...,
        description="Corpo do diálogo (não usar content/text)"
    )
    dialogue_type: DialogueType = Field(
        default=DialogueType.TEXT,
        description="Tipo do diálogo"
    )
    creation_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Momento de criação (não usar timestamp)"
    )
    parent_ref: Optional[str] = Field(
        default=None,
        description="Referência ao diálogo pai para threads"
    )
    metadata_blob: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados adicionais"
    )
    attachment_refs: List[str] = Field(
        default_factory=list,
        description="Referências a anexos"
    )


class TransmissionRecord(BaseModel):
    """
    Registro de transmissão - substitui conceitos de 'delivery'
    """
    record_ref: str = Field(
        default_factory=lambda: f"trx_{uuid4().hex[:12]}",
        description="Referência única do registro"
    )
    unit_ref: str = Field(
        ...,
        description="Referência ao DialogueUnit"
    )
    recipient_tag: str = Field(
        ...,
        description="Tag do destinatário"
    )
    transmission_status: TransmissionStatus = Field(
        default=TransmissionStatus.PENDING,
        description="Status atual da transmissão"
    )
    attempt_sequence: int = Field(
        default=1,
        description="Número da tentativa"
    )
    last_attempt_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Momento da última tentativa"
    )
    delivery_epoch: Optional[datetime] = Field(
        default=None,
        description="Momento da entrega bem-sucedida"
    )
    failure_reason: Optional[str] = Field(
        default=None,
        description="Razão da falha, se houver"
    )


class ConversationStream(BaseModel):
    """
    Fluxo de conversa - substitui 'thread', 'chat', 'conversation'
    """
    stream_ref: str = Field(
        default_factory=lambda: f"stm_{uuid4().hex[:12]}",
        description="Referência única do stream"
    )
    stream_title: str = Field(
        ...,
        description="Título do stream de conversa"
    )
    participant_tags: List[str] = Field(
        default_factory=list,
        description="Tags dos participantes"
    )
    dialogue_units: List[DialogueUnit] = Field(
        default_factory=list,
        description="Unidades de diálogo no stream"
    )
    creation_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Momento de criação do stream"
    )
    last_activity_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Última atividade no stream"
    )
    active_flag: bool = Field(
        default=True,
        description="Stream está ativo"
    )
    stream_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados do stream"
    )
    task_refs: List[str] = Field(
        default_factory=list,
        description="Referências a tarefas associadas"
    )


class ParticipantProfile(BaseModel):
    """
    Perfil do participante - substitui 'user', 'agent'
    """
    participant_tag: str = Field(
        ...,
        description="Tag única do participante"
    )
    display_label: str = Field(
        ...,
        description="Nome de exibição"
    )
    avatar_url: Optional[str] = Field(
        default=None,
        description="URL do avatar"
    )
    role_assignment: ParticipantRole = Field(
        default=ParticipantRole.SENDER,
        description="Papel do participante"
    )
    joined_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Momento de entrada"
    )
    last_seen_epoch: Optional[datetime] = Field(
        default=None,
        description="Último momento visto"
    )
    settings_blob: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configurações do participante"
    )
    capability_list: List[str] = Field(
        default_factory=list,
        description="Capacidades do participante"
    )


class TaskUnit(BaseModel):
    """
    Unidade de tarefa - substitui 'task' com nomenclatura clara
    """
    task_ref: str = Field(
        default_factory=lambda: f"tsk_{uuid4().hex[:12]}",
        description="Referência única da tarefa"
    )
    task_label: str = Field(
        ...,
        description="Rótulo da tarefa"
    )
    task_description: str = Field(
        default="",
        description="Descrição detalhada"
    )
    creator_tag: str = Field(
        ...,
        description="Tag do criador"
    )
    assignee_tags: List[str] = Field(
        default_factory=list,
        description="Tags dos responsáveis"
    )
    creation_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Momento de criação"
    )
    deadline_epoch: Optional[datetime] = Field(
        default=None,
        description="Prazo final"
    )
    completion_epoch: Optional[datetime] = Field(
        default=None,
        description="Momento de conclusão"
    )
    priority_level: int = Field(
        default=0,
        description="Nível de prioridade (0-10)"
    )
    task_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadados da tarefa"
    )


class EventRecord(BaseModel):
    """
    Registro de evento - substitui 'event' com nomenclatura clara
    """
    event_ref: str = Field(
        default_factory=lambda: f"evt_{uuid4().hex[:12]}",
        description="Referência única do evento"
    )
    actor_tag: str = Field(
        default="",
        description="Tag do ator do evento"
    )
    event_type: str = Field(
        ...,
        description="Tipo do evento"
    )
    event_payload: DialogueUnit = Field(
        ...,
        description="Conteúdo do evento"
    )
    occurrence_epoch: datetime = Field(
        default_factory=datetime.now,
        description="Momento de ocorrência"
    )
    context_ref: Optional[str] = Field(
        default=None,
        description="Referência ao contexto"
    )


# ========== REQUISIÇÕES E RESPOSTAS JSON-RPC ==========

class JSONRPCEnvelope(BaseModel):
    """Envelope base para JSON-RPC"""
    jsonrpc: Literal['2.0'] = '2.0'
    envelope_ref: str = Field(
        default_factory=lambda: f"rpc_{uuid4().hex[:12]}",
        description="Referência única do envelope"
    )


class RPCRequest(JSONRPCEnvelope):
    """Requisição RPC com nomenclatura clara"""
    operation_name: str = Field(
        ...,
        description="Nome da operação"
    )
    operation_params: Any = Field(
        default=None,
        description="Parâmetros da operação"
    )


class RPCResponse(JSONRPCEnvelope):
    """Resposta RPC com nomenclatura clara"""
    operation_result: Any = Field(
        default=None,
        description="Resultado da operação"
    )
    operation_error: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Erro da operação, se houver"
    )


# ========== OPERAÇÕES ESPECÍFICAS ==========

class DialogueSendRequest(RPCRequest):
    """Requisição para enviar diálogo"""
    operation_name: Literal['dialogue/send'] = 'dialogue/send'
    operation_params: DialogueUnit


class DialogueSendResponse(RPCResponse):
    """Resposta do envio de diálogo"""
    operation_result: Optional[Dict[str, str]] = None  # {unit_ref, stream_ref}


class StreamListRequest(RPCRequest):
    """Requisição para listar streams"""
    operation_name: Literal['stream/list'] = 'stream/list'
    operation_params: Optional[Dict[str, Any]] = None  # filtros


class StreamListResponse(RPCResponse):
    """Resposta da listagem de streams"""
    operation_result: Optional[List[ConversationStream]] = None


class StreamCreateRequest(RPCRequest):
    """Requisição para criar stream"""
    operation_name: Literal['stream/create'] = 'stream/create'
    operation_params: Dict[str, Any]  # {title, participant_tags}


class StreamCreateResponse(RPCResponse):
    """Resposta da criação de stream"""
    operation_result: Optional[ConversationStream] = None


class ParticipantRegisterRequest(RPCRequest):
    """Requisição para registrar participante"""
    operation_name: Literal['participant/register'] = 'participant/register'
    operation_params: ParticipantProfile


class ParticipantRegisterResponse(RPCResponse):
    """Resposta do registro de participante"""
    operation_result: Optional[str] = None  # participant_tag


class TaskCreateRequest(RPCRequest):
    """Requisição para criar tarefa"""
    operation_name: Literal['task/create'] = 'task/create'
    operation_params: TaskUnit


class TaskCreateResponse(RPCResponse):
    """Resposta da criação de tarefa"""
    operation_result: Optional[str] = None  # task_ref


class EventFetchRequest(RPCRequest):
    """Requisição para buscar eventos"""
    operation_name: Literal['event/fetch'] = 'event/fetch'
    operation_params: Optional[Dict[str, Any]] = None  # filtros


class EventFetchResponse(RPCResponse):
    """Resposta da busca de eventos"""
    operation_result: Optional[List[EventRecord]] = None


# ========== UTILITÁRIOS E HELPERS ==========

def create_dialogue_unit(
    author: str,
    body: str,
    dialogue_type: DialogueType = DialogueType.TEXT,
    parent: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> DialogueUnit:
    """Cria uma unidade de diálogo com defaults"""
    return DialogueUnit(
        author_tag=author,
        dialogue_body=body,
        dialogue_type=dialogue_type,
        parent_ref=parent,
        metadata_blob=metadata or {}
    )


def create_conversation_stream(
    title: str,
    participants: List[str],
    metadata: Optional[Dict] = None
) -> ConversationStream:
    """Cria um stream de conversa"""
    return ConversationStream(
        stream_title=title,
        participant_tags=participants,
        stream_metadata=metadata or {}
    )


def create_participant(
    tag: str,
    label: str,
    role: ParticipantRole = ParticipantRole.SENDER,
    capabilities: Optional[List[str]] = None
) -> ParticipantProfile:
    """Cria um perfil de participante"""
    return ParticipantProfile(
        participant_tag=tag,
        display_label=label,
        role_assignment=role,
        capability_list=capabilities or []
    )


# ========== MAPEAMENTO DE MIGRAÇÃO ==========

NOMENCLATURE_MAPPING = {
    # Mapeamento de nomes antigos para novos
    "message_id": "unit_ref",
    "messageId": "unit_ref",
    "message_Id": "unit_ref",
    "MessageId": "unit_ref",
    "user_id": "author_tag",
    "userId": "author_tag",
    "user": "participant_tag",
    "content": "dialogue_body",
    "text": "dialogue_body",
    "message": "dialogue_unit",
    "messages": "dialogue_units",
    "timestamp": "creation_epoch",
    "created_at": "creation_epoch",
    "updated_at": "last_activity_epoch",
    "conversation_id": "stream_ref",
    "conversationId": "stream_ref",
    "conversationid": "stream_ref",
    "thread_id": "stream_ref",
    "threadId": "stream_ref",
    "thread": "stream",
    "chat": "stream",
    "conversation": "stream",
    "task_id": "task_ref",
    "taskId": "task_ref",
    "task_ids": "task_refs",
    "event_id": "event_ref",
    "eventId": "event_ref",
    "method": "operation_name",
    "params": "operation_params",
    "result": "operation_result",
    "error": "operation_error",
    "id": "envelope_ref",
    "isactive": "active_flag",
    "name": "stream_title",
}


def get_new_name(old_name: str) -> str:
    """Retorna o novo nome para um nome antigo"""
    return NOMENCLATURE_MAPPING.get(old_name, old_name)