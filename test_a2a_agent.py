#!/usr/bin/env python3
"""
Teste do Agente A2A com Claude SDK.
Valida a diferença entre LLM e Agente.
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def test_agent():
    """Testa o agente A2A completo."""
    print("=" * 60)
    print("🤖 TESTE DO AGENTE A2A CLAUDE")
    print("=" * 60)
    
    from agents.claude_a2a_agent import ClaudeA2AAgent
    
    # Criar agente
    agent = ClaudeA2AAgent(
        name="Test Agent",
        description="Agente de teste"
    )
    
    print(f"\n✅ Agente criado: {agent.name}")
    print(f"   📦 Ferramentas: {list(agent.tools.keys())}")
    
    # Testar pensamento e ação
    test_messages = [
        "Quanto é 2 + 2?",
        "Lembre que meu nome é João",
        "Qual é meu nome?"
    ]
    
    session_id = "test-session"
    
    for msg in test_messages:
        print(f"\n👤 Usuário: {msg}")
        response = await agent._think_and_act(msg, session_id)
        print(f"🤖 Agente: {response[:200]}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent())