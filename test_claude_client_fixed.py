#!/usr/bin/env python3
"""
Testa o ClaudeClientV10 corrigido
"""

import asyncio
import logging
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Adicionar ao path
sys.path.insert(0, os.path.dirname(__file__))

async def test_client():
    """Testa o cliente Claude corrigido"""
    print("="*60)
    print("TESTE DO CLIENTE CLAUDE CORRIGIDO")
    print("="*60)
    
    try:
        # Importar com venv ativado
        from agents.claude_client import ClaudeClientV10
        
        print("\n1. Criando cliente...")
        client = ClaudeClientV10(system_prompt="Responda em português.")
        
        print("2. Inicializando...")
        await client.initialize()
        
        print("3. Testando conexão...")
        if await client.test_connection():
            print("   ✅ Conexão OK")
        else:
            print("   ❌ Falha na conexão")
            return False
        
        print("\n4. Enviando mensagem de teste...")
        response_text = ""
        async for part in client.send_message("Olá! Responda apenas: TESTE OK"):
            if part.get("type") == "text":
                response_text += part.get("content", "")
            elif part.get("type") == "error":
                print(f"   ❌ Erro: {part.get('content')}")
                return False
        
        if response_text:
            print(f"   ✅ Claude respondeu: {response_text[:100]}...")
            return True
        else:
            print("   ❌ Sem resposta")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Executa o teste"""
    success = await test_client()
    
    print("\n" + "="*60)
    if success:
        print("✅ TESTE PASSOU - CLIENTE FUNCIONANDO!")
    else:
        print("❌ TESTE FALHOU - VERIFIQUE OS LOGS")
    print("="*60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)