# Referência de API

## 📚 Documentação Completa da API

### Tipos Centrais

#### Message
```python
class Message(BaseModel):
    messageId: str = Field(default="", alias="message_id")
    content: str = Field(default="")
    author: str = Field(default="")
    timestamp: float = Field(default=0.0)
    contextId: Optional[str] = Field(default=None, alias="context_id")
    taskId: Optional[str] = Field(default=None, alias="task_id")
    conversationId: Optional[str] = Field(default=None, alias="conversation_id")
    parts: List[Any] = Field(default_factory=list)
    role: Optional[Any] = Field(default="user")
    metadata: Optional[Dict[str, Any]] = Field(default=None)
```

#### Conversation
```python
class ConversationFixed(BaseModel):
    conversationId: str = Field(alias="conversationid")
    isActive: bool = Field(alias="isactive")
    name: str = ''
    task_ids: List[str] = Field(default_factory=list)
    messages: List[Any] = Field(default_factory=list)
```

#### Task
```python
class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    status: str = "pending"
```

### Gerenciamento de Estado

#### AppState
```python
@me.stateclass
class AppState:
    sidenav_open: bool = False
    current_conversation_id: str = ''
    conversations: list[StateConversation]
    messages: list[StateMessage]
    task_list: list[SessionTask]
    background_tasks: dict[str, str]
    message_aliases: dict[str, str]
    completed_forms: dict[str, dict[str, Any] | None]
    form_responses: dict[str, str]
    polling_interval: int = 1
    api_key: str = ''
    uses_vertex_ai: bool = False
    api_key_dialog_open: bool = False
```

### APIs de Serviço

#### ConversationClient

##### Create Conversation
```python
async def CreateConversation() -> Conversation:
    """Create a new conversation"""
    # Returns: Conversation object with new ID
```

##### List Conversations
```python
async def ListConversations() -> List[Conversation]:
    """List all active conversations"""
    # Returns: List of Conversation objects
```

##### Send Message
```python
async def SendMessage(message: Message) -> Message:
    """Send a message to the agent"""
    # Parameters:
    #   message: Message object to send
    # Returns: Message object with server response
```

##### List Messages
```python
async def ListMessages(conversation_id: str) -> List[Message]:
    """List all messages in a conversation"""
    # Parameters:
    #   conversation_id: ID of the conversation
    # Returns: List of Message objects
```

### APIs de Componentes

#### Chat Bubble
```python
@me.component
def chat_bubble(message: StateMessage, key: str):
    """Render a chat message bubble"""
    # Parameters:
    #   message: StateMessage to display
    #   key: Unique key for the component
```

#### Conversation Component
```python
@me.component
def conversation():
    """Main conversation interface component"""
    # Handles:
    #   - Message display
    #   - Message input
    #   - Real-time polling
```

#### Form Renderer
```python
def render_form(message: StateMessage, app_state: AppState):
    """Render a form using native Mesop components"""
    # Parameters:
    #   message: StateMessage containing form data
    #   app_state: Current application state
```

### Manipuladores de Eventos

#### Message Events
```python
async def send_message(message: str, message_id: str = ''):
    """Send a message to the agent"""
    # Parameters:
    #   message: Text content to send
    #   message_id: Optional message ID

async def send_message_enter(e: me.InputEnterEvent):
    """Handle Enter key press in message input"""

async def send_message_button(e: me.ClickEvent):
    """Handle Send button click"""
```

#### Navigation Events
```python
def toggle_sidenav(e: me.ClickEvent):
    """Toggle the side navigation panel"""

def navigate_to_conversation(conversation_id: str):
    """Navigate to a specific conversation"""
```

### Endpoints JSON-RPC

#### Operações de Mensagens
```
POST /message/send
POST /message/list
POST /message/pending
```

#### Operações de Conversa
```
POST /conversation/create
POST /conversation/list
```

#### Operações de Tarefa
```
POST /task/list
```

#### Operações de Agente
```
POST /agent/register
POST /agent/list
```

#### Operações de Evento
```
POST /events/get
```

### Formatos de Resposta

#### Resposta de Sucesso
```json
{
    "jsonrpc": "2.0",
    "id": "unique-id",
    "result": {
        // Response data
    }
}
```

#### Resposta de Erro
```json
{
    "jsonrpc": "2.0",
    "id": "unique-id",
    "error": {
        "code": -32000,
        "message": "Error description",
        "data": {}
    }
}
```

### Eventos WebSocket (Futuro)

#### Conexão
```javascript
ws://localhost:8888/ws
```

#### Formato de Mensagem
```json
{
    "type": "message|typing|status",
    "data": {}
}
```

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `GOOGLE_API_KEY` | Chave da API do Google AI | Obrigatória |
| `A2A_UI_PORT` | Porta do servidor da UI | 8888 |
| `MESOP_DEFAULT_PORT` | Porta do framework Mesop | 8888 |
| `USE_VERTEX_AI` | Usar Vertex AI | false |

### Códigos de Erro

| Código | Descrição |
|--------|-----------|
| -32700 | Erro de parsing |
| -32600 | Requisição inválida |
| -32601 | Método não encontrado |
| -32602 | Parâmetros inválidos |
| -32603 | Erro interno |
| -32000 | Erro no servidor |

### Limites de Taxa

- Mensagens: 100/minuto por conversa
- Conversas: 10/minuto por sessão
- Upload de arquivos: tamanho máximo 10MB

### Autenticação

Atualmente usando autenticação por API key via variáveis de ambiente. Versões futuras terão suporte a:
- OAuth 2.0
- Tokens JWT
- Autenticação baseada em sessão