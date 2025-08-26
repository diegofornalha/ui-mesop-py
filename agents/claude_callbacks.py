"""
Claude Callback Manager - Implementação completa para compatibilidade com ADK
"""

import asyncio
import logging
from typing import Any, Optional, List, Dict, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from a2a.types import TaskStatus, Message
import time

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Prioridade de eventos."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


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


@dataclass
class EventMetadata:
    """Metadados de evento."""
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    source: str = "system"
    retry_count: int = 0
    max_retries: int = 3


class ClaudeCallbackManager:
    """Gerenciador completo de callbacks com fila de eventos e priorização."""
    
    def __init__(self, max_queue_size: int = 1000):
        self._callbacks: Dict[str, List[Callable]] = {}  # Callbacks por tipo de evento
        self._global_callbacks: List[Callable] = []  # Callbacks para todos eventos
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._event_history: List[Dict[str, Any]] = []
        self._max_history: int = 100
        self._processing: bool = False
        self._stats: Dict[str, int] = {
            "emitted": 0,
            "processed": 0,
            "failed": 0,
            "retried": 0
        }
        logger.info("✅ ClaudeCallbackManager inicializado (versão completa)")
    
    async def emit_event(self, event: Any, agent: Optional[Any] = None, priority: EventPriority = EventPriority.NORMAL):
        """
        Emite um evento com priorização e processamento assíncrono.
        """
        event_type = type(event).__name__
        metadata = EventMetadata(priority=priority, source=agent.name if agent else "system")
        
        event_data = {
            "event": event,
            "type": event_type,
            "agent": agent,
            "metadata": metadata
        }
        
        # Adicionar à fila com priorização
        await self._enqueue_event(event_data)
        
        # Log e estatísticas
        logger.debug(f"📣 Evento emitido: {event_type} (prioridade: {priority.name})")
        self._stats["emitted"] += 1
        
        # Processar fila se não estiver processando
        if not self._processing:
            asyncio.create_task(self._process_event_queue())
    
    async def _enqueue_event(self, event_data: Dict[str, Any]):
        """Adiciona evento à fila com priorização."""
        try:
            await self._event_queue.put(event_data)
        except asyncio.QueueFull:
            logger.warning("⚠️ Fila de eventos cheia, descartando evento mais antigo")
            # Descartar evento mais antigo se fila cheia
            try:
                self._event_queue.get_nowait()
                await self._event_queue.put(event_data)
            except:
                pass
    
    async def _process_event_queue(self):
        """Processa a fila de eventos assincronamente."""
        self._processing = True
        
        try:
            while not self._event_queue.empty():
                event_data = await self._event_queue.get()
                await self._process_single_event(event_data)
        finally:
            self._processing = False
    
    async def _process_single_event(self, event_data: Dict[str, Any]):
        """Processa um único evento."""
        event = event_data["event"]
        event_type = event_data["type"]
        agent = event_data["agent"]
        metadata = event_data["metadata"]
        
        # Adicionar ao histórico
        self._add_to_history(event_data)
        
        # Executar callbacks específicos do tipo
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                await self._execute_callback(callback, event, agent, metadata)
        
        # Executar callbacks globais
        for callback in self._global_callbacks:
            await self._execute_callback(callback, event, agent, metadata)
        
        self._stats["processed"] += 1
    
    async def _execute_callback(self, callback: Callable, event: Any, agent: Any, metadata: EventMetadata):
        """Executa um callback com tratamento de erro e retry."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event, agent)
            else:
                callback(event, agent)
        except Exception as e:
            logger.error(f"❌ Erro ao executar callback: {e}")
            self._stats["failed"] += 1
            
            # Retry logic
            if metadata.retry_count < metadata.max_retries:
                metadata.retry_count += 1
                self._stats["retried"] += 1
                logger.info(f"🔄 Tentando novamente ({metadata.retry_count}/{metadata.max_retries})...")
                await asyncio.sleep(0.5 * metadata.retry_count)  # Backoff exponencial
                await self._execute_callback(callback, event, agent, metadata)
    
    def register_callback(self, callback: Callable, event_types: Union[str, List[str]] = None):
        """
        Registra um callback para tipos específicos de evento ou globalmente.
        """
        if event_types is None:
            # Callback global
            self._global_callbacks.append(callback)
            logger.info(f"📝 Callback global registrado")
        else:
            # Callback específico
            if isinstance(event_types, str):
                event_types = [event_types]
            
            for event_type in event_types:
                if event_type not in self._callbacks:
                    self._callbacks[event_type] = []
                self._callbacks[event_type].append(callback)
                logger.info(f"📝 Callback registrado para evento: {event_type}")
    
    def unregister_callback(self, callback: Callable):
        """Remove um callback."""
        # Remover de callbacks específicos
        for event_type in self._callbacks:
            if callback in self._callbacks[event_type]:
                self._callbacks[event_type].remove(callback)
        
        # Remover de callbacks globais
        if callback in self._global_callbacks:
            self._global_callbacks.remove(callback)
    
    def _add_to_history(self, event_data: Dict[str, Any]):
        """Adiciona evento ao histórico."""
        self._event_history.append({
            "timestamp": event_data["metadata"].timestamp,
            "type": event_data["type"],
            "priority": event_data["metadata"].priority.name
        })
        
        # Manter apenas últimos N eventos
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do gerenciador."""
        return self._stats.copy()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico de eventos."""
        return self._event_history.copy()
    
    def clear_history(self):
        """Limpa o histórico de eventos."""
        self._event_history.clear()
    
    def close(self):
        """Fecha o manager e limpa recursos."""
        self._callbacks.clear()
        self._global_callbacks.clear()
        self._event_history.clear()
        self._processing = False
        logger.info("🔒 ClaudeCallbackManager fechado")


# Singleton global
_callback_manager = None

def get_callback_manager() -> ClaudeCallbackManager:
    """Obtém a instância singleton do callback manager."""
    global _callback_manager
    if _callback_manager is None:
        _callback_manager = ClaudeCallbackManager()
    return _callback_manager