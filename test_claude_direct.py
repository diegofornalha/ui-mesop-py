#!/usr/bin/env python3
"""
Teste direto do Claude Code SDK para verificar se está funcionando.
"""

import asyncio
import logging
from claude_code_sdk import query, ClaudeCodeOptions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_claude_sdk():
    """Testa o Claude SDK diretamente."""
    print("🧪 Testando Claude Code SDK diretamente...")
    
    try:
        # Configurar opções
        options = ClaudeCodeOptions(
            system_prompt="Você é um assistente útil. Responda de forma breve.",
            max_thinking_tokens=1000
        )
        
        print("📤 Enviando prompt: 'Responda apenas: TESTE OK'")
        
        # Query Claude
        response_text = ""
        async for message in query(
            prompt="Responda apenas: TESTE OK",
            options=options
        ):
            print(f"   Tipo da mensagem: {type(message)}")
            print(f"   Conteúdo: {message}")
            
            # Verificar diferentes tipos de mensagem
            if hasattr(message, 'content'):
                response_text += str(message.content)
                print(f"   Extraído: {message.content}")
        
        print(f"\n✅ Resposta completa: {response_text}")
        
        if response_text:
            print("✅ Claude SDK está funcionando!")
            return True
        else:
            print("❌ Claude SDK não retornou resposta")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Claude SDK: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = asyncio.run(test_claude_sdk())
    exit(0 if result else 1)