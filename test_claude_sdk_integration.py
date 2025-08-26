#!/usr/bin/env python3
"""
Teste de integração do Claude SDK no projeto ui-mesop-py
"""

import asyncio
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_claude_sdk():
    """Testa a integração do Claude SDK."""
    print("=" * 60)
    print("🧪 TESTE DE INTEGRAÇÃO CLAUDE SDK")
    print("=" * 60)
    
    # 1. Testar importação do SDK
    print("\n1️⃣ Testando importação do Claude SDK...")
    try:
        from claude_code_sdk import ClaudeSDKClient
        print("   ✅ Claude SDK importado com sucesso")
    except ImportError as e:
        print(f"   ❌ Erro ao importar SDK: {e}")
        return False
    
    # 2. Testar cliente customizado
    print("\n2️⃣ Testando cliente customizado...")
    try:
        from agents.claude_client import ClaudeClientV10
        client = ClaudeClientV10()
        await client.initialize()
        print("   ✅ Cliente customizado inicializado")
    except Exception as e:
        print(f"   ❌ Erro no cliente customizado: {e}")
        return False
    
    # 3. Testar conexão
    print("\n3️⃣ Testando conexão com Claude...")
    try:
        is_connected = await client.test_connection()
        if is_connected:
            print("   ✅ Conexão com Claude funcionando")
        else:
            print("   ⚠️ Conexão com Claude não disponível")
    except Exception as e:
        print(f"   ❌ Erro ao testar conexão: {e}")
    
    # 4. Testar Runner
    print("\n4️⃣ Testando ClaudeRunner...")
    try:
        from agents.claude_runner import ClaudeRunner
        runner = ClaudeRunner(app_name="test_app")
        await runner.initialize()
        print("   ✅ ClaudeRunner inicializado")
        
        # Testar execução simples
        result = await runner.run_async("Olá, teste!")
        print(f"   ✅ Runner executou: {str(result)[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro no Runner: {e}")
    
    # 5. Testar Host Manager
    print("\n5️⃣ Testando ClaudeADKHostManager...")
    try:
        from service.server.claude_adk_host_manager import ClaudeADKHostManager
        import httpx
        
        async with httpx.AsyncClient() as http_client:
            manager = ClaudeADKHostManager(http_client)
            # Criar conversa
            conv = await manager.create_conversation()
            print(f"   ✅ Conversa criada: {conv.conversationId[:8]}...")
            
            # Simular mensagem
            from a2a.types import Message, TextPart, Role
            message = Message(
                messageId="test-msg",
                contextId=conv.conversationId,
                role=Role.user,
                parts=[TextPart(text="Teste de mensagem")]
            )
            
            # Processar mensagem
            print("   🔄 Processando mensagem de teste...")
            response = await manager.process_message(message)
            print(f"   ✅ Mensagem processada: {type(response)}")
            
    except Exception as e:
        print(f"   ❌ Erro no Host Manager: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_claude_sdk())
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)