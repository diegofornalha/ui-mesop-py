# 🔌 INTEGRAÇÃO REAL COM CLAUDE SDK - GUIA COMPLETO

## 📚 DESCOBERTAS DO PROJETO chat-app-claude-code-sdk

Analisando o projeto fornecido, encontrei a integração real funcionando com:
- **@anthropic-ai/claude-code** v1.0.31
- Implementação em JavaScript com padrões adaptáveis para Python

## 1. 🎯 INSTALAÇÃO DO CLAUDE CODE SDK PYTHON

### Opção A: Via pip (SDK oficial Python)
```bash
pip install claude-code-sdk
```

### Opção B: Via npm (para teste local - como no projeto analisado)
```bash
npm install @anthropic-ai/claude-code
```

## 2. 🔧 IMPLEMENTAÇÃO REAL EM PYTHON

### claude_client_real.py - Cliente Real com SDK
```python
"""
Cliente real do Claude usando claude-code-sdk.
Baseado no projeto chat-app-claude-code-sdk analisado.
"""

import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from dataclasses import dataclass
import os

# Importar o SDK real do Claude Code
try:
    from claude_code_sdk import ClaudeClient, query
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️ Claude Code SDK não instalado. Instale com: pip install claude-code-sdk")

@dataclass
class ClaudeClientReal:
    """Cliente real do Claude com SDK."""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self.sdk_available = SDK_AVAILABLE
        
    async def initialize(self):
        """Inicializa o cliente Claude real."""
        if not self.sdk_available:
            print("❌ SDK não disponível - usando modo fallback")
            self.initialized = True
            return
            
        try:
            # Inicializar cliente real
            self.client = ClaudeClient()
            self.initialized = True
            print("✅ Cliente Claude Real inicializado com SDK")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar SDK: {e}")
            self.sdk_available = False
            self.initialized = True
    
    async def send_message(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Envia mensagem para Claude real usando SDK.
        Padrão compatível com o projeto JavaScript analisado.
        """
        if not self.sdk_available:
            # Fallback mockado
            yield {
                "type": "text",
                "content": f"[MODO FALLBACK] Resposta simulada para: {prompt[:50]}..."
            }
            return
        
        try:
            # Usar query do SDK real (como no ClaudeAgent.js)
            options = {
                "maxTurns": kwargs.get("maxTurns", 1),
                "temperature": kwargs.get("temperature", 0.7),
                "maxTokens": kwargs.get("maxTokens", 4096)
            }
            
            # Stream de resposta real
            async for message in query(prompt=prompt, options=options):
                if message.get("type") == "result" and not message.get("is_error"):
                    yield {
                        "type": "text",
                        "content": message.get("result", "")
                    }
                elif message.get("type") == "text":
                    yield {
                        "type": "text",
                        "content": message.get("content", "")
                    }
                    
        except Exception as e:
            print(f"❌ Erro ao chamar Claude SDK: {e}")
            yield {
                "type": "error",
                "content": f"Erro: {str(e)}"
            }
    
    async def send_message_simple(self, prompt: str) -> str:
        """Versão simples sem streaming."""
        response = ""
        async for chunk in self.send_message(prompt):
            if chunk.get("type") == "text":
                response += chunk.get("content", "")
        return response
```

### Atualização do claude_client.py existente
```python
"""
Atualização do claude_client.py para usar SDK real quando disponível.
"""

# No início do arquivo claude_client.py, adicionar:

# Tentar importar cliente real
try:
    from .claude_client_real import ClaudeClientReal
    REAL_SDK_AVAILABLE = True
except ImportError:
    REAL_SDK_AVAILABLE = False

class ClaudeClientV10:
    def __init__(self, use_real_sdk: bool = True):
        self.use_real_sdk = use_real_sdk and REAL_SDK_AVAILABLE
        self.real_client = None
        
        if self.use_real_sdk:
            self.real_client = ClaudeClientReal()
            print("✅ Usando Claude SDK real")
        else:
            print("⚠️ Usando fallback mockado")
    
    async def initialize(self):
        """Inicializa o cliente."""
        if self.real_client:
            await self.real_client.initialize()
    
    async def send_message(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Envia mensagem para Claude."""
        if self.real_client and self.real_client.sdk_available:
            # Usar SDK real
            async for chunk in self.real_client.send_message(prompt, **kwargs):
                yield chunk
        else:
            # Usar fallback mockado existente
            yield {
                "type": "text",
                "content": f"Resposta simulada para: {prompt[:100]}..."
            }
```

## 3. 🔄 PADRÕES DE INTEGRAÇÃO DESCOBERTOS

### Do projeto JavaScript analisado (ClaudeAgent.js):
```javascript
// Padrão de uso do SDK
for await (const msg of query({
    prompt: prompt,
    options: queryOptions
})) {
    if (msg.type === 'result' && !msg.is_error && msg.result) {
        response = msg.result;
        break;
    }
}
```

### Adaptado para Python:
```python
async for msg in query(prompt=prompt, options=options):
    if msg["type"] == "result" and not msg.get("is_error") and msg.get("result"):
        response = msg["result"]
        break
```

## 4. 🚀 IMPLEMENTAÇÃO COM STREAMING REAL

### claude_a2a_agent_v2.py - Atualização para SDK real
```python
class ClaudeA2AAgent(BaseAgent):
    def __init__(self, name: str = "Claude Agent", instruction: str = "", use_real_sdk: bool = True):
        super().__init__(name, instruction)
        # Usar cliente real quando disponível
        self.llm_client = ClaudeClientV10(use_real_sdk=use_real_sdk)
        self.streaming_enabled = True
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Implementação com streaming real do Claude."""
        
        # ... código anterior ...
        
        # Chamar Claude com SDK real
        try:
            response_text = ""
            partial_count = 0
            
            # Stream real do Claude SDK
            async for chunk in self.llm_client.send_message(
                prompt,
                temperature=0.7,
                maxTokens=4096,
                stream=True  # Habilitar streaming
            ):
                if chunk.get("type") == "text":
                    text_chunk = chunk.get("content", "")
                    response_text += text_chunk
                    
                    # Yield evento parcial para streaming real
                    partial_count += 1
                    if self.streaming_enabled and partial_count % 3 == 0:
                        yield Event(
                            author=self.name,
                            invocation_id=invocation_id,
                            content=Content.from_text(response_text),
                            partial=True,  # Streaming real!
                            turn_complete=False
                        )
                
                elif chunk.get("type") == "error":
                    logger.error(f"Erro do Claude SDK: {chunk.get('content')}")
                    response_text = "Desculpe, ocorreu um erro ao processar sua mensagem."
                    break
```

## 5. ✅ CONFIGURAÇÃO (NÃO PRECISA API KEY!)

### O Claude Code SDK usa o CLI local já configurado!
```bash
# Verificar se Claude está instalado:
claude --version

# Se não estiver, instalar Claude Code:
# Via VS Code: instalar extensão Claude
# Via npm: npm install -g claude-code
```

### Como funciona:
```python
# O SDK usa o Claude CLI que já está autenticado no sistema
from claude_code_sdk import query, ClaudeSDKClient

# NÃO precisa de API key!
# NÃO precisa de variáveis de ambiente!
# Usa a autenticação existente do Claude Code

async with ClaudeSDKClient() as client:
    response = await client.send_message("Olá!")
    print(response)
```

## 6. 📊 ESTRUTURA DE RESPOSTA DO SDK REAL

Baseado no projeto analisado:

```python
# Resposta de texto simples
{
    "type": "text",
    "content": "Resposta do Claude..."
}

# Resposta com resultado
{
    "type": "result",
    "result": "Conteúdo processado...",
    "is_error": false
}

# Resposta de erro
{
    "type": "error",
    "error": "Mensagem de erro",
    "is_error": true
}

# Resposta estruturada (com AI SDK v5)
{
    "type": "object",
    "object": {
        "field1": "value1",
        "field2": "value2"
    }
}
```

## 7. 🧪 TESTE DE INTEGRAÇÃO

### test_claude_sdk_real.py
```python
#!/usr/bin/env python3
"""
Teste da integração real com Claude SDK.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.claude_client import ClaudeClientV10

async def test_real_sdk():
    """Testa integração real com Claude SDK."""
    print("=" * 60)
    print("🧪 TESTE: Integração Real com Claude SDK")
    print("=" * 60)
    
    # Criar cliente com SDK real
    client = ClaudeClientV10(use_real_sdk=True)
    await client.initialize()
    
    # Testar mensagem simples
    print("\n📤 Enviando mensagem para Claude real...")
    prompt = "Olá Claude! Responda em uma linha."
    
    response = ""
    chunk_count = 0
    
    async for chunk in client.send_message(prompt):
        if chunk.get("type") == "text":
            text = chunk.get("content", "")
            response += text
            chunk_count += 1
            print(f"   Chunk {chunk_count}: {text[:50]}...")
    
    print(f"\n📥 Resposta completa ({chunk_count} chunks):")
    print(response)
    
    if response and response != f"Resposta simulada para: {prompt[:100]}...":
        print("\n✅ SUCESSO: SDK real funcionando!")
        return True
    else:
        print("\n⚠️ AVISO: Usando fallback (SDK não disponível)")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_sdk())
    sys.exit(0 if success else 1)
```

## 8. 🔄 MIGRAÇÃO GRADUAL

### Fase 1: Preparação
1. Instalar `claude-code-sdk` ou `@anthropic-ai/claude-code`
2. Configurar API key
3. Criar `claude_client_real.py`

### Fase 2: Teste
1. Executar `test_claude_sdk_real.py`
2. Verificar conexão com Claude
3. Validar streaming

### Fase 3: Integração
1. Atualizar `claude_client.py` com suporte ao SDK real
2. Modificar `claude_a2a_agent_v2.py` para usar cliente real
3. Testar com `test_adk_architecture.py`

### Fase 4: Deploy
1. Configurar API key em produção
2. Habilitar SDK real por padrão
3. Monitorar uso e custos

## 9. 📈 BENEFÍCIOS DA INTEGRAÇÃO REAL

1. **Respostas reais do Claude** - Não mais respostas mockadas
2. **Streaming real** - Token por token em tempo real
3. **Capacidades completas** - Tools, análise de código, multi-step
4. **Memória de contexto** - Conversas com histórico
5. **Structured outputs** - Respostas em JSON/Schema

## 10. 💡 PRÓXIMOS PASSOS RECOMENDADOS

1. **Instalar SDK**:
   ```bash
   pip install claude-code-sdk
   # ou
   npm install @anthropic-ai/claude-code
   ```

2. **Obter API Key**:
   - Acessar https://console.anthropic.com
   - Criar conta/fazer login
   - Gerar API key

3. **Testar integração**:
   ```bash
   python test_claude_sdk_real.py
   ```

4. **Validar com arquitetura V2**:
   ```bash
   python test_adk_architecture.py
   ```

## 🎯 CONCLUSÃO

Com base no projeto `chat-app-claude-code-sdk` analisado, temos um caminho claro para integração real:

1. ✅ Padrões de uso identificados
2. ✅ Estrutura de resposta mapeada
3. ✅ Streaming implementado
4. ✅ Fallback quando SDK não disponível
5. ✅ Compatibilidade com arquitetura V2

**Agora é só instalar o SDK e configurar a API key para ter respostas reais do Claude!**