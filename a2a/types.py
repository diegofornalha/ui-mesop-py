"""
A2A Protocol Types - Definições de tipos para compatibilidade
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid
from datetime import datetime


# Enum para Role
class Role(str, Enum):
    user = "user"
    agent = "agent" 
    system = "system"


# Classes básicas de mensagem
@dataclass
class TextPart:
    text: str
    kind: str = "text"


@dataclass 
class FilePart:
    file: Any
    kind: str = "file"


@dataclass
class DataPart:
    data: Any
    kind: str = "data"


@dataclass
class FileWithUri:
    mime_type: str
    uri: str


@dataclass
class FileWithBytes:
    mime_type: str
    bytes: str


# União de tipos de parte
Part = TextPart | FilePart | DataPart | Dict[str, Any]


@dataclass
class Message:
    messageId: str = field(default_factory=lambda: str(uuid.uuid4()))
    contextId: str = ""
    role: Role = Role.user
    parts: List[Part] = field(default_factory=list)
    taskId: Optional[str] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)


@dataclass
class TaskStatus:
    state: "TaskState"
    reason: Optional[str] = None


class TaskState(str, Enum):
    created = "created"
    submitted = "submitted"
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context_id: str = ""
    status: TaskStatus = field(default_factory=lambda: TaskStatus(state=TaskState.created))
    history: List[Message] = field(default_factory=list)
    artifacts: List[Any] = field(default_factory=list)


@dataclass
class AgentCapabilities:
    """Capabilities of an agent"""
    input_modes: List[str] = field(default_factory=list)
    output_modes: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)


@dataclass
class AgentCard:
    name: str = ""
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    url: str = ""
    capabilities: AgentCapabilities = field(default_factory=AgentCapabilities)
    defaultInputModes: List[str] = field(default_factory=list)
    defaultOutputModes: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)


@dataclass
class Artifact:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "text"
    content: Any = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    parts: List[Part] = field(default_factory=list)
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # Alias para compatibilidade


@dataclass
class TaskStatusUpdateEvent:
    task_id: str
    status: TaskStatus
    message: Optional[str] = None


@dataclass
class TaskArtifactUpdateEvent:
    task_id: str
    artifacts: List[Artifact]
    message: Optional[str] = None


@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor: str = ""
    content: Any = None
    timestamp: datetime = field(default_factory=datetime.now)


# Compatibilidade com imports antigos
__all__ = [
    "Role",
    "TextPart",
    "FilePart", 
    "DataPart",
    "FileWithUri",
    "FileWithBytes",
    "Part",
    "Message",
    "TaskStatus",
    "TaskState",
    "Task",
    "AgentCapabilities",
    "AgentCard",
    "Artifact",
    "TaskStatusUpdateEvent",
    "TaskArtifactUpdateEvent",
    "Event"
]