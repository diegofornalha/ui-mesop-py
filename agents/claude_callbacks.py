"""
Claude Callback Manager - Implementação mínima para compatibilidade
"""

import asyncio
import logging
from typing import Any, Optional
from dataclasses import dataclass
from a2a.types import TaskStatus, Message

logger = logging.getLogger(__name__)


@dataclass
class TaskStatusUpdateEvent:
    """Evento de atualização de status de task."""
    task_id: str
    status: TaskStatus
    context_id: str
    message: Optional[Message] = None


@dataclass
class TaskArtifactUpdateEvent:
    """Evento de atualização de artifact de task."""
    task_id: str
    artifact: Any
    context_id: str
    append: bool = False


class ClaudeCallbackManager:
    """Gerenciador mínimo de callbacks."""
    
    def __init__(self):
        self._callbacks = []
        logger.info("✅ ClaudeCallbackManager inicializado (versão mínima)")
    
    async def emit_event(self, event: Any, agent: Optional[Any] = None):
        """Emite um evento (implementação mínima)."""
        logger.debug(f"📣 Evento emitido: {type(event).__name__}")
        # Por agora, apenas log
        pass
    
    def register_callback(self, callback):
        """Registra um callback."""
        self._callbacks.append(callback)
    
    def close(self):
        """Fecha o manager."""
        self._callbacks.clear()


# Singleton global
_callback_manager = None

def get_callback_manager() -> ClaudeCallbackManager:
    """Obtém a instância singleton do callback manager."""
    global _callback_manager
    if _callback_manager is None:
        _callback_manager = ClaudeCallbackManager()
    return _callback_manager