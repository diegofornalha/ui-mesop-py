"""
ClaudeTaskManager - Gerenciador de Tasks com conversão automática entre tipos.
Resolve incompatibilidade entre a2a.types.Task (dataclass) e service.types.Task (Pydantic).
"""

import uuid
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict

# Tipos do A2A (dataclass)
from a2a.types import Task as A2ATask, TaskStatus, TaskState

# Tipos do service (Pydantic)
from service.types import Task as PydanticTask

logger = logging.getLogger(__name__)


class ClaudeTaskManager:
    """
    Gerenciador de tasks que mantém compatibilidade entre:
    - a2a.types.Task (dataclass) usado pelo ClaudeADKHostManager
    - service.types.Task (Pydantic) esperado pelo ListTaskResponse
    """
    
    def __init__(self):
        """Inicializa o gerenciador de tasks."""
        self._a2a_tasks: Dict[str, A2ATask] = {}  # Tasks originais do A2A
        self._pydantic_tasks: Dict[str, PydanticTask] = {}  # Tasks convertidas para Pydantic
        self._task_mapping: Dict[str, str] = {}  # Mapeamento entre IDs se necessário
        logger.info("✅ ClaudeTaskManager inicializado")
    
    def add_a2a_task(self, task: A2ATask) -> str:
        """
        Adiciona uma task do tipo A2A e cria versão Pydantic.
        
        Args:
            task: Task do tipo a2a.types.Task
            
        Returns:
            ID da task
        """
        task_id = task.id if hasattr(task, 'id') else str(uuid.uuid4())
        
        # Armazenar task A2A
        self._a2a_tasks[task_id] = task
        
        # Criar versão Pydantic
        pydantic_task = self._convert_a2a_to_pydantic(task)
        self._pydantic_tasks[task_id] = pydantic_task
        
        logger.debug(f"📌 Task adicionada: {task_id}")
        return task_id
    
    def _convert_a2a_to_pydantic(self, a2a_task: A2ATask) -> PydanticTask:
        """
        Converte Task do a2a.types para service.types.
        
        Args:
            a2a_task: Task dataclass do A2A
            
        Returns:
            Task Pydantic para API
        """
        # Extrair informações da task A2A
        task_id = a2a_task.id if hasattr(a2a_task, 'id') else str(uuid.uuid4())
        
        # Determinar status como string
        status_str = "pending"
        if hasattr(a2a_task, 'status') and a2a_task.status:
            if hasattr(a2a_task.status, 'state'):
                state = a2a_task.status.state
                if isinstance(state, TaskState):
                    status_str = state.value
                else:
                    status_str = str(state)
        
        # Criar título baseado no contexto ou mensagem
        title = f"Task {task_id[:8]}"
        description = ""
        
        # Tentar extrair informação das mensagens no histórico
        if hasattr(a2a_task, 'history') and a2a_task.history:
            try:
                first_message = a2a_task.history[0]
                if hasattr(first_message, 'parts') and first_message.parts:
                    for part in first_message.parts:
                        if hasattr(part, 'text'):
                            description = part.text[:100]  # Primeiros 100 chars
                            title = f"Chat: {part.text[:30]}..." if len(part.text) > 30 else f"Chat: {part.text}"
                            break
            except Exception as e:
                logger.debug(f"Não foi possível extrair texto da mensagem: {e}")
        
        # Criar task Pydantic
        return PydanticTask(
            id=task_id,
            title=title,
            description=description or f"Task processando no contexto {getattr(a2a_task, 'context_id', 'default')[:8]}",
            status=status_str
        )
    
    def _convert_pydantic_to_a2a(self, pydantic_task: PydanticTask) -> A2ATask:
        """
        Converte Task do service.types para a2a.types.
        
        Args:
            pydantic_task: Task Pydantic
            
        Returns:
            Task dataclass do A2A
        """
        # Mapear status string para TaskState
        state_map = {
            "pending": TaskState.pending,
            "running": TaskState.running,
            "completed": TaskState.completed,
            "failed": TaskState.failed,
            "submitted": TaskState.submitted,
            "created": TaskState.created
        }
        
        task_state = state_map.get(pydantic_task.status, TaskState.pending)
        
        return A2ATask(
            id=pydantic_task.id,
            context_id="default",  # Contexto padrão se não tiver
            status=TaskStatus(state=task_state),
            history=[],  # Histórico vazio por padrão
            artifacts=[]  # Artifacts vazios por padrão
        )
    
    def get_a2a_task(self, task_id: str) -> Optional[A2ATask]:
        """Obtém task no formato A2A."""
        return self._a2a_tasks.get(task_id)
    
    def get_pydantic_task(self, task_id: str) -> Optional[PydanticTask]:
        """Obtém task no formato Pydantic."""
        return self._pydantic_tasks.get(task_id)
    
    def get_all_a2a_tasks(self) -> List[A2ATask]:
        """Retorna todas as tasks A2A."""
        return list(self._a2a_tasks.values())
    
    def get_all_pydantic_tasks(self) -> List[PydanticTask]:
        """Retorna todas as tasks Pydantic para API."""
        return list(self._pydantic_tasks.values())
    
    def update_task_status(self, task_id: str, new_state: Union[TaskState, str]):
        """
        Atualiza status de uma task em ambos formatos.
        
        Args:
            task_id: ID da task
            new_state: Novo estado (TaskState ou string)
        """
        # Atualizar A2A task
        if task_id in self._a2a_tasks:
            a2a_task = self._a2a_tasks[task_id]
            if isinstance(new_state, TaskState):
                a2a_task.status.state = new_state
            else:
                # Converter string para TaskState
                try:
                    a2a_task.status.state = TaskState(new_state)
                except:
                    logger.warning(f"Estado inválido: {new_state}")
        
        # Atualizar Pydantic task
        if task_id in self._pydantic_tasks:
            pydantic_task = self._pydantic_tasks[task_id]
            if isinstance(new_state, TaskState):
                pydantic_task.status = new_state.value
            else:
                pydantic_task.status = str(new_state)
        
        logger.debug(f"📊 Task {task_id[:8]} atualizada para {new_state}")
    
    def remove_task(self, task_id: str) -> bool:
        """Remove uma task de ambos formatos."""
        removed = False
        
        if task_id in self._a2a_tasks:
            del self._a2a_tasks[task_id]
            removed = True
        
        if task_id in self._pydantic_tasks:
            del self._pydantic_tasks[task_id]
            removed = True
        
        if removed:
            logger.debug(f"🗑️ Task {task_id[:8]} removida")
        
        return removed
    
    def clear_all_tasks(self):
        """Limpa todas as tasks."""
        self._a2a_tasks.clear()
        self._pydantic_tasks.clear()
        self._task_mapping.clear()
        logger.info("🧹 Todas as tasks foram limpas")
    
    def get_tasks_for_api(self) -> List[Dict[str, Any]]:
        """
        Retorna tasks em formato adequado para API (dict).
        Usado pelo ListTaskResponse.
        """
        tasks_dict = []
        for pydantic_task in self._pydantic_tasks.values():
            # Converter para dict para garantir serialização
            tasks_dict.append(pydantic_task.model_dump())
        return tasks_dict
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do gerenciador."""
        return {
            "total_tasks": len(self._a2a_tasks),
            "pending": sum(1 for t in self._a2a_tasks.values() 
                          if t.status.state == TaskState.pending),
            "running": sum(1 for t in self._a2a_tasks.values() 
                          if t.status.state == TaskState.running),
            "completed": sum(1 for t in self._a2a_tasks.values() 
                           if t.status.state == TaskState.completed),
            "failed": sum(1 for t in self._a2a_tasks.values() 
                         if t.status.state == TaskState.failed)
        }


# Singleton global
_task_manager: Optional[ClaudeTaskManager] = None

def get_task_manager() -> ClaudeTaskManager:
    """Obtém instância singleton do task manager."""
    global _task_manager
    if _task_manager is None:
        _task_manager = ClaudeTaskManager()
    return _task_manager


# Funções utilitárias de conversão rápida
def convert_a2a_to_pydantic(a2a_task: A2ATask) -> PydanticTask:
    """Função helper para conversão rápida."""
    manager = get_task_manager()
    return manager._convert_a2a_to_pydantic(a2a_task)


def convert_pydantic_to_a2a(pydantic_task: PydanticTask) -> A2ATask:
    """Função helper para conversão rápida."""
    manager = get_task_manager()
    return manager._convert_pydantic_to_a2a(pydantic_task)