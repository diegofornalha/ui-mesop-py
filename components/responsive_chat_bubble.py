"""Chat bubble responsivo que se adapta a diferentes tamanhos de tela"""

import mesop as me
from state.state import AppState, StateMessage
from styles.responsive import (
    get_chat_bubble_style,
    get_message_container_style,
    get_responsive_config,
    MOBILE_BREAKPOINT,
)


@me.component
def responsive_chat_bubble(message: StateMessage, key: str):
    """Chat bubble responsivo"""
    app_state = me.state(AppState)
    show_progress_bar = (
        message.messageId in app_state.background_tasks
        or message.messageId in app_state.message_aliases.values()
    )
    progress_text = ""
    if show_progress_bar:
        progress_text = app_state.background_tasks.get(message.messageId, "")
    
    if not message.content:
        print("No message content")
        return
    
    # TODO: Detectar viewport real
    is_mobile = False  # Por enquanto, usar False como padrão
    
    for pair in message.content:
        responsive_chat_box(
            content=pair[0],
            media_type=pair[1],
            role=message.role,
            key=key,
            progress_bar=show_progress_bar,
            progress_text=progress_text,
            is_mobile=is_mobile,
        )


def responsive_chat_box(
    content: str,
    media_type: str,
    role: str,
    key: str,
    progress_bar: bool,
    progress_text: str,
    is_mobile: bool = False,
):
    """Renderiza um chat box responsivo"""
    config = get_responsive_config()
    
    # Container da mensagem com alinhamento baseado no role
    with me.box(
        style=get_message_container_style(role, is_mobile),
        key=key,
    ):
        # Container interno com largura responsiva
        with me.box(
            style=me.Style(
                display="flex",
                flex_direction="column",
                gap=5,
                width=config.chat_bubble_width,
                max_width=config.chat_bubble_max_width,
            )
        ):
            if media_type == "image/png":
                render_image(content, is_mobile)
            else:
                render_text_message(content, role, is_mobile)
            
            if progress_bar:
                render_progress_bar(progress_text, role, is_mobile)


def render_image(content: str, is_mobile: bool):
    """Renderiza imagem responsiva"""
    if "/message/file" not in content:
        content = "data:image/png;base64," + content
    
    me.image(
        src=content,
        style=me.Style(
            width="100%" if is_mobile else "80%",
            max_width="400px" if not is_mobile else "100%",
            height="auto",
            object_fit="contain",
            border_radius=10,
            margin=me.Margin(top=5, bottom=5),
        ),
    )


def render_text_message(content: str, role: str, is_mobile: bool):
    """Renderiza mensagem de texto responsiva"""
    me.markdown(
        content,
        style=get_chat_bubble_style(role, is_mobile),
    )


def render_progress_bar(progress_text: str, role: str, is_mobile: bool):
    """Renderiza barra de progresso responsiva"""
    config = get_responsive_config()
    
    # Estilo para progress bar
    progress_style = me.Style(
        font_family="Google Sans",
        font_size=config.font_size - 2,  # Fonte um pouco menor
        box_shadow=(
            "0 1px 2px 0 rgba(60, 64, 67, 0.3), "
            "0 1px 3px 1px rgba(60, 64, 67, 0.15)"
        ),
        padding=me.Padding(
            top=config.padding,
            left=config.padding,
            right=config.padding,
            bottom=config.padding,
        ),
        margin=me.Margin(top=5, bottom=5),
        background="#f0f0f0" if role == "user" else "#e3f2fd",
        border_radius=10,
        max_width=config.chat_bubble_max_width,
    )
    
    with me.box(style=progress_style):
        if not progress_text:
            progress_text = "Pensando..."
        
        me.text(
            progress_text,
            style=me.Style(
                margin=me.Margin(bottom=8),
                color="#666666",
            )
        )
        me.progress_bar(color="accent")
