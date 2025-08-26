#!/usr/bin/env python3
"""
Teste direto do Claude Code SDK Python.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar SDK ao path
SDK_PATH = Path("/home/codable/terminal/claude-code-sdk-python/src")
sys.path.insert(0, str(SDK_PATH))

print("🧪 Teste Direto do Claude Code SDK")
print("=" * 60)

# Teste 1: Importação
try:
    from claude_code_sdk import query, __version__
    from claude_code_sdk.client import ClaudeSDKClient
    print(f"✅ SDK importado! Versão: {__version__}")
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    sys.exit(1)

# Teste 2: Query simples (one-shot)
async def test_query():
    """Testa query one-shot."""
    print("\n📤 Testando query one-shot...")
    
    try:
        response_count = 0
        async for message in query(prompt="Responda apenas: OK"):
            response_count += 1
            print(f"   Resposta {response_count}: {message}")
            
            # Limitar para evitar loop infinito
            if response_count >= 3:
                break
        
        if response_count > 0:
            print(f"✅ Query funcionou! ({response_count} respostas)")
            return True
        else:
            print("❌ Sem resposta")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# Executar teste
print("\n🚀 Executando teste...")
try:
    # Usar timeout para evitar travamento
    result = asyncio.wait_for(
        test_query(),
        timeout=10.0
    )
    success = asyncio.run(result)
except asyncio.TimeoutError:
    print("⏱️ Timeout - Claude não respondeu em 10 segundos")
    print("   Isso pode significar que o Claude CLI não está ativo")
    success = False
except Exception as e:
    print(f"❌ Erro geral: {e}")
    success = False

print("\n" + "=" * 60)
if success:
    print("✅ SDK FUNCIONANDO COM CLAUDE REAL!")
    print("   O Claude Code SDK está conectado ao CLI local")
else:
    print("⚠️ SDK disponível mas Claude CLI não responde")
    print("   Verifique se o Claude está rodando: claude --version")

sys.exit(0 if success else 1)