"""Page scaffold responsivo com sidebar adaptativa"""

import mesop as me
import mesop.labs as mel

from state.host_agent_service import UpdateAppState
from state.state import AppState
from styles.colors import BACKGROUND
from styles.responsive import (
    get_responsive_config,
    SIDENAV_MOBILE_WIDTH,
    SIDENAV_TABLET_WIDTH,
    SIDENAV_DESKTOP_WIDTH,
    MOBILE_BREAKPOINT,
    TABLET_BREAKPOINT,
)

from .async_poller import AsyncAction, async_poller
from .responsive_sidenav import responsive_sidenav


@me.stateclass
class ResponsiveState:
    """Estado para controle de responsividade"""
    viewport_width: int = 1200  # Desktop por padrão
    is_mobile: bool = False
    is_tablet: bool = False
    is_desktop: bool = True
    show_mobile_menu: bool = False


async def refresh_app_state(e: mel.WebEvent):
    """Atualiza estado da aplicação"""
    yield
    app_state = me.state(AppState)
    await UpdateAppState(app_state, app_state.current_conversation_id)
    yield


def toggle_mobile_menu(e: me.ClickEvent):
    """Toggle do menu mobile"""
    responsive_state = me.state(ResponsiveState)
    responsive_state.show_mobile_menu = not responsive_state.show_mobile_menu


def close_mobile_menu(e: me.ClickEvent):
    """Fecha o menu mobile"""
    responsive_state = me.state(ResponsiveState)
    responsive_state.show_mobile_menu = False


@me.content_component
def responsive_page_scaffold():
    """Page scaffold responsivo"""
    app_state = me.state(AppState)
    responsive_state = me.state(ResponsiveState)
    
    # Determinar tipo de dispositivo
    viewport_width = responsive_state.viewport_width
    is_mobile = viewport_width <= MOBILE_BREAKPOINT
    is_tablet = MOBILE_BREAKPOINT < viewport_width <= TABLET_BREAKPOINT
    is_desktop = viewport_width > TABLET_BREAKPOINT
    
    # Atualizar estado responsivo
    responsive_state.is_mobile = is_mobile
    responsive_state.is_tablet = is_tablet
    responsive_state.is_desktop = is_desktop
    
    # Configuração de polling
    action = (
        AsyncAction(
            value=app_state,
            duration_seconds=app_state.polling_interval
        )
        if app_state
        else None
    )
    async_poller(action=action, trigger_event=refresh_app_state)
    
    # Obter largura da sidebar baseada no dispositivo
    sidebar_width = get_sidebar_width(is_mobile, is_tablet, app_state.sidenav_open)
    
    # Container principal
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="row",
            height="100vh",
            width="100vw",
            overflow="hidden",
            position="relative",
        )
    ):
        # Renderizar sidebar responsiva
        responsive_sidenav(
            is_mobile=is_mobile,
            is_tablet=is_tablet,
            show_mobile_menu=responsive_state.show_mobile_menu,
            on_close=close_mobile_menu,
        )
        
        # Conteúdo principal com margin adaptativa
        with me.box(
            style=me.Style(
                display="flex",
                flex_direction="column",
                flex="1",
                height="100%",
                margin_left=sidebar_width if not is_mobile else 0,
                transition="margin-left 0.3s ease",
                position="relative",
            )
        ):
            # Header mobile com botão de menu
            if is_mobile:
                render_mobile_header(toggle_mobile_menu)
            
            # Container de conteúdo
            with me.box(
                style=me.Style(
                    background=BACKGROUND,
                    flex="1",
                    overflow_y="auto",
                    overflow_x="hidden",
                    height="100%",
                )
            ):
                me.slot()
        
        # Overlay para fechar menu mobile
        if is_mobile and responsive_state.show_mobile_menu:
            render_mobile_overlay(close_mobile_menu)


def get_sidebar_width(is_mobile: bool, is_tablet: bool, is_open: bool) -> int:
    """Calcula largura da sidebar baseada no dispositivo e estado"""
    if is_mobile:
        return 0  # Sidebar oculta em mobile
    elif is_tablet:
        return SIDENAV_TABLET_WIDTH
    else:
        return SIDENAV_DESKTOP_WIDTH if is_open else SIDENAV_TABLET_WIDTH


def render_mobile_header(on_menu_click):
    """Renderiza header para dispositivos móveis"""
    with me.box(
        style=me.Style(
            display="flex",
            align_items="center",
            justify_content="space-between",
            height=56,
            padding=me.Padding(left=16, right=16),
            background="white",
            border_bottom="1px solid #e0e0e0",
            position="sticky",
            top=0,
            z_index=100,
        )
    ):
        # Botão de menu
        with me.content_button(
            type="icon",
            on_click=on_menu_click,
            style=me.Style(
                padding=me.Padding.all(8),
            )
        ):
            me.icon(icon="menu")
        
        # Logo ou título
        me.text(
            "Chat UI",
            style=me.Style(
                font_size=18,
                font_weight="bold",
                color="#333333",
            )
        )
        
        # Espaço para manter o título centralizado
        me.box(style=me.Style(width=40))


def render_mobile_overlay(on_close):
    """Renderiza overlay para fechar menu mobile"""
    with me.box(
        style=me.Style(
            position="fixed",
            top=0,
            left=0,
            right=0,
            bottom=0,
            background="rgba(0, 0, 0, 0.5)",
            z_index=998,
            cursor="pointer",
        ),
        on_click=on_close,
    ):
        pass


@me.content_component
def responsive_page_frame():
    """Frame de página responsivo"""
    responsive_state = me.state(ResponsiveState)
    config = get_responsive_config(responsive_state.viewport_width)
    
    with me.box(
        style=me.Style(
            display="flex",
            flex_direction="column",
            height="100%",
            width="100%",
            max_width=f"{config.chat_bubble_max_width}px" if not responsive_state.is_mobile else "100%",
            margin="0 auto",
            padding=me.Padding(
                top=config.padding,
                left=config.padding,
                right=config.padding,
                bottom=0,  # Sem padding bottom para o input ficar colado
            ),
        )
    ):
        me.slot()