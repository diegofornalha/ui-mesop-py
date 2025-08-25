"""Versão responsiva do UI com suporte para mobile, tablet e desktop.
run:
  uv main_responsive.py
"""

import os
from contextlib import asynccontextmanager

import httpx
import mesop as me

from components.api_key_dialog import api_key_dialog
from components.responsive_page_scaffold import responsive_page_scaffold, responsive_page_frame
from components.viewport_detector import viewport_detector
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from pages.agent_list import agent_list_page
from pages.responsive_conversation import responsive_conversation_page
from pages.event_list import event_list_page
from pages.home import home_page_content
from pages.settings import settings_page_content
from pages.task_list import task_list_page
from service.server.server import ConversationServer
from state import host_agent_service
from state.state import AppState


load_dotenv()


def on_load(e: me.LoadEvent):
    """On load event"""
    state = me.state(AppState)
    if 'conversationid' in me.query_params:
        state.current_conversation_id = me.query_params['conversationid']
    else:
        state.current_conversation_id = ''

    # Check API key configuration
    uses_vertex_ai = (
        os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').upper() == 'TRUE'
    )
    api_key = os.getenv('GOOGLE_API_KEY', '')

    if uses_vertex_ai:
        state.uses_vertex_ai = True
    elif api_key:
        state.api_key = api_key
    else:
        state.api_key_dialog_open = True


# Security policy for responsive styles
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
    title='Chat - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
    stylesheets=['/static/responsive.css'],  # CSS responsivo
)
def home_page():
    """Página principal responsiva"""
    state = me.state(AppState)
    
    # Detector de viewport
    viewport_detector()
    
    # Dialog de API key se necessário
    api_key_dialog()
    
    with responsive_page_scaffold():
        home_page_content(state)


@me.page(
    path='/agents',
    title='Agentes - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
    stylesheets=['/static/responsive.css'],
)
def agents_page():
    """Página de agentes responsiva"""
    viewport_detector()
    api_key_dialog()
    
    with responsive_page_scaffold():
        agent_list_page(me.state(AppState))


@me.page(
    path='/conversation',
    title='Conversa - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
    stylesheets=['/static/responsive.css'],
)
def chat_page():
    """Página de conversa responsiva"""
    viewport_detector()
    api_key_dialog()
    
    responsive_conversation_page(me.state(AppState))


@me.page(
    path='/event_list',
    title='Eventos - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
    stylesheets=['/static/responsive.css'],
)
def event_page():
    """Página de eventos responsiva"""
    viewport_detector()
    api_key_dialog()
    
    with responsive_page_scaffold():
        event_list_page(me.state(AppState))


@me.page(
    path='/settings',
    title='Configurações - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
    stylesheets=['/static/responsive.css'],
)
def settings_page():
    """Página de configurações responsiva"""
    viewport_detector()
    api_key_dialog()
    
    with responsive_page_scaffold():
        settings_page_content()


@me.page(
    path='/task_list',
    title='Tarefas - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
    stylesheets=['/static/responsive.css'],
)
def task_page():
    """Página de tarefas responsiva"""
    viewport_detector()
    api_key_dialog()
    
    with responsive_page_scaffold():
        task_list_page(me.state(AppState))


# HTTPXClientWrapper e configuração do servidor permanecem iguais
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
        assert self.async_client is not None
        return self.async_client


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

    # Setup connection details
    host = os.environ.get('A2A_UI_HOST', '0.0.0.0')
    preferred_port = int(os.environ.get('A2A_UI_PORT', '8888'))
    mesop_default_port = int(os.environ.get('MESOP_DEFAULT_PORT', '8888'))
    
    def is_port_available(port_to_check):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port_to_check))
                return True
        except OSError:
            return False
    
    # Try preferred port, fallback to Mesop default
    if is_port_available(preferred_port):
        port = preferred_port
        print(f"✅ Usando porta preferida: {port}")
    else:
        port = mesop_default_port
        print(f"⚠️  Porta {preferred_port} em uso, usando porta padrão do Mesop: {port}")
    
    # Set server URL
    host_agent_service.server_url = f'http://{host}:{port}'
    print(f"🚀 Iniciando servidor responsivo em http://{host}:{port}")
    print(f"📱 Interface otimizada para mobile, tablet e desktop!")

    uvicorn.run(
        app,
        host=host,
        port=port,
        timeout_graceful_shutdown=0,
    )