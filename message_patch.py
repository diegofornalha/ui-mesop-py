"""
Patch para corrigir o problema de Message com messageid
Este módulo deve ser importado ANTES de qualquer uso de a2a.types.Message
"""

from typing import Any, List, Optional, Dict, Union
from uuid import uuid4
from pydantic import BaseModel, Field, validator

# Salvar a classe original antes de patchear
try:
    from a2a.types import Message as OriginalMessage, Role
    HAS_A2A = True
except ImportError:
    HAS_A2A = False
    OriginalMessage = None
    Role = None


class MessagePatched(BaseModel):
    """
    Versão patchada de Message que aceita múltiplas variações de nomes de campos.
    Resolve o problema de messageid vs messageId.
    """
    # Configuração do Pydantic v1
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        extra = 'allow'  # Permite campos extras
        validate_assignment = True  # Valida atribuições após criação
    
    # Campos do modelo seguindo o PRD - camelCase como padrão
    messageId: str = Field(default="")
    content: str = Field(default="")
    author: str = Field(default="")
    timestamp: float = Field(default=0.0)
    contextId: Optional[str] = Field(default=None, alias="context_id")  # camelCase com alias snake_case
    parts: List[Any] = Field(default_factory=list)
    role: Optional[Any] = Field(default="user")  # Valor padrão 'user' ao invés de None
    
    # Campos adicionais para compatibilidade com o sistema
    taskId: Optional[str] = Field(default=None, alias="task_id")
    conversationId: Optional[str] = Field(default=None, alias="conversation_id")
    task: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    def __init__(self, **data):
        """Override init para normalizar campos - SIMPLIFICADO"""
        # Normalizar messageId - apenas 3 formatos principais
        if 'messageid' in data:
            data['messageId'] = data.pop('messageid')
        elif 'message_id' in data:
            data['messageId'] = data.pop('message_id')
        
        # Se ainda não tiver messageId, criar um
        if 'messageId' not in data:
            data['messageId'] = str(uuid4())
        
        # Normalizar text/content - apenas 'text' como alternativa
        if 'text' in data and 'content' not in data:
            data['content'] = data.pop('text')
        
        # Normalizar author - apenas formatos essenciais
        if 'user' in data and 'author' not in data:
            data['author'] = data.pop('user')
        elif 'user_id' in data and 'author' not in data:
            data['author'] = data.pop('user_id')
        
        # Normalizar contextId - apenas 2 formatos
        if 'context_id' in data:
            data['contextId'] = data.pop('context_id')
        elif 'contextid' in data:
            data['contextId'] = data.pop('contextid')
        
        # Role - sem variações (já vem correto)
        
        # Se role é uma string, tentar converter para Role enum se possível
        if 'role' in data and HAS_A2A and Role:
            role_value = data['role']
            # Se já é um Role enum, manter como está
            if hasattr(role_value, 'name'):
                pass  # Já é um enum Role
            # Se é uma string, tentar converter para enum
            elif isinstance(role_value, str):
                try:
                    # Tentar converter string para Role enum
                    if role_value.lower() == 'user':
                        data['role'] = Role.user
                    elif role_value.lower() == 'agent':
                        data['role'] = Role.agent
                    # Se não conseguir converter, manter como string
                except:
                    pass  # Manter como string se der erro
        
        # Normalizar taskId - apenas 2 formatos
        if 'task_id' in data:
            data['taskId'] = data.pop('task_id')
        elif 'taskid' in data:
            data['taskId'] = data.pop('taskid')
        
        # Normalizar conversationId - apenas 2 formatos  
        if 'conversation_id' in data:
            data['conversationId'] = data.pop('conversation_id')
        elif 'conversationid' in data:
            data['conversationId'] = data.pop('conversationid')
        
        # Chamar o init original
        super().__init__(**data)
    
    # Propriedades removidas - usar campos diretos
    
    @property
    def task_id_python(self) -> Optional[str]:
        """Propriedade Python - compatibilidade snake_case"""
        return self.taskId
    
    @property
    def conversation_id_python(self) -> Optional[str]:
        """Propriedade Python - compatibilidade snake_case"""
        return self.conversationId
    
    @property
    def parts_python(self) -> List[Any]:
        """Propriedade Python MUTÁVEL - retorna referência direta à lista"""
        return self.parts  # ✅ Retorna referência, permite append/extend
    
    @property
    def metadata_python(self) -> Optional[Dict[str, Any]]:
        """Propriedade Python MUTÁVEL - retorna referência direta ao dict"""
        return self.metadata  # ✅ Retorna referência, permite update
    
    # Métodos adicionais para compatibilidade
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override para garantir compatibilidade com v1 e v2"""
        return self.model_dump(**kwargs)
    
    def json(self, **kwargs) -> str:
        """Override para garantir compatibilidade com v1 e v2"""
        return self.model_dump_json(**kwargs)


def patch_a2a_message():
    """
    Aplica o patch no módulo a2a.types para usar nossa versão de Message
    """
    if HAS_A2A:
        import sys
        import a2a.types
        
        # Substituir a classe Message no módulo
        a2a.types.Message = MessagePatched
        
        # Também atualizar no cache de módulos
        if 'a2a.types' in sys.modules:
            sys.modules['a2a.types'].Message = MessagePatched
        
        print("[PATCH] a2a.types.Message foi patchado com sucesso!")
        return True
    else:
        print("[PATCH] a2a não está instalado, usando Message local")
        return False


# Aplicar o patch automaticamente quando este módulo for importado
if __name__ != "__main__":
    patch_a2a_message()