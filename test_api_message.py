#!/usr/bin/env python3
"""
Teste de envio de mensagem via API
Simula o caso exato do erro: messageid em minúsculo
"""

import json
import httpx
import asyncio
from datetime import datetime

async def test_message_api():
    """Testa envio de mensagem com campo problemático"""
    
    print("=" * 60)
    print("🎯 TESTE DE API - ENVIANDO MENSAGEM")
    print("=" * 60)
    
    # Dados exatos que causavam o erro
    message_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "messageid": "404bddf0-d123-4567-8901-234567890abc",  # minúsculo!
            "text": "oi",  # usando text em vez de content
            "timestamp": datetime.now().timestamp()
        }
    }
    
    print(f"\n📤 Enviando mensagem com:")
    print(f"   messageid: {message_data['params']['messageid']}")
    print(f"   text: {message_data['params']['text']}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8888/message/send",
                json=message_data,
                timeout=5.0
            )
            
            print(f"\n📥 Resposta do servidor:")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCESSO! Mensagem aceita")
                print(f"   Resposta: {json.dumps(result, indent=2)}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
    except httpx.ConnectError:
        print("\n⚠️  Servidor não está rodando em http://localhost:8888")
        print("   Execute primeiro: .venv/bin/python3 main.py")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

    print("\n" + "=" * 60)
    print("💡 RESULTADO:")
    print("=" * 60)
    print("""
Se o teste passou:
✅ O patch está funcionando em produção
✅ Mensagens com 'messageid' são aceitas
✅ O erro foi completamente resolvido

Se falhou:
❌ Verificar se o patch está sendo importado
❌ Verificar logs do servidor
❌ Confirmar que main.py tem: import message_patch
    """)

if __name__ == "__main__":
    asyncio.run(test_message_api())