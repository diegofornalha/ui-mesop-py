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
    
    # Propriedades para compatibilidade com snake_case
    @property
    def conversation_id(self) -> str:
        return self.conversationId
    
    @property
    def conversation_name(self) -> str:
        return self.conversationName
    
    @property
    def is_active(self) -> bool:
        return self.isActive
    
    @property
    def message_ids(self) -> list[str]:
        return self.messageIds
    
    # Propriedades para compatibilidade com lowercase
    @property
    def conversationid(self) -> str:
        return self.conversationId
    
    @property
    def conversationname(self) -> str:
        return self.conversationName
    
    @property
    def isactive(self) -> bool:
        return self.isActive
    
    @property
    def messageids(self) -> list[str]:
        return self.messageIds


@dataclass
class StateMessage:
    """StateMessage provides mesop state compliant view of a message"""

    messageId: str = ''
    taskId: str = ''
    contextId: str = ''
    role: str = ''
    
    # Propriedades para compatibilidade com snake_case
    @property
    def message_id(self) -> str:
        return self.messageId
    
    @property
    def task_id(self) -> str:
        return self.taskId
    
    @property
    def context_id(self) -> str:
        return self.contextId
    
    # Propriedades para compatibilidade com lowercase
    @property
    def messageid(self) -> str:
        return self.messageId
    
    @property
    def taskid(self) -> str:
        return self.taskId
    
    @property
    def contextid(self) -> str:
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
    
    # Propriedades para compatibilidade
    @property
    def task_id(self) -> str:
        return self.taskId
    
    @property
    def context_id(self) -> str | None:
        return self.contextId
    
    @property
    def taskid(self) -> str:
        return self.taskId
    
    @property
    def contextid(self) -> str | None:
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
    
    # Propriedades para compatibilidade
    @property
    def context_id(self) -> str:
        return self.contextId
    
    @property
    def contextid(self) -> str:
        return self.contextId


@dataclass
class StateEvent:
    """StateEvent provides mesop state compliant view of event"""

    contextId: str = ''
    actor: str = ''
    role: str = ''
    id: str = ''
    
    # Propriedades para compatibilidade
    @property
    def context_id(self) -> str:
        return self.contextId
    
    @property
    def contextid(self) -> str:
        return self.contextId
    # Each entry is a pair of (content, media type)
    content: list[tuple[ContentPart, str]] = dataclasses.field(
        default_factory=list
    )


@me.stateclass
class AppState:
    """Mesop Application State"""

    sidenav_open: bool = False
    theme_mode: Literal['system', 'light', 'dark'] = 'system'

    current_conversation_id: str = ''
    conversations: list[StateConversation]
    messages: list[StateMessage]
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
