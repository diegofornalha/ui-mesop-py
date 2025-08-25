# Implementation Guide

## 🚀 Implementation Details and Patterns

### Coding Standards

#### Python Style Guide
- Follow PEP 8 conventions
- Use type hints for all functions
- Maximum line length: 100 characters
- Use descriptive variable names

#### Naming Conventions
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

### Type System Implementation

#### Single Source of Truth
All types are defined in `service/types.py`:

```python
# ✅ CORRECT - Direct field access
message.messageId
conversation.conversationId

# ❌ WRONG - Redundant properties (removed)
message.message_id_python  # Don't use
message.messageid_python   # Don't use
```

#### Field Aliases
Use Pydantic aliases for compatibility:

```python
class Message(BaseModel):
    messageId: str = Field(default="", alias="message_id")
    # Accepts both: messageId and message_id
```

### Component Development

#### Creating a New Component
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

#### Component Best Practices
1. Use native Mesop components
2. Keep components under 100 lines
3. Separate logic from presentation
4. Use state management properly

### State Management Patterns

#### Accessing State
```python
def my_handler(e: me.ClickEvent):
    state = me.state(AppState)
    # Read state
    current_id = state.current_conversation_id
    # Update state
    state.current_conversation_id = "new-id"
```

#### Async Operations
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

### Message Handling

#### Sending Messages
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

#### Processing Responses
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

### Form Rendering (Simplified)

#### Native Mesop Forms
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

### Error Handling

#### Standard Error Pattern
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

#### User-Friendly Errors
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

### Performance Optimization

#### Async Polling
```python
async_poller(
    trigger_event=poll_messages,
    action=AsyncAction(
        value=app_state,
        duration_seconds=2  # Poll every 2 seconds
    )
)
```

#### Efficient State Updates
```python
# ✅ GOOD - Update only when needed
if len(new_messages) > len(app_state.messages):
    app_state.messages = new_messages

# ❌ BAD - Always update
app_state.messages = new_messages
```

### Testing Patterns

#### Unit Test Structure
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

#### Integration Test Pattern
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

### Debugging Tips

#### Debug Logging
```python
import logging

logger = logging.getLogger(__name__)

def debug_function():
    logger.debug(f"Entering function with state: {state}")
    # Function logic
    logger.debug(f"Exiting function with result: {result}")
```

#### State Inspection
```python
# Print entire state for debugging
print(f"Current state: {app_state.__dict__}")

# Check specific fields
print(f"Messages: {len(app_state.messages)}")
print(f"Conversations: {app_state.conversations}")
```

### Common Pitfalls

#### ❌ Avoid These
1. Using redundant properties (`message.message_id_python`)
2. Creating unnecessary state classes
3. Over-engineering simple components
4. Ignoring async/await patterns
5. Not handling errors properly

#### ✅ Do These Instead
1. Use direct field access (`message.messageId`)
2. Use existing state classes
3. Keep components simple and focused
4. Properly use async/await
5. Implement comprehensive error handling

### Migration Guide

#### From Old Pattern to New
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

### Deployment Checklist

- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Tests passing
- [ ] Port configuration correct
- [ ] API keys configured
- [ ] Logging configured
- [ ] Error handling in place

### Performance Monitoring

#### Key Metrics
- Response time < 200ms
- Memory usage < 500MB
- CPU usage < 50%
- Message throughput > 100/min

#### Monitoring Commands
```bash
# Check memory usage
ps aux | grep python

# Monitor logs
tail -f logs/app.log

# Check port usage
lsof -i :8888
```