#!/usr/bin/env python3
"""
Teste direto do Claude SDK.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar SDK ao path
SDK_PATH = Path("/home/codable/terminal/claude-code-sdk-python/src")
sys.path.insert(0, str(SDK_PATH))

from claude_code_sdk import query
from claude_code_sdk.client import ClaudeSDKClient
from claude_code_sdk.types import Message

async def test_claude_direct():
    """Testa comunicação direta com Claude."""
    print("🔧 Testando Claude SDK direto...")
    
    try:
        # Teste 1: Query simples
        print("\n📝 Teste 1: Query simples")
        async for message in query(prompt="Olá! Responda apenas: 'SDK funcionando!'"):
            print(f"✅ Resposta: {message}")
            break
        
        # Teste 2: Sessão interativa
        print("\n📝 Teste 2: Sessão com ClaudeSDKClient")
        async with ClaudeSDKClient() as client:
            # Enviar mensagem
            await client.query("Quanto é 2+2? Responda apenas o número.")
            
            # Receber resposta
            async for message in client.receive_messages():
                if message:
                    print(f"✅ Mensagem recebida: {message}")
                    break
        
        print("\n✅ Todos os testes passaram!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_claude_direct())
    sys.exit(0 if result else 1)