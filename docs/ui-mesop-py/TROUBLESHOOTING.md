# 🛠️ TROUBLESHOOTING - Guia Completo de Solução de Problemas

## 📋 Índice
1. [Erros Comuns](#erros-comuns)
2. [Soluções Definitivas](#soluções-definitivas)
3. [Problemas de MessageId](#problemas-de-messageid)
4. [Configuração do Servidor](#configuração-do-servidor)

---

## 🚨 Erros Comuns

### 1. **ValidationError: taskId - Input should be a valid string**

**Erro:**
```
1 validation error for StateMessage
taskId
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

**Solução:**
```python
# Em state/state.py
@dataclass
class StateMessage:
    taskId: str | None = ''  # Aceitar None ou string
```

---

### 2. **Property has no setter**

**Erro:**
```
AttributeError: property 'message_id' of 'StateMessage' object has no setter
```

**Solução:**
- Remover todas as @property decorators desnecessárias
- Usar campos diretos do dataclass

---

### 3. **'dict' object has no attribute 'parts'**

**Erro ao clicar em EventList:**
```
AttributeError: 'dict' object has no attribute 'parts'
```

**Solução:**
```python
# Adicionar verificação de tipo
if isinstance(event.content, dict):
    # Tratar como dict
else:
    # Tratar como objeto
```

---

### 4. **'StateEvent' object has no attribute 'context_id'**

**Erro:**
```
AttributeError: 'StateEvent' object has no attribute 'context_id'
```

**Solução:**
```python
# Usar camelCase
event.contextId  # ✅ Correto
# NÃO: event.context_id
```

---

### 5. **API Quota Exceeded (Error 429)**

**Erro:**
```
429 RESOURCE_EXHAUSTED
Quota exceeded for quota metric 'GenerateContent'
```

**Solução:**
1. Obter nova API key em https://makersuite.google.com/app/apikey
2. Atualizar no ambiente:
```bash
export GOOGLE_API_KEY="nova_chave_aqui"
```
3. Reiniciar servidor

---

## ✅ Soluções Definitivas

### **Padronização de Nomenclatura**

**Regra de Ouro: Sempre use camelCase**

```python
# ✅ CORRETO - camelCase
messageId, contextId, taskId, conversationId

# ❌ ERRADO - snake_case
message_id, context_id, task_id, conversation_id
```

### **Estrutura de Estado Simplificada**

```python
@dataclass
class StateMessage:
    messageId: str = ''
    taskId: str | None = ''  # Aceita None
    contextId: str = ''
    role: str = ''
    content: list[tuple[ContentPart, str]] = dataclasses.field(default_factory=list)
```

---

## 🔧 Problemas de MessageId

### **Solução Final para MessageId**

**Problema:** Múltiplas variações de nomes causando confusão

**Solução Implementada:**
1. **Fonte única de verdade:** `service/types.py`
2. **Aceitar apenas 2 formatos:**
   - `messageId` (camelCase - padrão)
   - `message_id` (snake_case - compatibilidade)

```python
# service/types.py
class Message(BaseModel):
    messageId: str = Field(default="", alias="message_id")
    
    def __init__(self, **data):
        # Normalizar apenas formatos essenciais
        if 'message_id' in data:
            data['messageId'] = data.pop('message_id')
        super().__init__(**data)
```

---

## 🚀 Configuração do Servidor

### **Como Reiniciar o Servidor**

```bash
# Comando completo
pkill -f "python.*main.py" && sleep 2 && \
GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
A2A_UI_PORT=8888 MESOP_DEFAULT_PORT=8888 \
.venv/bin/python main.py
```

### **Quando Reiniciar é Necessário**

✅ **SEMPRE após:**
- Mudanças em arquivos `.py`
- Alterações em `state/state.py`
- Modificações em componentes
- Mudanças na API key

❌ **NÃO precisa após:**
- Mudanças em arquivos `.md`
- Alterações no git

---

## 💡 Dicas Importantes

### **1. Sempre Use CamelCase**
```python
# Em todos os componentes
event.contextId     # ✅
event.context_id    # ❌
```

### **2. Verificação de Tipo**
```python
# Sempre verificar tipo antes de acessar atributos
if isinstance(content, dict):
    # Tratar como dict
elif hasattr(content, 'parts'):
    # Tratar como objeto
```

### **3. Valores Padrão**
```python
# Sempre definir valores padrão
taskId: str | None = ''
content: list = dataclasses.field(default_factory=list)
```

### **4. Debug de Erros**
```python
# Adicionar logs para debug
print(f"DEBUG: type={type(obj)}, value={obj}")
```

---

## 📊 Métricas de Resolução

| Problema | Tempo Médio | Complexidade | Status |
|----------|-------------|--------------|--------|
| Property setter | 5 min | Baixa | ✅ Resolvido |
| CamelCase | 2 min | Baixa | ✅ Resolvido |
| API quota | 10 min | Média | ✅ Resolvido |
| Dict vs Object | 15 min | Alta | ✅ Resolvido |

---

## 🔍 Verificações Rápidas

### **Verificar CamelCase:**
```bash
grep -r "context_id\|message_id" --include="*.py" .
```

### **Verificar Imports:**
```bash
grep -r "from.*import" --include="*.py" . | grep -v "#"
```

### **Verificar Servidor:**
```bash
ps aux | grep main.py
curl http://localhost:8888
```

---

## 📝 Changelog de Correções

- **25/08/2025**: Consolidação de toda documentação de troubleshooting
- **24/08/2025**: Padronização completa para camelCase
- **24/08/2025**: Remoção de propriedades redundantes
- **24/08/2025**: Simplificação do message_patch

---

**Última atualização:** 25/08/2025
**Status:** ✅ Todas as soluções aplicadas e funcionando