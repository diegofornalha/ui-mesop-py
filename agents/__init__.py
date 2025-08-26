"""
Módulo de agentes Claude - Componentes para integração com Claude AI.
Substitui completamente o uso de Google Gemini/ADK.
"""

# Cliente básico do Claude
from .claude_client import ClaudeClientV10

# Runner compatível com ADK
from .claude_runner import ClaudeRunner

# Serviços In-Memory
from .claude_services import (
    ClaudeSessionService,
    ClaudeMemoryService,
    ClaudeArtifactService,
    ClaudeEvent,
    ClaudeEventActions,
    ClaudeArtifact
)

# Conversores de mensagens
from .claude_converters import (
    claude_content_from_message,
    claude_content_to_message,
    build_claude_context,
    extract_text_from_message,
    batch_convert_to_claude,
    batch_convert_from_claude
)

# Host Manager
from .claude_host_manager import ClaudeHostManager

__all__ = [
    # Cliente
    'ClaudeClientV10',
    
    # Runner
    'ClaudeRunner',
    
    # Serviços
    'ClaudeSessionService',
    'ClaudeMemoryService',
    'ClaudeArtifactService',
    'ClaudeEvent',
    'ClaudeEventActions',
    'ClaudeArtifact',
    
    # Conversores
    'claude_content_from_message',
    'claude_content_to_message',
    'build_claude_context',
    'extract_text_from_message',
    'batch_convert_to_claude',
    'batch_convert_from_claude',
    
    # Manager
    'ClaudeHostManager'
]

# Versão do módulo
__version__ = '1.0.0'