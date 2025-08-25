#!/usr/bin/env python3
"""
Script para configurar a API Key do Gemini
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8888"
API_KEY = "AIzaSyDeyRoAZwxeA7_XcXwz4aTKurPBAWsnYY0"

async def set_api_key():
    """Configura a API Key do Gemini"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔑 Configurando API Key do Gemini...")
        print("-" * 50)
        
        # Configurar API Key
        api_key_data = {
            "api_key": API_KEY
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api_key/update",
                json=api_key_data
            )
            
            if response.status_code == 200:
                print(f"✅ API Key configurada com sucesso!")
                result = response.json()
                print(f"   Resposta: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Erro ao configurar API Key: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao configurar API Key: {str(e)}")
            return False
        
        # Verificar mensagens pendentes
        print("\n📋 Verificando mensagens pendentes...")
        pending_response = await client.post(
            f"{BASE_URL}/message/pending",
            json={}
        )
        
        if pending_response.status_code == 200:
            pending = pending_response.json()["result"]
            if pending:
                print(f"⏳ Mensagens pendentes encontradas: {len(pending)}")
                for msg_id, status in pending:
                    print(f"   - {msg_id[:8]}...: {status or 'Aguardando processamento'}")
                print("\n🔄 As mensagens devem começar a ser processadas agora...")
            else:
                print("✅ Sem mensagens pendentes")
        
        return True

async def main():
    try:
        success = await set_api_key()
        if success:
            print("\n🎉 API Key configurada com sucesso!")
            print("💡 As mensagens pendentes devem começar a ser processadas agora.")
        else:
            print("\n⚠️ Falha ao configurar API Key.")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════╗
║       CONFIGURAÇÃO DA API KEY DO GEMINI          ║
╚══════════════════════════════════════════════════╝
    """)
    print(f"🕐 Iniciando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL da aplicação: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print()
    
    asyncio.run(main())