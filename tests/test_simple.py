#!/usr/bin/env python3
"""Teste simples para debug"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o patch primeiro
import message_patch

# Tentar importar a Message patchada
try:
    from a2a.types import Message
    print("Usando a2a.types.Message (patchada)")
except ImportError:
    from service.types import Message  
    print("Usando service.types.Message (local)")

# Teste direto
print("Criando Message com contextId...")
msg = Message(
    messageId="msg-001",
    contextId="ctx-001",
    content="Test",
    author="user"
)

print(f"msg.__dict__: {msg.__dict__}")
print(f"msg.messageId: {msg.messageId}")
print(f"msg.contextId: {getattr(msg, 'contextId', 'NAO TEM')}")
print(f"msg.context_id: {getattr(msg, 'context_id', 'NAO TEM')}")

# Teste com dados em dict
print("\nCriando Message com dict...")
data = {
    "messageId": "msg-002",
    "contextId": "ctx-002",
    "content": "Test 2",
    "author": "user2"
}
msg2 = Message(**data)
print(f"msg2.__dict__: {msg2.__dict__}")
print(f"msg2.contextId: {getattr(msg2, 'contextId', 'NAO TEM')}")

# Verificar se o Message usado é o patched
print(f"\nClasse Message: {Message}")
print(f"MRO: {Message.__mro__}")