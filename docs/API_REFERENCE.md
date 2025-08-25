# Referência da API

## 📚 Documentação Completa da API

### Tipos Principais

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

### APIs de Serviços

#### ConversationClient

##### Criar Conversa
```python
async def CreateConversation() -> Conversation:
    """Criar uma nova conversa"""
    # Retorna: Objeto Conversation com novo ID
```

##### Listar Conversas
```python
async def ListConversations() -> List[Conversation]:
    """Listar todas as conversas ativas"""
    # Retorna: Lista de objetos Conversation
```

##### Enviar Mensagem
```python
async def SendMessage(message: Message) -> Message:
    """Enviar uma mensagem para o agente"""
    # Parâmetros:
    #   message: Objeto Message para enviar
    # Retorna: Objeto Message com resposta do servidor
```

##### Listar Mensagens
```python
async def ListMessages(conversation_id: str) -> List[Message]:
    """Listar todas as mensagens em uma conversa"""
    # Parâmetros:
    #   conversation_id: ID da conversa
    # Retorna: Lista de objetos Message
```

### APIs de Componentes

#### Chat Bubble
```python
@me.component
def chat_bubble(message: StateMessage, key: str):
    """Renderizar uma bolha de mensagem de chat"""
    # Parâmetros:
    #   message: StateMessage para exibir
    #   key: Chave única para o componente
```

#### Componente de Conversa
```python
@me.component
def conversation():
    """Componente principal da interface de conversa"""
    # Gerencia:
    #   - Exibição de mensagens
    #   - Entrada de mensagens
    #   - Polling em tempo real
```

#### Renderizador de Formulários
```python
def render_form(message: StateMessage, app_state: AppState):
    """Renderizar um formulário usando componentes nativos do Mesop"""
    # Parâmetros:
    #   message: StateMessage contendo dados do formulário
    #   app_state: Estado atual da aplicação
```

### Manipuladores de Eventos

#### Eventos de Mensagem
```python
async def send_message(message: str, message_id: str = ''):
    """Enviar uma mensagem para o agente"""
    # Parâmetros:
    #   message: Conteúdo de texto para enviar
    #   message_id: ID da mensagem opcional

async def send_message_enter(e: me.InputEnterEvent):
    """Manipular pressionamento da tecla Enter na entrada de mensagem"""

async def send_message_button(e: me.ClickEvent):
    """Manipular clique no botão Enviar"""
```

#### Eventos de Navegação
```python
def toggle_sidenav(e: me.ClickEvent):
    """Alternar o painel de navegação lateral"""

def navigate_to_conversation(conversation_id: str):
    """Navegar para uma conversa específica"""
```

### Endpoints JSON-RPC

#### Operações de Mensagem
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
        // Dados da resposta
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
        "message": "Descrição do erro",
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
| `A2A_UI_PORT` | Porta do servidor UI | 8888 |
| `MESOP_DEFAULT_PORT` | Porta padrão do framework Mesop | 8888 |
| `USE_VERTEX_AI` | Usar Vertex AI em vez de | false |

### Códigos de Erro

| Código | Descrição |
|--------|-----------|
| -32700 | Erro de parse |
| -32600 | Requisição inválida |
| -32601 | Método não encontrado |
| -32602 | Parâmetros inválidos |
| -32603 | Erro interno |
| -32000 | Erro do servidor |

### Limites de Taxa

- Mensagens: 100/minuto por conversa
- Conversas: 10/minuto por sessão
- Uploads de arquivo: 10MB tamanho máximo

### Autenticação

Atualmente usando autenticação por chave de API via variáveis de ambiente. Versões futuras suportarão:
- OAuth 2.0
- Tokens JWT
- Autenticação baseada em sessão