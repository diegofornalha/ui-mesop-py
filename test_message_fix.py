#!/usr/bin/env python3
"""
Teste específico para o erro de Message com messageid
"""

from service.types import Message

# Dados exatamente como estão vindo (com messageid minúsculo)
test_data = {
    'messageid': '8f9ddca6-6...',  # minúsculo - ESTE É O PROBLEMA
    'text': 'oi',  # usando 'text' em vez de 'content'
}

print("=" * 60)
print("TESTANDO CORREÇÃO DO Message")
print("=" * 60)

print(f"\nDados de entrada: {test_data}")

try:
    # Tentar criar Message com os dados problemáticos
    msg = Message(**test_data)
    print(f"✅ SUCESSO! Message criado:")
    print(f"   messageId: {msg.messageId}")
    print(f"   messageid (property): {msg.messageid}")
    print(f"   id (property): {msg.id}")
    print(f"   content: {msg.content}")
    print(f"   author: {msg.author if msg.author else 'Não definido'}")
except Exception as e:
    print(f"❌ ERRO: {e}")

# Testar outras variações
print("\n" + "=" * 60)
print("TESTANDO OUTRAS VARIAÇÕES")
print("=" * 60)

test_variations = [
    {"messageid": "123", "text": "teste 1"},
    {"message_id": "456", "content": "teste 2"},
    {"MessageId": "789", "body": "teste 3"},
    {"id": "101", "message": "teste 4"},
]

for i, data in enumerate(test_variations, 1):
    print(f"\nVariação {i}: {data}")
    try:
        msg = Message(**data)
        print(f"✅ messageId: {msg.messageId}, content: {msg.content}")
    except Exception as e:
        print(f"❌ ERRO: {e}")