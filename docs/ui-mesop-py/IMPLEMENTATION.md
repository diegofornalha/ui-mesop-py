# Guia de Implementação

## 🚀 Detalhes de Implementação e Padrões

### Padrões de Codificação

#### Guia de Estilo Python
- Seguir convenções PEP 8
- Usar type hints para todas as funções
- Comprimento máximo de linha: 100 caracteres
- Usar nomes de variáveis descritivos

#### Convenções de Nomenclatura
```python
# Classes: PascalCase
class StateMessage:
    pass

# Funções: snake_case
def send_message():
    pass

# Constantes: UPPER_SNAKE_CASE
DEFAULT_PORT = 8888

# Métodos privados: underscore inicial
def _internal_helper():
    pass
```

### Implementação do Sistema de Tipos

#### Fonte Única de Verdade
Todos os tipos são definidos em `service/types.py`:

```python
# ✅ CORRETO - Acesso direto aos campos
message.messageId
conversation.conversationId

# ❌ ERRADO - Propriedades redundantes (removidas)
message.message_id_python  # Não use
message.messageid_python   # Não use
```

#### Aliases de Campos
Use aliases Pydantic para compatibilidade:

```python
class Message(BaseModel):
    messageId: str = Field(default="", alias="message_id")
    # Aceita ambos: messageId e message_id
```

### Desenvolvimento de Componentes

#### Criando um Novo Componente
```python
import mesop as me
from state.state import AppState

@me.component
def my_component():
    """Descrição do componente"""
    state = me.state(AppState)
    
    with me.box(style=me.Style(
        padding=20,
        background="#f0f0f0",
        border_radius=8
    )):
        me.text("Conteúdo do componente")
```

#### Melhores Práticas de Componentes
1. Use componentes nativos do Mesop
2. Mantenha componentes com menos de 100 linhas
3. Separe lógica da apresentação
4. Use gerenciamento de estado adequadamente

### Padrões de Gerenciamento de Estado

#### Acessando Estado
```python
def my_handler(e: me.ClickEvent):
    state = me.state(AppState)
    # Ler estado
    current_id = state.current_conversation_id
    # Atualizar estado
    state.current_conversation_id = "new-id"
```

#### Operações Assíncronas
```python
async def async_handler(e: me.WebEvent):
    yield  # Yield inicial para atualização da UI
    
    # Executar operação assíncrona
    result = await some_async_function()
    
    # Atualizar estado
    state = me.state(AppState)
    state.data = result
    
    yield  # Yield final para atualizar UI
```

### Manipulação de Mensagens

#### Enviando Mensagens
```python
async def send_message(message: str, message_id: str = ''):
    state = me.state(PageState)
    app_state = me.state(AppState)
    
    # Encontrar conversa
    conversation = next(
        (x for x in await ListConversations() 
         if x.conversationId == state.conversationid),
        None
    )
    
    # Criar mensagem
    request = Message(
        messageId=message_id or str(uuid.uuid4()),
        contextId=state.conversationid,
        role=Role.user,
        parts=[Part(root=TextPart(text=message))]
    )
    
    # Enviar mensagem
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
        print(f"Erro ao atualizar mensagens: {e}")
```

### Renderização de Formulários (Simplificada)

#### Formulários Nativos do Mesop
```python
def render_form(message: StateMessage, app_state: AppState):
    """Renderizar formulário usando componentes nativos do Mesop"""
    if message.messageId in app_state.completed_forms:
        # Mostrar formulário completado
        with me.box(style=me.Style(
            padding=20, 
            background="#f0f0f0", 
            border_radius=8
        )):
            me.text("Formulário enviado", type="headline-6")
            data = app_state.completed_forms[message.messageId]
            if data:
                for key, value in data.items():
                    me.text(f"{key}: {value}")
    else:
        # Renderizar formulário ativo
        with me.box(style=me.Style(padding=20)):
            me.text("Formulário", type="headline-6")
            # Adicionar campos do formulário conforme necessário
```

### Tratamento de Erros

#### Padrão de Erro Padrão
```python
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Erro específico: {e}")
    # Tratar erro específico
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
    # Tratar erro geral
finally:
    # Limpeza se necessário
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
        me.text(f"Erro: {message}")
```

### Otimização de Performance

#### Polling Assíncrono
```python
async_poller(
    trigger_event=poll_messages,
    action=AsyncAction(
        value=app_state,
        duration_seconds=2  # Poll a cada 2 segundos
    )
)
```

#### Atualizações Eficientes de Estado
```python
# ✅ BOM - Atualizar apenas quando necessário
if len(new_messages) > len(app_state.messages):
    app_state.messages = new_messages

# ❌ RUIM - Sempre atualizar
app_state.messages = new_messages
```

### Padrões de Testes

#### Estrutura de Teste Unitário
```python
def test_message_creation():
    """Testar criação de mensagem com várias entradas"""
    msg = Message(
        messageId="test-id",
        content="Conteúdo de teste"
    )
    assert msg.messageId == "test-id"
    assert msg.content == "Conteúdo de teste"
```

#### Padrão de Teste de Integração
```python
async def test_send_message_flow():
    """Testar fluxo completo de envio de mensagem"""
    # Criar conversa
    conv = await CreateConversation()
    
    # Enviar mensagem
    msg = Message(
        contextId=conv.conversationId,
        content="Teste"
    )
    response = await SendMessage(msg)
    
    # Verificar resposta
    assert response.messageId is not None
```

### Dicas de Debug

#### Logging de Debug
```python
import logging

logger = logging.getLogger(__name__)

def debug_function():
    logger.debug(f"Entrando na função com estado: {state}")
    # Lógica da função
    logger.debug(f"Saindo da função com resultado: {result}")
```

#### Inspeção de Estado
```python
# Imprimir estado completo para debug
print(f"Estado atual: {app_state.__dict__}")

# Verificar campos específicos
print(f"Mensagens: {len(app_state.messages)}")
print(f"Conversas: {app_state.conversations}")
```

### Armadilhas Comuns

#### ❌ Evite Estes
1. Usar propriedades redundantes (`message.message_id_python`)
2. Criar classes de estado desnecessárias
3. Super-engenhar componentes simples
4. Ignorar padrões async/await
5. Não tratar erros adequadamente

#### ✅ Faça Estes Em Vez Disso
1. Use acesso direto aos campos (`message.messageId`)
2. Use classes de estado existentes
3. Mantenha componentes simples e focados
4. Use async/await adequadamente
5. Implemente tratamento abrangente de erros

### Guia de Migração

#### Do Padrão Antigo para o Novo
```python
# ANTIGO (removido)
message.message_id_python
message.messageid_python

# NOVO (use este)
message.messageId

# Se precisar de snake_case (raro)
message_dict = message.dict(by_alias=True)
message_dict['message_id']  # versão snake_case
```

### Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Dependências instaladas
- [ ] Testes passando
- [ ] Configuração de porta correta
- [ ] Chaves de API configuradas
- [ ] Logging configurado
- [ ] Tratamento de erros implementado

### Monitoramento de Performance

#### Métricas Principais
- Tempo de resposta < 200ms
- Uso de memória < 500MB
- Uso de CPU < 50%
- Taxa de mensagens > 100/min

#### Comandos de Monitoramento
```bash
# Verificar uso de memória
ps aux | grep python

# Monitorar logs
tail -f logs/app.log

# Verificar uso de porta
lsof -i :8888
```