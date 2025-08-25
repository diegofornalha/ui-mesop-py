"""
Teste completo de todas as propriedades mutáveis
Verifica que append(), extend(), remove() funcionam em todas as propriedades
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.state import StateConversation, StateMessage
from service.types import Message, ConversationFixed
from message_patch import MessagePatched

def test_state_conversation_mutable():
    """Testa propriedades mutáveis em StateConversation"""
    print("\n🔍 Testando StateConversation...")
    
    conv = StateConversation(
        conversationId="conv-123",
        conversationName="Test",
        isActive=True
    )
    
    # Testar que retorna referência direta
    assert conv.message_ids_python is conv.messageIds
    print("✅ message_ids_python retorna referência direta")
    
    # Testar operações mutáveis
    conv.message_ids_python.append("msg-1")
    assert "msg-1" in conv.messageIds
    print("✅ append() funciona em message_ids_python")
    
    conv.message_ids_python.extend(["msg-2", "msg-3"])
    assert len(conv.messageIds) == 3
    print("✅ extend() funciona em message_ids_python")
    
    conv.message_ids_python.remove("msg-1")
    assert "msg-1" not in conv.messageIds
    print("✅ remove() funciona em message_ids_python")
    
    conv.message_ids_python[0] = "msg-novo"
    assert conv.messageIds[0] == "msg-novo"
    print("✅ Modificação por índice funciona")
    
    conv.message_ids_python.clear()
    assert len(conv.messageIds) == 0
    print("✅ clear() funciona em message_ids_python")

def test_message_mutable():
    """Testa propriedades mutáveis em Message"""
    print("\n🔍 Testando Message...")
    
    msg = Message(
        messageId="msg-456",
        content="Test",
        parts=["part1", "part2"]
    )
    
    # Testar que retorna referência direta
    assert msg.parts_python is msg.parts
    print("✅ parts_python retorna referência direta")
    
    # Testar operações mutáveis
    msg.parts_python.append("part3")
    assert "part3" in msg.parts
    print("✅ append() funciona em parts_python")
    
    msg.parts_python.extend(["part4", "part5"])
    assert len(msg.parts) == 5
    print("✅ extend() funciona em parts_python")
    
    msg.parts_python.remove("part1")
    assert "part1" not in msg.parts
    print("✅ remove() funciona em parts_python")

def test_message_patched_mutable():
    """Testa propriedades mutáveis em MessagePatched"""
    print("\n🔍 Testando MessagePatched...")
    
    msg = MessagePatched(
        messageId="msg-789",
        parts=["a", "b"],
        metadata={"key1": "value1"}
    )
    
    # Testar lista mutável
    assert msg.parts_python is msg.parts
    print("✅ parts_python retorna referência direta")
    
    msg.parts_python.append("c")
    assert "c" in msg.parts
    print("✅ append() funciona em parts_python")
    
    # Testar dict mutável
    if msg.metadata:
        assert msg.metadata_python is msg.metadata
        print("✅ metadata_python retorna referência direta")
        
        msg.metadata_python["key2"] = "value2"
        assert "key2" in msg.metadata
        print("✅ Update de dict funciona em metadata_python")
        
        msg.metadata_python.update({"key3": "value3"})
        assert msg.metadata["key3"] == "value3"
        print("✅ update() funciona em metadata_python")

def test_conversation_fixed_mutable():
    """Testa propriedades mutáveis em ConversationFixed"""
    print("\n🔍 Testando ConversationFixed...")
    
    conv = ConversationFixed(
        conversationId="conv-321",
        isActive=True,
        messages=[]
    )
    
    # Testar que retorna referência direta
    assert conv.messages_python is conv.messages
    print("✅ messages_python retorna referência direta")
    
    # Criar mensagem mock
    msg = Message(messageId="test-msg", content="test")
    
    # Testar operações mutáveis
    conv.messages_python.append(msg)
    assert msg in conv.messages
    print("✅ append() funciona em messages_python")
    
    assert len(conv.messages) == 1
    print("✅ Mensagem adicionada com sucesso")

def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTANDO TODAS AS PROPRIEDADES MUTÁVEIS")
    print("=" * 60)
    
    try:
        test_state_conversation_mutable()
        test_message_mutable()
        test_message_patched_mutable()
        test_conversation_fixed_mutable()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Propriedades MUTÁVEIS funcionam perfeitamente!")
        print("✅ Problema 'property has no setter' COMPLETAMENTE RESOLVIDO!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)