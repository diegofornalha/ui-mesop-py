#!/usr/bin/env python
"""
Teste direto do Claude Code SDK - Verifica se a LLM responde.
"""

import asyncio
from claude_code_sdk import query, ClaudeCodeOptions

async def test_direct_sdk():
    """Testa o SDK diretamente sem passar pelo servidor."""
    print("🧪 TESTE DIRETO DO CLAUDE CODE SDK")
    print("="*50)
    
    try:
        # Configurar opções
        options = ClaudeCodeOptions(
            system_prompt="Você é um assistente útil que responde em português",
            max_turns=1
        )
        
        # Testar com pergunta simples
        test_prompts = [
            "Responda com uma palavra: qual é a capital do Brasil?",
            "Quanto é 2 + 2? Responda apenas o número.",
            "Diga 'OLÁ MUNDO' em maiúsculas"
        ]
        
        for prompt in test_prompts:
            print(f"\n📤 Pergunta: {prompt}")
            print("⏳ Aguardando resposta do Claude...")
            
            response_text = ""
            async for message in query(prompt=prompt, options=options):
                # Processar resposta
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_text += block.text
                elif hasattr(message, 'text'):
                    response_text += message.text
                elif isinstance(message, str):
                    response_text += message
            
            if response_text:
                print(f"✅ Claude respondeu: {response_text[:100]}")
            else:
                print("❌ Sem resposta do Claude")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def test_via_subprocess():
    """Testa Claude via subprocess direto."""
    import subprocess
    
    print("\n" + "="*50)
    print("🧪 TESTE VIA SUBPROCESS (CLI DIRETO)")
    print("="*50)
    
    try:
        # Teste 1: Verificar versão
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"📌 Claude CLI: {result.stdout.strip()}")
        
        # Teste 2: Enviar mensagem simples
        print("\n📤 Enviando: 'Diga apenas OK'")
        result = subprocess.run(
            "echo 'Diga apenas OK' | claude",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            print(f"✅ Resposta CLI: {result.stdout[:100]}...")
            return True
        else:
            print(f"❌ CLI não respondeu ou erro: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao chamar Claude CLI")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def test_integration():
    """Testa a integração completa."""
    print("\n" + "="*50)
    print("🧪 TESTE DE INTEGRAÇÃO COM O SERVIDOR")
    print("="*50)
    
    try:
        # Verificar se o servidor está rodando
        import httpx
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Teste 1: Verificar se servidor responde
            try:
                response = await client.get("http://localhost:8888/")
                if response.status_code == 200:
                    print("✅ Servidor respondendo em localhost:8888")
                else:
                    print(f"⚠️ Servidor retornou status: {response.status_code}")
            except:
                print("❌ Servidor não está acessível")
                return False
            
            # Teste 2: Criar conversa
            print("\n📝 Criando conversa...")
            response = await client.post(
                "http://localhost:8888/conversation/create",
                json={}
            )
            
            if response.status_code != 200:
                print(f"❌ Erro ao criar conversa: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return False
            
            data = response.json()
            if not data.get("result"):
                print("❌ Resposta sem resultado")
                return False
                
            conversation_id = data["result"].get("conversationId")
            print(f"✅ Conversa criada: {conversation_id[:8]}...")
            
            # Teste 3: Enviar mensagem
            import uuid
            print("\n💬 Enviando mensagem de teste...")
            message = {
                "params": {
                    "messageId": str(uuid.uuid4()),
                    "contextId": conversation_id,
                    "role": "user",
                    "parts": [{"text": "Olá Claude! Responda com uma saudação em português."}]
                }
            }
            
            response = await client.post(
                "http://localhost:8888/message/send",
                json=message
            )
            
            if response.status_code == 200:
                print("✅ Mensagem enviada com sucesso")
                
                # Aguardar processamento
                await asyncio.sleep(3)
                
                # Buscar mensagens
                response = await client.post(
                    "http://localhost:8888/message/list",
                    json={"params": conversation_id}
                )
                
                if response.status_code == 200:
                    messages = response.json().get("result", [])
                    print(f"📨 Total de mensagens na conversa: {len(messages)}")
                    
                    # Procurar resposta do Claude
                    for msg in messages:
                        if msg.get("role") == "agent":
                            print("✅ Claude respondeu!")
                            return True
                    
                    print("⚠️ Nenhuma resposta do agente encontrada")
                    return False
            else:
                print(f"❌ Erro ao enviar mensagem: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🚀 TESTE COMPLETO DO CLAUDE CODE SDK")
    print("="*60)
    
    results = {}
    
    # Teste 1: SDK Direto
    print("\n[1/3] Testando SDK diretamente...")
    results['sdk'] = await test_direct_sdk()
    
    # Teste 2: CLI via subprocess
    print("\n[2/3] Testando CLI via subprocess...")
    results['cli'] = await test_via_subprocess()
    
    # Teste 3: Integração com servidor
    print("\n[3/3] Testando integração com servidor...")
    results['integration'] = await test_integration()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    print(f"SDK Direto:    {'✅ PASSOU' if results.get('sdk') else '❌ FALHOU'}")
    print(f"CLI Direto:    {'✅ PASSOU' if results.get('cli') else '❌ FALHOU'}")
    print(f"Integração:    {'✅ PASSOU' if results.get('integration') else '❌ FALHOU'}")
    
    if all(results.values()):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Claude está respondendo corretamente!")
    else:
        print("\n⚠️ Alguns testes falharam")
        print("Verifique os logs acima para detalhes")
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)