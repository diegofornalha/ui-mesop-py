#!/usr/bin/env python
"""Teste rápido do chat."""

import httpx
import json
import uuid
import time

# Configuração
BASE_URL = "http://localhost:8888"

print("🧪 TESTE RÁPIDO DO CHAT CLAUDE")
print("="*40)

# 1. Criar conversa
print("\n1️⃣ Criando conversa...")
response = httpx.post(f"{BASE_URL}/conversation/create", json={})
if response.status_code == 200:
    data = response.json()
    conversation_id = data["result"]["conversationId"]
    print(f"✅ Conversa criada: {conversation_id[:8]}...")
else:
    print(f"❌ Erro: {response.status_code}")
    exit(1)

# 2. Enviar mensagem
print("\n2️⃣ Enviando mensagem...")
message = {
    "params": {
        "messageId": str(uuid.uuid4()),
        "contextId": conversation_id,
        "role": "user",
        "parts": [{"text": "Olá Claude! Responda com uma palavra em português."}]
    }
}

response = httpx.post(f"{BASE_URL}/message/send", json=message)
if response.status_code == 200:
    print("✅ Mensagem enviada")
else:
    print(f"❌ Erro ao enviar: {response.status_code}")

# 3. Aguardar processamento
print("\n⏳ Aguardando resposta...")
time.sleep(3)

# 4. Buscar mensagens
print("\n3️⃣ Buscando mensagens...")
response = httpx.post(
    f"{BASE_URL}/message/list",
    json={"params": conversation_id}
)

if response.status_code == 200:
    messages = response.json().get("result", [])
    print(f"📨 Total de mensagens: {len(messages)}")
    
    # Mostrar mensagens
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        parts = msg.get("parts", [])
        
        # Extrair texto
        text = ""
        for part in parts:
            if isinstance(part, dict):
                if "text" in part:
                    text = part["text"]
                elif "root" in part and isinstance(part["root"], dict):
                    text = part["root"].get("text", "")
        
        print(f"\n   [{role.upper()}]: {text[:200]}")
else:
    print(f"❌ Erro ao buscar mensagens: {response.status_code}")

print("\n" + "="*40)
print("✅ Teste concluído!")