#!/usr/bin/env python3
"""Testa interação com o Claude enviando mensagem e aguardando resposta."""

import httpx
import asyncio
import json
import uuid
from datetime import datetime

async def interact_with_claude():
    conv_id = "dea345dc-bda5-4bc9-8c44-9ede2481aea5"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"\n🔍 Testando interação na conversa {conv_id[:8]}...")
        print("="*60)
        
        # 1. Verificar mensagens atuais
        print("\n📋 Estado inicial:")
        resp = await client.post(
            "http://localhost:8888/message/list",
            json={"jsonrpc": "2.0", "method": "message/list", "params": conv_id, "id": 1}
        )
        
        if resp.status_code == 200:
            messages = resp.json().get('result', [])
            print(f"   Mensagens atuais: {len(messages)}")
            for i, msg in enumerate(messages):
                role = msg.get('role', 'unknown')
                parts = msg.get('parts', [])
                text = ""
                for part in parts:
                    if isinstance(part, dict) and 'text' in part:
                        text = part['text'][:50] + "..." if len(part['text']) > 50 else part['text']
                print(f"   [{i+1}] {role}: {text}")
        
        # 2. Enviar nova mensagem
        print("\n📤 Enviando mensagem teste...")
        test_message = {
            "messageId": str(uuid.uuid4()),
            "content": "Olá Claude, você está funcionando? Responda apenas: TESTE OK",
            "contextId": conv_id,
            "role": "user",
            "parts": [{"text": "Olá Claude, você está funcionando? Responda apenas: TESTE OK", "kind": "text"}]
        }
        
        resp = await client.post(
            "http://localhost:8888/message/send",
            json={"jsonrpc": "2.0", "method": "message/send", "params": test_message, "id": 2}
        )
        
        if resp.status_code == 200:
            print("   ✅ Mensagem enviada com sucesso")
        else:
            print(f"   ❌ Erro ao enviar: {resp.status_code}")
            return
        
        # 3. Aguardar processamento
        print("\n⏳ Aguardando resposta do Claude...")
        for attempt in range(10):  # Tentar por 10 segundos
            await asyncio.sleep(1)
            print(f"   Tentativa {attempt + 1}/10...")
            
            resp = await client.post(
                "http://localhost:8888/message/list",
                json={"jsonrpc": "2.0", "method": "message/list", "params": conv_id, "id": 3}
            )
            
            if resp.status_code == 200:
                messages = resp.json().get('result', [])
                
                if len(messages) > len(messages):  # Nova mensagem chegou
                    print(f"\n✅ RESPOSTA RECEBIDA!")
                    break
                elif len(messages) == 3:  # Esperamos 3 mensagens (original + nossa + resposta)
                    print(f"\n✅ Total de mensagens: {len(messages)}")
                    break
        
        # 4. Verificar resultado final
        print("\n📊 Estado final:")
        resp = await client.post(
            "http://localhost:8888/message/list",
            json={"jsonrpc": "2.0", "method": "message/list", "params": conv_id, "id": 4}
        )
        
        if resp.status_code == 200:
            messages = resp.json().get('result', [])
            print(f"   Total de mensagens: {len(messages)}")
            
            for i, msg in enumerate(messages):
                role = msg.get('role', 'unknown')
                parts = msg.get('parts', [])
                text = ""
                for part in parts:
                    if isinstance(part, dict) and 'text' in part:
                        text = part['text']
                
                print(f"\n   Mensagem {i+1}:")
                print(f"     Role: {role}")
                if text:
                    preview = text[:100] + "..." if len(text) > 100 else text
                    print(f"     Texto: {preview}")
            
            # Verificar se há resposta do agente
            agent_messages = [m for m in messages if 'agent' in str(m.get('role', '')).lower()]
            
            if agent_messages:
                print(f"\n✅ Claude respondeu! ({len(agent_messages)} mensagem(s) do agente)")
                for msg in agent_messages:
                    parts = msg.get('parts', [])
                    for part in parts:
                        if isinstance(part, dict) and 'text' in part:
                            print(f"\n🤖 Claude disse: {part['text']}")
            else:
                print("\n❌ Nenhuma resposta do Claude foi encontrada")
                print("   Possíveis causas:")
                print("   - Claude SDK não está instalado")
                print("   - Processamento assíncrono ainda não completou")
                print("   - Erro no processamento da mensagem")

if __name__ == "__main__":
    asyncio.run(interact_with_claude())