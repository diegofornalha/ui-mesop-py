# 🎯 PRD: Migração A2A Framework - Claude Code SDK Exclusivo
## Remoção de Múltiplos Providers para SDK Único

---

## 📋 Sumário Executivo

**Objetivo**: Remover completamente Gemini e OpenAI do A2A Framework, usando APENAS Claude Code SDK  
**Situação Atual**: 3 providers (Gemini, OpenAI, Base abstrato)  
**Situação Desejada**: 1 provider único (Claude Code SDK v0.0.20)  
**Complexidade**: BAIXA - Simplificação significativa  
**Timeline**: 30 minutos de implementação  

---

## 🔍 Análise do Estado Atual

### Arquivos de Providers Existentes
```
/agents/a2a/src/llm_providers/
├── base.py       # Interface abstrata (142 linhas) - MANTER SIMPLIFICADO
├── gemini.py     # Google Gemini (347 linhas) - REMOVER
├── openai.py     # OpenAI GPT (305 linhas) - REMOVER  
├── registry.py   # Registry pattern (57 linhas) - SIMPLIFICAR
└── config.py     # Configurações - ADAPTAR
```

### Dependências Atuais no pyproject.toml
```toml
# REMOVER:
google-generativeai
openai

# ADICIONAR:
claude-code-sdk = "^0.0.20"
anthropic = "^0.35.0"
```

---

## 🚀 Plano de Implementação

### 1. Criar Claude Provider Simples
```python
# /agents/a2a/src/llm_providers/claude.py
"""Claude Code SDK Provider - Único provider do sistema."""

from typing import Any, AsyncIterator, Dict, List, Optional, Union
import os
import sys

# Adiciona Claude SDK ao path
sys.path.insert(0, '/home/codable/terminal/claude-code-sdk-python/src')

from claude_code_sdk import ClaudeSDKClient, query
from claude_code_sdk.types import PermissionMode

from .base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    MessageRole,
    ProviderConfig,
    ThinkingBlock,
    ToolCall,
)


class ClaudeProvider(BaseLLMProvider):
    """Claude Code SDK - Provider exclusivo do A2A."""
    
    MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        """Inicializa com Claude SDK."""
        if config is None:
            # Config padrão se não fornecida
            config = ProviderConfig(
                api_key=os.environ.get('ANTHROPIC_API_KEY', ''),
                model="claude-3-opus-20240229",
                temperature=0.7
            )
        
        super().__init__(config)
        self.client = None
        self._connected = False
    
    async def _ensure_connected(self):
        """Garante conexão com Claude SDK."""
        if not self._connected:
            self.client = ClaudeSDKClient()
            await self.client.connect()
            self._connected = True
    
    def _convert_messages(self, messages: List[LLMMessage]) -> str:
        """Converte mensagens A2A para formato Claude."""
        prompt = ""
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                prompt += f"System: {msg.content}\n\n"
            elif msg.role == MessageRole.USER:
                prompt += f"Human: {msg.content}\n\n"
            elif msg.role == MessageRole.ASSISTANT:
                prompt += f"Assistant: {msg.content}\n\n"
            elif msg.role == MessageRole.THINKING:
                prompt += f"<thinking>\n{msg.content}\n</thinking>\n\n"
        
        # Adiciona prompt final se não terminar com Assistant
        if not prompt.strip().endswith("Assistant:"):
            prompt += "Assistant:"
        
        return prompt
    
    async def generate(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_results: Optional[List["ToolResult"]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[LLMResponse, AsyncIterator[LLMResponse]]:
        """Gera resposta usando Claude SDK."""
        await self._ensure_connected()
        
        # Converte mensagens
        prompt = self._convert_messages(messages)
        
        if stream:
            return self._stream_response(prompt)
        else:
            # Usa query síncrona para simplicidade
            response = query(prompt)
            
            # Parse thinking blocks
            content, thinking_blocks = self.parse_thinking_blocks(response)
            
            return LLMResponse(
                content=content,
                thinking_blocks=thinking_blocks,
                tool_calls=[],  # Claude SDK não usa tool calls direto
                usage=None,
                raw_response={"prompt": prompt, "response": response}
            )
    
    async def _stream_response(self, prompt: str) -> AsyncIterator[LLMResponse]:
        """Stream de resposta do Claude."""
        await self._ensure_connected()
        
        # Envia mensagem e recebe stream
        await self.client.query(prompt)
        
        accumulated = ""
        async for response in self.client.receive_messages():
            if response.content:
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        accumulated += content_block.text
                        
                        # Parse thinking blocks
                        content, thinking_blocks = self.parse_thinking_blocks(accumulated)
                        
                        yield LLMResponse(
                            content=content,
                            thinking_blocks=thinking_blocks,
                            tool_calls=[],
                            usage=None
                        )
    
    def supports_thinking(self) -> bool:
        """Claude suporta thinking blocks nativamente."""
        return True
    
    def supports_tools(self) -> bool:
        """Claude SDK usa MCP tools."""
        return True
    
    def get_model_list(self) -> List[str]:
        """Lista de modelos Claude disponíveis."""
        return self.MODELS
    
    async def disconnect(self):
        """Desconecta do Claude SDK."""
        if self._connected and self.client:
            await self.client.disconnect()
            self._connected = False
```

### 2. Simplificar Registry para Único Provider
```python
# /agents/a2a/src/llm_providers/__init__.py
"""LLM Provider - Apenas Claude Code SDK."""

from .base import BaseLLMProvider, LLMMessage, LLMResponse, MessageRole, ProviderConfig
from .claude import ClaudeProvider

# Provider único global
_claude_provider = None

def get_provider(config: Optional[ProviderConfig] = None) -> BaseLLMProvider:
    """Retorna o provider Claude (único disponível)."""
    global _claude_provider
    
    if _claude_provider is None:
        _claude_provider = ClaudeProvider(config)
    
    return _claude_provider

def reset_provider():
    """Reseta o provider (útil para testes)."""
    global _claude_provider
    if _claude_provider:
        import asyncio
        asyncio.run(_claude_provider.disconnect())
    _claude_provider = None

# Exportações públicas
__all__ = [
    'BaseLLMProvider',
    'LLMMessage', 
    'LLMResponse',
    'MessageRole',
    'ProviderConfig',
    'ClaudeProvider',
    'get_provider',
    'reset_provider',
]
```

### 3. Remover Arquivos Desnecessários
```bash
# Arquivos a DELETAR:
rm /agents/a2a/src/llm_providers/gemini.py
rm /agents/a2a/src/llm_providers/openai.py  
rm /agents/a2a/src/llm_providers/registry.py
rm /agents/a2a/src/llm_providers/config.py  # Se existir
```

### 4. Atualizar pyproject.toml
```toml
[project]
name = "a2a-framework"
dependencies = [
    # REMOVER:
    # "google-generativeai",
    # "openai",
    
    # ADICIONAR:
    "claude-code-sdk>=0.0.20",
    "anthropic>=0.35.0",
    "anyio>=4.0.0",  # Dependência do Claude SDK
]
```

### 5. Atualizar Agent.py para Usar Claude
```python
# /agents/a2a/src/a2a/agent.py (simplificado)
from llm_providers import get_provider

class Agent:
    def __init__(self):
        # Sempre usa Claude agora
        self.llm = get_provider()
    
    async def process_message(self, message: str):
        """Processa mensagem com Claude."""
        response = await self.llm.generate([
            LLMMessage(role=MessageRole.USER, content=message)
        ])
        return response.content
```

---

## 🧪 Teste de Validação

### Script de Teste Completo
```python
# /agents/a2a/test_claude_migration.py
#!/usr/bin/env python3
"""Teste da migração para Claude SDK exclusivo."""

import asyncio
import sys
sys.path.insert(0, 'src')

from llm_providers import get_provider, LLMMessage, MessageRole

async def test_claude_provider():
    """Testa o provider Claude."""
    print("🔧 Testando Claude Provider...")
    
    # Obtém provider (sempre Claude agora)
    provider = get_provider()
    print(f"✅ Provider obtido: {provider.__class__.__name__}")
    
    # Testa geração simples
    messages = [
        LLMMessage(role=MessageRole.SYSTEM, content="Você é um assistente útil."),
        LLMMessage(role=MessageRole.USER, content="Diga apenas 'OK' sem mais nada.")
    ]
    
    response = await provider.generate(messages)
    print(f"✅ Resposta: {response.content}")
    
    # Testa thinking blocks
    if provider.supports_thinking():
        print("✅ Thinking blocks suportados")
    
    # Desconecta
    await provider.disconnect()
    print("✅ Provider desconectado")
    
    print("\n🎉 MIGRAÇÃO COMPLETA! Apenas Claude Code SDK ativo!")

if __name__ == "__main__":
    asyncio.run(test_claude_provider())
```

---

## ✅ Checklist de Implementação

- [ ] Criar `/llm_providers/claude.py` com ClaudeProvider
- [ ] Atualizar `/llm_providers/__init__.py` para exportar apenas Claude
- [ ] Deletar `gemini.py`, `openai.py`, `registry.py`
- [ ] Atualizar `pyproject.toml` com dependências Claude
- [ ] Executar teste de validação
- [ ] Confirmar que A2A funciona apenas com Claude

---

## 🎯 Benefícios da Simplificação

1. **Redução de Código**: De ~800 linhas para ~200 linhas
2. **Menos Dependências**: Remove 2 SDKs grandes
3. **Manutenção Simples**: Um único provider
4. **Performance**: Menos overhead de abstração
5. **Clareza**: Sem complexidade de múltiplos providers

---

## ⚡ Comandos de Execução

```bash
# 1. Navegar para o diretório A2A
cd /home/codable/terminal/app-agentflix/web/ui-mesop-py/agents/a2a

# 2. Instalar dependências Claude
pip install claude-code-sdk==0.0.20 anthropic

# 3. Executar teste
python test_claude_migration.py

# 4. Confirmar funcionamento
python -m a2a.cli --help
```

---

**Documento**: PRD A2A Claude SDK Exclusivo  
**Data**: 2025-08-25  
**Status**: ✅ Pronto para Implementação  
**Tempo Estimado**: 30 minutos  

---

*Simplificação radical: de 3 providers para 1, usando apenas Claude Code SDK v0.0.20*