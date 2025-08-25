"""Chat responsivo seguindo estritamente as práticas do Mesop"""

import mesop as me
from typing import List, Optional
import uuid

from state.state import AppState, StateMessage
from components.mesop_responsive_utils import (
    responsive_container,
    responsive_text_size,
    responsive_padding,
    RESPONSIVE_ROOT_STYLE,
    RESPONSIVE_MAIN_CONTENT_STYLE,
    RESPONSIVE_CHAT_INPUT_STYLE,
    RESPONSIVE_CHAT_BUBBLE_CONTAINER,
    RESPONSIVE_INPUT_WRAPPER_STYLE,
)


@me.component
def mesop_chat_bubble(message: StateMessage, is_user: bool = False):
    """
    Chat bubble responsivo seguindo o padrão Mesop.
    Usa width responsiva com min() CSS.
    """
    # Container da mensagem com alinhamento baseado no remetente
    with me.box(
        style=me.Style(
            **RESPONSIVE_CHAT_BUBBLE_CONTAINER.to_dict(),
            justify_content="flex-end" if is_user else "flex-start",
        )
    ):
        # Bubble com largura responsiva
        bubble_style = me.Style(
            background="#d8407f" if is_user else "#ffe0ec",
            color="white" if is_user else "#333333",
            padding=me.Padding.all(16),
            border_radius=16,
            max_width="min(600px, 80%)",  # Responsivo usando min()
            font_size=responsive_text_size()["medium"],
            font_weight="500",
            box_shadow="0 1px 2px rgba(0, 0, 0, 0.1)",

        )
        
        with me.box(style=bubble_style):
            if message.content:
                for content, content_type in message.content:
                    if content_type == "text/plain":
                        me.markdown(content)
                    elif content_type == "image/png":
                        render_responsive_image(content)


def render_responsive_image(content: str):
    """Renderiza imagem responsiva"""
    if "/message/file" not in content:
        content = f"data:image/png;base64,{content}"
    
    me.image(
        src=content,
        style=me.Style(
            width="100%",
            max_width="min(400px, 100%)",  # Responsivo
            height="auto",
            border_radius=8,
            margin=me.Margin.symmetric(vertical=8),
        ),
    )


@me.component
def mesop_chat_input(
    value: str,
    on_change: Optional[callable] = None,
    on_submit: Optional[callable] = None,
):
    """Input de chat responsivo seguindo o padrão Mesop"""
    with me.box(style=RESPONSIVE_CHAT_INPUT_STYLE):
        with me.box(style=RESPONSIVE_INPUT_WRAPPER_STYLE):
            # Input responsivo
            me.input(
                label="Digite sua mensagem...",
                value=value,
                on_blur=on_change,
                on_enter=on_submit,
                style=me.Style(
                    flex_grow=1,
                    font_size=responsive_text_size()["medium"],
                ),
            )
            
            # Botão de envio
            with me.content_button(
                type="flat",
                on_click=on_submit,
                style=me.Style(
                    background="#d8407f",
                    color="white",
                    border_radius="50%",
                    min_width=48,
                    min_height=48,
                    width=48,
                    height=48,
                    padding=me.Padding.all(0),
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
            ):
                me.icon(icon="send", style=me.Style(color="white", font_size=24))


@me.component
def mesop_responsive_chat():
    """Componente de chat totalmente responsivo seguindo Mesop"""
    app_state = me.state(AppState)
    
    with me.box(style=RESPONSIVE_ROOT_STYLE):
        # Container principal com scroll
        with me.box(
            style=me.Style(
                flex_grow=1,
                overflow_y="auto",
                padding=responsive_padding()["medium"],
                padding_bottom=100,  # Espaço para input fixo
            )
        ):
            # Container de conteúdo centralizado e responsivo
            with me.box(style=responsive_container(max_width="min(900px, 100%)")):
                # Renderizar mensagens
                for message in app_state.messages:
                    is_user = message.role == "user"
                    mesop_chat_bubble(message, is_user=is_user)
        
        # Input fixo no fundo
        mesop_chat_input(
            value="",
            on_submit=send_message,
        )


def send_message(e: me.ClickEvent):
    """Handler para envio de mensagem"""
    # Implementação simplificada
    app_state = me.state(AppState)
    # Lógica de envio aqui


@me.component
def mesop_responsive_sidebar():
    """
    Sidebar responsiva usando apenas recursos do Mesop.
    Em telas pequenas, usa um overlay.
    """
    app_state = me.state(AppState)
    
    # Estilo da sidebar com largura responsiva
    sidebar_style = me.Style(
        position="fixed",
        left=0,
        top=0,
        height="100vh",
        width="min(280px, 80vw)",  # Máximo 280px ou 80% da viewport
        background="white",
        border="0 1px 0 0 solid #e0e0e0",
        overflow_y="auto",
        z_index=1000,
        transform="translateX(-100%)" if not app_state.sidenav_open else "translateX(0)",
        transition="transform 0.3s ease",
    )
    
    with me.box(style=sidebar_style):
        # Header da sidebar
        with me.box(
            style=me.Style(
                padding=me.Padding.all(16),
                border_bottom="1px solid #e0e0e0",
                display="flex",
                justify_content="space-between",
                align_items="center",
            )
        ):
            me.text("Conversas", style=me.Style(font_size=18, font_weight="bold"))
            
            # Botão fechar
            with me.content_button(
                type="icon",
                on_click=toggle_sidebar,
                style=me.Style(padding=me.Padding.all(4)),
            ):
                me.icon(icon="close")
        
        # Lista de conversas
        render_conversations_list()
    
    # Overlay quando sidebar está aberta
    if app_state.sidenav_open:
        with me.box(
            style=me.Style(
                position="fixed",
                top=0,
                left=0,
                right=0,
                bottom=0,
                background="rgba(0, 0, 0, 0.5)",
                z_index=999,
            ),
            on_click=toggle_sidebar,
        ):
            pass


def toggle_sidebar(e: me.ClickEvent):
    """Toggle da sidebar"""
    app_state = me.state(AppState)
    app_state.sidenav_open = not app_state.sidenav_open


def render_conversations_list():
    """Renderiza lista de conversas"""
    app_state = me.state(AppState)
    
    with me.box(style=me.Style(padding=me.Padding.all(16))):
        # Botão nova conversa
        with me.content_button(
            type="flat",
            on_click=lambda e: me.navigate("/"),
            style=me.Style(
                width="100%",
                padding=me.Padding.all(12),
                background="#d8407f",
                color="white",
                border_radius=8,
                margin_bottom=16,
                display="flex",
                align_items="center",
                gap=8,
            ),
        ):
            me.icon(icon="add", style=me.Style(color="white"))
            me.text("Nova Conversa")
        
        # Lista de conversas
        for conv in app_state.conversations:
            with me.box(
                style=me.Style(
                    padding=me.Padding.all(12),
                    border_radius=8,
                    cursor="pointer",
                    margin_bottom=8,
                    background="#f5f5f5" if conv.conversationId == app_state.current_conversation_id else "transparent",

                ),
                on_click=lambda e, cid=conv.conversationId: me.navigate(f"/conversation?conversationid={cid}"),
            ):
                me.text(
                    conv.title or f"Conversa {conv.conversationId[:8]}",
                    style=me.Style(font_weight="500"),
                )