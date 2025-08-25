import mesop as me

from components.event_viewer import event_list
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.agent_state import AgentState
from state.state import AppState


def event_list_page():
    """Página da Lista de Eventos"""
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Lista de Eventos', 'list'):
                pass
            event_list()
