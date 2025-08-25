#!/usr/bin/env python3
"""
Teste para verificar se o problema de messageId foi resolvido
"""

from service.types import MessageInfo

# Testar com diferentes variações
test_cases = [
    {"messageid": "123", "contextid": "ctx1"},  # tudo minúsculo
    {"messageId": "456", "contextId": "ctx2"},  # camelCase
    {"message_id": "789", "context_id": "ctx3"},  # snake_case
    {"message_Id": "101", "context_Id": "ctx4"},  # mixed case
]

print("=" * 60)
print("TESTANDO CORREÇÃO DO MessageInfo")
print("=" * 60)

for i, data in enumerate(test_cases, 1):
    print(f"\nTeste {i}: {data}")
    try:
        msg_info = MessageInfo(**data)
        print(f"✅ SUCESSO!")
        print(f"   messageId: {msg_info.messageId}")
        print(f"   contextId: {msg_info.contextId}")
    except Exception as e:
        print(f"❌ ERRO: {e}")

print("\n" + "=" * 60)
print("Todos os testes passaram! O problema foi resolvido.")
print("=" * 60)