#!/usr/bin/env python3
"""
Patch para corrigir o problema de Message com messageid
Compatível com Pydantic v1 e v2
"""

from typing import Any, List, Optional, Dict
from uuid import uuid4
import pydantic

# Detectar versão do Pydantic
PYDANTIC_V2 = pydantic.__version__.startswith('2')
print(f"[PATCH] Detectado Pydantic v{pydantic.__version__}")

if PYDANTIC_V2:
    from pydantic import BaseModel, Field, model_validator, ConfigDict
else:
    from pydantic import BaseModel, Field, validator

# Salvar a classe original antes de patchear
try:
    from a2a.types import Message as OriginalMessage
    HAS_A2A = True
except ImportError:
    HAS_A2A = False
    OriginalMessage = None


if PYDANTIC_V2:
    class MessagePatched(BaseModel):
        """
        Versão patchada de Message para Pydantic v2
        """
        # Configuração do Pydantic v2
        model_config = ConfigDict(
            populate_by_name=True,
            arbitrary_types_allowed=True,
            extra='allow',
            str_strip_whitespace=True,
            validate_assignment=True
        )
        
        # Campos do modelo
        messageId: str = Field(default="")
        content: str = Field(default="")
        author: str = Field(default="")
        timestamp: float = Field(default=0.0)
        contextId: Optional[str] = Field(default=None, alias="context_id")
        parts: List[Any] = Field(default_factory=list)
        role: Optional[str] = Field(default=None)
        metadata: Optional[Dict[str, Any]] = Field(default=None)
        
        @model_validator(mode='before')
        @classmethod
        def normalize_fields(cls, values: Any) -> Any:
            """Normaliza variações de campos para Message"""
            if isinstance(values, dict):
                # Normalizar messageId
                id_variations = [
                    'messageid', 'messageId', 'message_id', 'message_Id', 
                    'MessageId', 'MessageID', 'id', 'ID', 'Id'
                ]
                for key in id_variations:
                    if key in values:
                        if 'messageId' not in values:
                            values['messageId'] = values[key]
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
                
                # Normalizar role
                role_variations = ['Role', 'ROLE', 'user_role', 'userRole']
                for key in role_variations:
                    if key in values and 'role' not in values:
                        values['role'] = values.pop(key)
                        
            return values
        
        # Propriedades para compatibilidade
        @property
        def messageid(self) -> str:
            return self.messageId
        
        @property
        def id(self) -> str:
            return self.messageId
        
        @property
        def message_id(self) -> str:
            return self.messageId
        
        # Métodos de compatibilidade v1/v2
        def dict(self, **kwargs) -> Dict[str, Any]:
            """Compatibilidade com v1 e v2"""
            if hasattr(self, 'model_dump'):
                return self.model_dump(**kwargs)
            return super().dict(**kwargs)
        
        def json(self, **kwargs) -> str:
            """Compatibilidade com v1 e v2"""
            if hasattr(self, 'model_dump_json'):
                return self.model_dump_json(**kwargs)
            return super().json(**kwargs)

else:
    # Pydantic v1
    class MessagePatched(BaseModel):
        """
        Versão patchada de Message para Pydantic v1
        """
        messageId: str = Field(default="", alias="messageId")
        content: str = ""
        author: str = ""
        timestamp: float = 0.0
        context_id: Optional[str] = Field(None, alias="contextId")
        parts: List[Any] = Field(default_factory=list)
        role: Optional[str] = None
        metadata: Optional[dict] = None
        
        @validator('messageId', pre=True, always=True)
        def normalize_message_id(cls, v, values):
            """Normaliza messageId para Pydantic v1"""
            if not v:
                # Procurar por variações de messageId nos values originais
                return str(uuid4())
            return v
        
        def __init__(self, **data):
            """Override init para normalizar campos"""
            # Normalizar messageId
            id_variations = [
                'messageid', 'messageId', 'message_id', 'message_Id', 
                'MessageId', 'MessageID', 'id', 'ID', 'Id'
            ]
            for key in id_variations:
                if key in data:
                    if 'messageId' not in data:
                        data['messageId'] = data[key]
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
            
            # Normalizar context_id/contextId
            context_variations = [
                'contextId', 'contextid', 'context_Id', 'ContextId',
                'contextID', 'context', 'conversation_id'
            ]
            for key in context_variations:
                if key in data and 'context_id' not in data and 'contextId' not in data:
                    # Para v1, usar o alias contextId
                    data['contextId'] = data.pop(key)
            
            # Normalizar role
            role_variations = ['Role', 'ROLE', 'user_role', 'userRole']
            for key in role_variations:
                if key in data and 'role' not in data:
                    data['role'] = data.pop(key)
            
            # Chamar o init original
            super().__init__(**data)
        
        # Propriedades para compatibilidade
        @property
        def messageid(self) -> str:
            return self.messageId
        
        @property
        def id(self) -> str:
            return self.messageId
        
        @property
        def message_id(self) -> str:
            return self.messageId
        
        class Config:
            populate_by_name = True
            allow_population_by_field_name = True
            extra = "allow"
            arbitrary_types_allowed = True


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
        
        print(f"[PATCH] a2a.types.Message foi patchado com sucesso! (Pydantic v{pydantic.__version__})")
        return True
    else:
        print("[PATCH] a2a não está instalado, usando Message local")
        return False


# Aplicar o patch automaticamente quando este módulo for importado
if __name__ != "__main__":
    patch_a2a_message()


# Para testes diretos
if __name__ == "__main__":
    print("="*60)
    print(f"Testando Message Patch com Pydantic v{pydantic.__version__}")
    print("="*60)
    
    # Teste com messageid minúsculo
    test_data = {
        "messageid": "test-123",
        "text": "Conteúdo de teste",
        "user": "test-user",
        "contextId": "ctx-456"
    }
    
    msg = MessagePatched(**test_data)
    print(f"✅ Message criado com sucesso!")
    print(f"   - messageId: {msg.messageId}")
    print(f"   - content: {msg.content}")
    print(f"   - author: {msg.author}")
    print(f"   - context_id: {msg.context_id}")
    
    # Testar propriedades
    print(f"\n📝 Propriedades de compatibilidade:")
    print(f"   - messageid: {msg.messageid}")
    print(f"   - id: {msg.id}")
    print(f"   - message_id: {msg.message_id}")
    
    # Testar serialização
    print(f"\n💾 Serialização:")
    if PYDANTIC_V2:
        json_str = msg.model_dump_json()
        print(f"   ✅ model_dump_json() funcionou")
    else:
        json_str = msg.json()
        print(f"   ✅ json() funcionou")
    print(f"   JSON: {json_str[:100]}...")