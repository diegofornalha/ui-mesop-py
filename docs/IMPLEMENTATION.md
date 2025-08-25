# Guia de Implementação

## 🚀 Detalhes e Padrões de Implementação

### Padrões de Código

#### Guia de Estilo Python
- Siga as convenções do PEP 8
- Use type hints em todas as funções
- Comprimento máximo de linha: 100 caracteres
- Use nomes de variáveis descritivos

#### Convenções de Nomenclatura
```python
# Classes: PascalCase
class StateMessage:
    pass

# Functions: snake_case
def send_message():
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_PORT = 8888

# Private methods: leading underscore
def _internal_helper():
    pass
```

### Implementação do Sistema de Tipos

#### Fonte Única de Verdade
Todos os tipos são definidos em `service/types.py`:

```python
# ✅ CORRECT - Direct field access
message.messageId
conversation.conversationId

# ❌ WRONG - Redundant properties (removed)
message.message_id_python  # Don't use
message.messageid_python   # Don't use
```

#### Aliases de Campos
Use aliases do Pydantic para compatibilidade:

```python
class Message(BaseModel):
    messageId: str = Field(default="", alias="message_id")
    # Accepts both: messageId and message_id
```

### Desenvolvimento de Componentes

#### Criando um Novo Componente
```python
import mesop as me
from state.state import AppState

@me.component
def my_component():
    """Component description"""
    state = me.state(AppState)
    
    with me.box(style=me.Style(
        padding=20,
        background="#f0f0f0",
        border_radius=8
    )):
        me.text("Component content")
```

#### Boas Práticas de Componentes
1. Use componentes nativos do Mesop
2. Mantenha componentes com menos de 100 linhas
3. Separe lógica de apresentação
4. Use o gerenciamento de estado corretamente

### Padrões de Gerenciamento de Estado

#### Acessando o Estado
```python
def my_handler(e: me.ClickEvent):
    state = me.state(AppState)
    # Read state
    current_id = state.current_conversation_id
    # Update state
    state.current_conversation_id = "new-id"
```

#### Operações Assíncronas
```python
async def async_handler(e: me.WebEvent):
    yield  # Initial yield for UI update
    
    # Perform async operation
    result = await some_async_function()
    
    # Update state
    state = me.state(AppState)
    state.data = result
    
    yield  # Final yield to update UI
```

### Manipulação de Mensagens

#### Enviando Mensagens
```python
async def send_message(message: str, message_id: str = ''):
    state = me.state(PageState)
    app_state = me.state(AppState)
    
    # Find conversation
    conversation = next(
        (x for x in await ListConversations() 
         if x.conversationId == state.conversationid),
        None
    )
    
    # Create message
    request = Message(
        messageId=message_id or str(uuid.uuid4()),
        contextId=state.conversationid,
        role=Role.user,
        parts=[Part(root=TextPart(text=message))]
    )
    
    # Send message
    await SendMessage(request)
```

#### Processando Respostas
```python
async def refresh_messages():
    page_state = me.state(PageState)
    app_state = me.state(AppState)
    
    if not page_state.conversationid:
        return
    
    try:
        messages = await ListMessages(page_state.conversationid)
        state_messages = [
            convert_message_to_state(msg) 
            for msg in messages
        ]
        
        if len(state_messages) > len(app_state.messages):
            app_state.messages = state_messages
            
    except Exception as e:
        print(f"Error updating messages: {e}")
```

### Renderização de Formulários (Simplificada)

#### Formulários Nativos do Mesop
```python
def render_form(message: StateMessage, app_state: AppState):
    """Render form using native Mesop components"""
    if message.messageId in app_state.completed_forms:
        # Show completed form
        with me.box(style=me.Style(
            padding=20, 
            background="#f0f0f0", 
            border_radius=8
        )):
            me.text("Form submitted", type="headline-6")
            data = app_state.completed_forms[message.messageId]
            if data:
                for key, value in data.items():
                    me.text(f"{key}: {value}")
    else:
        # Render active form
        with me.box(style=me.Style(padding=20)):
            me.text("Form", type="headline-6")
            # Add form fields as needed
```

### Tratamento de Erros

#### Padrão de Erro Padrão
```python
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    # Handle specific error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle general error
finally:
    # Cleanup if needed
    pass
```

#### Erros Amigáveis ao Usuário
```python
def show_error(message: str):
    with me.box(style=me.Style(
        background="#ff5252",
        color="white",
        padding=10,
        border_radius=4
    )):
        me.text(f"Error: {message}")
```

### Otimização de Performance

#### Polling Assíncrono
```python
async_poller(
    trigger_event=poll_messages,
    action=AsyncAction(
        value=app_state,
        duration_seconds=2  # Poll every 2 seconds
    )
)
```

#### Atualizações de Estado Eficientes
```python
# ✅ GOOD - Update only when needed
if len(new_messages) > len(app_state.messages):
    app_state.messages = new_messages

# ❌ BAD - Always update
app_state.messages = new_messages
```

### Padrões de Testes

#### Estrutura de Testes de Unidade
```python
def test_message_creation():
    """Test message creation with various inputs"""
    msg = Message(
        messageId="test-id",
        content="Test content"
    )
    assert msg.messageId == "test-id"
    assert msg.content == "Test content"
```

#### Padrão de Teste de Integração
```python
async def test_send_message_flow():
    """Test complete message send flow"""
    # Create conversation
    conv = await CreateConversation()
    
    # Send message
    msg = Message(
        contextId=conv.conversationId,
        content="Test"
    )
    response = await SendMessage(msg)
    
    # Verify response
    assert response.messageId is not None
```

### Dicas de Depuração

#### Logs de Depuração
```python
import logging

logger = logging.getLogger(__name__)

def debug_function():
    logger.debug(f"Entering function with state: {state}")
    # Function logic
    logger.debug(f"Exiting function with result: {result}")
```

#### Inspeção de Estado
```python
# Print entire state for debugging
print(f"Current state: {app_state.__dict__}")

# Check specific fields
print(f"Messages: {len(app_state.messages)}")
print(f"Conversations: {app_state.conversations}")
```

### Armadilhas Comuns

#### ❌ Evite Isto
1. Usar propriedades redundantes (`message.message_id_python`)
2. Criar classes de estado desnecessárias
3. Superengenharia em componentes simples
4. Ignorar padrões async/await
5. Não tratar erros adequadamente

#### ✅ Faça Isto em Vez Disso
1. Use acesso direto aos campos (`message.messageId`)
2. Use classes de estado existentes
3. Mantenha os componentes simples e focados
4. Use corretamente async/await
5. Implemente tratamento de erros abrangente

### Guia de Migração

#### Do Padrão Antigo para o Novo
```python
# OLD (removed)
message.message_id_python
message.messageid_python

# NEW (use this)
message.messageId

# If you need snake_case (rare)
message_dict = message.dict(by_alias=True)
message_dict['message_id']  # snake_case version
```

### Checklist de Deploy

- [ ] Variáveis de ambiente definidas
- [ ] Dependências instaladas
- [ ] Testes passando
- [ ] Configuração de porta correta
- [ ] API keys configuradas
- [ ] Logging configurado
- [ ] Tratamento de erros implementado

### Monitoramento de Performance

#### Métricas-Chave
- Tempo de resposta < 200ms
- Uso de memória < 500MB
- Uso de CPU < 50%
- Vazão de mensagens > 100/min

#### Comandos de Monitoramento
```bash
# Check memory usage
ps aux | grep python

# Monitor logs
tail -f logs/app.log

# Check port usage
lsof -i :8888
```