"""Versão limpa e corrigida do Chat UI Mesop Responsivo
run:
  python main_mesop_clean.py
"""

import os
from contextlib import asynccontextmanager

import httpx
import mesop as me

from components.api_key_dialog import api_key_dialog
from components.page_scaffold import page_scaffold
from components.conversation import conversation
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from pages.home import home_page_content
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

    # Check API key
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


# Security policy
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
    title='Chat UI - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
)
def home_page():
    """Página principal com estilos responsivos inline"""
    state = me.state(AppState)
    
    # Dialog de API key
    api_key_dialog()
    
    # Container responsivo principal
    with me.box(
        style=me.Style(
            min_height="100vh",
            display="flex",
            flex_direction="column",
            font_family="Inter, system-ui, -apple-system, sans-serif",
        )
    ):
        # Header responsivo
        with me.box(
            style=me.Style(
                padding=me.Padding.all(16),
                background="white",
                border="0 0 1px 0 solid #e0e0e0",
                position="sticky",
                top=0,
                z_index=100,
            )
        ):
            me.text(
                "Chat UI Responsivo",
                style=me.Style(
                    font_size="clamp(20px, 4vw, 28px)",
                    font_weight="bold",
                    text_align="center",
                )
            )
        
        # Conteúdo principal
        with me.box(
            style=me.Style(
                flex_grow=1,
                width="min(1200px, 100%)",
                margin="0 auto",
                padding=me.Padding.all(16),
            )
        ):
            home_page_content(state)


@me.page(
    path='/conversation',
    title='Conversa - Responsivo',
    on_load=on_load,
    security_policy=security_policy,
)
def chat_page():
    """Página de conversa responsiva"""
    api_key_dialog()
    
    with me.box(
        style=me.Style(
            height="100vh",
            display="flex",
            flex_direction="column",
            overflow="hidden",
        )
    ):
        # Container de conversa responsivo
        with me.box(
            style=me.Style(
                flex_grow=1,
                width="min(900px, 100%)",
                margin="0 auto",
                display="flex",
                flex_direction="column",
                height="100%",
            )
        ):
            conversation()


# HTTPXClientWrapper
class HTTPXClientWrapper:
    async_client: httpx.AsyncClient = None

    def start(self):
        self.async_client = httpx.AsyncClient(timeout=30)

    async def stop(self):
        await self.async_client.aclose()
        self.async_client = None

    def __call__(self):
        assert self.async_client is not None
        return self.async_client


httpx_client_wrapper = HTTPXClientWrapper()


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

    host = os.environ.get('A2A_UI_HOST', '0.0.0.0')
    preferred_port = int(os.environ.get('A2A_UI_PORT', '8888'))
    
    def is_port_available(port_to_check):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port_to_check))
                return True
        except OSError:
            return False
    
    if is_port_available(preferred_port):
        port = preferred_port
        print(f"✅ Usando porta: {port}")
    else:
        port = 8889
        print(f"⚠️  Porta {preferred_port} em uso, usando: {port}")
    
    host_agent_service.server_url = f'http://{host}:{port}'
    print(f"🚀 Servidor responsivo em http://{host}:{port}")
    print(f"📱 Usando estilos inline do Mesop (sem CSS externo)")

    uvicorn.run(
        app,
        host=host,
        port=port,
        timeout_graceful_shutdown=0,
    )