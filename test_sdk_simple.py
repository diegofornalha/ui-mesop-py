#!/usr/bin/env python3
"""
Teste simples e direto do Claude SDK.
"""

import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def test_direct():
    """Teste direto do SDK."""
    print("🧪 Teste Direto do Claude SDK")
    print("-" * 40)
    
    try:
        # Configuração simples
        options = ClaudeCodeOptions(
            system_prompt="Responda sempre em português."
        )
        
        # Query simples
        print("📤 Enviando: 'Diga apenas OK'")
        
        response_count = 0
        async for message in query(prompt="Diga apenas OK", options=options):
            response_count += 1
            print(f"📨 Resposta {response_count}: {type(message).__name__}")
            
            # Tentar extrair texto
            if hasattr(message, 'content'):
                if isinstance(message.content, str):
                    print(f"   Texto: {message.content}")
                elif isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            print(f"   Texto: {block.text}")
            
            # Parar após 3 mensagens
            if response_count >= 3:
                break
        
        if response_count > 0:
            print(f"\n✅ SDK funcionando! ({response_count} mensagens recebidas)")
            return True
        else:
            print("\n❌ Nenhuma resposta recebida")
            return False
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct())
    exit(0 if success else 1)