# 📋 PLANO DE IMPLEMENTAÇÃO E ROLLBACK - MIGRAÇÃO CLAUDE SDK V10
## Documento de Controle de Mudanças com Marcos de Reversão

---

## 🎯 OBJETIVO DO DOCUMENTO

Estabelecer marcos claros de implementação com pontos de rollback seguros, garantindo reversibilidade total em caso de problemas.

## 🔄 ESTRATÉGIA DE ROLLBACK

### Princípio FUNDAMENTAL:
**"Cada mudança deve ser reversível em menos de 5 minutos"**

### Tipos de Rollback:
1. **Rollback Parcial**: Reverter apenas o componente problemático
2. **Rollback Total**: Voltar completamente ao Gemini
3. **Rollback Híbrido**: Manter Claude em teste, Gemini em produção

---

## 📊 MARCOS DE IMPLEMENTAÇÃO (MILESTONES)

### 🔷 MILESTONE 0: PREPARAÇÃO (30 min)
**Status Gate**: Sistema deve estar 100% funcional com Gemini

#### Ações:
```bash
# 1. Criar branch de implementação
git checkout -b migration-claude-v10
git status  # Confirmar branch limpo

# 2. Backup completo do estado atual
tar -czf backup_gemini_$(date +%Y%m%d_%H%M%S).tar.gz \
  agents/ \
  components/ \
  pages/ \
  main.py

# 3. Salvar configuração atual no Neo4j
```

#### Validação:
- [ ] Sistema rodando com Gemini
- [ ] Backup criado e verificado
- [ ] Branch de trabalho criado

#### 🔴 ROLLBACK M0:
```bash
git checkout main
rm -rf backup_gemini_*.tar.gz
```

---

### 🔷 MILESTONE 1: INSTALAÇÃO DE DEPENDÊNCIAS (15 min)
**Status Gate**: Todas dependências instaladas sem conflitos

#### Ações:
```bash
# 1. Salvar requirements atual
pip freeze > requirements_backup.txt

# 2. Instalar Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. Verificar instalação
claude --version > install_log.txt

# 4. Instalar SDK Python
pip install claude-code-sdk==0.0.20

# 5. Verificar importação
python -c "import claude_code_sdk; print('OK')"
```

#### Validação:
- [ ] CLI Claude instalado e funcionando
- [ ] SDK Python importa sem erros
- [ ] Sistema Gemini ainda funcional

#### 🔴 ROLLBACK M1:
```bash
# Remover Claude CLI
npm uninstall -g @anthropic-ai/claude-code

# Restaurar pip
pip uninstall claude-code-sdk -y
pip install -r requirements_backup.txt

# Verificar
python main.py  # Deve funcionar com Gemini
```

---

### 🔷 MILESTONE 2: CRIAÇÃO DOS ARQUIVOS CLAUDE (20 min)
**Status Gate**: Arquivos criados sem afetar sistema existente

#### Ações:
```bash
# 1. Criar arquivos novos (NÃO sobrescrever!)
cd agents/
touch claude_sdk_client.py
touch claude_host_manager_sdk.py

# 2. Adicionar código dos arquivos
# (copiar do PRD V10 DEFINITIVO)

# 3. Testar isoladamente
python -c "from claude_sdk_client import ClaudeSDKClientV10; print('Import OK')"
```

#### Validação:
- [ ] Arquivos criados com sucesso
- [ ] Imports funcionam isoladamente
- [ ] Sistema Gemini não afetado

#### 🔴 ROLLBACK M2:
```bash
# Simplesmente deletar arquivos novos
rm agents/claude_sdk_client.py
rm agents/claude_host_manager_sdk.py
git status  # Confirmar apenas arquivos novos removidos
```

---

### 🔷 MILESTONE 3: TESTE ISOLADO CLAUDE (20 min)
**Status Gate**: Claude funciona em teste sem integração

#### Ações:
```python
# test_claude_isolated.py
import asyncio
from agents.claude_host_manager_sdk import ClaudeHostManagerSDKV10

async def test():
    host = await ClaudeHostManagerSDKV10().initialize()
    
    # Teste simples
    async for response in host.process_message(
        session_id="test",
        message="Diga apenas: OK"
    ):
        print(response)
        if "OK" in str(response):
            print("✅ TESTE PASSOU!")
            return True
    
    print("❌ TESTE FALHOU!")
    return False

success = asyncio.run(test())
exit(0 if success else 1)
```

#### Validação:
- [ ] Teste isolado passa
- [ ] Claude responde corretamente
- [ ] Sem erros de autenticação

#### 🔴 ROLLBACK M3:
```bash
# Apenas parar testes, nada a reverter
rm test_claude_isolated.py
```

---

### 🔷 MILESTONE 4: INTEGRAÇÃO SWITCH MODE (30 min)
**Status Gate**: Sistema com capacidade de switch Gemini/Claude

#### Ações:
```python
# agents/__init__.py - Adicionar switch
import os
USE_CLAUDE = os.getenv('USE_CLAUDE', 'false').lower() == 'true'

if USE_CLAUDE:
    from .claude_host_manager_sdk import ClaudeHostManagerSDKV10 as HostManager
else:
    from .gemini_host import GeminiHost as HostManager

# Host global com switch
current_host = HostManager()
```

#### Teste com Switch:
```bash
# Testar com Gemini (padrão)
python main.py  # Deve usar Gemini

# Testar com Claude
USE_CLAUDE=true python main.py  # Deve usar Claude

# Voltar para Gemini
python main.py  # Deve usar Gemini novamente
```

#### Validação:
- [ ] Switch funciona corretamente
- [ ] Gemini funciona quando USE_CLAUDE=false
- [ ] Claude funciona quando USE_CLAUDE=true

#### 🔴 ROLLBACK M4:
```bash
# Reverter agents/__init__.py
git checkout agents/__init__.py

# Confirmar Gemini funcionando
python main.py
```

---

### 🔷 MILESTONE 5: TESTE A/B EM PRODUÇÃO (45 min)
**Status Gate**: Ambos sistemas funcionando em paralelo

#### Ações:
```python
# main.py - Adicionar roteamento A/B
import random

def get_host_for_session(session_id):
    # 10% das sessões para Claude (teste)
    if random.random() < 0.1:
        return claude_host
    return gemini_host
```

#### Monitoramento:
```python
# Adicionar logging
logger.info(f"Session {session_id} using {'Claude' if use_claude else 'Gemini'}")

# Métricas
METRICS = {
    'gemini_requests': 0,
    'claude_requests': 0,
    'gemini_errors': 0,
    'claude_errors': 0
}
```

#### Validação:
- [ ] 90% tráfego em Gemini
- [ ] 10% tráfego em Claude
- [ ] Métricas sendo coletadas
- [ ] Sem aumento de erros

#### 🔴 ROLLBACK M5:
```bash
# Remover A/B testing
git checkout main.py

# Forçar apenas Gemini
export USE_CLAUDE=false
python main.py
```

---

### 🔷 MILESTONE 6: MIGRAÇÃO COMPLETA (30 min)
**Status Gate**: 100% tráfego em Claude, Gemini como backup

#### Ações:
```bash
# 1. Aumentar gradualmente
# 25% -> 50% -> 75% -> 100%

# 2. Modificar default
export USE_CLAUDE=true

# 3. Manter Gemini disponível para rollback
```

#### Validação Final:
- [ ] Claude handling 100% do tráfego
- [ ] Performance aceitável (< 2s resposta)
- [ ] Sem erros críticos por 30 minutos
- [ ] Logs limpos

#### 🔴 ROLLBACK M6:
```bash
# ROLLBACK IMEDIATO
export USE_CLAUDE=false
systemctl restart mesop  # ou pm2 restart main

# Verificar
curl http://localhost:8080/health
```

---

## 🚨 MATRIZ DE DECISÃO DE ROLLBACK

| Situação | Severidade | Ação | Tempo Max |
|----------|-----------|------|-----------|
| CLI Claude não instala | CRÍTICA | Rollback M1 | 2 min |
| Import error no SDK | CRÍTICA | Rollback M2 | 2 min |
| Erro de autenticação | ALTA | Rollback M3 | 5 min |
| Performance > 5s | MÉDIA | Rollback M5 | 10 min |
| Taxa erro > 5% | ALTA | Rollback M5 | 5 min |
| Crash do sistema | CRÍTICA | Rollback TOTAL | 1 min |

---

## 📝 SCRIPT DE ROLLBACK AUTOMATIZADO

```bash
#!/bin/bash
# rollback.sh - Rollback de emergência

MILESTONE=${1:-"TOTAL"}

case $MILESTONE in
  M1)
    echo "🔄 Rollback M1: Removendo dependências..."
    npm uninstall -g @anthropic-ai/claude-code
    pip uninstall claude-code-sdk -y
    ;;
  
  M2|M3)
    echo "🔄 Rollback M2/M3: Removendo arquivos Claude..."
    rm -f agents/claude_sdk_client.py
    rm -f agents/claude_host_manager_sdk.py
    ;;
  
  M4|M5)
    echo "🔄 Rollback M4/M5: Revertendo integração..."
    git checkout agents/__init__.py
    git checkout main.py
    ;;
  
  TOTAL)
    echo "🚨 ROLLBACK TOTAL: Voltando ao Gemini..."
    export USE_CLAUDE=false
    git checkout main
    git branch -D migration-claude-v10
    
    # Restaurar backup se necessário
    if [ -f backup_gemini_*.tar.gz ]; then
      tar -xzf backup_gemini_*.tar.gz
    fi
    ;;
esac

echo "✅ Rollback $MILESTONE completado!"
echo "🔍 Verificando sistema..."
python -c "import main; print('Sistema OK')" && echo "✅ Sistema funcionando!"
```

---

## 📊 CHECKLIST PÓS-IMPLEMENTAÇÃO

### Funcional:
- [ ] Sistema responde em < 2 segundos
- [ ] Todas rotas da API funcionando
- [ ] Interface Mesop sem erros
- [ ] Logs sem warnings críticos

### Performance:
- [ ] CPU < 80% utilização
- [ ] Memória < 4GB uso
- [ ] Sem memory leaks após 1h
- [ ] Response time P95 < 3s

### Segurança:
- [ ] Sem API keys expostas
- [ ] Logs sem informações sensíveis
- [ ] Autenticação local funcionando

### Rollback:
- [ ] Script de rollback testado
- [ ] Backup Gemini disponível
- [ ] Switch mode funcionando
- [ ] Documentação atualizada

---

## 📈 MONITORAMENTO CONTÍNUO

```python
# monitor.py - Monitoramento em tempo real
import time
import requests

while True:
    try:
        # Testar health
        resp = requests.get('http://localhost:8080/health')
        
        if resp.status_code != 200:
            print("🚨 ALERTA: Sistema degradado!")
            # Trigger rollback automático
            os.system('./rollback.sh M5')
        
        # Verificar latência
        if resp.elapsed.total_seconds() > 3:
            print("⚠️ WARNING: Latência alta!")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        os.system('./rollback.sh TOTAL')
    
    time.sleep(30)
```

---

## 🎯 CRITÉRIOS DE SUCESSO

✅ **Implementação bem-sucedida quando:**
1. 100% tráfego em Claude por 2 horas
2. Zero erros críticos
3. Performance equivalente ou melhor que Gemini
4. Rollback testado e funcional

❌ **Abortar implementação se:**
1. Mais de 3 rollbacks necessários
2. Erros afetando > 10% dos usuários
3. Performance degradada > 50%
4. Problemas de autenticação recorrentes

---

## 📝 REGISTRO DE IMPLEMENTAÇÃO

| Data/Hora | Milestone | Status | Responsável | Observações |
|-----------|-----------|--------|-------------|-------------|
| | M0 | ⏳ Aguardando | | |
| | M1 | ⏳ Aguardando | | |
| | M2 | ⏳ Aguardando | | |
| | M3 | ⏳ Aguardando | | |
| | M4 | ⏳ Aguardando | | |
| | M5 | ⏳ Aguardando | | |
| | M6 | ⏳ Aguardando | | |

---

**Documento criado**: 2025-08-26  
**Versão**: 1.0  
**Próxima revisão**: Pós-implementação

⚠️ **IMPORTANTE**: Sempre ter o script `rollback.sh` pronto e testado ANTES de iniciar a migração!