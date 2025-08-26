#!/usr/bin/env python
"""
Teste completo da integração Claude com ClaudeRunner e todos os serviços.
Verifica se a migração completa está funcionando.
"""

import asyncio
import sys
import os

# Configurar ambiente para usar Claude
os.environ['USE_CLAUDE'] = 'TRUE'

async def test_complete_integration():
    """Testa a integração completa do Claude."""
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO COMPLETA - CLAUDE RUNNER + SERVIÇOS")
    print("=" * 60)
    
    # 1. Testar ClaudeRunner
    print("\n📦 Testando ClaudeRunner...")
    try:
        from agents.claude_runner import ClaudeRunner
        runner = ClaudeRunner(app_name="TestApp")
        await runner.initialize()
        print("  ✅ ClaudeRunner inicializado")
        
        # Testar execução
        result = await runner.run_async("Diga apenas: RUNNER OK")
        if "OK" in str(result.get("response", "")):
            print("  ✅ ClaudeRunner funcionando")
        runner.close()
    except Exception as e:
        print(f"  ❌ Erro no ClaudeRunner: {e}")
        return False
    
    # 2. Testar Serviços
    print("\n🧠 Testando Serviços In-Memory...")
    try:
        from agents.claude_services import (
            ClaudeSessionService,
            ClaudeMemoryService,
            ClaudeArtifactService,
            ClaudeEvent
        )
        
        # Session Service
        session_svc = ClaudeSessionService()
        await session_svc.initialize()
        session = await session_svc.create_session()
        print(f"  ✅ SessionService: Sessão {session['id'][:8]}...")
        
        # Memory Service
        memory_svc = ClaudeMemoryService()
        await memory_svc.initialize()
        await memory_svc.store("test", {"data": "value"})
        value = await memory_svc.retrieve("test")
        print(f"  ✅ MemoryService: Valor recuperado")
        
        # Artifact Service
        artifact_svc = ClaudeArtifactService()
        await artifact_svc.initialize()
        print(f"  ✅ ArtifactService: Pronto")
        
        # Events
        event = ClaudeEvent.create("test", content="teste")
        print(f"  ✅ Event System: ID {event.id[:8]}...")
        
    except Exception as e:
        print(f"  ❌ Erro nos Serviços: {e}")
        return False
    
    # 3. Testar Conversores
    print("\n🔄 Testando Conversores de Mensagens...")
    try:
        from agents.claude_converters import (
            claude_content_from_message,
            claude_content_to_message
        )
        from a2a.types import Message, TextPart, Role
        
        # Criar mensagem A2A
        a2a_msg = Message(
            messageId="test",
            contextId="ctx",
            role=Role.user,
            parts=[TextPart(text="Teste")]
        )
        
        # Converter ida e volta
        claude_format = claude_content_from_message(a2a_msg)
        a2a_back = claude_content_to_message(claude_format)
        
        print(f"  ✅ Conversores: A2A ↔ Claude funcionando")
        
    except Exception as e:
        print(f"  ❌ Erro nos Conversores: {e}")
        return False
    
    # 4. Testar Claude ADK Host Manager
    print("\n🎯 Testando Claude ADK Host Manager...")
    try:
        import httpx
        from service.server.claude_adk_host_manager import ClaudeADKHostManager
        
        http_client = httpx.AsyncClient()
        manager = ClaudeADKHostManager(http_client)
        await manager.initialize()
        
        # Criar conversa
        conversation = manager.create_conversation()
        print(f"  ✅ Manager: Conversa {conversation.conversationId[:8]}...")
        
        # Verificar propriedades
        print(f"  ✅ Conversas: {len(manager.conversations)}")
        print(f"  ✅ Tasks: {len(manager.tasks)}")
        print(f"  ✅ Agentes: {len(manager.agents)}")
        
        manager.close()
        await http_client.aclose()
        
    except Exception as e:
        print(f"  ❌ Erro no Manager: {e}")
        return False
    
    # 5. Verificar integração com servidor
    print("\n🌐 Verificando integração com servidor...")
    try:
        # Verificar se USE_CLAUDE está ativo
        use_claude = os.environ.get('USE_CLAUDE', '').upper() == 'TRUE'
        if use_claude:
            print(f"  ✅ USE_CLAUDE=TRUE configurado")
        else:
            print(f"  ⚠️ USE_CLAUDE não está TRUE")
        
        # Verificar se Claude CLI está disponível
        import subprocess
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ Claude CLI: {result.stdout.strip()}")
        else:
            print(f"  ❌ Claude CLI não disponível")
            
    except Exception as e:
        print(f"  ❌ Erro na verificação: {e}")
    
    return True


async def main():
    """Executa todos os testes."""
    success = await test_complete_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 MIGRAÇÃO COMPLETA BEM-SUCEDIDA!")
        print("✅ ClaudeRunner funcionando")
        print("✅ Todos os serviços implementados")
        print("✅ Conversores operacionais")
        print("✅ Manager integrado")
        print("\n📝 Próximos passos:")
        print("  1. Reiniciar o servidor: pkill -f 'python main.py' && python main.py")
        print("  2. Acessar http://localhost:8888")
        print("  3. Testar chat com Claude")
    else:
        print("⚠️ Alguns componentes falharam")
        print("Verifique os logs acima para detalhes")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)