#!/usr/bin/env python
"""
Script para interagir com o chat remotamente via API.
Testa o sistema Claude enviando mensagens diretamente.
"""

import asyncio
import httpx
import json
import uuid
from typing import Optional, Dict, Any

class RemoteChatClient:
    """Cliente para interagir com o chat remotamente."""
    
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.conversation_id: Optional[str] = None
    
    async def create_conversation(self) -> str:
        """Cria uma nova conversa."""
        try:
            response = await self.client.post(
                f"{self.base_url}/conversation/create",
                json={}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                self.conversation_id = data["result"]["conversationId"]
                print(f"✅ Conversa criada: {self.conversation_id[:8]}...")
                return self.conversation_id
            else:
                print("❌ Erro ao criar conversa")
                return ""
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return ""
    
    async def send_message(self, text: str) -> Dict[str, Any]:
        """Envia uma mensagem para o chat."""
        if not self.conversation_id:
            await self.create_conversation()
        
        message = {
            "params": {
                "messageId": str(uuid.uuid4()),
                "contextId": self.conversation_id,
                "role": "user",
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        }
        
        try:
            print(f"\n📤 Enviando: {text}")
            response = await self.client.post(
                f"{self.base_url}/message/send",
                json=message
            )
            response.raise_for_status()
            data = response.json()
            
            # Aguardar processamento
            await asyncio.sleep(2)
            
            # Buscar mensagens
            messages = await self.list_messages()
            
            # Pegar última mensagem do agente
            if messages:
                for msg in reversed(messages):
                    if msg.get("role") == "agent":
                        response_text = self._extract_text(msg.get("parts", []))
                        print(f"📥 Claude: {response_text}")
                        return {"success": True, "response": response_text}
            
            return {"success": False, "error": "Sem resposta"}
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_messages(self) -> list:
        """Lista mensagens da conversa atual."""
        if not self.conversation_id:
            return []
        
        try:
            response = await self.client.post(
                f"{self.base_url}/message/list",
                json={"params": self.conversation_id}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("result", [])
            
        except Exception as e:
            print(f"❌ Erro ao listar mensagens: {e}")
            return []
    
    def _extract_text(self, parts: list) -> str:
        """Extrai texto das parts da mensagem."""
        texts = []
        for part in parts:
            if isinstance(part, dict):
                if "text" in part:
                    texts.append(part["text"])
                elif "root" in part and "text" in part["root"]:
                    texts.append(part["root"]["text"])
            elif isinstance(part, str):
                texts.append(part)
        return " ".join(texts)
    
    async def interactive_chat(self):
        """Modo de chat interativo."""
        print("\n" + "="*60)
        print("💬 CHAT REMOTO COM CLAUDE")
        print("="*60)
        print("Digite 'sair' para encerrar\n")
        
        # Criar conversa
        await self.create_conversation()
        
        while True:
            try:
                # Pegar input do usuário
                user_input = input("\n👤 Você: ")
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    print("\n👋 Encerrando chat...")
                    break
                
                # Enviar mensagem
                await self.send_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    async def test_connection(self) -> bool:
        """Testa se o servidor está respondendo."""
        try:
            response = await self.client.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        """Fecha o cliente."""
        await self.client.aclose()


async def test_automated():
    """Testa o chat automaticamente com mensagens pré-definidas."""
    print("\n🤖 TESTE AUTOMATIZADO DO CHAT")
    print("="*60)
    
    client = RemoteChatClient()
    
    # Verificar conexão
    if not await client.test_connection():
        print("❌ Servidor não está respondendo em http://localhost:8888")
        print("   Verifique se o servidor está rodando: ./start_server.sh")
        await client.close()
        return
    
    print("✅ Servidor online")
    
    # Criar conversa
    await client.create_conversation()
    
    # Testar mensagens
    test_messages = [
        "Olá! Você está funcionando?",
        "Qual é 2 + 2?",
        "Me diga uma palavra em português"
    ]
    
    for msg in test_messages:
        result = await client.send_message(msg)
        await asyncio.sleep(1)
    
    print("\n✅ Teste automatizado concluído!")
    await client.close()


async def main():
    """Menu principal."""
    print("\n" + "="*60)
    print("🚀 CLIENTE REMOTO PARA CHAT CLAUDE")
    print("="*60)
    
    client = RemoteChatClient()
    
    # Verificar conexão
    print("\n🔍 Verificando servidor...")
    if not await client.test_connection():
        print("❌ Servidor não está respondendo em http://localhost:8888")
        print("\n📝 Para iniciar o servidor:")
        print("   1. Em outro terminal, vá para o diretório do projeto")
        print("   2. Execute: ./start_server.sh")
        print("   3. Aguarde o servidor iniciar")
        print("   4. Execute este script novamente")
        await client.close()
        return
    
    print("✅ Servidor online!")
    
    print("\n📋 Escolha uma opção:")
    print("1. Chat interativo")
    print("2. Teste automatizado")
    print("3. Sair")
    
    try:
        choice = input("\nOpção: ")
        
        if choice == "1":
            await client.interactive_chat()
        elif choice == "2":
            await test_automated()
        else:
            print("👋 Saindo...")
    
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Programa encerrado")