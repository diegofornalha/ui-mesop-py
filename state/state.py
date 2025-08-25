import dataclasses

from typing import Any, Literal

import mesop as me

from pydantic.dataclasses import dataclass


ContentPart = str | dict[str, Any]


@dataclass
class StateConversation:
    """StateConversation provides mesop state compliant view of a conversation"""

    conversationId: str = ''
    conversationName: str = ''
    isActive: bool = True
    messageIds: list[str] = dataclasses.field(default_factory=list)
    
    # Temporariamente removidas as propriedades para evitar erro na UI
    # Use apenas os campos diretos: messageIds, conversationId, etc.


@dataclass
class StateMessage:
    """StateMessage provides mesop state compliant view of a message"""

    messageId: str = ''
    taskId: str | None = ''  # Aceitar None ou string vazia
    contextId: str = ''
    role: str = ''
    
    # Propriedades para compatibilidade com snake_case
    # Propriedades Python com nomes DIFERENTES para evitar confusão
    @property
    def message_id_python(self) -> str:
        """Propriedade read-only para compatibilidade Python"""
        return self.messageId
    
    @property
    def task_id_python(self) -> str:
        """Propriedade read-only para compatibilidade Python"""
        return self.taskId
    
    @property
    def context_id_python(self) -> str:
        """Propriedade read-only para compatibilidade Python"""
        return self.contextId
    
    # Propriedades para compatibilidade com lowercase
    @property
    def messageid_python(self) -> str:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.messageId
    
    @property
    def taskid_python(self) -> str:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.taskId
    
    @property
    def contextid_python(self) -> str:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.contextId
    # Each content entry is a content, media type pair.
    content: list[tuple[ContentPart, str]] = dataclasses.field(
        default_factory=list
    )


@dataclass
class StateTask:
    """StateTask provides mesop state compliant view of task"""

    taskId: str = ''
    contextId: str | None = None
    state: str | None = None
    
    # Propriedades Python com nomes DIFERENTES para evitar confusão
    @property
    def task_id_python(self) -> str:
        """Propriedade read-only para compatibilidade Python"""
        return self.taskId
    
    @property
    def context_id_python(self) -> str | None:
        """Propriedade read-only para compatibilidade Python"""
        return self.contextId
    
    @property
    def taskid_python(self) -> str:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.taskId
    
    @property
    def contextid_python(self) -> str | None:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.contextId
    message: StateMessage = dataclasses.field(default_factory=StateMessage)
    artifacts: list[list[tuple[ContentPart, str]]] = dataclasses.field(
        default_factory=list
    )


@dataclass
class SessionTask:
    """SessionTask organizes tasks based on conversation"""

    contextId: str = ''
    task: StateTask = dataclasses.field(default_factory=StateTask)
    
    # Propriedades Python com nomes DIFERENTES para evitar confusão
    @property
    def context_id_python(self) -> str:
        """Propriedade read-only para compatibilidade Python"""
        return self.contextId
    
    @property
    def contextid_python(self) -> str:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.contextId


@dataclass
class StateEvent:
    """StateEvent provides mesop state compliant view of event"""

    contextId: str = ''
    actor: str = ''
    role: str = ''
    id: str = ''
    
    # Propriedades Python com nomes DIFERENTES para evitar confusão
    @property
    def context_id_python(self) -> str:
        """Propriedade read-only para compatibilidade Python"""
        return self.contextId
    
    @property
    def contextid_python(self) -> str:
        """Propriedade read-only para compatibilidade lowercase"""
        return self.contextId
    # Each entry is a pair of (content, media type)
    content: list[tuple[ContentPart, str]] = dataclasses.field(
        default_factory=list
    )


@me.stateclass
class AppState:
    """Mesop Application State"""

    sidenav_open: bool = False
    
    current_conversation_id: str = ''
    conversations: list[StateConversation] = dataclasses.field(default_factory=list)
    messages: list[StateMessage] = dataclasses.field(default_factory=list)
    task_list: list[SessionTask] = dataclasses.field(default_factory=list)
    background_tasks: dict[str, str] = dataclasses.field(default_factory=dict)
    message_aliases: dict[str, str] = dataclasses.field(default_factory=dict)
    # This is used to track the data entered in a form
    completed_forms: dict[str, dict[str, Any] | None] = dataclasses.field(
        default_factory=dict
    )
    # This is used to track the message sent to agent with form data
    form_responses: dict[str, str] = dataclasses.field(default_factory=dict)
    polling_interval: int = 1

    # Added for API key management
    api_key: str = ''
    uses_vertex_ai: bool = False
    api_key_dialog_open: bool = False


@me.stateclass
class SettingsState:
    """Settings State"""

    output_mime_types: list[str] = dataclasses.field(
        default_factory=lambda: [
            'image/*',
            'text/plain',
        ]
    )
