#!/usr/bin/env python3
"""
Script interativo para testar conversas com Gemini
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8888"

async def interactive_test():
    """Teste interativo com múltiplas mensagens"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("╔══════════════════════════════════════════════════╗")
        print("║      TESTE INTERATIVO COM GEMINI                 ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        print(f"🕐 Iniciando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL da aplicação: {BASE_URL}")
        print()
        
        # Criar nova conversa
        print("📝 Criando nova conversa...")
        response = await client.post(f"{BASE_URL}/conversation/create")
        conversation = response.json()["result"]
        conversation_id = conversation["conversationid"]
        print(f"✅ Conversa criada: {conversation_id}")
        print(f"🔗 Abra no navegador: {BASE_URL}/conversation?conversationid={conversation_id}")
        print()
        
        # Lista de mensagens para testar
        test_messages = [
            "Olá! Você pode se apresentar brevemente?",
            "Qual é a capital do Brasil?",
            "Me dê 3 dicas rápidas de programação Python",
            "Qual é 25 + 37?",
            "Escreva um haiku sobre programação"
        ]
        
        print("💬 Enviando mensagens de teste...")
        print("-" * 50)
        
        for i, msg_text in enumerate(test_messages, 1):
            print(f"\n[{i}] Enviando: {msg_text}")
            
            # Enviar mensagem
            message_data = {
                "conversationid": conversation_id,
                "message": msg_text
            }
            
            response = await client.post(
                f"{BASE_URL}/message/send",
                json=message_data
            )
            
            if response.status_code == 200:
                print(f"   ✅ Mensagem enviada!")
                
                # Aguardar resposta
                print("   ⏳ Aguardando resposta do Gemini...")
                await asyncio.sleep(3)
                
                # Buscar mensagens
                messages_response = await client.post(
                    f"{BASE_URL}/message/list",
                    json={"conversationid": conversation_id}
                )
                
                if messages_response.status_code == 200:
                    messages = messages_response.json()["result"]
                    
                    # Encontrar a resposta mais recente
                    if len(messages) > i * 2 - 1:
                        # Devemos ter pelo menos a mensagem do usuário e a resposta
                        for msg in messages[-2:]:
                            if msg["role"] == "agent":
                                content = msg["parts"][0]["root"]["text"] if msg["parts"] else "Sem resposta"
                                print(f"   💡 Resposta: {content[:100]}...")
                                break
                    else:
                        print("   ⚠️ Aguardando mais tempo...")
                        await asyncio.sleep(2)
                        
                # Pequena pausa entre mensagens
                await asyncio.sleep(1)
            else:
                print(f"   ❌ Erro ao enviar: {response.status_code}")
        
        print()
        print("-" * 50)
        print(f"✅ Teste concluído!")
        print(f"📊 Total de mensagens enviadas: {len(test_messages)}")
        print(f"🔗 Veja a conversa completa em:")
        print(f"   {BASE_URL}/conversation?conversationid={conversation_id}")

async def main():
    try:
        await interactive_test()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())