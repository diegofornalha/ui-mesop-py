"""
Tipos corretos do Google ADK para compatibilidade total.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import time


@dataclass
class Content:
    """Conteúdo de uma mensagem/evento."""
    parts: List[Any] = field(default_factory=list)
    
    @classmethod
    def from_text(cls, text: str):
        """Cria Content a partir de texto."""
        from a2a.types import TextPart
        return cls(parts=[TextPart(text=text)])


@dataclass
class EventActions:
    """Ações que um evento pode carregar."""
    state_delta: Optional[Dict[str, Any]] = None
    artifact_delta: Optional[Dict[str, Any]] = None
    transfer_to_agent: Optional[str] = None
    escalate: bool = False


@dataclass
class Event:
    """Evento padrão do ADK."""
    # Campos obrigatórios
    author: str
    invocation_id: str
    
    # Campos opcionais
    content: Optional[Content] = None
    actions: Optional[EventActions] = None
    partial: bool = False
    turn_complete: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte Event para dict."""
        result = {
            "author": self.author,
            "invocation_id": self.invocation_id,
            "id": self.id,
            "timestamp": self.timestamp,
            "partial": self.partial,
            "turn_complete": self.turn_complete
        }
        
        if self.content:
            result["content"] = {
                "parts": [
                    {"text": part.text} if hasattr(part, 'text') else str(part)
                    for part in self.content.parts
                ]
            }
        
        if self.actions:
            result["actions"] = {
                "state_delta": self.actions.state_delta,
                "artifact_delta": self.actions.artifact_delta,
                "transfer_to_agent": self.actions.transfer_to_agent,
                "escalate": self.actions.escalate
            }
        
        return result


@dataclass
class Session:
    """Sessão com estado e eventos."""
    id: str
    state: Dict[str, Any] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_event(self, event: Event):
        """Adiciona evento à sessão."""
        self.events.append(event)
        self.updated_at = datetime.now()
        
        # Aplicar state_delta se existir
        if event.actions and event.actions.state_delta:
            self.state.update(event.actions.state_delta)


@dataclass
class InvocationContext:
    """Contexto de invocação para agentes."""
    session: Session
    invocation_id: str
    agent: Any  # Referência ao agente
    session_service: Any  # SessionService
    artifact_service: Any  # ArtifactService
    memory_service: Optional[Any] = None  # MemoryService opcional
    credential_service: Optional[Any] = None  # CredentialService opcional
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Obtém valor do estado da sessão."""
        return self.session.state.get(key, default)
    
    def set_state(self, key: str, value: Any):
        """Define valor no estado da sessão."""
        self.session.state[key] = value
    
    def get_user_state(self, key: str, default: Any = None) -> Any:
        """Obtém estado do usuário (cross-session)."""
        return self.session.state.get(f"user:{key}", default)
    
    def set_user_state(self, key: str, value: Any):
        """Define estado do usuário (cross-session)."""
        self.session.state[f"user:{key}"] = value
    
    def get_app_state(self, key: str, default: Any = None) -> Any:
        """Obtém estado da aplicação (global)."""
        return self.session.state.get(f"app:{key}", default)
    
    def set_app_state(self, key: str, value: Any):
        """Define estado da aplicação (global)."""
        self.session.state[f"app:{key}"] = value
    
    def get_temp_state(self, key: str, default: Any = None) -> Any:
        """Obtém estado temporário (não persistido)."""
        return self.session.state.get(f"temp:{key}", default)
    
    def set_temp_state(self, key: str, value: Any):
        """Define estado temporário (não persistido)."""
        self.session.state[f"temp:{key}"] = value


@dataclass
class RunConfig:
    """Configuração de execução."""
    timeout: Optional[float] = None
    max_events: Optional[int] = None
    stream: bool = False