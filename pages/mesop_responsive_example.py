"""Exemplo de página responsiva seguindo as práticas do Mesop"""

import mesop as me
from components.mesop_responsive_layout import (
    mesop_responsive_layout,
    mesop_responsive_grid,
    mesop_responsive_card,
)
from components.mesop_responsive_chat import mesop_responsive_chat
from components.mesop_responsive_utils import (
    responsive_container,
    responsive_text_size,
)


@me.page(
    path="/mesop-responsive",
    title="Chat Responsivo - Mesop",
)
def mesop_responsive_page():
    """Página de exemplo totalmente responsiva seguindo Mesop"""
    
    with mesop_responsive_layout():
        # Container principal responsivo
        with me.box(style=responsive_container()):
            # Título responsivo usando clamp()
            me.text(
                "Chat UI Responsivo",
                style=me.Style(
                    font_size="clamp(24px, 5vw, 36px)",  # Responsivo
                    font_weight="bold",
                    margin_bottom=24,
                    text_align="center",
                )
            )
            
            # Subtítulo responsivo
            me.text(
                "Interface adaptativa usando apenas recursos nativos do Mesop",
                style=me.Style(
                    font_size="clamp(16px, 2vw, 20px)",
                    color="#666",
                    margin_bottom=32,
                    text_align="center",
                )
            )
            
            # Grid de features responsivo
            render_features_grid()
            
            # Seção de chat
            render_chat_section()


def render_features_grid():
    """Grid de features responsivo"""
    with me.box(style=me.Style(margin_bottom=48)):
        me.text(
            "Features Responsivas",
            style=me.Style(
                font_size="clamp(20px, 3vw, 28px)",
                font_weight="bold",
                margin_bottom=24,
            )
        )
        
        with mesop_responsive_grid():
            # Card 1
            mesop_responsive_card(
                title="📱 Mobile First",
                content="Design otimizado para dispositivos móveis usando min() e clamp() CSS"
            )
            
            # Card 2
            mesop_responsive_card(
                title="🎨 Layout Fluido",
                content="Containers e grids que se adaptam automaticamente ao viewport"
            )
            
            # Card 3
            mesop_responsive_card(
                title="⚡ Performance",
                content="Sem JavaScript adicional, apenas CSS nativo para responsividade"
            )
            
            # Card 4
            mesop_responsive_card(
                title="🔧 Mesop Nativo",
                content="Usando apenas recursos e padrões oficiais do framework Mesop"
            )


def render_chat_section():
    """Seção de demonstração do chat"""
    with me.box(
        style=me.Style(
            margin_top=48,
            border_top="1px solid #e0e0e0",
            padding_top=32,
        )
    ):
        me.text(
            "Demo do Chat Responsivo",
            style=me.Style(
                font_size="clamp(20px, 3vw, 28px)",
                font_weight="bold",
                margin_bottom=24,
            )
        )
        
        # Container do chat com altura fixa e responsiva
        with me.box(
            style=me.Style(
                height="min(600px, 70vh)",  # Altura responsiva
                border="1px solid #e0e0e0",
                border_radius=8,
                overflow="hidden",
                display="flex",
                flex_direction="column",
            )
        ):
            # Chat responsivo
            mesop_responsive_chat()


# Exemplo de uso com viewport queries CSS
@me.component
def responsive_info_box():
    """Box de informação que muda baseado no viewport"""
    with me.box(
        style=me.Style(
            background="#f0f0f0",
            padding=me.Padding.all(16),
            border_radius=8,
            margin=me.Margin.symmetric(vertical=16),
        )
    ):
        # Texto que muda de tamanho responsivamente
        me.text(
            "Esta interface se adapta ao seu dispositivo",
            style=me.Style(
                font_size="clamp(14px, 2vw, 18px)",
                margin_bottom=8,
            )
        )
        
        # Lista de características responsivas
        features = [
            "✓ Larguras usando min() e max()",
            "✓ Fontes com clamp()",
            "✓ Grid com auto-fit",
            "✓ Containers fluidos",
        ]
        
        for feature in features:
            me.text(
                feature,
                style=me.Style(
                    font_size="clamp(12px, 1.5vw, 16px)",
                    color="#666",
                    margin_bottom=4,
                )
            )


# Técnicas CSS responsivas no Mesop
def mesop_responsive_techniques():
    """
    Demonstra técnicas responsivas usando apenas CSS no Mesop:
    
    1. min() e max() - Para larguras e alturas responsivas
       width="min(600px, 90%)"
    
    2. clamp() - Para tamanhos de fonte responsivos
       font_size="clamp(16px, 2vw, 24px)"
    
    3. calc() - Para cálculos dinâmicos
       padding="calc(1rem + 2vw)"
    
    4. vw/vh units - Unidades de viewport
       width="80vw", height="60vh"
    
    5. CSS Grid auto-fit/auto-fill
       grid_template_columns="repeat(auto-fit, minmax(250px, 1fr))"
    
    6. Flexbox com wrap
       display="flex", flex_wrap="wrap"
    """
    pass