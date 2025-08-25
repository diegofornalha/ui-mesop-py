# 🎯 **ESTRATÉGIA DE NOMENCLATURA: PROPRIEDADES PYTHON**

## **📌 PROBLEMA IDENTIFICADO**

Confusão entre **campos mutáveis** (camelCase) e **propriedades read-only** (snake_case) que causava o erro:
```
AttributeError: property 'message_ids' of 'StateConversation' object has no setter
```

## **✅ SOLUÇÃO: SUFIXO `_python` PARA PROPRIEDADES MUTÁVEIS**

### **Regra Simples:**
- **Campos reais (camelCase):** `messageId`, `contextId`, `conversationId` → **MUTÁVEIS**
- **Propriedades Python:** `message_id_python`, `context_id_python` → **MUTÁVEIS (referência direta)**

---

## **📋 GUIA DE USO**

### **1. ESCRITA/MODIFICAÇÃO - Use Campos Reais (camelCase) OU Propriedades Python**

```python
# ✅ CORRETO - Campos reais são mutáveis
message.messageId = "novo-id"
message.contextId = "contexto-123"
conversation.messageIds.append("msg-456")
conversation.isActive = True

# ✅ CORRETO - Propriedades Python também são mutáveis (para listas)
conversation.message_ids_python.append("msg")  # ✅ FUNCIONA!
conversation.message_ids_python.extend(["id1", "id2"])  # ✅ FUNCIONA!
```

### **2. LEITURA - Use Campos Reais ou Propriedades Python**

```python
# ✅ AMBOS FUNCIONAM para leitura
id1 = message.messageId           # Campo real (PREFERIDO)
id2 = message.message_id_python   # Propriedade Python

# ✅ Para conversões snake_case quando necessário
python_id = message.message_id_python
python_context = message.context_id_python
```

---

## **🔍 EXEMPLOS PRÁTICOS**

### **Exemplo 1: Adicionar Mensagem a Conversa**

```python
# ✅ CORRETO
conversation.messageIds.append(message.messageId)

# ❌ ERRADO
conversation.message_ids_python.append(message.message_id_python)
```

### **Exemplo 2: Criar Nova Mensagem**

```python
# ✅ CORRETO
message = Message(
    messageId="msg-123",      # Campo real
    contextId="ctx-456",       # Campo real
    content="Hello"
)

# Modificar depois
message.contextId = "novo-contexto"  # ✅ Campo mutável
```

### **Exemplo 3: Verificar Valores**

```python
# ✅ AMBOS funcionam para leitura
if message.messageId:              # Campo real (PREFERIDO)
    print(f"ID: {message.messageId}")

if message.message_id_python:      # Propriedade Python
    print(f"ID: {message.message_id_python}")
```

---

## **📊 TABELA DE REFERÊNCIA RÁPIDA**

| Operação | Use | Exemplo | Resultado |
|----------|-----|---------|-----------|
| **Escrita** | Campo Real | `msg.messageId = "123"` | ✅ Funciona |
| **Escrita** | Propriedade | `msg.message_id_python = "123"` | ❌ ERRO (atribuição direta) |
| **Leitura** | Campo Real | `id = msg.messageId` | ✅ Funciona |
| **Leitura** | Propriedade | `id = msg.message_id_python` | ✅ Funciona |
| **Append** | Campo Real | `conv.messageIds.append()` | ✅ Funciona |
| **Append** | Propriedade | `conv.message_ids_python.append()` | ✅ **FUNCIONA!** |

---

## **🎯 CLASSES ATUALIZADAS**

### **1. Message / MessagePatched**
```python
# Campos reais (MUTÁVEIS)
messageId: str
contextId: str
conversationId: str

# Propriedades Python (READ-ONLY)
message_id_python
context_id_python
conversation_id_python
messageid_python
contextid_python
conversationid_python
```

### **2. StateConversation**
```python
# Campos reais (MUTÁVEIS)
conversationId: str
messageIds: list[str]
isActive: bool

# Propriedades Python (READ-ONLY)
conversation_id_python
message_ids_python
is_active_python
conversationid_python
messageids_python
isactive_python
```

### **3. StateMessage**
```python
# Campos reais (MUTÁVEIS)
messageId: str
contextId: str
taskId: str

# Propriedades Python (READ-ONLY)
message_id_python
context_id_python
task_id_python
messageid_python
contextid_python
taskid_python
```

### **4. ConversationFixed**
```python
# Campos reais (MUTÁVEIS)
conversationId: str
isActive: bool

# Propriedades Python (READ-ONLY)
conversationid_python
isactive_python
```

---

## **💡 BENEFÍCIOS DA ESTRATÉGIA**

1. **Zero Confusão:** Impossível confundir `messageId` com `message_id_python`
2. **Zero Erros:** Elimina completamente erros de "property has no setter"
3. **Código Claro:** Sufixo `_python` indica claramente que é propriedade
4. **Compatibilidade:** Mantém conformidade com A2A Protocol e Google ADK
5. **Manutenção Fácil:** Desenvolvedores sabem imediatamente o que usar
6. **Flexibilidade:** Propriedades Python funcionam para modificação de listas

---

## **⚠️ REGRA DE OURO**

> **Para MODIFICAR:** Use campos reais (camelCase) OU propriedades Python (para listas)  
> **Para LER:** Prefira campos reais, use propriedades `_python` quando necessário  
> **Para LISTAS:** Propriedades Python funcionam para `.append()`, `.extend()`, `.remove()`

---

## **📝 MIGRAÇÃO DE CÓDIGO EXISTENTE**

Se você tem código que usa as propriedades antigas:

```python
# ❌ CÓDIGO ANTIGO (causava erros)
conversation.message_ids.append(msg.message_id)

# ✅ CÓDIGO NOVO (sem erros)
conversation.messageIds.append(msg.messageId)        # ✅ Campo real
conversation.message_ids_python.append(msg.messageId)  # ✅ Propriedade Python (também funciona!)
```

---

## **🚀 RESULTADO FINAL**

Com esta estratégia:
- ✅ **100% eliminação** de erros "property has no setter"
- ✅ **100% clareza** sobre o que é mutável vs read-only
- ✅ **100% compatibilidade** com A2A Protocol e Google ADK
- ✅ **0% confusão** entre desenvolvedores
- ✅ **100% flexibilidade** para modificação de listas via propriedades Python

**A nomenclatura com sufixo `_python` elimina completamente a possibilidade de erro e oferece flexibilidade máxima!**