#!/usr/bin/env python3
"""
Teste da nova arquitetura alinhada com Google ADK real.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.claude_runner_v2 import ClaudeRunner
from agents.claude_a2a_agent_v2 import SimpleTestAgent, ClaudeA2AAgent
from agents.claude_types import Content, Session


async def test_runner_as_orchestrator():
    """Testa Runner como orquestrador principal (padrão ADK correto)."""
    print("\n" + "=" * 60)
    print("🧪 TESTE: Runner como Orquestrador Principal")
    print("=" * 60)
    
    # 1. Criar agente simples para teste
    agent = SimpleTestAgent()
    
    # 2. Criar Runner (ORQUESTRADOR)
    runner = ClaudeRunner(
        agent=agent,
        app_name="test_app"
    )
    
    # 3. Inicializar
    await runner.initialize()
    print("✅ Runner e Agent inicializados")
    
    # 4. Testar run_async com pattern correto
    user_id = "test_user"
    session_id = "test_session_001"
    message = Content.from_text("Olá, teste do padrão ADK!")
    
    print(f"\n📤 Enviando mensagem: 'Olá, teste do padrão ADK!'")
    print("📡 Eventos recebidos:")
    
    events = []
    async for event in runner.run_async(user_id, session_id, message):
        print(f"   → {event.author}: turn_complete={event.turn_complete}")
        events.append(event)
        
        if event.content:
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    print(f"      Texto: {part.text[:50]}...")
        
        if event.actions and event.actions.state_delta:
            print(f"      State delta: {event.actions.state_delta}")
    
    print(f"\n✅ Total de eventos: {len(events)}")
    
    # Verificar que temos eventos corretos
    has_user_event = any(e.author == "user" for e in events)
    has_agent_event = any(e.author != "user" and e.turn_complete for e in events)
    
    if has_user_event and has_agent_event:
        print("✅ SUCESSO: Padrão ADK funcionando corretamente!")
        return True
    else:
        print("❌ FALHA: Eventos esperados não encontrados")
        return False


async def test_agent_run_async_impl():
    """Testa Agent com _run_async_impl (não run_iteration!)."""
    print("\n" + "=" * 60)
    print("🧪 TESTE: Agent com _run_async_impl")
    print("=" * 60)
    
    # Criar agente com Claude (mockado)
    from unittest.mock import AsyncMock
    agent = ClaudeA2AAgent(
        name="TestClaudeAgent",
        instruction="Você é um assistente de teste."
    )
    
    # Mockar cliente LLM
    agent.llm_client.send_message = AsyncMock(return_value=[
        {"type": "text", "content": "Resposta mockada do Claude"}
    ])
    
    # Criar contexto de teste
    from agents.claude_types import InvocationContext, Session
    session = Session(id="test_session")
    
    # Adicionar evento de usuário
    from agents.claude_types import Event
    user_event = Event(
        author="user",
        invocation_id="test_invocation",
        content=Content.from_text("Teste do _run_async_impl")
    )
    session.add_event(user_event)
    
    ctx = InvocationContext(
        session=session,
        invocation_id="test_invocation",
        agent=agent,
        session_service=None,
        artifact_service=None
    )
    
    # Inicializar agente
    await agent.initialize()
    
    print("\n📤 Testando _run_async_impl...")
    
    events = []
    async for event in agent._run_async_impl(ctx):
        print(f"   → Evento: {event.author}, partial={event.partial}, complete={event.turn_complete}")
        events.append(event)
    
    print(f"\n✅ Total de eventos do agente: {len(events)}")
    
    # Verificar que temos resposta final
    has_final = any(e.turn_complete for e in events)
    has_state_delta = any(e.actions and e.actions.state_delta for e in events)
    
    if has_final:
        print("✅ SUCESSO: _run_async_impl funcionando!")
        if has_state_delta:
            print("✅ BONUS: state_delta implementado!")
        return True
    else:
        print("❌ FALHA: Sem evento final")
        return False


async def test_invocation_context():
    """Testa InvocationContext e state management."""
    print("\n" + "=" * 60)
    print("🧪 TESTE: InvocationContext e State Management")
    print("=" * 60)
    
    from agents.claude_types import InvocationContext, Session
    
    # Criar sessão
    session = Session(id="test_session")
    
    # Criar contexto
    ctx = InvocationContext(
        session=session,
        invocation_id="test_invocation",
        agent=None,
        session_service=None,
        artifact_service=None
    )
    
    # Testar state management
    print("\n📝 Testando state management...")
    
    # Session state
    ctx.set_state("test_key", "test_value")
    assert ctx.get_state("test_key") == "test_value"
    print("✅ Session state funcionando")
    
    # User state (cross-session)
    ctx.set_user_state("user_pref", "dark_mode")
    assert ctx.get_user_state("user_pref") == "dark_mode"
    assert session.state["user:user_pref"] == "dark_mode"
    print("✅ User state (cross-session) funcionando")
    
    # App state (global)
    ctx.set_app_state("version", "2.0")
    assert ctx.get_app_state("version") == "2.0"
    assert session.state["app:version"] == "2.0"
    print("✅ App state (global) funcionando")
    
    # Temp state (não persistido)
    ctx.set_temp_state("temp_calc", 42)
    assert ctx.get_temp_state("temp_calc") == 42
    assert session.state["temp:temp_calc"] == 42
    print("✅ Temp state funcionando")
    
    print("\n✅ SUCESSO: InvocationContext completo!")
    return True


async def test_event_structure():
    """Testa estrutura de Event e EventActions."""
    print("\n" + "=" * 60)
    print("🧪 TESTE: Event e EventActions Structure")
    print("=" * 60)
    
    from agents.claude_types import Event, EventActions, Content
    
    # Criar evento completo
    event = Event(
        author="test_agent",
        invocation_id="test_inv_001",
        content=Content.from_text("Teste de evento"),
        actions=EventActions(
            state_delta={"counter": 1},
            artifact_delta={"file.txt": "content"},
            transfer_to_agent="other_agent",
            escalate=False
        ),
        partial=False,
        turn_complete=True
    )
    
    print("\n📋 Estrutura do Event:")
    print(f"   author: {event.author}")
    print(f"   invocation_id: {event.invocation_id}")
    print(f"   content: {event.content.parts[0].text if event.content else 'None'}")
    print(f"   partial: {event.partial}")
    print(f"   turn_complete: {event.turn_complete}")
    
    print("\n📋 EventActions:")
    print(f"   state_delta: {event.actions.state_delta}")
    print(f"   artifact_delta: {event.actions.artifact_delta}")
    print(f"   transfer_to_agent: {event.actions.transfer_to_agent}")
    print(f"   escalate: {event.actions.escalate}")
    
    # Converter para dict
    event_dict = event.to_dict()
    assert "author" in event_dict
    assert "invocation_id" in event_dict
    assert "actions" in event_dict
    
    print("\n✅ SUCESSO: Event structure correto!")
    return True


async def main():
    """Executa todos os testes da nova arquitetura."""
    print("\n" + "=" * 60)
    print("🎯 TESTE DA ARQUITETURA ADK CORRETA")
    print("=" * 60)
    
    tests = [
        ("Runner como Orquestrador", test_runner_as_orchestrator),
        ("Agent _run_async_impl", test_agent_run_async_impl),
        ("InvocationContext", test_invocation_context),
        ("Event Structure", test_event_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Erro no teste {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    all_passed = all(success for _, success in results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status}: {test_name}")
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ Arquitetura alinhada com Google ADK:")
        print("  • Runner é o orquestrador principal")
        print("  • Agent usa _run_async_impl (não run_iteration)")
        print("  • InvocationContext gerencia estado")
        print("  • Event/EventActions estrutura correta")
        print("  • state_delta processamento automático")
        return True
    else:
        print("\n⚠️ Alguns testes falharam")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)