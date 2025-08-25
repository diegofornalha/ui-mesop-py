"""
Módulo para conexão com agentes remotos.
"""

from typing import Any, Dict, Optional


class TaskCallbackArg:
    """Argumento para callback de tarefas."""
    
    def __init__(self, task_id: str, status: str, result: Optional[Any] = None):
        self.task_id = task_id
        self.status = status
        self.result = result
        self.metadata: Dict[str, Any] = {}
    
    def add_metadata(self, key: str, value: Any):
        """Adiciona metadados à tarefa."""
        self.metadata[key] = value
