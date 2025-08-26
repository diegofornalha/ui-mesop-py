#!/usr/bin/env python3
"""
Teste completo da integração do Claude SDK com a arquitetura V2.
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar paths necessários
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/home/codable/terminal/claude-code-sdk-python/src")

print("=" * 60)
print("🧪 TESTE COMPLETO DE INTEGRAÇÃO")
print("=" * 60)

# Teste 1: SDK Python disponível
print("\n1️⃣ Testando disponibilidade do SDK Python...")
try:
    from claude_code_sdk import query, __version__
    from claude_code_sdk.client import ClaudeSDKClient
    print(f"   ✅ SDK Python: v{__version__}")
except ImportError as e:
    print(f"   ❌ SDK Python não disponível: {e}")

# Teste 2: Claude CLI disponível
print("\n2️⃣ Testando Claude CLI...")
import subprocess
try:
    result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"   ✅ Claude CLI: {result.stdout.strip()}")
    else:
        print(f"   ❌ Claude CLI erro: {result.stderr}")
except Exception as e:
    print(f"   ❌ Claude CLI não encontrado: {e}")

# Teste 3: Cliente Real V2
print("\n3️⃣ Testando Cliente Real V2...")
try:
    from agents.claude_client_real_v2 import ClaudeClientRealV2, ClaudeCodeOptions
    
    async def test_client_v2():
        client = ClaudeClientRealV2(
            ClaudeCodeOptions(
                system_prompt="Você é um assistente de teste. Responda brevemente.",
                max_turns=1
            )
        )
        
        await client.initialize()
        status = client.get_status()
        
        print(f"   Status: {status}")
        
        if status["available"]:
            # Testar mensagem
            response = ""
            async for chunk in client.send_message("Responda apenas: TESTE OK"):
                if chunk["type"] == "text":
                    response += chunk["content"]
            
            if response:
                print(f"   ✅ Resposta: {response[:50]}")
                return True
            else:
                print("   ⚠️ Sem resposta")
                return False
        else:
            print("   ❌ Cliente não disponível")
            return False
    
    result = asyncio.run(asyncio.wait_for(test_client_v2(), timeout=10))
    
except Exception as e:
    print(f"   ❌ Erro no Cliente V2: {e}")
    result = False

# Teste 4: Arquitetura V2
print("\n4️⃣ Testando Arquitetura V2...")
try:
    from agents.claude_runner_v2 import ClaudeRunner
    from agents.claude_a2a_agent_v2 import ClaudeA2AAgent
    from agents.claude_types import Content, Event, InvocationContext
    
    print("   ✅ Runner V2 importado")
    print("   ✅ Agent V2 importado")
    print("   ✅ Types V2 importados")
    
    # Testar criação
    agent = ClaudeA2AAgent(use_real_sdk=True)
    runner = ClaudeRunner(agent=agent, app_name="test")
    print("   ✅ Componentes V2 criados")
    
except Exception as e:
    print(f"   ❌ Erro na Arquitetura V2: {e}")

# Teste 5: Server V2
print("\n5️⃣ Testando Server V2...")
try:
    from service.server.server_v2 import ConversationServerV2
    print("   ✅ Server V2 importado")
    
    # Verificar se está usando SDK real
    import inspect
    source = inspect.getsource(ConversationServerV2.__init__)
    if "use_real_sdk=True" in source:
        print("   ✅ Server configurado para usar SDK real")
    else:
        print("   ⚠️ Server não configurado para SDK real")
        
except Exception as e:
    print(f"   ❌ Erro no Server V2: {e}")

# Resumo
print("\n" + "=" * 60)
print("📊 RESUMO DA INTEGRAÇÃO")
print("=" * 60)

checks = [
    ("SDK Python", "claude_code_sdk" in sys.modules),
    ("Claude CLI", os.system("which claude > /dev/null 2>&1") == 0),
    ("Cliente V2", result if 'result' in locals() else False),
    ("Arquitetura V2", "ClaudeRunner" in locals()),
    ("Server V2", "ConversationServerV2" in locals())
]

all_ok = True
for name, status in checks:
    emoji = "✅" if status else "❌"
    print(f"{emoji} {name}: {'OK' if status else 'FALHOU'}")
    if not status:
        all_ok = False

print("\n" + "=" * 60)
if all_ok:
    print("🎉 INTEGRAÇÃO 100% COMPLETA!")
    print("✅ Sistema pronto para usar Claude real!")
else:
    print("⚠️ Alguns componentes não estão prontos")
    print("📝 Verifique os erros acima")

print("\n📋 Para ativar o servidor V2:")
print("   1. Pare o servidor atual (Ctrl+C)")
print("   2. Execute: ./start_server_v2.sh")
print("   3. Acesse: http://localhost:8888")

sys.exit(0 if all_ok else 1)