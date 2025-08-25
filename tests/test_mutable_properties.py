"""
Teste das propriedades mutáveis em StateConversation
Verifica que message_ids_python.append() funciona corretamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.state import StateConversation

def test_mutable_properties():
    """Testa que propriedades Python são mutáveis via referência"""
    
    # Criar conversação
    conversation = StateConversation(
        conversationId="conv-123",
        conversationName="Test Conversation",
        isActive=True
    )
    
    print("✅ Conversação criada")
    
    # Testar que a propriedade retorna a mesma referência
    assert conversation.message_ids_python is conversation.messageIds
    print("✅ message_ids_python retorna referência direta")
    
    # Testar append via campo real
    conversation.messageIds.append("msg-1")
    assert len(conversation.messageIds) == 1
    assert conversation.messageIds[0] == "msg-1"
    print("✅ Append via messageIds funciona")
    
    # Testar append via propriedade Python MUTÁVEL
    conversation.message_ids_python.append("msg-2")
    assert len(conversation.messageIds) == 2
    assert conversation.messageIds[1] == "msg-2"
    print("✅ Append via message_ids_python FUNCIONA!")
    
    # Verificar que ambos apontam para a mesma lista
    assert conversation.message_ids_python == conversation.messageIds
    assert conversation.message_ids_python == ["msg-1", "msg-2"]
    print("✅ Ambos apontam para a mesma lista")
    
    # Testar outras operações mutáveis
    conversation.message_ids_python.extend(["msg-3", "msg-4"])
    assert len(conversation.messageIds) == 4
    print("✅ Extend via message_ids_python funciona")
    
    conversation.message_ids_python.remove("msg-1")
    assert "msg-1" not in conversation.messageIds
    print("✅ Remove via message_ids_python funciona")
    
    conversation.message_ids_python.clear()
    assert len(conversation.messageIds) == 0
    print("✅ Clear via message_ids_python funciona")
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Propriedades Python MUTÁVEIS funcionam perfeitamente!")
    print("✅ Problema 'property has no setter' RESOLVIDO!")

if __name__ == "__main__":
    test_mutable_properties()