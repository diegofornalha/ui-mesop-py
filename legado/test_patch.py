#!/usr/bin/env python3
"""
Teste para verificar se o patch de Message está funcionando
"""

print("=" * 60)
print("TESTANDO PATCH DO MESSAGE")
print("=" * 60)

# Importar o patch primeiro
import message_patch

# Agora tentar importar e usar o Message da a2a
try:
    from a2a.types import Message
    print("\n✅ a2a.types.Message importado com sucesso")
    
    # Testar com dados problemáticos
    test_data = {
        'messageid': '404bddf0-d...',  # minúsculo - o problema!
        'text': 'oi'
    }
    
    print(f"\nTestando com dados problemáticos: {test_data}")
    
    msg = Message(**test_data)
    print(f"✅ SUCESSO! Message criado:")
    print(f"   messageId: {msg.messageId}")
    print(f"   content: {msg.content}")
    
    # Verificar propriedades
    print(f"\n📊 Propriedades de compatibilidade:")
    print(f"   msg.messageid: {msg.messageid}")
    print(f"   msg.id: {msg.id}")
    
except ImportError as e:
    print(f"\n⚠️  a2a não está instalado: {e}")
    print("Usando Message local do patch")
    
    from message_patch import MessagePatched as Message
    
    test_data = {
        'messageid': '404bddf0-d...',
        'text': 'oi'
    }
    
    msg = Message(**test_data)
    print(f"✅ Message local funciona:")
    print(f"   messageId: {msg.messageId}")
    print(f"   content: {msg.content}")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTANDO VARIAÇÕES")
print("=" * 60)

# Importar a versão correta
try:
    from a2a.types import Message
except ImportError:
    from message_patch import MessagePatched as Message

variations = [
    {"messageid": "123", "text": "teste 1"},
    {"message_id": "456", "content": "teste 2"}, 
    {"MessageId": "789", "body": "teste 3"},
    {"id": "101", "message": "teste 4"},
]

for i, data in enumerate(variations, 1):
    try:
        msg = Message(**data)
        print(f"✅ Variação {i}: messageId={msg.messageId}, content={msg.content}")
    except Exception as e:
        print(f"❌ Variação {i} falhou: {e}")