"""
Testes para validar o campo taskid no MessagePatched
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from message_patch import MessagePatched


def test_taskid_field_creation():
    """Testa criação de Message com campo taskid"""
    msg = MessagePatched(
        messageId="test-123",
        content="Test message",
        taskid="task-456"
    )
    
    assert msg.taskid == "task-456"
    assert msg.taskId == "task-456"  # Propriedade de compatibilidade
    assert msg.task_id == "task-456"  # Outra propriedade de compatibilidade
    print("✓ Campo taskid criado corretamente")


def test_taskid_normalization():
    """Testa normalização de variações de taskid"""
    
    # Teste com taskId (camelCase)
    msg1 = MessagePatched(
        messageId="test-1",
        content="Test",
        taskId="task-1"  # CamelCase
    )
    assert msg1.taskid == "task-1"
    print("✓ Normalização de taskId funciona")
    
    # Teste com task_id (snake_case)
    msg2 = MessagePatched(
        messageId="test-2",
        content="Test",
        task_id="task-2"  # Snake case
    )
    assert msg2.taskid == "task-2"
    print("✓ Normalização de task_id funciona")
    
    # Teste com TaskId (PascalCase)
    msg3 = MessagePatched(
        messageId="test-3",
        content="Test",
        TaskId="task-3"  # Pascal case
    )
    assert msg3.taskid == "task-3"
    print("✓ Normalização de TaskId funciona")
    
    # Teste com task (simples)
    msg4 = MessagePatched(
        messageId="test-4",
        content="Test",
        task="task-4"  # Simples
    )
    assert msg4.taskid == "task-4"
    assert msg4.task == "task-4"  # Campo task também deve estar presente
    print("✓ Normalização de task funciona")


def test_conversation_id_field():
    """Testa campo conversation_id"""
    msg = MessagePatched(
        messageId="test-123",
        content="Test message",
        conversation_id="conv-789"
    )
    
    assert msg.conversation_id == "conv-789"
    assert msg.conversationId == "conv-789"  # Propriedade de compatibilidade
    print("✓ Campo conversation_id funciona")


def test_conversation_id_normalization():
    """Testa normalização de variações de conversation_id"""
    
    # Teste com conversationId (camelCase)
    msg1 = MessagePatched(
        messageId="test-1",
        content="Test",
        conversationId="conv-1"  # CamelCase
    )
    assert msg1.conversation_id == "conv-1"
    print("✓ Normalização de conversationId funciona")
    
    # Teste com ConversationId (PascalCase)
    msg2 = MessagePatched(
        messageId="test-2",
        content="Test",
        ConversationId="conv-2"  # Pascal case
    )
    assert msg2.conversation_id == "conv-2"
    print("✓ Normalização de ConversationId funciona")


def test_optional_fields():
    """Testa que taskid e conversation_id são opcionais"""
    msg = MessagePatched(
        messageId="test-123",
        content="Test message"
    )
    
    assert msg.taskid is None
    assert msg.conversation_id is None
    print("✓ Campos taskid e conversation_id são opcionais")


def test_compatibility_with_existing_code():
    """Testa compatibilidade com código existente que usa taskid"""
    msg = MessagePatched(
        messageId="test-123",
        content="Test message",
        taskid="task-999"
    )
    
    # Simula o uso no código existente
    # O código existente usa msg.taskid diretamente
    task_value = msg.taskid
    assert task_value == "task-999"
    
    # Teste de atribuição direta (como pode ocorrer no código)
    msg.taskid = "new-task-111"
    assert msg.taskid == "new-task-111"
    print("✓ Compatibilidade com código existente mantida")


def test_message_dict_output():
    """Testa que o dict() inclui taskid"""
    msg = MessagePatched(
        messageId="test-123",
        content="Test message",
        taskid="task-456",
        conversation_id="conv-789"
    )
    
    data = msg.model_dump()
    assert 'taskid' in data
    assert data['taskid'] == "task-456"
    assert 'conversation_id' in data
    assert data['conversation_id'] == "conv-789"
    print("✓ model_dump() inclui taskid e conversation_id")


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 TESTANDO CORREÇÕES DO CAMPO TASKID")
    print("="*60 + "\n")
    
    try:
        test_taskid_field_creation()
        test_taskid_normalization()
        test_conversation_id_field()
        test_conversation_id_normalization()
        test_optional_fields()
        test_compatibility_with_existing_code()
        test_message_dict_output()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*60 + "\n")
        return True
        
    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)