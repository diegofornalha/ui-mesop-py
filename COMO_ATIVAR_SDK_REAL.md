# 🚀 COMO ATIVAR O SDK REAL DO CLAUDE

## ⚠️ STATUS ATUAL
O servidor está usando a arquitetura antiga (V1). Para usar o SDK real precisamos:

## 📋 PASSOS PARA ATIVAR

### 1. Parar o servidor atual
```bash
# No terminal onde está rodando o servidor
Ctrl+C
```

### 2. Executar com o servidor V2
```bash
cd /home/codable/terminal/app-agentflix/web/ui-mesop-py

# Tornar executável
chmod +x start_server_v2.sh

# Iniciar servidor V2
./start_server_v2.sh
```

### 3. Se precisar voltar ao servidor antigo
```bash
# Editar main.py linha 24
# Trocar:
from service.server.server_v2 import ConversationServerV2 as ConversationServer
# Por:
from service.server.server import ConversationServer

# E executar
./start_server.sh
```

## 🔧 ARQUIVOS MODIFICADOS

1. **main.py** - Importa server_v2 ao invés de server
2. **server_v2.py** - Usa ClaudeRunner V2 com SDK real
3. **claude_a2a_agent_v2.py** - Aceita parâmetro use_real_sdk
4. **claude_client.py** - Importa SDK path automaticamente

## ✅ VERIFICAÇÃO

Quando o SDK real estiver funcionando, você verá:
```
✅ Claude Code SDK Python disponível
✅ Cliente Claude SDK pronto (usando CLI local)
```

E as respostas serão reais do Claude, não mockadas.

## 🔍 TROUBLESHOOTING

### Se não funcionar:
1. Verificar se Claude CLI está instalado: `claude --version`
2. Verificar se SDK existe: `ls /home/codable/terminal/claude-code-sdk-python/src`
3. Ver logs detalhados no terminal do servidor

### Para testar SDK isoladamente:
```bash
cd /home/codable/terminal/app-agentflix/web/ui-mesop-py
python3 test_sdk_direto.py
```

## 📝 RESUMO

**Atualmente:** Servidor V1 sem SDK real
**Para ativar:** Reiniciar com `./start_server_v2.sh`
**SDK:** Já configurado e testado funcionando!