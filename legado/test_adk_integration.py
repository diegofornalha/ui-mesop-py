#!/usr/bin/env python3
"""
Script para testar integração com Google ADK
"""

import os
import asyncio
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai.types import GenerateContentConfig, Content, Part

# Configurar API Key
os.environ['GOOGLE_API_KEY'] = "AIzaSyDeyRoAZwxeA7_XcXwz4aTKurPBAWsnYY0"
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'false'

print("🔧 Testando integração com Google ADK...")
print("-" * 50)

async def test_adk():
    try:
        # Criar agente LLM
        print("\n1️⃣ Criando agente LLM...")
        agent = LlmAgent(
            name="TestAgent",
            description="Agente de teste para ADK",
            model="gemini-1.5-flash",
            instruction="Você é um assistente de teste. Responda de forma simples e direta.",
            generate_content_config=GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1024
            )
        )
        
        # Criar serviços necessários
        print("2️⃣ Criando serviços...")
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        memory_service = InMemoryMemoryService()
        
        # Criar runner
        print("3️⃣ Criando runner...")
        runner = Runner(
            app_name="TestApp",
            agent=agent,
            session_service=session_service,
            artifact_service=artifact_service,
            memory_service=memory_service
        )
        
        # Criar sessão
        print("4️⃣ Criando sessão...")
        session = await session_service.create_session(
            app_name="TestApp",
            user_id="test_user"
        )
        
        # Testar processamento
        print("5️⃣ Enviando mensagem de teste...")
        test_message = Content(
            parts=[Part(text="Olá! Responda apenas: 'ADK funcionando!'")],
            role="user"
        )
        
        # Executar agente
        print("6️⃣ Processando mensagem...")
        response_received = False
        
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=test_message
        ):
            print(f"   📨 Evento recebido: {event.author}")
            
            # Verificar se há conteúdo na resposta
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"\n✅ Resposta do agente: {part.text}")
                        response_received = True
                        break
            
            if response_received:
                break
        
        if response_received:
            print("\n🎉 SUCESSO! Google ADK está funcionando corretamente!")
        else:
            print("\n⚠️ Nenhuma resposta textual recebida do agente")
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\n💡 Debug:")
        import traceback
        traceback.print_exc()

# Executar teste
if __name__ == "__main__":
    asyncio.run(test_adk())