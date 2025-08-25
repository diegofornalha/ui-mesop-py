"""
Teste específico para verificar problemas de inicialização na UI
Simula o comportamento da UI ao criar e modificar StateConversation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dataclasses
from dataclasses import dataclass, field
from state.state import StateConversation

def test_ui_initialization_scenario():
    """Simula exatamente como a UI cria e modifica StateConversation"""
    
    print("\n🔍 Testando cenário de inicialização da UI...")
    
    # Cenário 1: Criação vazia (como Mesop pode fazer)
    conv1 = StateConversation()
    print(f"✅ Criação vazia: messageIds={conv1.messageIds}")
    
    # Teste de modificação
    try:
        conv1.message_ids_python.append("msg-1")
        print(f"✅ Append funcionou: {conv1.messageIds}")
    except AttributeError as e:
        print(f"❌ ERRO no append: {e}")
        return False
    
    # Cenário 2: Criação com dados
    conv2 = StateConversation(
        conversationId="test-123",
        messageIds=["existing-1", "existing-2"]
    )
    print(f"✅ Criação com dados: messageIds={conv2.messageIds}")
    
    # Teste de modificação
    try:
        conv2.message_ids_python.append("msg-3")
        print(f"✅ Append funcionou: {conv2.messageIds}")
    except AttributeError as e:
        print(f"❌ ERRO no append: {e}")
        return False
    
    # Cenário 3: Verificar que NÃO podemos atribuir diretamente
    try:
        conv2.message_ids_python = ["nova", "lista"]
        print("❌ PROBLEMA: Atribuição direta funcionou (não deveria)")
        return False
    except AttributeError as e:
        print(f"✅ Atribuição direta bloqueada corretamente: {e}")
    
    # Cenário 4: Teste de referência vs cópia
    ids_ref = conv2.message_ids_python
    ids_ref.append("via-ref")
    if "via-ref" in conv2.messageIds:
        print("✅ Modificação via referência funcionou")
    else:
        print("❌ ERRO: Referência não está funcionando")
        return False
    
    # Cenário 5: Verificar que é a mesma referência
    if conv2.message_ids_python is conv2.messageIds:
        print("✅ Propriedade retorna referência direta (não cópia)")
    else:
        print("❌ ERRO: Propriedade está retornando cópia!")
        return False
    
    return True

def test_mesop_stateclass_behavior():
    """Testa comportamento específico com @me.stateclass"""
    print("\n🔍 Testando comportamento de @dataclass...")
    
    # Simular como Mesop pode criar objetos
    conv = StateConversation()
    
    # Verificar atributos
    print(f"  conversationId: {conv.conversationId} (tipo: {type(conv.conversationId)})")
    print(f"  messageIds: {conv.messageIds} (tipo: {type(conv.messageIds)})")
    print(f"  message_ids_python: {conv.message_ids_python} (tipo: {type(conv.message_ids_python)})")
    
    # Verificar se são a mesma referência
    same_ref = conv.message_ids_python is conv.messageIds
    print(f"  Mesma referência? {same_ref}")
    
    if not same_ref:
        print("❌ PROBLEMA ENCONTRADO: Propriedade não retorna referência!")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TESTE DE INICIALIZAÇÃO DA UI")
    print("=" * 60)
    
    success = True
    
    success = test_ui_initialization_scenario() and success
    success = test_mesop_stateclass_behavior() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("✅ Propriedades mutáveis funcionam corretamente")
        print("✅ Não há problemas de inicialização")
    else:
        print("❌ PROBLEMAS ENCONTRADOS!")
    print("=" * 60)
    
    exit(0 if success else 1)