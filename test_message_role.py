#!/usr/bin/env python3
"""
Teste simples para verificar o role das mensagens
"""

import asyncio
import httpx
import json
import uuid
import os

os.environ['USE_CLAUDE'] = 'TRUE'

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Criar conversa
        print("1. Criando conversa...")
        resp = await client.post("http://localhost:8888/conversation/create", json={})
        result = resp.json()
        print(f"   Response: {result}")
        
        # Tentar diferentes formatos
        if "result" in result:
            if isinstance(result["result"], dict):
                # Tentar com camelCase e lowercase
                if "conversationId" in result["result"]:
                    conv_id = result["result"]["conversationId"]
                elif "conversationid" in result["result"]:
                    conv_id = result["result"]["conversationid"]
                else:
                    print(f"   Result keys: {result['result'].keys()}")
                    raise ValueError("Cannot find conversationId")
            else:
                raise ValueError("Result is not a dict")
        else:
            raise ValueError("No result in response")
        
        print(f"   Conversa: {conv_id[:8]}...")
        
        # Enviar mensagem
        print("\n2. Enviando mensagem...")
        message = {
            "params": {
                "messageId": str(uuid.uuid4()),
                "contextId": conv_id,
                "role": "user",
                "parts": [{"text": "Olá! Diga apenas: TESTE OK"}]
            }
        }
        
        resp = await client.post("http://localhost:8888/message/send", json=message)
        print(f"   Status: {resp.status_code}")
        
        # Aguardar
        print("\n3. Aguardando 5 segundos...")
        await asyncio.sleep(5)
        
        # Listar mensagens
        print("\n4. Listando mensagens...")
        resp = await client.post("http://localhost:8888/message/list", json={"params": conv_id})
        messages = resp.json()["result"]
        
        print(f"\n5. Análise das {len(messages)} mensagens:")
        for i, msg in enumerate(messages):
            role = msg.get("role", "SEM_ROLE")
            text = ""
            if msg.get("parts"):
                for part in msg["parts"]:
                    if isinstance(part, dict) and "text" in part:
                        text = part["text"][:30]
            print(f"   Msg {i}: role='{role}' | texto: {text}...")

if __name__ == "__main__":
    print("="*60)
    print("TESTE DE ROLE DAS MENSAGENS")
    print("="*60)
    asyncio.run(test())