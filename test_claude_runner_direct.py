#!/usr/bin/env python3
"""
Teste direto do ClaudeRunner para verificar se está funcionando
"""

import asyncio
import os
import sys

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

async def test_runner():
    """Testa o ClaudeRunner diretamente"""
    print("="*60)
    print("TESTE DIRETO DO CLAUDE RUNNER")
    print("="*60)
    
    try:
        from agents.claude_runner import ClaudeRunner
        from agents.claude_services import (
            ClaudeSessionService,
            ClaudeMemoryService,
            ClaudeArtifactService
        )
        
        print("\n1. Criando ClaudeRunner...")
        runner = ClaudeRunner(
            app_name="TestApp",
            session_service=ClaudeSessionService(),
            memory_service=ClaudeMemoryService(),
            artifact_service=ClaudeArtifactService()
        )
        
        print("2. Inicializando...")
        await runner.initialize()
        print(f"   Inicializado: {runner.is_initialized}")
        
        print("\n3. Enviando mensagem de teste...")
        result = await runner.run_async(
            prompt="Olá! Responda apenas: TESTE OK",
            session_id="test-session"
        )
        
        print(f"\n4. Resultado:")
        print(f"   Type: {type(result)}")
        print(f"   Content: {result}")
        
        if result and "response" in result:
            print(f"\n✅ SUCESSO! Claude respondeu: {result['response'][:100]}...")
        else:
            print(f"\n❌ FALHA! Sem resposta do Claude")
        
        runner.close()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_runner())