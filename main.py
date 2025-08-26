"""A UI solution and host service to interact with the agent framework.
run:
  uv main.py
"""

import os

from contextlib import asynccontextmanager

import httpx
import mesop as me

# api_key_dialog removido - Claude não precisa de API key
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
from service.server.server_v2 import ConversationServerV2 as ConversationServer
from state import host_agent_service
from state.state import AppState


load_dotenv()


def on_load(e: me.LoadEvent):  # pylint: disable=unused-argument
    """On load event"""
    state = me.state(AppState)
    if 'conversationid' in me.query_params:
        state.current_conversation_id = me.query_params['conversationid']
    else:
        state.current_conversation_id = ''

    # Claude está sempre ativo - não precisa de API key
    state.uses_claude = True
    state.api_key = ''  # Claude usa CLI local, sem API key


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
    # Claude não precisa de dialog de API key
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
    # Claude não precisa de dialog de API key
    agent_list_page(me.state(AppState))


@me.page(
    path='/conversation',
    title='Conversa',
    on_load=on_load,
    security_policy=security_policy,
)
def chat_page():
    """Página de Conversa."""
    # Claude não precisa de dialog de API key
    conversation_page(me.state(AppState))


@me.page(
    path='/event_list',
    title='Lista de Eventos',
    on_load=on_load,
    security_policy=security_policy,
)
def event_page():
    """Página da Lista de Eventos."""
    # Claude não precisa de dialog de API key
    event_list_page()


@me.page(
    path='/settings',
    title='Configurações',
    on_load=on_load,
    security_policy=security_policy,
)
def settings_page():
    """Página de Configurações."""
    # Claude não precisa de dialog de API key
    settings_page_content()


@me.page(
    path='/task_list',
    title='Lista de Tarefas',
    on_load=on_load,
    security_policy=security_policy,
)
def task_page():
    """Página da Lista de Tarefas."""
    # Claude não precisa de dialog de API key
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
