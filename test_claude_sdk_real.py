#!/usr/bin/env python3
"""
Teste da integração real com Claude SDK.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.claude_client import ClaudeClientV10

async def test_real_sdk():
    """Testa integração real com Claude SDK."""
    print("=" * 60)
    print("🧪 TESTE: Integração Real com Claude SDK")
    print("=" * 60)
    
    # Criar cliente com SDK real
    client = ClaudeClientV10(use_real_sdk=True)
    await client.initialize()
    
    # Verificar status
    if hasattr(client, '_real_client') and client._real_client:
        status = client._real_client.get_status()
        print(f"\n📊 Status do SDK:")
        print(f"   Disponível: {status['available']}")
        print(f"   Tipo: {status['type']}")
        print(f"   Usa CLI local: {'✅ Sim' if status.get('uses_cli') else '❌ Não'}")
        print(f"   Precisa API Key: {'❌ NÃO!' if not status.get('needs_api_key') else '⚠️ Sim'}")
    
    # Testar mensagem simples
    print("\n📤 Enviando mensagem de teste...")
    prompt = "Olá! Responda em uma linha curta."
    
    response = ""
    chunk_count = 0
    
    async for chunk in client.send_message(prompt):
        if chunk.get("type") == "text":
            text = chunk.get("content", "")
            response += text
            chunk_count += 1
            if chunk_count == 1:
                print(f"   Primeiro chunk: {text[:50]}...")
    
    print(f"\n📥 Resposta completa ({chunk_count} chunk(s)):")
    print(f"   {response[:200]}...")
    
    # Verificar se é resposta real ou fallback
    is_fallback = "[FALLBACK]" in response
    
    if is_fallback:
        print("\n⚠️ AVISO: Usando fallback mockado")
        print("\n📋 Para usar o SDK real:")
        print("   1. O SDK já existe em: /home/codable/terminal/claude-code-sdk-python")
        print("   2. Claude CLI já está instalado: claude --version")
        print("   3. NÃO precisa API key - usa CLI local autenticado!")
        print("   4. Execute novamente este teste")
        return False
    else:
        print("\n✅ SUCESSO: SDK real funcionando!")
        return True

async def test_streaming():
    """Testa streaming real."""
    print("\n" + "=" * 60)
    print("🧪 TESTE: Streaming de Resposta")
    print("=" * 60)
    
    client = ClaudeClientV10(use_real_sdk=True)
    await client.initialize()
    
    prompt = "Conte de 1 a 5 lentamente, um número por linha."
    print(f"\n📤 Testando streaming: {prompt}")
    print("📥 Chunks recebidos:")
    
    chunk_count = 0
    async for chunk in client.send_message(prompt, stream=True):
        if chunk.get("type") == "text":
            chunk_count += 1
            content = chunk.get("content", "")
            print(f"   Chunk {chunk_count}: {content[:30]}...")
    
    if chunk_count > 1:
        print(f"\n✅ Streaming funcionando! ({chunk_count} chunks)")
        return True
    else:
        print(f"\n⚠️ Sem streaming real (apenas {chunk_count} chunk)")
        return False

async def main():
    """Executa todos os testes."""
    print("\n🎯 TESTE DE INTEGRAÇÃO COM CLAUDE SDK REAL")
    print("=" * 60)
    
    tests_passed = []
    
    # Teste 1: SDK básico
    try:
        result = await test_real_sdk()
        tests_passed.append(("SDK Real", result))
    except Exception as e:
        print(f"❌ Erro no teste SDK: {e}")
        tests_passed.append(("SDK Real", False))
    
    # Teste 2: Streaming (só se SDK disponível)
    if tests_passed[0][1]:  # Se primeiro teste passou
        try:
            result = await test_streaming()
            tests_passed.append(("Streaming", result))
        except Exception as e:
            print(f"❌ Erro no teste streaming: {e}")
            tests_passed.append(("Streaming", False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, passed in tests_passed:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in tests_passed)
    
    if all_passed:
        print("\n🎉 Todos os testes passaram! SDK real funcionando!")
    else:
        print("\n📝 Como ativar o SDK real:")
        print("   1. SDK Python: /home/codable/terminal/claude-code-sdk-python/src")
        print("   2. Claude CLI: já instalado (claude --version)")
        print("   3. NÃO precisa API key - usa CLI local!")
        print("   4. Executar: python3 test_claude_sdk_real.py")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)