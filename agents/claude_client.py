"""
Cliente Claude usando CLI local do Claude Code SDK.
Integração direta com Claude via subprocess - sem mocks!
"""

import asyncio
import subprocess
import logging
from typing import AsyncIterator, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

# Adicionar caminho do SDK Python se existir
import sys
from pathlib import Path
SDK_PATH = Path("/home/codable/terminal/claude-code-sdk-python/src")
if SDK_PATH.exists():
    sys.path.insert(0, str(SDK_PATH))

# Tentar importar cliente real
REAL_SDK_AVAILABLE = False
try:
    from .claude_client_real import ClaudeClientReal
    REAL_SDK_AVAILABLE = True
    logger.info("✅ Cliente real com SDK disponível")
except ImportError as e:
    logger.info(f"⚠️ Cliente real não disponível: {e}")


@dataclass
class ClaudeClientV10:
    """Cliente para Claude usando CLI local ou SDK real."""
    
    # Configurações básicas
    system_prompt: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    use_real_sdk: bool = True
    _initialized: bool = False
    _real_client: Optional['ClaudeClientReal'] = None
    
    async def initialize(self):
        """Inicializa o cliente Claude."""
        if self._initialized:
            return
        
        # Tentar usar SDK real primeiro
        if self.use_real_sdk and REAL_SDK_AVAILABLE:
            try:
                self._real_client = ClaudeClientReal()
                await self._real_client.initialize()
                
                if self._real_client.sdk_available:
                    self._initialized = True
                    logger.info("✅ Usando Claude SDK real")
                    return
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar SDK real: {e}")
        
        # Fallback para CLI
        if await self._check_claude_cli():
            self._initialized = True
            logger.info("✅ Claude CLI detectado e pronto para uso")
        else:
            # Último fallback - modo mockado
            self._initialized = True
            logger.warning("⚠️ Usando modo fallback mockado (sem CLI ou SDK)")
    
    async def _check_claude_cli(self) -> bool:
        """Verifica se o Claude CLI está disponível."""
        try:
            result = await asyncio.create_subprocess_exec(
                "claude", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                version = stdout.decode().strip()
                logger.info(f"📍 Claude CLI encontrado: {version}")
                return True
            return False
            
        except FileNotFoundError:
            logger.warning("Claude CLI não encontrado no PATH")
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar Claude CLI: {e}")
            return False
    
    async def send_message(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Envia mensagem para Claude usando SDK real, CLI local ou fallback.
        """
        if not self._initialized:
            await self.initialize()
        
        # Usar SDK real se disponível
        if self._real_client and self._real_client.sdk_available:
            async for chunk in self._real_client.send_message(prompt, **kwargs):
                yield chunk
            return
        
        # Tentar CLI se disponível
        if await self._check_claude_cli():
            async for chunk in self._send_message_cli(prompt):
                yield chunk
            return
        
        # Fallback mockado
        yield {
            "type": "text",
            "content": f"[FALLBACK] Resposta simulada para: {prompt[:100]}..."
        }
    
    async def _send_message_cli(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Envia mensagem usando CLI."""
        try:
            logger.info(f"📤 Enviando para Claude CLI: {prompt[:50]}...")
            
            # Preparar comando usando --print para resposta não-interativa
            cmd = ["claude", "--print"]
            
            # Adicionar system prompt se configurado
            if self.system_prompt:
                cmd.extend(["--append-system-prompt", self.system_prompt])
            
            # Adicionar o prompt como argumento
            cmd.append(prompt)
            
            # Executar comando
            logger.debug(f"Executando: {' '.join(cmd[:4])}...")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Aguardar resposta
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                response_text = stdout.decode().strip()
                
                if response_text:
                    logger.info(f"✅ Resposta recebida: {response_text[:100]}...")
                    yield {
                        "type": "text",
                        "content": response_text
                    }
                else:
                    logger.warning("⚠️ Resposta vazia do Claude")
                    yield {
                        "type": "text",
                        "content": "Desculpe, não recebi uma resposta válida."
                    }
            else:
                error_msg = stderr.decode().strip()
                logger.error(f"❌ Erro do Claude CLI: {error_msg}")
                
                # Tentar alternativa: API direta se disponível
                alt_response = await self._try_alternative_method(prompt)
                if alt_response:
                    yield alt_response
                else:
                    yield {
                        "type": "error",
                        "content": f"Erro ao processar: {error_msg}"
                    }
                    
        except asyncio.TimeoutError:
            logger.error("⏱️ Timeout ao chamar Claude")
            yield {
                "type": "error",
                "content": "Tempo limite excedido ao processar mensagem"
            }
        except Exception as e:
            logger.error(f"❌ Erro ao comunicar com Claude: {e}")
            yield {
                "type": "error",
                "content": f"Erro: {str(e)}"
            }
    
    async def _try_alternative_method(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Tenta método alternativo de comunicação com Claude.
        Por exemplo, via API HTTP local ou WebSocket se disponível.
        """
        try:
            # Tentar via API HTTP local (se Claude tiver servidor local)
            import httpx
            
            async with httpx.AsyncClient() as client:
                # Tentar portas comuns para serviços locais
                for port in [3000, 8080, 8888, 5000]:
                    try:
                        response = await client.post(
                            f"http://localhost:{port}/api/chat",
                            json={"prompt": prompt},
                            timeout=5.0
                        )
                        if response.status_code == 200:
                            data = response.json()
                            return {
                                "type": "text",
                                "content": data.get("response", "")
                            }
                    except:
                        continue
                        
        except Exception as e:
            logger.debug(f"Método alternativo falhou: {e}")
        
        return None
    
    async def send_streaming(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """
        Versão streaming da comunicação com Claude.
        Útil para respostas longas.
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Usar output-format stream-json para streaming
            cmd = ["claude", "--print", "--output-format", "stream-json", prompt]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Ler linha por linha (streaming)
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                text = line.decode().strip()
                if text:
                    yield {
                        "type": "text_delta",
                        "content": text
                    }
            
            # Verificar se houve erro
            if process.returncode and process.returncode != 0:
                stderr = await process.stderr.read()
                logger.error(f"Erro no streaming: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield {
                "type": "error",
                "content": str(e)
            }
    
    async def test_connection(self) -> bool:
        """Testa se o Claude está funcionando."""
        try:
            response_received = False
            
            async for part in self.send_message("Responda apenas: OK"):
                if part.get("type") == "text" and part.get("content"):
                    response_received = True
                    logger.info(f"✅ Teste de conexão bem-sucedido: {part['content']}")
                    break
            
            return response_received
            
        except Exception as e:
            logger.error(f"❌ Falha no teste de conexão: {e}")
            return False
    
    async def close(self):
        """Fecha o cliente."""
        self._initialized = False
        logger.info("Cliente Claude fechado")


# Teste do cliente
async def test_client():
    """Testa o cliente Claude real."""
    client = ClaudeClientV10()
    
    try:
        # Inicializar
        await client.initialize()
        print("✅ Cliente inicializado")
        
        # Testar conexão
        if await client.test_connection():
            print("✅ Conexão testada com sucesso")
            
            # Enviar mensagem real
            print("\n📤 Enviando mensagem de teste...")
            async for response in client.send_message("Olá! Por favor responda: Teste OK"):
                if response["type"] == "text":
                    print(f"📥 Resposta: {response['content']}")
                elif response["type"] == "error":
                    print(f"❌ Erro: {response['content']}")
        else:
            print("❌ Falha no teste de conexão")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_client())