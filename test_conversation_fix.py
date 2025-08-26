#!/usr/bin/env python
"""
Script para testar envio de mensagens em uma conversa existente.
Demonstra como usar corretamente o conversation_id.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:32123"

def test_conversation_persistence():
    print("=" * 50)
    print("TESTE: Envio de Mensagens na MESMA Conversa")
    print("=" * 50)
    
    # 1. Criar uma nova conversa
    print("\n1️⃣ Criando nova conversa...")
    response = requests.post(f"{BASE_URL}/conversation/create")
    data = response.json()
    conversation_id = data["result"]["conversationId"]
    print(f"   ✅ Conversa criada: {conversation_id}")
    
    # 2. Enviar primeira mensagem
    print("\n2️⃣ Enviando primeira mensagem...")
    message1 = {
        "messageId": "msg-001",
        "contextId": conversation_id,  # IMPORTANTE: usar o conversation_id aqui!
        "role": "user",
        "parts": [{"text": "Olá, esta é a primeira mensagem"}]
    }
    
    response = requests.post(
        f"{BASE_URL}/message/send",
        json={"params": message1}
    )
    print(f"   ✅ Primeira mensagem enviada")
    time.sleep(2)
    
    # 3. Enviar segunda mensagem NA MESMA conversa
    print("\n3️⃣ Enviando segunda mensagem na MESMA conversa...")
    message2 = {
        "messageId": "msg-002",
        "contextId": conversation_id,  # USAR O MESMO conversation_id!
        "role": "user",
        "parts": [{"text": "Esta é a segunda mensagem na mesma conversa"}]
    }
    
    response = requests.post(
        f"{BASE_URL}/message/send",
        json={"params": message2}
    )
    print(f"   ✅ Segunda mensagem enviada")
    time.sleep(2)
    
    # 4. Verificar quantas mensagens tem na conversa
    print("\n4️⃣ Verificando mensagens na conversa...")
    response = requests.post(
        f"{BASE_URL}/message/list",
        json={"params": conversation_id}
    )
    messages = response.json()["result"]
    print(f"   📊 Total de mensagens na conversa: {len(messages)}")
    
    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        content = ""
        if msg.get("parts"):
            content = msg["parts"][0].get("text", "")[:50]
        print(f"   {i}. [{role}]: {content}...")
    
    # 5. Listar todas as conversas para verificar
    print("\n5️⃣ Listando todas as conversas...")
    response = requests.post(f"{BASE_URL}/conversation/list")
    conversations = response.json()["result"]
    print(f"   📊 Total de conversas: {len(conversations)}")
    
    for conv in conversations[:5]:  # Mostrar apenas as 5 primeiras
        conv_id = conv["conversationId"]
        is_active = conv.get("isActive", False)
        message_count = len(conv.get("messageIds", []))
        print(f"   - {conv_id[:8]}... | Ativa: {is_active} | Mensagens: {message_count}")
    
    print("\n" + "=" * 50)
    print("✅ TESTE COMPLETO!")
    print("=" * 50)
    
    print("\n📝 ANÁLISE DO PROBLEMA:")
    print("Se você vê múltiplas conversas com 0 mensagens, o problema está em:")
    print("1. O conversationid não está sendo preservado no PageState")
    print("2. Cada envio de mensagem pode estar criando nova conversa")
    print("3. O contextId precisa ser sempre o mesmo conversation_id")
    
    print("\n💡 SOLUÇÃO:")
    print("Garantir que o conversation_id seja:")
    print("- Armazenado no PageState quando a conversa é criada/selecionada")
    print("- Usado em TODAS as mensagens enviadas (no contextId)")
    print("- Preservado entre refreshes da página")
    
    return conversation_id

if __name__ == "__main__":
    try:
        conv_id = test_conversation_persistence()
        print(f"\n🎯 Use este ID para continuar a conversa: {conv_id}")
        print(f"URL: {BASE_URL}/conversation?conversationid={conv_id}")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)