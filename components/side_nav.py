import mesop as me

from state.state import AppState
from styles.styles import (
    DEFAULT_MENU_STYLE,
    SIDENAV_MAX_WIDTH,
    SIDENAV_MIN_WIDTH,
    _FANCY_TEXT_GRADIENT,
)


page_json = [
    {'display': 'Home', 'icon': 'message', 'route': '/'},
    {'display': 'Agents', 'icon': 'smart_toy', 'route': '/agents'},
    {'display': 'Event List', 'icon': 'list', 'route': '/event_list'},
    {'display': 'Task List', 'icon': 'task', 'route': '/task_list'},
    {'display': 'Settings', 'icon': 'settings', 'route': '/settings'},
]


def on_sidenav_menu_click(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Side navigation menu click handler"""
    state = me.state(AppState)
    state.sidenav_open = not state.sidenav_open


def navigate_to(e: me.ClickEvent):
    """Navigate to a specific page"""
    s = me.state(AppState)
    idx = int(e.key)
    if idx > len(page_json):
        return
    page = page_json[idx]
    s.current_page = page['route']
    me.navigate(s.current_page)
    yield


@me.component
def sidenav(current_page: str):
    """Render side navigation"""
    app_state = me.state(AppState)

    with me.sidenav(
        opened=True,
        style=me.Style(
            width=SIDENAV_MAX_WIDTH
            if app_state.sidenav_open
            else SIDENAV_MIN_WIDTH,
            background='#f8f9fa',  # Sidebar com leve destaque cinza claro
        ),
    ):
        with me.box(
            style=me.Style(
                margin=me.Margin(top=16, left=16, right=16, bottom=16),
                display='flex',
                flex_direction='column',
                gap=5,
            ),
        ):
            with me.box(
                style=me.Style(
                    display='flex',
                    flex_direction='row',
                    gap=5,
                    align_items='center',
                ),
            ):
                with me.content_button(
                    type='icon',
                    on_click=on_sidenav_menu_click,
                ):
                    with me.box():
                        with me.tooltip(message='Expand menu'):
                            me.icon(icon='menu')
                if app_state.sidenav_open:
                    me.text('STUDIO', style=_FANCY_TEXT_GRADIENT)
            me.box(style=me.Style(height=16))
            for idx, page in enumerate(page_json):
                menu_item(
                    idx,
                    page['icon'],
                    page['display'],
                    not app_state.sidenav_open,
                )
            # Removido toggle de tema - usando cores fixas


def menu_item(
    key: int,
    icon: str,
    text: str,
    minimized: bool = True,
    content_style: me.Style = DEFAULT_MENU_STYLE,
):
    """Render menu item"""
    if minimized:  # minimized
        with me.box(
            style=me.Style(
                display='flex',
                flex_direction='row',
                gap=5,
                align_items='center',
            ),
        ):
            with me.content_button(
                key=str(key),
                on_click=navigate_to,
                style=content_style,
                type='icon',
            ):
                with me.tooltip(message=text):
                    me.icon(icon=icon)

    else:  # expanded
        with me.content_button(
            key=str(key),
            on_click=navigate_to,
            style=content_style,
        ):
            with me.box(
                style=me.Style(
                    display='flex',
                    flex_direction='row',
                    gap=5,
                    align_items='center',
                ),
            ):
                me.icon(icon=icon)
                me.text(text)


# Funções de toggle de tema removidas - usando cores fixas


MENU_BOTTOM = me.Style(
    display='flex',
    flex_direction='column',
    position='absolute',
    bottom=8,
    align_content='left',
)
