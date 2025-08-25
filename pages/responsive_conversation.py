"""Página de conversa responsiva"""

import mesop as me
from components.responsive_page_scaffold import responsive_page_scaffold, responsive_page_frame
from components.responsive_conversation import responsive_conversation
from state.state import AppState


def responsive_conversation_page(state: AppState):
    """Renderiza a página de conversa responsiva"""
    with responsive_page_scaffold():
        with responsive_page_frame():
            # Título da página apenas em desktop
            with me.box(
                style=me.Style(
                    display="none",  # Será mostrado via CSS em desktop
                    margin_bottom=24,
                    class_name="desktop-only",
                )
            ):
                me.text(
                    "Conversa",
                    style=me.Style(
                        font_size=24,
                        font_weight="bold",
                        color="#333333",
                    )
                )
            
            # Componente de conversa responsivo
            responsive_conversation()