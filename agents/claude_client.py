"""
Cliente Claude usando o SDK oficial claude-code-sdk.
Integração completa com Claude Code via SDK Python.
"""

import asyncio
import logging
from typing import AsyncIterator, Optional, Dict, Any
from dataclasses import dataclass

# Importar o SDK real do Claude Code
try:
    from claude_code_sdk import query, ClaudeCodeOptions
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False
    logging.warning("⚠️ Claude SDK não disponível - instale com: pip install claude-code-sdk")

logger = logging.getLogger(__name__)

@dataclass
class ClaudeClientV10:
    """Cliente para Claude usando SDK oficial."""
    
    # Configurações básicas
    system_prompt: str = "You are a helpful AI assistant. Respond in Portuguese (pt-BR) when appropriate."
    max_thinking_tokens: int = 8000  # Parâmetro correto do Claude SDK
    _client: Optional[Any] = None
    _initialized: bool = False
    
    @property
    def is_initialized(self) -> bool:
        """Verifica se o cliente está inicializado."""
        return self._initialized and self._client is not None
    
    async def initialize(self):
        """Inicializa o cliente Claude SDK."""
        if self._initialized:
            return
            
        if not CLAUDE_SDK_AVAILABLE:
            logger.error("Claude SDK não está instalado!")
            raise ImportError("Claude SDK não disponível. Execute: pip install claude-code-sdk")
        
        try:
            # Cliente será criado quando necessário usando context manager
            self._initialized = True
            logger.info("✅ ClaudeClientV10 inicializado (SDK disponível)")
        except Exception as e:
            logger.error(f"Erro ao inicializar Claude SDK: {e}")
            raise
    
    async def send_message(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Envia mensagem para Claude usando o SDK oficial.
        """
        if not self._initialized:
            await self.initialize()
        
        if not CLAUDE_SDK_AVAILABLE:
            yield {
                "type": "error",
                "content": "Claude SDK não instalado"
            }
            return
        
        try:
            logger.info(f"📤 Enviando mensagem para Claude: {prompt[:50]}...")
            
            # Configurar opções (ClaudeCodeOptions tem parâmetros limitados)
            options = ClaudeCodeOptions(
                system_prompt=self.system_prompt,
                max_thinking_tokens=self.max_thinking_tokens
            )
            
            # Enviar query usando o método correto
            response_text = ""
            async for message in query(prompt=prompt, options=options):
                # Log do tipo de mensagem
                logger.debug(f"Tipo de mensagem recebida: {type(message).__name__}")
                
                # Processar diferentes tipos de mensagem baseado na classe
                if hasattr(message, '__class__'):
                    class_name = message.__class__.__name__
                    
                    if class_name == 'AssistantMessage':
                        # Extrair texto do AssistantMessage
                        if hasattr(message, 'content') and message.content:
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    response_text += block.text
                                    logger.debug(f"Texto extraído: {block.text[:50]}...")
                    
                    elif class_name == 'SystemMessage':
                        # Ignorar mensagens do sistema
                        logger.debug(f"Mensagem do sistema recebida: {message.subtype if hasattr(message, 'subtype') else 'unknown'}")
                    
                    elif class_name == 'ResultMessage':
                        # Log do resultado mas não adicionar ao texto
                        if hasattr(message, 'result'):
                            logger.debug(f"Resultado final: {str(message.result)[:100]}...")
            
            if response_text:
                logger.info(f"✅ Resposta completa recebida: {response_text[:100]}...")
                yield {
                    "type": "text",
                    "content": response_text
                }
            else:
                logger.warning("⚠️ Nenhuma resposta recebida do Claude")
                yield {
                    "type": "text",
                    "content": "Desculpe, não recebi resposta."
                }
                    
        except Exception as e:
            logger.error(f"❌ Erro ao comunicar com Claude SDK: {e}")
            yield {
                "type": "error",
                "content": f"Erro: {str(e)}"
            }

    async def test_connection(self) -> bool:
        """Testa se o Claude SDK está funcionando."""
        try:
            if not CLAUDE_SDK_AVAILABLE:
                logger.warning("Claude SDK não disponível")
                return False
            
            # Testar com uma query simples
            options = ClaudeCodeOptions()  # Usar opções padrão
            response_received = False
            
            async for message in query(prompt="Say OK", options=options):
                response_received = True
                break  # Só precisamos saber se funcionou
            
            if response_received:
                logger.info("✅ Conexão com Claude SDK testada com sucesso")
                return True
            else:
                logger.warning("⚠️ Claude SDK não respondeu ao teste")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar Claude SDK: {e}")
            return False
    
    async def close(self):
        """Fecha o cliente se necessário."""
        self._client = None
        self._initialized = False
        logger.info("Cliente Claude fechado")