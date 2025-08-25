import uuid
import asyncio

import mesop as me

from a2a.types import Message, Part, Role, TextPart
from state.host_agent_service import (
    ListConversations,
    SendMessage,
    ListMessages,
    convert_message_to_state,
)
from state.state import AppState, StateMessage

from .chat_bubble import chat_bubble
from .form_render import form_sent, is_form, render_form
from .async_poller import async_poller, AsyncAction


@me.stateclass
class PageState:
    """Local Page State"""

    conversationid: str = ''
    message_content: str = ''


def on_blur(e: me.InputBlurEvent):
    """Input handler"""
    state = me.state(PageState)
    state.message_content = e.value


async def send_message(message: str, messageid: str = ''):
    state = me.state(PageState)
    app_state = me.state(AppState)
    c = next(
        (
            x
            for x in await ListConversations()
            if x.conversationid == state.conversationid
        ),
        None,
    )
    if not c:
        print('Conversation id ', state.conversationid, ' not found')
    request = Message(
        messageid=messageid,
        contextid=state.conversationid,
        role=Role.user,
        parts=[Part(root=TextPart(text=message))],
    )
    # Add message to state until refresh replaces it.
    state_message = convert_message_to_state(request)
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(state_message)
    conversation = next(
        filter(
            lambda x: c and x.conversationid == c.conversationid,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.messageids.append(state_message.messageid)
    await SendMessage(request)


async def send_message_enter(e: me.InputEnterEvent):  # pylint: disable=unused-argument
    """Send message handler"""
    yield
    state = me.state(PageState)
    state.message_content = e.value
    app_state = me.state(AppState)
    messageid = str(uuid.uuid4())
    app_state.background_tasks[messageid] = ''
    yield
    await send_message(state.message_content, messageid)
    yield


async def send_message_button(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Send message button handler"""
    yield
    state = me.state(PageState)
    app_state = me.state(AppState)
    messageid = str(uuid.uuid4())
    app_state.background_tasks[messageid] = ''
    await send_message(state.message_content, messageid)
    yield


async def refresh_messages():
    """Refresh messages from server"""
    page_state = me.state(PageState)
    app_state = me.state(AppState)
    
    if not page_state.conversationid:
        return
    
    try:
        # Buscar mensagens do servidor
        messages = await ListMessages(page_state.conversationid)
        
        # Converter mensagens para o formato do estado
        state_messages = []
        for msg in messages:
            state_msg = convert_message_to_state(msg)
            state_messages.append(state_msg)
        
        # Atualizar o estado apenas se houver novas mensagens
        if len(state_messages) > len(app_state.messages):
            app_state.messages = state_messages
            
    except Exception as e:
        print(f"Erro ao atualizar mensagens: {e}")


async def poll_messages(e: me.WebEvent):
    """Handler para polling de mensagens"""
    await refresh_messages()
    yield


@me.component
def conversation():
    """Conversation component"""
    page_state = me.state(PageState)
    app_state = me.state(AppState)
    if 'conversationid' in me.query_params:
        page_state.conversationid = me.query_params['conversationid']
        app_state.current_conversation_id = page_state.conversationid
    
    # Adicionar async poller para atualizar mensagens
    async_poller(
        trigger_event=poll_messages,
        action=AsyncAction(
            value=app_state,
            duration_seconds=2  # Poll a cada 2 segundos
        )
    )
    
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            flex_direction='column',
        )
    ):
        for message in app_state.messages:
            if is_form(message):
                render_form(message, app_state)
            elif form_sent(message, app_state):
                chat_bubble(
                    StateMessage(
                        messageid=message.messageid,
                        role=message.role,
                        content=[('Form submitted', 'text/plain')],
                    ),
                    message.messageid,
                )
            else:
                chat_bubble(message, message.messageid)

        with me.box(
            style=me.Style(
                display='flex',
                flex_direction='row',
                gap=5,
                align_items='center',
                min_width=500,
                width='100%',
            )
        ):
            me.input(
                label='How can I help you?',
                on_blur=on_blur,
                on_enter=send_message_enter,
                style=me.Style(min_width='80vw'),
            )
            with me.content_button(
                type='flat',
                on_click=send_message_button,
            ):
                me.icon(icon='send')
