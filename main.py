"""A UI solution and host service to interact with the agent framework.
run:
  uv main.py
"""

import os

from contextlib import asynccontextmanager

import httpx
import mesop as me

from components.api_key_dialog import api_key_dialog
from components.page_scaffold import page_scaffold
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from pages.agent_list import agent_list_page
from pages.conversation import conversation_page
from pages.event_list import event_list_page
from pages.home import home_page_content
from pages.settings import settings_page_content
from pages.task_list import task_list_page
from service.server.server import ConversationServer
from state import host_agent_service
from state.state import AppState


load_dotenv()


def on_load(e: me.LoadEvent):  # pylint: disable=unused-argument
    """On load event"""
    state = me.state(AppState)
    # Theme mode removido - usando cores fixas
    if 'conversationid' in me.query_params:
        state.current_conversation_id = me.query_params['conversationid']
    else:
        state.current_conversation_id = ''

    # check if the API key is set in the environment
    # and if the user is using Vertex AI
    uses_vertex_ai = (
        os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').upper() == 'TRUE'
    )
    api_key = os.getenv('GOOGLE_API_KEY', '')

    if uses_vertex_ai:
        state.uses_vertex_ai = True
    elif api_key:
        state.api_key = api_key
    else:
        # Show the API key dialog if both are not set
        state.api_key_dialog_open = True


# Policy to allow the lit custom element to load
security_policy = me.SecurityPolicy(
    allowed_script_srcs=[
        'https://cdn.jsdelivr.net',
        'https://lit.dev',
        'https://unpkg.com',
    ],
    allowed_font_srcs=[
        'https://fonts.gstatic.com',
        'https://r2cdn.perplexity.ai',
        'data:',
    ],
    allowed_connect_srcs=[
        'https://api.perplexity.ai',
        'https://generativelanguage.googleapis.com',
        'http://localhost:*',
        'https://*.googleapis.com',
    ],
    allowed_iframe_parents=['*'],
)


@me.page(
    path='/',
    title='Chat',
    on_load=on_load,
    security_policy=security_policy,
)
def home_page():
    """Main Page"""
    state = me.state(AppState)
    # Show API key dialog if needed
    api_key_dialog()
    with page_scaffold():  # pylint: disable=not-context-manager
        home_page_content(state)


@me.page(
    path='/agents',
    title='Agents',
    on_load=on_load,
    security_policy=security_policy,
)
def another_page():
    """Another Page"""
    api_key_dialog()
    agent_list_page(me.state(AppState))


@me.page(
    path='/conversation',
    title='Conversation',
    on_load=on_load,
    security_policy=security_policy,
)
def chat_page():
    """Conversation Page."""
    api_key_dialog()
    conversation_page(me.state(AppState))


@me.page(
    path='/event_list',
    title='Event List',
    on_load=on_load,
    security_policy=security_policy,
)
def event_page():
    """Event List Page."""
    api_key_dialog()
    event_list_page(me.state(AppState))


@me.page(
    path='/settings',
    title='Settings',
    on_load=on_load,
    security_policy=security_policy,
)
def settings_page():
    """Settings Page."""
    api_key_dialog()
    settings_page_content()


@me.page(
    path='/task_list',
    title='Task List',
    on_load=on_load,
    security_policy=security_policy,
)
def task_page():
    """Task List Page."""
    api_key_dialog()
    task_list_page(me.state(AppState))


class HTTPXClientWrapper:
    """Wrapper to return the singleton client where needed."""

    async_client: httpx.AsyncClient = None

    def start(self):
        """Instantiate the client. Call from the FastAPI startup hook."""
        self.async_client = httpx.AsyncClient(timeout=30)

    async def stop(self):
        """Gracefully shutdown. Call from FastAPI shutdown hook."""
        await self.async_client.aclose()
        self.async_client = None

    def __call__(self):
        """Calling the instantiated HTTPXClientWrapper returns the wrapped singleton."""
        # Ensure we don't use it if not started / running
        assert self.async_client is not None
        return self.async_client


# Setup the server global objects
httpx_client_wrapper = HTTPXClientWrapper()
agent_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    httpx_client_wrapper.start()
    ConversationServer(app, httpx_client_wrapper())
    app.openapi_schema = None
    app.mount(
        '/',
        WSGIMiddleware(
            me.create_wsgi_app(
                debug_mode=os.environ.get('DEBUG_MODE', '') == 'true'
            )
        ),
    )
    app.setup()
    yield
    await httpx_client_wrapper.stop()


if __name__ == '__main__':
    import uvicorn
    import socket

    app = FastAPI(lifespan=lifespan)

    # Setup the connection details, these should be set in the environment
    host = os.environ.get('A2A_UI_HOST', '0.0.0.0')
    preferred_port = int(os.environ.get('A2A_UI_PORT', '8888'))
    mesop_default_port = int(os.environ.get('MESOP_DEFAULT_PORT', '8888'))
    
    # Função para verificar se uma porta está disponível
    def is_port_available(port_to_check):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port_to_check))
                return True
        except OSError:
            return False
    
    # Tentar usar a porta preferida, senão usar a porta padrão do Mesop
    if is_port_available(preferred_port):
        port = preferred_port
        print(f"✅ Usando porta preferida: {port}")
    else:
        port = mesop_default_port
        print(f"⚠️  Porta {preferred_port} em uso, usando porta padrão do Mesop: {port}")
    
    # Set the client to talk to the server
    host_agent_service.server_url = f'http://{host}:{port}'
    print(f"🚀 Iniciando servidor em http://{host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        timeout_graceful_shutdown=0,
    )
