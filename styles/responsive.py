"""Utilitários e configurações de responsividade para o chat UI"""

import mesop as me
from dataclasses import dataclass
from typing import Optional


# Breakpoints responsivos (em pixels)
MOBILE_BREAKPOINT = 768
TABLET_BREAKPOINT = 1024
DESKTOP_BREAKPOINT = 1200

# Larguras da sidebar responsivas
SIDENAV_MOBILE_WIDTH = 0  # Sidebar oculta em mobile
SIDENAV_TABLET_WIDTH = 60
SIDENAV_DESKTOP_WIDTH = 200

# Espaçamentos responsivos
PADDING_MOBILE = 8
PADDING_TABLET = 12
PADDING_DESKTOP = 16
PADDING_LARGE = 24

# Gaps responsivos
GAP_MOBILE = 8
GAP_TABLET = 12
GAP_DESKTOP = 16

# Tamanhos de fonte responsivos
FONT_SIZE_MOBILE = 14
FONT_SIZE_TABLET = 16
FONT_SIZE_DESKTOP = 16

# Tamanhos de input responsivos
INPUT_HEIGHT_MOBILE = 40
INPUT_HEIGHT_TABLET = 48
INPUT_HEIGHT_DESKTOP = 56

# Larguras máximas
MAX_CONTENT_WIDTH = 1200
MAX_CHAT_BUBBLE_WIDTH = 600
MAX_INPUT_WIDTH = 800


@dataclass
class ResponsiveConfig:
    """Configuração responsiva baseada no tamanho da tela"""
    padding: int
    gap: int
    font_size: int
    sidebar_width: int
    input_height: int
    chat_bubble_width: str
    chat_bubble_max_width: str


def get_responsive_config(viewport_width: Optional[int] = None) -> ResponsiveConfig:
    """
    Retorna configuração responsiva baseada na largura da viewport.
    Por enquanto retorna config desktop como padrão.
    """
    # TODO: Implementar detecção real de viewport_width
    # Por enquanto, vamos usar desktop como padrão
    
    if viewport_width and viewport_width <= MOBILE_BREAKPOINT:
        return ResponsiveConfig(
            padding=PADDING_MOBILE,
            gap=GAP_MOBILE,
            font_size=FONT_SIZE_MOBILE,
            sidebar_width=SIDENAV_MOBILE_WIDTH,
            input_height=INPUT_HEIGHT_MOBILE,
            chat_bubble_width="90%",
            chat_bubble_max_width="100%"
        )
    elif viewport_width and viewport_width <= TABLET_BREAKPOINT:
        return ResponsiveConfig(
            padding=PADDING_TABLET,
            gap=GAP_TABLET,
            font_size=FONT_SIZE_TABLET,
            sidebar_width=SIDENAV_TABLET_WIDTH,
            input_height=INPUT_HEIGHT_TABLET,
            chat_bubble_width="80%",
            chat_bubble_max_width=f"{MAX_CHAT_BUBBLE_WIDTH}px"
        )
    else:
        return ResponsiveConfig(
            padding=PADDING_DESKTOP,
            gap=GAP_DESKTOP,
            font_size=FONT_SIZE_DESKTOP,
            sidebar_width=SIDENAV_DESKTOP_WIDTH,
            input_height=INPUT_HEIGHT_DESKTOP,
            chat_bubble_width="70%",
            chat_bubble_max_width=f"{MAX_CHAT_BUBBLE_WIDTH}px"
        )


def get_responsive_padding(is_mobile: bool = False, is_tablet: bool = False) -> me.Padding:
    """Retorna padding responsivo baseado no tipo de dispositivo"""
    if is_mobile:
        return me.Padding.all(PADDING_MOBILE)
    elif is_tablet:
        return me.Padding.all(PADDING_TABLET)
    else:
        return me.Padding.all(PADDING_DESKTOP)


def get_responsive_margin(is_mobile: bool = False, is_tablet: bool = False) -> me.Margin:
    """Retorna margin responsivo baseado no tipo de dispositivo"""
    if is_mobile:
        return me.Margin.all(PADDING_MOBILE)
    elif is_tablet:
        return me.Margin.all(PADDING_TABLET)
    else:
        return me.Margin.all(PADDING_DESKTOP)


def get_container_style(is_mobile: bool = False) -> me.Style:
    """Retorna estilo de container responsivo"""
    config = get_responsive_config()
    
    return me.Style(
        display="flex",
        flex_direction="column",
        width="100%",
        max_width=f"{MAX_CONTENT_WIDTH}px" if not is_mobile else "100%",
        margin=me.Margin.all(0),
        padding=get_responsive_padding(is_mobile=is_mobile),
    )


def get_input_container_style(is_mobile: bool = False) -> me.Style:
    """Retorna estilo do container de input responsivo"""
    config = get_responsive_config()
    
    return me.Style(
        display="flex",
        flex_direction="row",
        gap=GAP_MOBILE if is_mobile else GAP_DESKTOP,
        align_items="center",
        width="100%",
        max_width=f"{MAX_INPUT_WIDTH}px" if not is_mobile else "100%",
        padding=get_responsive_padding(is_mobile=is_mobile),
        position="sticky",
        bottom=0,
        background="white",
        border_top="1px solid #e0e0e0",
        z_index=10,
    )


def get_chat_bubble_style(role: str, is_mobile: bool = False) -> me.Style:
    """Retorna estilo de chat bubble responsivo"""
    config = get_responsive_config()
    
    # Cores baseadas no role
    if role == "user":
        background = "#d8407f"  # Rosa escuro
        color = "white"
    else:
        background = "#ffe0ec"  # Rosa claro
        color = "#333333"
    
    return me.Style(
        font_family="Google Sans",
        font_size=config.font_size,
        font_weight="bold",
        box_shadow=(
            "0 1px 2px 0 rgba(60, 64, 67, 0.3), "
            "0 1px 3px 1px rgba(60, 64, 67, 0.15)"
        ),
        padding=get_responsive_padding(is_mobile=is_mobile),
        margin=me.Margin(
            top=5 if is_mobile else 8,
            bottom=5 if is_mobile else 8,
            left=0,
            right=0
        ),
        background=background,
        color=color,
        border_radius=15,
        max_width=config.chat_bubble_max_width,
        word_wrap="break-word",
        overflow_wrap="break-word",
    )


def get_message_container_style(role: str, is_mobile: bool = False) -> me.Style:
    """Retorna estilo do container de mensagem responsivo"""
    config = get_responsive_config()
    
    return me.Style(
        display="flex",
        justify_content="flex-end" if role == "user" else "flex-start",
        width="100%",
        padding=me.Padding(
            left=PADDING_MOBILE if is_mobile else PADDING_DESKTOP,
            right=PADDING_MOBILE if is_mobile else PADDING_DESKTOP,
        ),
    )
