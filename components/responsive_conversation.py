"""Componente de conversa responsivo com layout adaptativo"""

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
from styles.responsive import (
    get_container_style,
    get_input_container_style,
    get_responsive_config,
    get_responsive_padding,
    GAP_MOBILE,
    GAP_DESKTOP,
)

from .responsive_chat_bubble import responsive_chat_bubble
from .form_render import form_sent, is_form, render_form
from .async_poller import async_poller, AsyncAction


@me.stateclass
class ResponsivePageState:
    """Estado local da página responsiva"""
    conversationid: str = ""
    message_content: str = ""
    is_mobile: bool = False
    is_tablet: bool = False


def on_blur(e: me.InputBlurEvent):
    """Handler para blur do input"""
    state = me.state(ResponsivePageState)
    state.message_content = e.value


async def send_message(message: str, message_id: str = ""):
    """Envia mensagem para o servidor"""
    state = me.state(ResponsivePageState)
    app_state = me.state(AppState)
    
    c = next(
        (
            x
            for x in await ListConversations()
            if x.conversationId == state.conversationid
        ),
        None,
    )
    
    if not c:
        print("Conversation id", state.conversationid, "not found")
        return
    
    request = Message(
        messageId=message_id,
        contextId=state.conversationid,
        role=Role.user,
        parts=[Part(root=TextPart(text=message))],
    )
    
    # Adiciona mensagem ao estado
    state_message = convert_message_to_state(request)
    if not app_state.messages:
        app_state.messages = []
    app_state.messages.append(state_message)
    
    # Atualiza conversa
    conversation = next(
        filter(
            lambda x: c and x.conversationId == c.conversationId,
            app_state.conversations,
        ),
        None,
    )
    if conversation:
        conversation.messageIds.append(state_message.messageId)
    
    await SendMessage(request)


async def send_message_enter(e: me.InputEnterEvent):
    """Handler para envio de mensagem com Enter"""
    yield
    state = me.state(ResponsivePageState)
    state.message_content = e.value
    app_state = me.state(AppState)
    messageid = str(uuid.uuid4())
    app_state.background_tasks[messageid] = ""
    yield
    await send_message(state.message_content, messageid)
    state.message_content = ""  # Limpar input após envio
    yield


async def send_message_button(e: me.ClickEvent):
    """Handler para botão de envio"""
    yield
    state = me.state(ResponsivePageState)
    app_state = me.state(AppState)
    messageid = str(uuid.uuid4())
    app_state.background_tasks[messageid] = ""
    await send_message(state.message_content, messageid)
    state.message_content = ""  # Limpar input após envio
    yield


async def refresh_messages():
    """Atualiza mensagens do servidor"""
    page_state = me.state(ResponsivePageState)
    app_state = me.state(AppState)
    
    if not page_state.conversationid:
        return
    
    try:
        messages = await ListMessages(page_state.conversationid)
        state_messages = []
        for msg in messages:
            state_msg = convert_message_to_state(msg)
            state_messages.append(state_msg)
        
        if len(state_messages) > len(app_state.messages):
            app_state.messages = state_messages
    except Exception as e:
        print(f"Erro ao atualizar mensagens: {e}")


async def poll_messages(e: me.WebEvent):
    """Handler para polling de mensagens"""
    await refresh_messages()
    yield


@me.component
def responsive_conversation():
    """Componente de conversa responsivo"""
    page_state = me.state(ResponsivePageState)
    app_state = me.state(AppState)
    
    # Verificar parâmetros de query
    if "conversationid" in me.query_params:
        page_state.conversationid = me.query_params["conversationid"]
        app_state.current_conversation_id = page_state.conversationid
    
    # Configuração responsiva
    config = get_responsive_config()
    is_mobile = page_state.is_mobile
    
    # Polling de mensagens
    async_poller(
        trigger_event=poll_messages,
        action=AsyncAction(
            value=app_state,
            duration_seconds=2
        )
    )
    
    # Container principal responsivo
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column",
            height="100vh",
            width="100%",
            overflow="hidden",
            position="relative",
        )
    ):
        # Container de mensagens com scroll
        with me.box(
            style=me.Style(
                flex="1",
                overflow_y="auto",
                overflow_x="hidden",
                padding=get_responsive_padding(is_mobile=is_mobile),
                padding_bottom=100,  # Espaço para o input fixo
                display="flex",
                flex_direction="column",
                gap=GAP_MOBILE if is_mobile else GAP_DESKTOP,
            )
        ):
            # Renderizar mensagens
            for message in app_state.messages:
                if is_form(message):
                    render_form(message, app_state)
                elif form_sent(message, app_state):
                    responsive_chat_bubble(
                        StateMessage(
                            messageId=message.messageId,
                            role=message.role,
                            content=[("Form submitted", "text/plain")],
                        ),
                        message.messageId,
                    )
                else:
                    responsive_chat_bubble(message, message.messageId)
        
        # Container de input fixo na parte inferior
        render_input_area(page_state, is_mobile)


def render_input_area(page_state: ResponsivePageState, is_mobile: bool):
    """Renderiza área de input responsiva"""
    config = get_responsive_config()
    
    with me.box(style=get_input_container_style(is_mobile=is_mobile)):
        # Input responsivo
        me.input(
            label="Como posso ajudar?",
            value=page_state.message_content,
            on_blur=on_blur,
            on_enter=send_message_enter,
            style=me.Style(
                flex="1",
                min_height=f"{config.input_height}px",
                font_size=config.font_size,
                border_radius=20,
                padding=me.Padding(
                    left=16,
                    right=16,
                    top=8,
                    bottom=8,
                ),
                border="1px solid #e0e0e0",
                background="white",
            ),
        )
        
        # Botão de envio responsivo
        with me.content_button(
            type="flat",
            on_click=send_message_button,
            style=me.Style(
                background="#d8407f",
                color="white",
                border_radius="50%",
                min_width=f"{config.input_height}px",
                min_height=f"{config.input_height}px",
                width=f"{config.input_height}px",
                height=f"{config.input_height}px",
                padding=me.Padding.all(0),
                display="flex",
                align_items="center",
                justify_content="center",
                cursor="pointer",
                transition="all 0.2s ease",
                hover_background="#c2366d",  # Tom mais escuro no hover
            ),
        ):
            me.icon(
                icon="send",
                style=me.Style(
                    color="white",
                    font_size=20 if is_mobile else 24,
                )
            )