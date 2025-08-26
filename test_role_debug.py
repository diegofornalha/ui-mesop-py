#!/usr/bin/env python3
"""
Script para debugar o problema do role nas mensagens do Claude
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime

# Configurar USE_CLAUDE
os.environ['USE_CLAUDE'] = 'TRUE'

import httpx
from a2a.types import Message, TextPart, Role

async def test_role_assignment():
    """Testa a atribuição de role nas mensagens"""
    
    print("🔍 TESTE DE DEBUG DO ROLE")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Criar conversa
        print("\n1️⃣ Criando conversa...")
        response = await client.post(
            "http://localhost:8888/conversation/create",
            json={}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao criar conversa: {response.status_code}")
            return
        
        data = response.json()
        conversation_id = data["result"]["conversationId"]
        print(f"✅ Conversa criada: {conversation_id[:8]}...")
        
        # 2. Enviar mensagem
        print("\n2️⃣ Enviando mensagem de teste...")
        message_id = str(uuid.uuid4())
        message = {
            "params": {
                "messageId": message_id,
                "contextId": conversation_id,
                "role": "user",  # Enviando como user
                "parts": [{"text": "Olá! Responda com: TESTE OK"}]
            }
        }
        
        response = await client.post(
            "http://localhost:8888/message/send",
            json=message
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            return
        
        print(f"✅ Mensagem enviada: {message_id[:8]}...")
        
        # 3. Aguardar processamento
        print("\n⏳ Aguardando processamento do Claude...")
        await asyncio.sleep(5)
        
        # 4. Listar mensagens
        print("\n3️⃣ Verificando mensagens...")
        response = await client.post(
            "http://localhost:8888/message/list",
            json={"params": conversation_id}
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao listar mensagens: {response.status_code}")
            return
        
        messages = response.json().get("result", [])
        print(f"📨 Total de mensagens: {len(messages)}")
        
        # 5. Analisar roles
        print("\n4️⃣ Análise dos roles:")
        print("-"*40)
        
        for i, msg in enumerate(messages, 1):
            msg_id = msg.get("messageId", "?")[:8]
            role = msg.get("role", "INDEFINIDO")
            
            # Extrair texto
            text = ""
            if msg.get("parts"):
                for part in msg["parts"]:
                    if isinstance(part, dict) and "text" in part:
                        text = part["text"][:50]
                    elif isinstance(part, dict) and "root" in part:
                        root = part["root"]
                        if isinstance(root, dict) and "text" in root:
                            text = root["text"][:50]
            
            # Indicadores visuais
            if role == "agent":
                emoji = "🤖"
                side = "DIREITA (correto)"
            elif role == "user":
                emoji = "👤"
                side = "ESQUERDA"
            else:
                emoji = "❓"
                side = "INDEFINIDO"
            
            print(f"{i}. {emoji} Role: {role:10} | Lado: {side:20} | ID: {msg_id}... | Texto: {text}...")
            
            # Debug detalhado da estrutura
            if role != "agent" and i > 1:  # Se não é agent e não é a primeira mensagem
                print(f"   ⚠️ POSSÍVEL PROBLEMA: Mensagem {i} deveria ser 'agent' mas é '{role}'")
                print(f"   Raw data: {msg}")
        
        # 6. Verificar se há resposta do Claude
        print("\n5️⃣ Diagnóstico:")
        print("-"*40)
        
        agent_messages = [m for m in messages if m.get("role") == "agent"]
        user_messages = [m for m in messages if m.get("role") == "user"]
        
        print(f"👤 Mensagens do usuário: {len(user_messages)}")
        print(f"🤖 Mensagens do agente: {len(agent_messages)}")
        
        if len(agent_messages) == 0 and len(messages) > 1:
            print("\n❌ PROBLEMA CONFIRMADO: Claude respondeu mas o role não está como 'agent'!")
            print("   As mensagens do Claude estão aparecendo como 'user'")
            print("\n📝 Solução necessária:")
            print("   1. Verificar claude_adk_host_manager.py linha 201")
            print("   2. Garantir que Role.agent está sendo serializado corretamente")
            print("   3. Verificar se o objeto Message está preservando o role")
        elif len(agent_messages) > 0:
            print("\n✅ TUDO OK: Mensagens do Claude têm role='agent'")
        else:
            print("\n⚠️ Apenas mensagem do usuário encontrada")

async def main():
    """Executa o teste"""
    try:
        await test_role_assignment()
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️ CERTIFIQUE-SE QUE O SERVIDOR ESTÁ RODANDO EM localhost:8888")
    print("   Com USE_CLAUDE=TRUE configurado\n")
    asyncio.run(main())