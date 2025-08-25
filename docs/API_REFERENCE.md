# API Reference

## 📚 Complete API Documentation

### Core Types

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

### State Management

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

### Service APIs

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

### Component APIs

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

### Event Handlers

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

### JSON-RPC Endpoints

#### Message Operations
```
POST /message/send
POST /message/list
POST /message/pending
```

#### Conversation Operations
```
POST /conversation/create
POST /conversation/list
```

#### Task Operations
```
POST /task/list
```

#### Agent Operations
```
POST /agent/register
POST /agent/list
```

#### Event Operations
```
POST /events/get
```

### Response Formats

#### Success Response
```json
{
    "jsonrpc": "2.0",
    "id": "unique-id",
    "result": {
        // Response data
    }
}
```

#### Error Response
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

### WebSocket Events (Future)

#### Connection
```javascript
ws://localhost:8888/ws
```

#### Message Format
```json
{
    "type": "message|typing|status",
    "data": {}
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `A2A_UI_PORT` | UI server port | 8888 |
| `MESOP_DEFAULT_PORT` | Mesop framework port | 8888 |
| `USE_VERTEX_AI` | Use Vertex AI instead | false |

### Error Codes

| Code | Description |
|------|-------------|
| -32700 | Parse error |
| -32600 | Invalid request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| -32000 | Server error |

### Rate Limits

- Messages: 100/minute per conversation
- Conversations: 10/minute per session
- File uploads: 10MB max size

### Authentication

Currently using API key authentication via environment variables. Future versions will support:
- OAuth 2.0
- JWT tokens
- Session-based auth