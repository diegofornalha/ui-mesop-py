#!/usr/bin/env python3
"""
Teste da API do servidor Mesop/Claude
"""

import httpx
import asyncio
import json
import uuid

async def test_api():
    """Testa a API do servidor."""
    
    async with httpx.AsyncClient(base_url="http://localhost:8888") as client:
        # 1. Criar conversa
        print("📝 Criando conversa...")
        response = await client.post("/conversation/create")
        conv_data = response.json()
        conversation_id = conv_data["result"]["conversationId"]
        print(f"✅ Conversa criada: {conversation_id}")
        
        # 2. Enviar mensagem
        print("\n📤 Enviando mensagem...")
        message_id = str(uuid.uuid4())
        message_data = {
            "params": {
                "messageId": message_id,
                "contextId": conversation_id,
                "role": "user",
                "parts": [
                    {"text": "Olá Claude! Responda em português: você está funcionando?"}
                ]
            }
        }
        
        response = await client.post("/message/send", json=message_data)
        send_result = response.json()
        print(f"✅ Mensagem enviada: {send_result}")
        
        # 3. Aguardar processamento
        print("\n⏳ Aguardando processamento...")
        await asyncio.sleep(5)
        
        # 4. Listar mensagens
        print("\n📋 Listando mensagens...")
        response = await client.post("/message/list", json={"params": conversation_id})
        messages = response.json()
        
        print(f"\n📥 Mensagens recebidas: {len(messages['result'])}")
        for i, msg in enumerate(messages["result"]):
            role = msg.get("role", "unknown")
            content = ""
            if "parts" in msg:
                for part in msg["parts"]:
                    if isinstance(part, dict) and "text" in part:
                        content += part["text"]
            print(f"\n  Mensagem {i+1}:")
            print(f"    Role: {role}")
            print(f"    Conteúdo: {content[:100]}...")
        
        # 5. Checar mensagens pendentes
        print("\n📋 Verificando mensagens pendentes...")
        response = await client.post("/message/pending")
        pending = response.json()
        print(f"Mensagens pendentes: {pending}")

if __name__ == "__main__":
    asyncio.run(test_api())