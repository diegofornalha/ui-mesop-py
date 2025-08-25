import mesop as me

from components.conversation import conversation, refresh_messages
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.state import AppState


def conversation_page(app_state: AppState):
    """Página de Conversa"""
    state = me.state(AppState)
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Conversa', 'chat'):
                pass
            conversation()
