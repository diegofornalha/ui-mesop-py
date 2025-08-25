"""Sidebar responsiva com suporte para mobile drawer"""

import mesop as me
from typing import Callable

from state.state import AppState
from styles.colors import TEXT_PRIMARY, TEXT_SECONDARY, BACKGROUND
from styles.responsive import (
    SIDENAV_MOBILE_WIDTH,
    SIDENAV_TABLET_WIDTH,
    SIDENAV_DESKTOP_WIDTH,
    get_responsive_padding,
)


def toggle_sidenav(e: me.ClickEvent):
    """Toggle da sidebar"""
    app_state = me.state(AppState)
    app_state.sidenav_open = not app_state.sidenav_open


def navigate_to_conversation(e: me.ClickEvent):
    """Navega para uma conversa"""
    app_state = me.state(AppState)
    conversation_id = e.key
    app_state.current_conversation_id = conversation_id
    me.navigate(f"/conversation?conversationid={conversation_id}")


@me.component
def responsive_sidenav(
    is_mobile: bool = False,
    is_tablet: bool = False,
    show_mobile_menu: bool = False,
    on_close: Callable = None,
):
    """Sidebar responsiva"""
    app_state = me.state(AppState)
    
    # Determinar largura da sidebar
    if is_mobile:
        sidebar_width = 280  # Largura fixa para drawer mobile
        is_open = show_mobile_menu
    elif is_tablet:
        sidebar_width = SIDENAV_TABLET_WIDTH
        is_open = False  # Sempre colapsada em tablet
    else:
        sidebar_width = SIDENAV_DESKTOP_WIDTH if app_state.sidenav_open else SIDENAV_TABLET_WIDTH
        is_open = app_state.sidenav_open
    
    # Estilo base da sidebar
    sidebar_style = me.Style(
        position="fixed" if is_mobile else "relative",
        left=0 if not is_mobile else (-sidebar_width if not show_mobile_menu else 0),
        top=0,
        height="100vh",
        width=sidebar_width,
        background="white",
        border_right="1px solid #e0e0e0",
        display="flex",
        flex_direction="column",
        transition="left 0.3s ease, width 0.3s ease",
        z_index=999 if is_mobile else 1,
        overflow_y="auto",
        overflow_x="hidden",
    )
    
    with me.box(style=sidebar_style):
        # Header da sidebar
        render_sidebar_header(is_mobile, is_tablet, is_open, on_close)
        
        # Lista de conversas
        render_conversations_list(app_state, is_mobile, is_tablet, is_open)
        
        # Footer com toggle (apenas desktop)
        if not is_mobile and not is_tablet:
            render_sidebar_footer(is_open)


def render_sidebar_header(is_mobile: bool, is_tablet: bool, is_open: bool, on_close: Callable):
    """Renderiza header da sidebar"""
    with me.box(
        style=me.Style(
            display="flex",
            align_items="center",
            justify_content="space-between",
            padding=me.Padding(
                top=16,
                bottom=16,
                left=16 if is_open or is_mobile else 12,
                right=16 if is_open or is_mobile else 12,
            ),
            border_bottom="1px solid #e0e0e0",
            min_height=60,
        )
    ):
        # Logo/Título
        if is_open or is_mobile:
            me.text(
                "Conversas",
                style=me.Style(
                    font_size=18,
                    font_weight="bold",
                    color=TEXT_PRIMARY,
                )
            )
        else:
            # Ícone quando colapsada
            me.icon(
                icon="chat",
                style=me.Style(
                    color=TEXT_PRIMARY,
                    font_size=24,
                )
            )
        
        # Botão de fechar (apenas mobile)
        if is_mobile and on_close:
            with me.content_button(
                type="icon",
                on_click=on_close,
                style=me.Style(
                    padding=me.Padding.all(4),
                )
            ):
                me.icon(icon="close")


def render_conversations_list(app_state: AppState, is_mobile: bool, is_tablet: bool, is_open: bool):
    """Renderiza lista de conversas"""
    with me.box(
        style=me.Style(
            flex="1",
            overflow_y="auto",
            padding=get_responsive_padding(is_mobile=is_mobile),
        )
    ):
        # Botão de nova conversa
        with me.content_button(
            type="flat",
            on_click=lambda e: me.navigate("/"),
            style=me.Style(
                width="100%",
                margin_bottom=16,
                padding=me.Padding(
                    top=12,
                    bottom=12,
                    left=16 if is_open or is_mobile else 8,
                    right=16 if is_open or is_mobile else 8,
                ),
                background="#d8407f",
                color="white",
                border_radius=8,
                display="flex",
                align_items="center",
                justify_content="center" if not is_open and not is_mobile else "flex-start",
                gap=8,
            ),
        ):
            me.icon(icon="add", style=me.Style(color="white"))
            if is_open or is_mobile:
                me.text("Nova Conversa", style=me.Style(color="white"))
        
        # Lista de conversas
        for conversation in app_state.conversations:
            render_conversation_item(
                conversation,
                app_state.current_conversation_id,
                is_open or is_mobile,
                navigate_to_conversation,
            )


def render_conversation_item(conversation, current_id: str, is_open: bool, on_click: Callable):
    """Renderiza item de conversa"""
    is_active = conversation.conversationId == current_id
    
    with me.box(
        key=conversation.conversationId,
        on_click=on_click,
        style=me.Style(
            padding=me.Padding(
                top=12,
                bottom=12,
                left=16 if is_open else 12,
                right=16 if is_open else 12,
            ),
            background="#f5f5f5" if is_active else "transparent",
            border_left=f"3px solid #d8407f" if is_active else "3px solid transparent",
            cursor="pointer",
            transition="all 0.2s ease",
            hover_background="#f0f0f0",
            display="flex",
            align_items="center",
            gap=12,
        ),
    ):
        # Ícone
        me.icon(
            icon="forum",
            style=me.Style(
                color="#d8407f" if is_active else TEXT_SECONDARY,
                font_size=20,
            )
        )
        
        # Título (apenas quando expandida)
        if is_open:
            with me.box(
                style=me.Style(
                    flex="1",
                    min_width=0,  # Permite truncar texto
                )
            ):
                me.text(
                    conversation.title or f"Conversa {conversation.conversationId[:8]}",
                    style=me.Style(
                        color=TEXT_PRIMARY if is_active else TEXT_SECONDARY,
                        font_size=14,
                        font_weight="bold" if is_active else "normal",
                        white_space="nowrap",
                        overflow="hidden",
                        text_overflow="ellipsis",
                    )
                )
                
                # Número de mensagens
                if conversation.messageIds:
                    me.text(
                        f"{len(conversation.messageIds)} mensagens",
                        style=me.Style(
                            color=TEXT_SECONDARY,
                            font_size=12,
                            margin_top=2,
                        )
                    )


def render_sidebar_footer(is_open: bool):
    """Renderiza footer da sidebar com toggle"""
    with me.box(
        style=me.Style(
            padding=me.Padding.all(16),
            border_top="1px solid #e0e0e0",
            display="flex",
            justify_content="center" if not is_open else "flex-end",
        )
    ):
        with me.content_button(
            type="icon",
            on_click=toggle_sidenav,
            style=me.Style(
                padding=me.Padding.all(8),
            )
        ):
            me.icon(
                icon="chevron_left" if is_open else "chevron_right",
                style=me.Style(color=TEXT_SECONDARY)
            )