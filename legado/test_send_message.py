#!/usr/bin/env python3
"""
Script para testar envio de mensagem na conversa existente
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8888"
CONVERSATION_ID = "d0455b23-0315-4be7-937b-fe3782f875ba"

async def send_test_message():
    """Envia uma mensagem de teste para a conversa"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🤖 Testando envio de mensagem...")
        print("-" * 50)
        
        # 1. Verificar estado inicial da conversa
        print("\n1️⃣ Verificando conversa atual...")
        list_response = await client.post(
            f"{BASE_URL}/conversation/list",
            json={}
        )
        
        if list_response.status_code == 200:
            conversations = list_response.json()["result"]
            for conv in conversations:
                if conv["conversationid"] == CONVERSATION_ID:
                    print(f"✅ Conversa encontrada: {CONVERSATION_ID}")
                    print(f"   Mensagens atuais: {len(conv.get('messages', []))}")
                    break
        
        # 2. Enviar mensagem de teste
        print("\n2️⃣ Enviando mensagem: 'Olá, este é um teste!'...")
        message_id = str(uuid.uuid4())
        
        message_data = {
            "params": {
                "message_id": message_id,
                "context_id": CONVERSATION_ID,
                "role": "user",
                "parts": [
                    {
                        "text": "Olá! Este é um teste de envio de mensagem. Você pode me confirmar que recebeu?"
                    }
                ]
            }
        }
        
        try:
            send_response = await client.post(
                f"{BASE_URL}/message/send",
                json=message_data
            )
            
            if send_response.status_code == 200:
                print(f"✅ Mensagem enviada com sucesso!")
                result = send_response.json()
                print(f"   ID da mensagem: {message_id[:8]}...")
            else:
                print(f"❌ Erro ao enviar mensagem: {send_response.status_code}")
                print(f"   Resposta: {send_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {str(e)}")
            return False
        
        # 3. Aguardar processamento
        print("\n3️⃣ Aguardando processamento...")
        await asyncio.sleep(3)
        
        # 4. Verificar mensagens pendentes
        print("\n4️⃣ Verificando status...")
        pending_response = await client.post(
            f"{BASE_URL}/message/pending",
            json={}
        )
        
        if pending_response.status_code == 200:
            pending = pending_response.json()["result"]
            if pending:
                print(f"⏳ Mensagens sendo processadas: {len(pending)}")
                for msg_id, status in pending:
                    print(f"   - {msg_id[:8]}...: {status or 'Processando...'}")
            else:
                print("✅ Sem mensagens pendentes")
        
        # 5. Buscar mensagens da conversa
        print("\n5️⃣ Buscando mensagens...")
        messages_response = await client.post(
            f"{BASE_URL}/message/list",
            json={"params": CONVERSATION_ID}
        )
        
        if messages_response.status_code == 200:
            messages = messages_response.json()["result"]
            print(f"📨 Total de mensagens na conversa: {len(messages)}")
            
            if messages:
                print("\n" + "=" * 50)
                print("💬 MENSAGENS NA CONVERSA:")
                print("=" * 50)
                
                for msg in messages:
                    role = msg.get("role", "unknown")
                    msg_id = msg.get("message_id", msg.get("messageid", "N/A"))
                    parts = msg.get("parts", [])
                    
                    print(f"\n[{role.upper()}] (ID: {msg_id[:8] if msg_id != 'N/A' else 'N/A'}...)")
                    
                    for part in parts:
                        if isinstance(part, dict):
                            if "text" in part:
                                print(f"   {part['text']}")
                            elif "content" in part:
                                print(f"   {part['content']}")
                            else:
                                print(f"   {json.dumps(part, indent=2)}")
                    
                    print("-" * 30)
            else:
                print("\n⚠️ Nenhuma mensagem encontrada na conversa")
        
        # 6. Verificar estado final
        print("\n6️⃣ Verificando estado final da conversa...")
        final_response = await client.post(
            f"{BASE_URL}/conversation/list",
            json={}
        )
        
        if final_response.status_code == 200:
            conversations = final_response.json()["result"]
            for conv in conversations:
                if conv["conversationid"] == CONVERSATION_ID:
                    final_count = len(conv.get('messages', []))
                    print(f"✅ Mensagens finais: {final_count}")
                    if final_count > 0:
                        print("   🎉 Mensagem adicionada com sucesso!")
                    break
        
        print("\n" + "=" * 50)
        print("✅ TESTE CONCLUÍDO")
        print("=" * 50)
        return True

async def main():
    try:
        success = await send_test_message()
        if success:
            print("\n🎉 Teste executado com sucesso!")
        else:
            print("\n⚠️ Teste falhou. Verifique os logs acima.")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║         TESTE DE ENVIO DE MENSAGEM               ║
╚══════════════════════════════════════════════════╝
    """)
    print(f"🕐 Iniciando teste em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL da aplicação: {BASE_URL}")
    print(f"📝 Conversa ID: {CONVERSATION_ID}")
    print()
    
    asyncio.run(main())