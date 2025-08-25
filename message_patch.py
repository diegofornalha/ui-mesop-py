"""
Patch para corrigir o problema de Message com messageid
Este módulo deve ser importado ANTES de qualquer uso de a2a.types.Message
"""

from typing import Any, List, Optional, Dict, Union
from uuid import uuid4
from pydantic import BaseModel, Field, model_validator, ConfigDict

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
    # Configuração do Pydantic v2
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra='allow',  # Permite campos extras
        str_strip_whitespace=True,  # Remove espaços em branco
        validate_assignment=True  # Valida atribuições após criação
    )
    
    # Campos do modelo com aliases flexíveis
    messageId: str = Field(default="", alias="messageId")
    content: str = Field(default="")
    author: str = Field(default="")
    timestamp: float = Field(default=0.0)
    context_id: Optional[str] = Field(default=None, alias="contextId")
    parts: List[Any] = Field(default_factory=list)
    role: Optional[Any] = Field(default=None)  # Pode ser Role enum ou string
    
    # Campos adicionais para compatibilidade com o sistema
    taskid: Optional[str] = Field(default=None, alias="taskId")
    conversation_id: Optional[str] = Field(default=None, alias="conversationId")
    task: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    @model_validator(mode='before')
    @classmethod
    def normalize_fields(cls, values: Any) -> Any:
        """Normaliza variações de campos para Message"""
        if isinstance(values, dict):
            # Debug: mostrar o que está chegando
            # print(f"[MessagePatched] Recebendo: {values.keys()}")
            
            # Normalizar messageId - aceitar TODAS as variações possíveis
            id_variations = [
                'messageid', 'messageId', 'message_id', 'message_Id', 
                'MessageId', 'MessageID', 'id', 'ID', 'Id'
            ]
            for key in id_variations:
                if key in values:
                    if 'messageId' not in values:
                        values['messageId'] = values[key]
                    # Não remover o campo original ainda, pode ser necessário
                    if key != 'messageId':
                        values.pop(key, None)
            
            # Se ainda não tiver messageId, criar um
            if 'messageId' not in values:
                values['messageId'] = str(uuid4())
            
            # Normalizar text/content
            content_variations = ['text', 'message', 'body', 'Text', 'TEXT']
            for key in content_variations:
                if key in values and 'content' not in values:
                    values['content'] = values.pop(key)
            
            # Normalizar author
            author_variations = [
                'user', 'userId', 'user_id', 'sender', 'from', 
                'User', 'UserID', 'userid', 'author_id'
            ]
            for key in author_variations:
                if key in values and 'author' not in values:
                    values['author'] = values.pop(key)
            
            # Normalizar context_id
            context_variations = [
                'contextId', 'contextid', 'context_Id', 'ContextId',
                'contextID', 'context', 'conversation_id'
            ]
            for key in context_variations:
                if key in values and 'context_id' not in values:
                    values['context_id'] = values.pop(key)
            
            # Normalizar role - preservar o tipo original (Role enum ou string)
            role_variations = ['Role', 'ROLE', 'user_role', 'userRole']
            for key in role_variations:
                if key in values and 'role' not in values:
                    values['role'] = values.pop(key)
            
            # Se role é uma string, tentar converter para Role enum se possível
            if 'role' in values and HAS_A2A and Role:
                role_value = values['role']
                # Se já é um Role enum, manter como está
                if hasattr(role_value, 'name'):
                    pass  # Já é um enum Role
                # Se é uma string, tentar converter para enum
                elif isinstance(role_value, str):
                    try:
                        # Tentar converter string para Role enum
                        if role_value.lower() == 'user':
                            values['role'] = Role.user
                        elif role_value.lower() == 'agent':
                            values['role'] = Role.agent
                        # Se não conseguir converter, manter como string
                    except:
                        pass  # Manter como string se der erro
            
            # Normalizar taskid - aceitar TODAS as variações possíveis
            taskid_variations = [
                'taskid', 'taskId', 'task_id', 'task_Id',
                'TaskId', 'TaskID', 'task', 'Task', 'TASK'
            ]
            for key in taskid_variations:
                if key in values:
                    if 'taskid' not in values:
                        values['taskid'] = values[key]
                    # Remover variações para evitar duplicação
                    if key != 'taskid' and key != 'task':
                        values.pop(key, None)
            
            # Normalizar conversation_id
            conversation_variations = [
                'conversationId', 'conversationid', 'conversation_Id',
                'ConversationId', 'ConversationID', 'conversation',
                'Conversation', 'conv_id', 'convId'
            ]
            for key in conversation_variations:
                if key in values and 'conversation_id' not in values:
                    values['conversation_id'] = values.pop(key)
                    
        return values
    
    # Propriedades para compatibilidade total
    @property
    def messageid(self) -> str:
        return self.messageId
    
    @property
    def id(self) -> str:
        return self.messageId
    
    @property
    def message_id(self) -> str:
        return self.messageId
    
    @property
    def taskId(self) -> Optional[str]:
        return self.taskid
    
    @property
    def task_id(self) -> Optional[str]:
        return self.taskid
    
    @property
    def TaskId(self) -> Optional[str]:
        return self.taskid
    
    @property
    def conversationId(self) -> Optional[str]:
        return self.conversation_id
    
    @property
    def conversation_Id(self) -> Optional[str]:
        return self.conversation_id
    
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