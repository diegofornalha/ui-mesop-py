"""
Gerenciador de Tasks para conversão entre A2A (dataclass) e Service (Pydantic).
"""

import logging
from typing import Dict, List, Optional
from dataclasses import asdict

from a2a.types import Task as A2ATask, TaskState
from service.types import Task as ServiceTask

logger = logging.getLogger(__name__)


class ClaudeTaskManager:
    """Gerencia conversão entre tasks A2A e Service."""
    
    def __init__(self):
        self._a2a_tasks: Dict[str, A2ATask] = {}
        self._service_tasks: Dict[str, ServiceTask] = {}
        logger.info("✅ ClaudeTaskManager inicializado")
    
    def add_a2a_task(self, task: A2ATask) -> ServiceTask:
        """Adiciona uma task A2A e retorna a versão Service."""
        self._a2a_tasks[task.id] = task
        
        # Converter para ServiceTask (versão simplificada)
        service_task = ServiceTask(
            id=task.id,
            title=f"Task {task.id[:8]}",
            description=f"Status: {task.status.state if task.status else 'unknown'}",
            status=task.status.state if task.status else "pending",
            contextId=getattr(task, 'context_id', '')  # Adicionar contextId
        )
        
        self._service_tasks[task.id] = service_task
        logger.debug(f"📋 Task convertida: A2A -> Service ({task.id[:8]})")
        return service_task
    
    def get_service_tasks(self) -> List[ServiceTask]:
        """Retorna lista de tasks no formato Service."""
        return list(self._service_tasks.values())
    
    def get_all_pydantic_tasks(self) -> List[ServiceTask]:
        """Alias para get_service_tasks - retorna tasks Pydantic."""
        return self.get_service_tasks()
    
    def get_a2a_task(self, task_id: str) -> Optional[A2ATask]:
        """Obtém task A2A original."""
        return self._a2a_tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskState):
        """Atualiza status de uma task."""
        if task_id in self._a2a_tasks:
            task = self._a2a_tasks[task_id]
            if task.status:
                task.status.state = status
            
            # Atualizar ServiceTask correspondente
            if task_id in self._service_tasks:
                self._service_tasks[task_id].status = str(status)
                self._service_tasks[task_id].description = f"Status: {status}"
                logger.debug(f"📝 Task {task_id[:8]} atualizada: {status}")
    
    def update_a2a_task(self, task: A2ATask):
        """Atualiza task A2A e sua versão Service."""
        self._a2a_tasks[task.id] = task
        
        # Atualizar ServiceTask correspondente
        if task.id in self._service_tasks:
            self._service_tasks[task.id].status = task.status.state if task.status else "pending"
            self._service_tasks[task.id].description = f"Status: {task.status.state if task.status else 'unknown'}"
    
    def clear(self):
        """Limpa todas as tasks."""
        self._a2a_tasks.clear()
        self._service_tasks.clear()


# Singleton global
_task_manager = None

def get_task_manager() -> ClaudeTaskManager:
    """Obtém instância singleton do task manager."""
    global _task_manager
    if _task_manager is None:
        _task_manager = ClaudeTaskManager()
    return _task_manager