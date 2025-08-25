"""Layout responsivo principal seguindo as práticas do Mesop"""

import mesop as me
from components.mesop_responsive_utils import (
    responsive_container,
    RESPONSIVE_ROOT_STYLE,
    RESPONSIVE_HEADER_STYLE,
)
from state.state import AppState


@me.content_component
def mesop_responsive_layout():
    """
    Layout responsivo usando apenas recursos nativos do Mesop.
    Usa min(), max() e calc() do CSS para responsividade.
    """
    app_state = me.state(AppState)
    
    with me.box(style=RESPONSIVE_ROOT_STYLE):
        # Header responsivo
        render_responsive_header()
        
        # Container principal com margin adaptativa
        main_style = me.Style(
            display="flex",
            flex_grow=1,
            width="100%",
            overflow="hidden",
        )
        
        with me.box(style=main_style):
            # Sidebar (desktop) ou nada (mobile)
            render_desktop_sidebar()
            
            # Conteúdo principal
            with me.box(
                style=me.Style(
                    flex_grow=1,
                    overflow_y="auto",
                    margin_left="200px" if app_state.sidenav_open else "68px",
                    transition="margin-left 0.3s ease",
                )
            ):
                # Slot para conteúdo
                me.slot()


def render_responsive_header():
    """Header responsivo com menu mobile"""
    app_state = me.state(AppState)
    
    with me.box(style=RESPONSIVE_HEADER_STYLE):
        with me.box(
            style=me.Style(
                display="flex",
                align_items="center",
                justify_content="space-between",
                max_width="1200px",
                margin=me.Margin.symmetric(horizontal="auto"),
                width="100%",
            )
        ):
            # Menu button (visível em telas pequenas)
            with me.box(
                style=me.Style(
                    display="block",

                )
            ):
                with me.content_button(
                    type="icon",
                    on_click=toggle_mobile_menu,
                ):
                    me.icon(icon="menu")
            
            # Logo/Título
            me.text(
                "Chat UI",
                style=me.Style(
                    font_size="clamp(18px, 4vw, 24px)",  # Tamanho responsivo
                    font_weight="bold",
                )
            )
            
            # Espaço para manter título centralizado
            me.box(style=me.Style(width=40))


def render_desktop_sidebar():
    """Sidebar para desktop (oculta em mobile)"""
    app_state = me.state(AppState)
    
    # Sidebar apenas em telas grandes
    sidebar_width = "200px" if app_state.sidenav_open else "68px"
    
    with me.box(
        style=me.Style(
            position="fixed",
            left=0,
            top=56,  # Altura do header
            bottom=0,
            width=sidebar_width,
            background="white",
            border="0 1px 0 0 solid #e0e0e0",
            overflow_y="auto",
            transition="width 0.3s ease",
            display="none",  # Oculta por padrão

        )
    ):
        render_sidebar_content()


def render_sidebar_content():
    """Conteúdo da sidebar"""
    app_state = me.state(AppState)
    
    # Toggle button
    with me.box(
        style=me.Style(
            padding=me.Padding.all(16),
            display="flex",
            justify_content="flex-end" if app_state.sidenav_open else "center",
        )
    ):
        with me.content_button(
            type="icon",
            on_click=toggle_sidebar,
        ):
            me.icon(
                icon="chevron_left" if app_state.sidenav_open else "chevron_right"
            )
    
    # Conteúdo baseado no estado
    if app_state.sidenav_open:
        # Lista completa
        render_full_sidebar()
    else:
        # Apenas ícones
        render_collapsed_sidebar()


def render_full_sidebar():
    """Sidebar expandida"""
    app_state = me.state(AppState)
    
    with me.box(style=me.Style(padding=me.Padding.symmetric(horizontal=16))):
        # Nova conversa
        with me.content_button(
            type="flat",
            style=me.Style(
                width="100%",
                padding=me.Padding.all(12),
                background="#d8407f",
                color="white",
                border_radius=8,
                margin_bottom=16,
            ),
            on_click=lambda e: me.navigate("/"),
        ):
            me.text("Nova Conversa")
        
        # Lista de conversas
        for conv in app_state.conversations:
            with me.box(
                style=me.Style(
                    padding=me.Padding.all(12),
                    border_radius=8,
                    margin_bottom=8,
                    cursor="pointer",
                    background="#f5f5f5" if conv.conversationId == app_state.current_conversation_id else "transparent",
                ),
                on_click=lambda e, cid=conv.conversationId: navigate_to_conversation(cid),
            ):
                me.text(conv.title or f"Conversa {conv.conversationId[:8]}")


def render_collapsed_sidebar():
    """Sidebar colapsada com apenas ícones"""
    app_state = me.state(AppState)
    
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column",
            align_items="center",
            padding=me.Padding.symmetric(vertical=16),
            gap=16,
        )
    ):
        # Botão nova conversa
        with me.content_button(
            type="icon",
            style=me.Style(
                background="#d8407f",
                color="white",
                border_radius="50%",
                padding=me.Padding.all(12),
            ),
            on_click=lambda e: me.navigate("/"),
        ):
            me.icon(icon="add", style=me.Style(color="white"))
        
        # Ícones das conversas
        for conv in app_state.conversations:
            with me.content_button(
                type="icon",
                style=me.Style(
                    background="#f5f5f5" if conv.conversationId == app_state.current_conversation_id else "transparent",
                ),
                on_click=lambda e, cid=conv.conversationId: navigate_to_conversation(cid),
            ):
                me.icon(icon="forum")


def toggle_sidebar(e: me.ClickEvent):
    """Toggle sidebar expandida/colapsada"""
    app_state = me.state(AppState)
    app_state.sidenav_open = not app_state.sidenav_open


def toggle_mobile_menu(e: me.ClickEvent):
    """Toggle menu mobile"""
    # Em uma implementação real, isso abriria um drawer
    pass


def navigate_to_conversation(conversation_id: str):
    """Navega para uma conversa"""
    app_state = me.state(AppState)
    app_state.current_conversation_id = conversation_id
    me.navigate(f"/conversation?conversationid={conversation_id}")


# Componente de grade responsiva usando CSS Grid nativo
@me.component
def mesop_responsive_grid(columns: str = "repeat(auto-fit, minmax(300px, 1fr))", gap: int = 16):
    """
    Grid responsivo usando CSS Grid com auto-fit.
    
    Args:
        columns: String de template de colunas (padrão: auto-fit com mínimo 300px)
        gap: Espaçamento entre itens
    """
    with me.box(
        style=me.Style(
            display="grid",
            grid_template_columns=columns,
            gap=gap,
            width="100%",
        )
    ):
        me.slot()


# Componente de card responsivo
@me.component
def mesop_responsive_card(title: str, content: str):
    """Card responsivo com sombra e padding adaptativo"""
    with me.box(
        style=me.Style(
            background="white",
            border_radius=8,
            padding=me.Padding.all(16),
            box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
            transition="box-shadow 0.2s ease",
            cursor="pointer",

        )
    ):
        me.text(
            title,
            style=me.Style(
                font_size="clamp(16px, 2vw, 20px)",
                font_weight="bold",
                margin_bottom=8,
            )
        )
        me.text(
            content,
            style=me.Style(
                font_size="clamp(14px, 1.5vw, 16px)",
                color="#666",
            )
        )