#!/usr/bin/env python3
"""
Teste específico para validar integração do Claude SDK com o chat Mesop.
"""

import asyncio
import logging
import sys

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_sdk_import():
    """Testa importação do SDK."""
    print("\n1️⃣ Testando importação do Claude SDK...")
    try:
        from claude_code_sdk import query, ClaudeCodeOptions
        print("   ✅ Função query importada")
        print("   ✅ ClaudeCodeOptions importado")
        return True
    except ImportError as e:
        print(f"   ❌ Erro: {e}")
        return False

async def test_sdk_query():
    """Testa query simples com o SDK."""
    print("\n2️⃣ Testando query do SDK...")
    try:
        from claude_code_sdk import query, ClaudeCodeOptions
        
        options = ClaudeCodeOptions(
            max_tokens=100,
            temperature=0.7,
            max_turns=1
        )
        
        print("   🔄 Enviando query de teste...")
        response_received = False
        
        async for message in query(prompt="Diga apenas: OK", options=options):
            response_received = True
            print(f"   📨 Resposta: {type(message).__name__}")
            
            # Tentar extrair texto
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(f"   💬 Texto: {block.text[:50]}")
            break  # Parar após primeira resposta
        
        if response_received:
            print("   ✅ Query funcionou!")
            return True
        else:
            print("   ⚠️ Nenhuma resposta recebida")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_claude_client():
    """Testa o cliente Claude customizado."""
    print("\n3️⃣ Testando ClaudeClientV10...")
    try:
        from agents.claude_client import ClaudeClientV10
        
        client = ClaudeClientV10()
        await client.initialize()
        print("   ✅ Cliente inicializado")
        
        # Testar envio de mensagem
        print("   🔄 Enviando mensagem de teste...")
        response_text = ""
        
        async for response in client.send_message("Responda com: Teste OK"):
            if response["type"] == "text":
                response_text = response["content"]
                print(f"   💬 Resposta: {response_text[:100]}")
            elif response["type"] == "error":
                print(f"   ❌ Erro: {response['content']}")
        
        if response_text:
            print("   ✅ Cliente funcionando!")
            return True
        else:
            print("   ⚠️ Sem resposta do cliente")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro no cliente: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_chat_flow():
    """Testa o fluxo completo do chat."""
    print("\n4️⃣ Simulando fluxo do chat Mesop...")
    try:
        from agents.claude_runner import ClaudeRunner
        
        runner = ClaudeRunner(app_name="test_chat")
        await runner.initialize()
        print("   ✅ Runner inicializado")
        
        # Simular conversa
        session_id = "test-session"
        messages = [
            "Olá, você está funcionando?",
            "Qual é 2+2?",
            "Obrigado!"
        ]
        
        for msg in messages:
            print(f"\n   👤 Usuário: {msg}")
            result = await runner.run_async(msg, session_id)
            response = result.get("response", "")
            print(f"   🤖 Claude: {response[:100]}...")
            
            if not response:
                print("   ⚠️ Resposta vazia")
                return False
        
        print("\n   ✅ Fluxo do chat funcionando!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no fluxo: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 TESTE DE INTEGRAÇÃO CLAUDE SDK - CHAT MESOP")
    print("=" * 60)
    
    results = []
    
    # Executar testes
    results.append(("Importação SDK", await test_sdk_import()))
    results.append(("Query SDK", await test_sdk_query()))
    results.append(("Cliente Claude", await test_claude_client()))
    results.append(("Fluxo Chat", await test_chat_flow()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("O Claude SDK está pronto para o chat Mesop!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)