# 🚀 PRD - Migração para Claude Code SDK v3.0
## Documento Consolidado - Análise Completa e Implementação

---

## 📋 Sumário Executivo

**Produto**: AgentFlix UI - Sistema A2A com Mesop  
**Versão SDK**: Claude Code SDK v0.0.20 (já testado e funcionando)  
**Estratégia**: Duas opções - Migração Completa vs Multi-Provider  
**Timeline Realista**: 
- Migração Completa: 6-10 semanas (ALTO RISCO)
- Multi-Provider: 2-3 semanas (RECOMENDADO)
**Risco**: ALTO para completa / MÉDIO para multi-provider  

---

## 🎯 Análise de Viabilidade Consolidada

### ✅ FATORES FAVORÁVEIS (Confirmados)

1. **Claude Code SDK v0.0.20 Funcionando**
   - ✅ SDK instalado e testado
   - ✅ Cliente assíncrono operacional
   - ✅ Função query síncrona disponível
   - ✅ Importações funcionando corretamente
   
2. **Capacidades Superiores do Claude**
   - Context window: 200k tokens (6x maior que Gemini 32k)
   - Thinking blocks nativos para debug transparente
   - MCP (Model Context Protocol) tools robusto
   - Superior em geração de código
   - Streaming nativo com SSE

3. **Arquitetura Compatível**
   - Sistema já usa async/await
   - FastAPI com suporte SSE nativo
   - Threading model pode ser mantido

### 🔴 PONTOS CRÍTICOS DE INVIABILIDADE

#### 1. **Google ADK Runner - CORE DO SISTEMA** (CRÍTICO)
```python
# PROBLEMA FUNDAMENTAL
self._host_runner = Runner(
    app_name=self.app_name,
    agent=agent,
    artifact_service=self._artifact_service,
    session_service=self._session_service,
    memory_service=self._memory_service,
)

# O Runner gerencia:
- Todo ciclo de vida da conversa
- Estado de sessão
- Eventos assíncronos
- Coordenação de agentes
- Artifacts e memória

# IMPACTO: Reescrever tudo = 3-4 semanas só neste componente
```

#### 2. **Session Management Incompatível** (CRÍTICO)
```python
# Google ADK usa 3 serviços integrados:
InMemorySessionService()   # Sessões persistentes
InMemoryArtifactService()   # Artefatos de conversa
InMemoryMemoryService()     # Memória de contexto

# Claude não tem equivalentes diretos
# IMPACTO: Implementar do zero = 1-2 semanas
```

#### 3. **Event Loop Específico** (CRÍTICO)
```python
# ADK tem event loop proprietário
async for event in self._host_runner.run_async(...):
    if event.actions.state_delta:
        # Processa mudanças de estado
    if event.message:
        # Processa mensagem

# Claude tem modelo completamente diferente
# IMPACTO: Adapter complexo = 1 semana
```

#### 4. **Protocolo A2A Dependencies** (ALTO)
```python
# A2A espera formato específico:
Message(
    messageId=str,
    contextId=str, 
    taskId=str,
    parts=[TextPart, FilePart, ...],
    role=Role.USER/ASSISTANT
)

# Claude usa formato diferente
# IMPACTO: Conversão bidirecional = 1 semana
```

#### 5. **Custos e Limites**
- **Custo**: Claude $0.25/M vs Gemini $0.15/M (+66%)
- **Rate limits**: Variam por tier no Claude
- **Latência**: Pode ser maior em Claude

---

## 🏗️ Duas Estratégias Possíveis

### Opção A: MIGRAÇÃO COMPLETA (6-10 semanas) ⚠️

#### Arquitetura Nova Completa
```
┌─────────────────────────────────┐
│       Mesop UI (Python)         │
├─────────────────────────────────┤
│    FastAPI Server               │
├─────────────────────────────────┤
│     ClaudeHostManager           │ ← NOVO (2-3 semanas)
│   ┌──────────────────────┐      │
│   │ ClaudeSessionStore   │      │ ← NOVO (1-2 semanas)  
│   │ ClaudeEventProcessor │      │ ← NOVO (1 semana)
│   │ ClaudeStateManager   │      │ ← NOVO (1 semana)
│   └──────────────────────┘      │
├─────────────────────────────────┤
│    ClaudeAgent (SDK)            │ ← NOVO (3-5 dias)
├─────────────────────────────────┤
│      Claude API                 │
└─────────────────────────────────┘
```

**Componentes Necessários:**
1. ClaudeHostManager - Substitui ADKHostManager completamente
2. ClaudeSessionStore - Gerencia sessões sem ADK
3. ClaudeEventProcessor - Converte eventos
4. ClaudeStateManager - Gerencia estado
5. ClaudeA2AAdapter - Converte protocolos

### Opção B: MULTI-PROVIDER (2-3 semanas) ✅ RECOMENDADO

#### Arquitetura Incremental
```
┌─────────────────────────────────┐
│       Mesop UI (Python)         │
├─────────────────────────────────┤
│    FastAPI Server               │
├─────────────────────────────────┤
│    ProviderManager              │ ← NOVO (3 dias)
│   ┌─────────┬─────────┐        │
│   │  ADK    │ Claude  │        │
│   │ Manager │Provider │        │
│   └─────────┴─────────┘        │
├─────────────────────────────────┤
│    Provider Interface           │ ← NOVO (2 dias)
├─────────────────────────────────┤
│ Gemini API │ Claude API         │
└─────────────────────────────────┘
```

---

## 📦 Implementação Prática com SDK v0.0.20

### Fase 1: Claude Provider (Baseado no SDK testado)

```python
# /service/providers/claude_provider.py
import asyncio
import os
from typing import AsyncIterator, Optional
from claude_code_sdk import ClaudeSDKClient, query
from claude_code_sdk.types import PermissionMode

class ClaudeProvider:
    """Provider usando Claude SDK v0.0.20 testado"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.client = None
        self._connected = False
        
    async def connect(self):
        """Conecta ao Claude SDK"""
        if not self._connected:
            self.client = ClaudeSDKClient()
            await self.client.connect()
            self._connected = True
            
    async def disconnect(self):
        """Desconecta do Claude SDK"""
        if self.client and self._connected:
            await self.client.disconnect()
            self._connected = False
    
    async def send_message(self, message: str) -> AsyncIterator[str]:
        """Envia mensagem e recebe resposta em streaming"""
        if not self._connected:
            await self.connect()
            
        # Envia mensagem
        await self.client.send_message(message)
        
        # Recebe respostas em streaming
        async for response in self.client.receive_messages():
            if response.content and len(response.content) > 0:
                yield response.content[0].text
    
    def query_sync(self, message: str) -> str:
        """Query síncrona para compatibilidade"""
        return query(message)
```

### Fase 2: Adapter A2A

```python
# /service/providers/claude_a2a_adapter.py
from a2a.types import Message, Role, TextPart, Part
from typing import AsyncIterator
import uuid

class ClaudeA2AAdapter:
    """Converte entre Claude SDK e protocolo A2A"""
    
    def __init__(self, claude_provider):
        self.provider = claude_provider
        
    def extract_text_from_a2a(self, message: Message) -> str:
        """Extrai texto de mensagem A2A"""
        text_parts = []
        for part in message.parts:
            if hasattr(part, 'root') and hasattr(part.root, 'text'):
                text_parts.append(part.root.text)
            elif isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])
        return ' '.join(text_parts)
    
    def create_a2a_response(self, text: str, context_id: str) -> Message:
        """Cria mensagem A2A a partir de texto"""
        return Message(
            messageId=str(uuid.uuid4()),
            contextId=context_id,
            role=Role.ASSISTANT,
            parts=[Part(root=TextPart(text=text))],
            author="claude"
        )
        
    async def process_message(self, a2a_message: Message) -> AsyncIterator[Message]:
        """Processa mensagem A2A com Claude"""
        text = self.extract_text_from_a2a(a2a_message)
        
        async for response_text in self.provider.send_message(text):
            yield self.create_a2a_response(
                response_text, 
                a2a_message.contextId
            )
```

### Fase 3: Manager Multi-Provider

```python
# /service/server/multi_provider_manager.py
from typing import Optional
from service.server.adk_host_manager import ADKHostManager
from service.providers.claude_provider import ClaudeProvider
from service.providers.claude_a2a_adapter import ClaudeA2AAdapter

class MultiProviderManager(ApplicationManager):
    """Gerencia múltiplos providers (Gemini + Claude)"""
    
    def __init__(self, http_client, api_key: str = '', 
                 provider: str = 'gemini'):
        self.provider_name = provider
        self.http_client = http_client
        
        if provider == 'claude':
            self.claude_provider = ClaudeProvider(api_key)
            self.adapter = ClaudeA2AAdapter(self.claude_provider)
            self.use_claude = True
        else:
            # Usa ADK/Gemini existente
            self.adk_manager = ADKHostManager(
                http_client, 
                api_key=api_key
            )
            self.use_claude = False
            
    async def process_message(self, message: Message):
        """Processa mensagem com provider selecionado"""
        if self.use_claude:
            # Usa Claude
            async for response in self.adapter.process_message(message):
                self._handle_response(response)
        else:
            # Usa Gemini/ADK existente
            await self.adk_manager.process_message(message)
```

---

## 📊 Plano de Implementação Detalhado

### Para MULTI-PROVIDER (RECOMENDADO) - 2-3 semanas

#### Semana 1: Setup e Provider
- [ ] Dia 1-2: Implementar ClaudeProvider com SDK v0.0.20
- [ ] Dia 3: Implementar ClaudeA2AAdapter
- [ ] Dia 4-5: Testes unitários do provider

#### Semana 2: Integração
- [ ] Dia 1-2: Implementar MultiProviderManager
- [ ] Dia 3: Integrar com server.py (feature flag)
- [ ] Dia 4-5: Testes de integração

#### Semana 3: Deploy e Monitoramento
- [ ] Dia 1-2: Deploy em staging
- [ ] Dia 3-4: A/B testing
- [ ] Dia 5: Documentação e rollout

### Para MIGRAÇÃO COMPLETA - 6-10 semanas

#### Fase 1: Preparação (1 semana)
- Setup ambiente
- Documentação arquitetura atual
- Testes de regressão

#### Fase 2: Core Components (3-4 semanas)
- ClaudeHostManager
- ClaudeSessionStore
- ClaudeEventProcessor
- ClaudeStateManager

#### Fase 3: Integração (2 semanas)
- Adapter A2A
- Conversão de mensagens
- Task management

#### Fase 4: Testes (1-2 semanas)
- Unit tests
- Integration tests
- Performance tests

#### Fase 5: Migração (1 semana)
- Feature flags
- Gradual rollout
- Monitoring

---

## ⚠️ Análise de Riscos Consolidada

### Riscos Críticos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| ADK Runner incompatível | CERTEZA | CRÍTICO | Multi-provider strategy |
| Sessões perdidas | ALTA | CRÍTICO | Redis ou custom store |
| Breaking changes A2A | ALTA | CRÍTICO | Adapter robusto + testes |
| Performance degradada | MÉDIA | ALTO | Caching + otimizações |
| Aumento custos 66% | CERTEZA | MÉDIO | Rate limiting + cache |
| Rollback complexo | ALTA | ALTO | Feature flags |

---

## 💰 Análise de Custos

### Desenvolvimento
- **Multi-Provider**: $5k-10k (2-3 semanas, 1-2 devs)
- **Migração Completa**: $30k-50k (6-10 semanas, 2-3 devs)

### Operacional (mensal)
- **Gemini apenas**: ~$150/mês
- **Claude apenas**: ~$250/mês (+66%)
- **Multi-Provider**: ~$200/mês (uso misto)

---

## 🚫 Critérios de Parada (Kill Switches)

### DEVE PARAR A MIGRAÇÃO COMPLETA SE:

1. **PoC Session Management falhar em 1 semana**
   - Teste: Implementar store básico
   - Se falhar → PARAR

2. **Performance 3x pior em testes**
   - Benchmark: 100 mensagens
   - Se latência > 6s → PARAR

3. **Adapter A2A não funcionar em 1 semana**
   - Teste: Converter 10 mensagens
   - Se falhar → PARAR

4. **Custo > 5x em dev/staging**
   - Monitor: Usage diário
   - Se exceder → PARAR

---

## 🎯 Recomendação Final Consolidada

### Viabilidade por Estratégia:

#### ❌ Migração Completa: NÃO RECOMENDADO
- **Viabilidade**: POSSÍVEL mas MUITO ARRISCADO
- **Complexidade**: MUITO ALTA
- **Timeline**: 6-10 semanas
- **Risco**: ALTO
- **Custo**: $30k-50k
- **ROI**: Questionável

#### ✅ Multi-Provider: ALTAMENTE RECOMENDADO
- **Viabilidade**: ALTA
- **Complexidade**: MÉDIA
- **Timeline**: 2-3 semanas
- **Risco**: MÉDIO-BAIXO
- **Custo**: $5k-10k
- **ROI**: Positivo

### 💡 Estratégia Recomendada:

```python
# Implementar Multi-Provider com Feature Flag
if os.environ.get('LLM_PROVIDER') == 'claude':
    manager = ClaudeProviderManager()
else:
    manager = ADKHostManager()  # Gemini default

# Permite:
# - A/B testing
# - Rollback instantâneo
# - Migração gradual
# - Menor risco
```

---

## 📝 Próximos Passos Imediatos

### Semana 1 (FAZER AGORA):
1. **Dia 1**: Criar branch `feature/multi-provider`
2. **Dia 2-3**: Implementar ClaudeProvider com SDK v0.0.20
3. **Dia 4**: Implementar ClaudeA2AAdapter
4. **Dia 5**: Testes básicos e validação

### Decisão Go/No-Go:
- Após Semana 1: Avaliar PoC
- Se funcionar: Continuar multi-provider
- Se falhar: Reavaliar estratégia

---

## 📊 Métricas de Sucesso

### Multi-Provider Success Criteria:
- [ ] Feature flag funcionando
- [ ] Latência Claude < 3s
- [ ] Zero breaking changes
- [ ] A/B test mostrando paridade
- [ ] Rollback < 1 minuto
- [ ] Custo < 2x Gemini

### KPIs para Monitorar:
1. Response time (p50, p95, p99)
2. Error rate
3. Token usage
4. Cost per conversation
5. User satisfaction (NPS)

---

**Documento Consolidado**: PRD v3.0  
**Data**: 2025-08-25  
**Status**: ✅ Multi-Provider Recomendado / ⚠️ Migração Completa Arriscada  
**Decisão**: Implementar Multi-Provider Strategy primeiro  
**Timeline Recomendado**: 2-3 semanas  
**Próxima Revisão**: Após PoC Semana 1