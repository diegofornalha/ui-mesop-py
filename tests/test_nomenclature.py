#!/usr/bin/env python3
"""
Teste de padronização de nomenclatura
Verifica se a nomenclatura está funcionando corretamente após refatoração
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o patch primeiro
import message_patch

# Importar Message patchada
try:
    from a2a.types import Message
except ImportError:
    from service.types import Message

from service.types import MessageInfoFixed, ConversationFixed
from state.state import StateMessage, StateConversation, StateEvent
from pydantic import ValidationError
import json

def test_message_fields():
    """Testa campos de Message com diferentes formatos"""
    print("🧪 Testando Message...")
    
    # Teste 1: Criação com camelCase (padrão)
    msg1 = Message(
        messageId="msg-001",
        contextId="ctx-001",
        content="Test message",
        author="user"
    )
    assert msg1.messageId == "msg-001"
    assert msg1.contextId == "ctx-001"
    print("✅ Message com camelCase OK")
    
    # Teste 2: Criação com snake_case (via alias)
    msg2 = Message(
        messageId="msg-002",
        context_id="ctx-002",  # Deve funcionar via alias
        content="Test message 2",
        author="user"
    )
    assert msg2.contextId == "ctx-002"
    print("✅ Message com context_id alias OK")
    
    # Teste 3: Propriedades de compatibilidade
    assert msg1.messageid == "msg-001"  # lowercase
    assert msg1.id == "msg-001"  # id property
    print("✅ Propriedades de compatibilidade OK")
    
    # Teste 4: Normalização de variações
    msg3_data = {
        "messageid": "msg-003",  # lowercase
        "context_id": "ctx-003",  # snake_case
        "text": "Test content"  # text em vez de content
    }
    msg3 = Message(**msg3_data)
    assert msg3.messageId == "msg-003"
    assert msg3.contextId == "ctx-003"
    assert msg3.content == "Test content"
    print("✅ Normalização de variações OK")

def test_conversation_fields():
    """Testa campos de Conversation"""
    print("\n🧪 Testando Conversation...")
    
    # Teste com diferentes variações
    conv_data = {
        "conversationId": "conv-001",  # camelCase
        "isActive": True,  # camelCase
        "name": "Test Conversation"
    }
    conv = ConversationFixed(**conv_data)
    assert conv.conversationid == "conv-001"  # Campo interno é lowercase
    assert conv.isactive == True
    print("✅ Conversation com normalização OK")

def test_state_classes():
    """Testa classes de estado"""
    print("\n🧪 Testando classes State...")
    
    # StateMessage
    state_msg = StateMessage(
        messageId="msg-001",
        contextId="ctx-001",
        taskId="task-001",
        role="user"
    )
    
    # Testa propriedades de compatibilidade
    assert state_msg.message_id == "msg-001"  # snake_case property
    assert state_msg.context_id == "ctx-001"
    assert state_msg.messageid == "msg-001"  # lowercase property
    assert state_msg.contextid == "ctx-001"
    print("✅ StateMessage com propriedades OK")
    
    # StateConversation
    state_conv = StateConversation(
        conversationId="conv-001",
        conversationName="Test",
        isActive=True,
        messageIds=["msg-001", "msg-002"]
    )
    
    assert state_conv.conversation_id == "conv-001"
    assert state_conv.conversationid == "conv-001"
    assert state_conv.is_active == True
    assert state_conv.isactive == True
    print("✅ StateConversation com propriedades OK")

def test_messageinfo():
    """Testa MessageInfo corrigido"""
    print("\n🧪 Testando MessageInfo...")
    
    # Teste com camelCase (padrão)
    info1 = MessageInfoFixed(
        messageId="msg-001",
        contextId="ctx-001"
    )
    assert info1.messageId == "msg-001"
    assert info1.contextId == "ctx-001"
    print("✅ MessageInfo com camelCase OK")
    
    # Teste com variações
    info2_data = {
        "messageid": "msg-002",  # lowercase
        "context_id": "ctx-002"  # snake_case
    }
    info2 = MessageInfoFixed(**info2_data)
    assert info2.messageId == "msg-002"
    assert info2.contextId == "ctx-002"
    print("✅ MessageInfo com normalização OK")

def test_json_serialization():
    """Testa serialização JSON"""
    print("\n🧪 Testando serialização JSON...")
    
    msg = Message(
        messageId="msg-001",
        contextId="ctx-001",
        content="Test",
        author="user"
    )
    
    # Serializar para JSON
    json_str = msg.model_dump_json()
    json_data = json.loads(json_str)
    
    # Verificar campos no JSON
    assert json_data["messageId"] == "msg-001"
    assert "contextId" in json_data or "context_id" in json_data
    print("✅ Serialização JSON OK")
    
    # Desserializar de volta
    msg2 = Message(**json_data)
    assert msg2.messageId == "msg-001"
    print("✅ Desserialização JSON OK")

def main():
    """Executa todos os testes"""
    print("=" * 50)
    print("🚀 INICIANDO TESTES DE NOMENCLATURA")
    print("=" * 50)
    
    try:
        test_message_fields()
        test_conversation_fields()
        test_state_classes()
        test_messageinfo()
        test_json_serialization()
        
        print("\n" + "=" * 50)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 50)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ ERRO: Teste falhou - {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)