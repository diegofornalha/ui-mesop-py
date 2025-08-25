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
        """Override init para normalizar campos"""
        # Normalizar messageId - aceitar TODAS as variações possíveis
        id_variations = [
            'messageid', 'messageId', 'message_id', 'message_Id', 
            'MessageId', 'MessageID', 'id', 'ID', 'Id'
        ]
        for key in id_variations:
            if key in data:
                if 'messageId' not in data:
                    data['messageId'] = data[key]
                # Não remover o campo original ainda, pode ser necessário
                if key != 'messageId':
                    data.pop(key, None)
        
        # Se ainda não tiver messageId, criar um
        if 'messageId' not in data:
            data['messageId'] = str(uuid4())
        
        # Normalizar text/content
        content_variations = ['text', 'message', 'body', 'Text', 'TEXT']
        for key in content_variations:
            if key in data and 'content' not in data:
                data['content'] = data.pop(key)
        
        # Normalizar author
        author_variations = [
            'user', 'userId', 'user_id', 'sender', 'from', 
            'User', 'UserID', 'userid', 'author_id'
        ]
        for key in author_variations:
            if key in data and 'author' not in data:
                data['author'] = data.pop(key)
        
        # Normalizar contextId - aceitar todas as variações
        context_variations = [
            'context_id', 'contextid', 'context_Id', 'ContextId',
            'contextID', 'context'
        ]
        for key in context_variations:
            if key in data and 'contextId' not in data:
                data['contextId'] = data[key]
                if key != 'contextId':
                    data.pop(key, None)
        
        # Normalizar role - preservar o tipo original (Role enum ou string)
        role_variations = ['Role', 'ROLE', 'user_role', 'userRole']
        for key in role_variations:
            if key in data and 'role' not in data:
                data['role'] = data.pop(key)
        
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
        
        # Normalizar taskId - aceitar todas as variações
        taskid_variations = [
            'task_id', 'taskid', 'task_Id',
            'TaskId', 'TaskID', 'task', 'Task', 'TASK'
        ]
        for key in taskid_variations:
            if key in data and 'taskId' not in data:
                data['taskId'] = data[key]
                if key != 'taskId' and key != 'task':
                    data.pop(key, None)
        
        # Normalizar conversationId
        conversation_variations = [
            'conversation_id', 'conversationid', 'conversation_Id',
            'ConversationId', 'ConversationID', 'conversation',
            'Conversation', 'conv_id', 'convId'
        ]
        for key in conversation_variations:
            if key in data and 'conversationId' not in data:
                data['conversationId'] = data.pop(key)
        
        # Chamar o init original
        super().__init__(**data)
    
    # Propriedades Python MUTÁVEIS - retornam referências diretas
    @property
    def message_id_python(self) -> str:
        """Propriedade Python - compatibilidade snake_case"""
        return self.messageId
    
    @property
    def context_id_python(self) -> Optional[str]:
        """Propriedade Python - compatibilidade snake_case"""
        return self.contextId
    
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