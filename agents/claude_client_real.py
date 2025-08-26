"""
Cliente real do Claude usando claude-code-sdk.
NÃO PRECISA DE API KEY - usa o Claude CLI local já autenticado!
"""

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Adicionar caminho do SDK Python local
SDK_PATH = Path("/home/codable/terminal/claude-code-sdk-python/src")
if SDK_PATH.exists():
    sys.path.insert(0, str(SDK_PATH))
    logger.info(f"✅ Adicionado caminho do SDK: {SDK_PATH}")

# Verificar disponibilidade do SDK
SDK_AVAILABLE = False

try:
    from claude_code_sdk import query
    from claude_code_sdk.client import ClaudeSDKClient
    from claude_code_sdk.types import Message
    SDK_AVAILABLE = True
    logger.info("✅ Claude Code SDK Python disponível")
except ImportError as e:
    logger.warning(f"⚠️ Claude Code SDK não disponível: {e}")


@dataclass
class ClaudeClientReal:
    """Cliente real do Claude com SDK - usa CLI local autenticado."""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self.sdk_available = SDK_AVAILABLE
    
    async def initialize(self):
        """Inicializa o cliente Claude real."""
        if not self.sdk_available:
            logger.info("❌ SDK não disponível - usando modo fallback")
            self.initialized = True
            return
        
        try:
            # Cliente não precisa ser inicializado, será criado no contexto
            self.initialized = True
            logger.info("✅ Cliente Claude SDK pronto (usando CLI local)")
            
        except Exception as e:
            logger.error(f"⚠️ Erro ao inicializar SDK: {e}")
            self.sdk_available = False
            self.initialized = True
    
    async def send_message(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Envia mensagem para Claude real usando SDK.
        Usa o Claude CLI local já autenticado - não precisa API key!
        """
        if not self.sdk_available:
            # Fallback mockado
            yield {
                "type": "text",
                "content": f"[FALLBACK] Resposta simulada para: {prompt[:50]}..."
            }
            return
        
        try:
            # Método 1: Usar ClaudeSDKClient (preferido para sessões)
            if kwargs.get("use_session", True):
                async with ClaudeSDKClient() as client:
                    # Enviar mensagem usando query
                    await client.query(prompt)
                    
                    # Receber resposta
                    async for message in client.receive_messages():
                        if message and hasattr(message, 'content'):
                            # Processar content da mensagem
                            if isinstance(message.content, list):
                                for part in message.content:
                                    if hasattr(part, 'text'):
                                        yield {
                                            "type": "text",
                                            "content": part.text
                                        }
                            else:
                                yield {
                                    "type": "text",
                                    "content": str(message.content)
                                }
                        
                        # Parar após primeira resposta completa
                        if message and hasattr(message, 'stop_reason'):
                            break
            
            # Método 2: Usar query (para one-shot)
            else:
                response_text = ""
                async for message in query(prompt=prompt):
                    # Processar mensagem
                    if isinstance(message, Message):
                        if hasattr(message, 'content') and message.content:
                            for part in message.content:
                                if hasattr(part, 'text'):
                                    response_text += part.text
                                    
                        # Yield parcial para streaming
                        if response_text:
                            yield {
                                "type": "text",
                                "content": response_text
                            }
                            response_text = ""  # Limpar para próximo chunk
                    else:
                        # Mensagem simples
                        yield {
                            "type": "text",
                            "content": str(message)
                        }
                        
        except Exception as e:
            logger.error(f"❌ Erro ao chamar Claude SDK: {e}")
            yield {
                "type": "error",
                "content": f"Erro: {str(e)}"
            }
    
    async def send_message_simple(self, prompt: str) -> str:
        """Versão simples sem streaming."""
        response = ""
        async for chunk in self.send_message(prompt, use_session=False):
            if chunk.get("type") == "text":
                response += chunk.get("content", "")
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do cliente."""
        return {
            "available": self.sdk_available,
            "type": "python_sdk",
            "initialized": self.initialized,
            "uses_cli": True,  # Sempre usa CLI local
            "needs_api_key": False  # NÃO precisa API key!
        }