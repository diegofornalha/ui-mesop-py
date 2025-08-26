"""
Claude Host Manager V10 - Integração com ADKRunner.
Versão simplificada sem API key, usando Claude CLI local.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime

from .claude_client import ClaudeClientV10

logger = logging.getLogger(__name__)

@dataclass  
class ClaudeHostManager:
    """Host Manager para integração Claude com ADKRunner."""
    
    # Cliente Claude
    client: ClaudeClientV10 = field(default_factory=ClaudeClientV10)
    
    # Estado básico
    active_sessions: Dict[str, Dict] = field(default_factory=dict)
    message_history: List[Dict] = field(default_factory=list)
    
    async def initialize(self):
        """Inicializa o host manager."""
        logger.info("Inicializando Claude Host Manager V10 (CLI sem API key)")
        
        # Verificar se CLI está funcionando
        if await self.client.test_connection():
            logger.info("✅ Claude CLI conectado e funcionando!")
        else:
            logger.warning("⚠️ Claude CLI não detectado. Instale com: npm install -g @anthropic-ai/claude-code")
        
        return self
    
    async def process_message(self, 
                             session_id: str,
                             message: str,
                             context: Optional[Dict] = None) -> AsyncIterator[Dict]:
        """Processa mensagem usando Claude CLI."""
        
        # Registrar sessão se nova
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                'created_at': datetime.now().isoformat(),
                'message_count': 0
            }
        
        # Atualizar contador
        self.active_sessions[session_id]['message_count'] += 1
        
        # Adicionar contexto se fornecido
        if context:
            full_prompt = f"Context: {json.dumps(context)}\n\nUser: {message}"
        else:
            full_prompt = message
        
        # Salvar no histórico
        self.message_history.append({
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': message
        })
        
        try:
            # Processar com Claude (sem API key!)
            response_parts = []
            async for part in self.client.send_message(full_prompt):
                response_parts.append(part)
                yield part
            
            # Salvar resposta no histórico
            self.message_history.append({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'assistant_response': response_parts
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            yield {
                "type": "error",
                "content": f"Erro: {str(e)}"
            }
    
    async def handle_adk_event(self, event: Dict) -> Dict:
        """Processa evento do ADKRunner e retorna resposta."""
        event_type = event.get('type', '')
        
        if event_type == 'message':
            # Processar mensagem
            session_id = event.get('session_id', 'default')
            content = event.get('content', '')
            
            responses = []
            async for response in self.process_message(session_id, content):
                responses.append(response)
            
            return {
                'type': 'response',
                'session_id': session_id,
                'content': responses
            }
        
        elif event_type == 'status':
            # Retornar status do sistema
            return {
                'type': 'status_response',
                'active_sessions': len(self.active_sessions),
                'total_messages': len(self.message_history),
                'cli_status': 'operational' if await self.client.test_connection() else 'not_connected',
                'api_key_required': False  # Claude CLI não precisa!
            }
        
        else:
            return {
                'type': 'unknown_event',
                'original': event
            }
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Retorna histórico de uma sessão."""
        return [
            msg for msg in self.message_history 
            if msg.get('session_id') == session_id
        ]
    
    async def cleanup(self):
        """Limpeza de recursos."""
        logger.info("Finalizando Claude Host Manager")
        self.active_sessions.clear()
        self.message_history.clear()


# Exemplo de uso e teste
async def test_claude_host():
    """Testa o Host Manager."""
    logging.basicConfig(level=logging.INFO)
    
    # Criar e inicializar
    host = await ClaudeHostManager().initialize()
    
    # Testar mensagem simples
    print("\n🧪 Testando Claude Host Manager...")
    async for response in host.process_message(
        session_id="test-001",
        message="Responda apenas: SISTEMA FUNCIONANDO"
    ):
        if response.get('type') == 'text':
            print(f"✅ Resposta: {response.get('content')}")
    
    # Testar evento ADK
    event = {
        'type': 'status'
    }
    
    result = await host.handle_adk_event(event)
    print(f"📊 Status: {result}")
    
    # Cleanup
    await host.cleanup()
    print("✅ Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_claude_host())