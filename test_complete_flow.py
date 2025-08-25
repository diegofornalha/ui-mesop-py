#!/usr/bin/env python3
"""
Script para testar fluxo completo de mensagens com API Key configurada
"""

import asyncio
import httpx
import uuid
import json
from datetime import datetime

BASE_URL = "http://localhost:8888"

async def test_full_flow():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔧 Testando fluxo completo com API Key configurada...")
        print("-" * 50)
        
        # 1. Criar nova conversa
        print("\n1️⃣ Criando nova conversa...")
        create_response = await client.post(
            f"{BASE_URL}/conversation/create",
            json={}
        )
        
        if create_response.status_code != 200:
            print(f"❌ Erro ao criar conversa: {create_response.status_code}")
            return
            
        conversation_data = create_response.json()
        conversation_id = conversation_data["result"]["conversationid"]
        print(f"✅ Nova conversa criada: {conversation_id}")
        
        # 2. Enviar mensagem de teste
        print("\n2️⃣ Enviando mensagem de teste...")
        message_id = str(uuid.uuid4())
        
        message_data = {
            "params": {
                "message_id": message_id,
                "context_id": conversation_id,
                "role": "user",
                "parts": [
                    {
                        "text": "Olá! Você está funcionando? Por favor responda com uma mensagem simples confirmando que está operacional."
                    }
                ]
            }
        }
        
        send_response = await client.post(
            f"{BASE_URL}/message/send",
            json=message_data
        )
        
        if send_response.status_code == 200:
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"   ID da mensagem: {message_id[:8]}...")
        else:
            print(f"❌ Erro ao enviar: {send_response.status_code}")
            return
        
        # 3. Aguardar processamento
        print("\n3️⃣ Aguardando processamento...")
        for i in range(15):
            await asyncio.sleep(1)
            print(f"   {i+1}/15 segundos...", end="\r")
        print()
        
        # 4. Verificar mensagens
        print("\n4️⃣ Verificando mensagens na conversa...")
        messages_response = await client.post(
            f"{BASE_URL}/message/list",
            json={"params": conversation_id}
        )
        
        if messages_response.status_code == 200:
            messages = messages_response.json()["result"]
            print(f"📨 Total de mensagens: {len(messages)}")
            
            if messages:
                print("\n💬 CONVERSA COMPLETA:")
                print("=" * 50)
                for i, msg in enumerate(messages, 1):
                    role = msg.get("role", "unknown")
                    msg_id = msg.get("message_id", msg.get("messageid", "N/A"))
                    parts = msg.get("parts", [])
                    
                    print(f"\n[{i}] {role.upper()} (ID: {msg_id[:8] if msg_id != 'N/A' else 'N/A'}...)")
                    
                    for part in parts:
                        if isinstance(part, dict):
                            if "text" in part:
                                text = part["text"]
                                # Mostrar texto completo ou truncado se muito longo
                                if len(text) > 200:
                                    print(f"    {text[:200]}...")
                                else:
                                    print(f"    {text}")
                print("\n" + "=" * 50)
                
                # Verificar se há resposta do assistente
                assistant_messages = [m for m in messages if m.get("role") == "assistant"]
                if assistant_messages:
                    print("✅ SUCESSO! O assistente respondeu!")
                else:
                    print("⚠️ Ainda aguardando resposta do assistente...")
            else:
                print("⚠️ Nenhuma mensagem processada ainda")
        
        # 5. Verificar mensagens pendentes
        print("\n5️⃣ Verificando mensagens pendentes...")
        pending_response = await client.post(
            f"{BASE_URL}/message/pending",
            json={}
        )
        
        if pending_response.status_code == 200:
            pending = pending_response.json()["result"]
            print(f"⏳ Total de mensagens pendentes: {len(pending)}")
            if pending:
                print("   Detalhes:")
                for msg_id, status in pending[:5]:  # Mostrar até 5
                    print(f"   - {msg_id[:8]}...: {status or 'Em processamento'}")
        
        # 6. Verificar estado final da conversa
        print("\n6️⃣ Verificando estado final...")
        list_response = await client.post(
            f"{BASE_URL}/conversation/list",
            json={}
        )
        
        if list_response.status_code == 200:
            conversations = list_response.json()["result"]
            for conv in conversations:
                if conv["conversationid"] == conversation_id:
                    message_count = len(conv.get("messages", []))
                    print(f"✅ Conversa encontrada com {message_count} mensagem(ns)")
                    
                    if message_count > 1:
                        print("\n🎉 SUCESSO COMPLETO! Sistema funcionando!")
                    elif message_count == 1:
                        print("\n⚠️ Apenas mensagem do usuário. Aguardando resposta do AI...")
                    else:
                        print("\n❌ Nenhuma mensagem registrada na conversa")
                    break
        
        return conversation_id

async def main():
    try:
        print("""
╔══════════════════════════════════════════════════╗
║   TESTE COMPLETO DO SISTEMA COM GEMINI API       ║
╚══════════════════════════════════════════════════╝
        """)
        print(f"🕐 Iniciando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 URL da aplicação: {BASE_URL}")
        print()
        
        conversation_id = await test_full_flow()
        
        if conversation_id:
            print(f"\n📝 ID da conversa para referência: {conversation_id}")
            print("\n💡 Dica: Você pode verificar esta conversa na interface web")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())