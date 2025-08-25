# 🚨 Erros Comuns e Soluções

## 1. ValidationError: taskId - Input should be a valid string

### **Erro:**
```
1 validation error for StateMessage
taskId
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.11/v/string_type
```

### **Causa:**
Este erro ocorre porque o Pydantic v2 tem validação mais rigorosa e não aceita `None` em campos definidos como `str`.

### **Solução:**

#### **Opção 1: Aceitar None no tipo (RECOMENDADO)**
```python
# Em state/state.py
@dataclass
class StateMessage:
    messageId: str = ''
    taskId: str | None = ''  # Aceitar None ou string
    contextId: str = ''
    role: str = ''
```

#### **Opção 2: Garantir valor padrão na criação**
```python
# Em state/host_agent_service.py
return StateMessage(
    messageId=message.messageId,
    contextId=message.contextId if message.contextId else '',
    taskId=getattr(message, 'taskId', '') or '',  # Garante string vazia
    role=role_value,
    content=extract_content(message.parts),
)
```

### **Prevenção:**
Sempre use `getattr(obj, 'campo', '')` ou `obj.campo or ''` para garantir que `None` seja convertido para string vazia.

---

## 2. AttributeError: 'MessagePatched' object has no attribute 'contextId'

### **Erro:**
```
AttributeError: 'MessagePatched' object has no attribute 'contextId'
```

### **Causa:**
Incompatibilidade entre Pydantic v1 e v2, ou campo não definido corretamente.

### **Solução:**

#### **Para Pydantic v1:**
```python
class MessagePatched(BaseModel):
    contextId: Optional[str] = Field(default=None, alias="context_id")
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
```

#### **Para Pydantic v2:**
```python
class MessagePatched(BaseModel):
    contextId: Optional[str] = Field(default=None, alias="context_id")
    
    model_config = ConfigDict(
        populate_by_name=True
    )
```

### **Verificação:**
```python
# Testar se o campo existe
import message_patch
msg = message_patch.MessagePatched(contextId='test')
print(hasattr(msg, 'contextId'))  # Deve retornar True
```

---

## 3. AttributeError: property 'context_id' has no setter

### **Erro:**
```
AttributeError: property 'context_id' of 'MessagePatched' object has no setter
```

### **Causa:**
Tentando atribuir valor a uma propriedade read-only.

### **Solução:**

#### **Errado:**
```python
test_image.context_id = context_id  # ❌ Propriedade read-only
```

#### **Correto:**
```python
test_image.contextId = context_id  # ✅ Campo principal
```

### **Regra:**
- **Campos principais:** Use para escrita (`obj.contextId = valor`)
- **Propriedades:** Use apenas para leitura (`valor = obj.context_id`)

---

## 4. Conflito de versões Pydantic

### **Erro:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
mesop 0.8.0 requires pydantic==1.10.13, but you have pydantic 2.11.7
```

### **Causa:**
Mesop 0.8.0 requer Pydantic v1, mas o projeto tenta usar v2.

### **Solução:**

#### **Fixar versão no pyproject.toml:**
```toml
[tool.poetry.dependencies]
pydantic = "==1.10.13"  # Versão requerida pelo Mesop
```

#### **Reinstalar:**
```bash
pip uninstall pydantic
pip install pydantic==1.10.13
```

### **Importante:**
Mesop 0.8.0 **NÃO** é compatível com Pydantic v2. Sempre use v1.10.13.

---

## 5. Nomenclatura Inconsistente

### **Problema:**
Múltiplas variações do mesmo campo causando erros:
- `context_id` (snake_case)
- `contextid` (lowercase)
- `contextId` (camelCase)
- `context_Id` (mixed)

### **Solução Padrão:**

```python
class Message(BaseModel):
    # Campo principal em camelCase (A2A Protocol)
    contextId: Optional[str] = Field(default=None, alias="context_id")
    
    class Config:
        populate_by_name = True  # Aceita ambos os formatos
    
    # Propriedade para compatibilidade Python
    @property
    def context_id(self) -> str:
        return self.contextId
    
    # Propriedade para compatibilidade lowercase
    @property
    def contextid(self) -> str:
        return self.contextId
```

### **Uso:**
```python
# Todos funcionam:
msg = Message(contextId='test')     # ✅ camelCase
msg = Message(context_id='test')    # ✅ snake_case (alias)
print(msg.contextId)                # ✅ Campo principal
print(msg.context_id)               # ✅ Propriedade
print(msg.contextid)                # ✅ Propriedade lowercase
```

---

## 6. Porta 8888 em uso

### **Erro:**
```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8888): address already in use
```

### **Solução:**

#### **Liberar porta:**
```bash
# Encontrar e matar processo
lsof -i :8888 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Ou usar outra porta
A2A_UI_PORT=8889 MESOP_DEFAULT_PORT=8889 python main.py
```

---

## 7. Import Error com message_patch

### **Erro:**
```
ImportError: cannot import name 'model_validator' from 'pydantic'
```

### **Causa:**
Código escrito para Pydantic v2 mas usando v1.

### **Solução:**

#### **Pydantic v1:**
```python
from pydantic import BaseModel, Field, validator

class MessagePatched(BaseModel):
    messageId: str = Field(default="")
    
    @validator('messageId', pre=True)
    def normalize_message_id(cls, v):
        return v or ""
```

#### **Pydantic v2:**
```python
from pydantic import BaseModel, Field, model_validator

class MessagePatched(BaseModel):
    messageId: str = Field(default="")
    
    @model_validator(mode='before')
    def normalize_fields(cls, values):
        return values
```

---

## 8. AttributeError: property 'message_ids' has no setter

### **Erro:**
```
AttributeError: property 'message_ids' of 'StateConversation' object has no setter
```

### **Causa:**
Tentando modificar uma propriedade read-only que foi criada para compatibilidade.

### **Estrutura do Problema:**
```python
@dataclass
class StateConversation:
    messageIds: list[str] = field(default_factory=list)  # Campo real - mutável
    
    @property
    def message_ids(self) -> list[str]:  # Propriedade - read-only
        return self.messageIds
```

### **Solução:**

#### **Errado:**
```python
conversation.messageids.append(message.messageid)  # ❌ Propriedade read-only
```

#### **Correto:**
```python
conversation.messageIds.append(message.messageId)  # ✅ Campo real mutável
```

### **Regra Importante:**
- **Campos reais (camelCase):** Use para leitura E escrita
- **Propriedades (snake_case):** Use APENAS para leitura
- **Nunca modifique** propriedades diretamente

---

## 📋 Checklist de Resolução

Ao encontrar um erro de validação:

1. ✅ Verificar versão do Pydantic: `python -c "import pydantic; print(pydantic.__version__)"`
2. ✅ Verificar se o campo aceita None: `campo: str | None`
3. ✅ Usar getattr com valor padrão: `getattr(obj, 'campo', '')`
4. ✅ Não atribuir a propriedades read-only
5. ✅ Usar campo principal para escrita, propriedades para leitura
6. ✅ Garantir aliases configurados corretamente

---

## 🎯 Padrão Recomendado

Para evitar todos esses erros, sempre siga este padrão:

```python
# Modelo Pydantic
class MyModel(BaseModel):
    myField: str | None = Field(default="", alias="my_field")
    
    class Config:
        populate_by_name = True
    
    @property
    def my_field(self) -> str:
        return self.myField or ""

# Uso seguro
model = MyModel(my_field="value")  # Funciona com alias
model.myField = "new_value"        # Escrita no campo principal
value = model.my_field              # Leitura via propriedade
```

Este padrão garante compatibilidade total e evita erros de validação.