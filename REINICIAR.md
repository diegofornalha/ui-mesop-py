# 🔄 Como Reiniciar o Servidor

## 🚀 **Comando Rápido (Copiar e Colar):**

```bash
# Para e reinicia o servidor
pkill -f "python.*main.py" && sleep 2 && \
GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
A2A_UI_PORT=8888 MESOP_DEFAULT_PORT=8888 \
.venv/bin/python main.py
```

---

## 📋 **Passo a Passo:**

### 1️⃣ **Parar o servidor atual:**
```bash
pkill -f "python.*main.py"
```

### 2️⃣ **Aguardar 2 segundos:**
```bash
sleep 2
```

### 3️⃣ **Iniciar novamente:**
```bash
GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
A2A_UI_PORT=8888 MESOP_DEFAULT_PORT=8888 \
.venv/bin/python main.py
```

---

## ⚠️ **Quando Reiniciar é Necessário:**

✅ **SEMPRE reiniciar após:**
- Mudanças em arquivos Python (`.py`)
- Alterações em `state/state.py`
- Modificações em componentes
- Mudanças em configurações
- Alterações na API key

❌ **NÃO precisa reiniciar após:**
- Mudanças em arquivos `.md`
- Alterações no git
- Mudanças em documentação

---

## 🔑 **Variáveis de Ambiente:**

```bash
GOOGLE_API_KEY="sua_chave_aqui"    # API key do Gemini
A2A_UI_PORT=8888                   # Porta do servidor
MESOP_DEFAULT_PORT=8888             # Porta padrão Mesop
```

---

## 🛠️ **Troubleshooting:**

### **Erro: "Porta 8888 já em uso"**
```bash
# Força parar todos os processos na porta
lsof -ti:8888 | xargs kill -9
```

### **Verificar se está rodando:**
```bash
ps aux | grep main.py
```

### **Ver logs em tempo real:**
```bash
# Em outro terminal
tail -f logs/*.log
```

---

## 💡 **Dicas:**

1. **Usar `&` para rodar em background:**
```bash
.venv/bin/python main.py &
```

2. **Verificar servidor:**
```bash
curl http://localhost:8888
```

3. **Abrir no navegador:**
```bash
open http://localhost:8888
```

---

## 📌 **Atalho para Terminal:**

Adicione ao seu `.bashrc` ou `.zshrc`:

```bash
alias reiniciar="pkill -f 'python.*main.py' && sleep 2 && \
GOOGLE_API_KEY='AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI' \
A2A_UI_PORT=8888 MESOP_DEFAULT_PORT=8888 \
.venv/bin/python main.py"
```

Depois use apenas:
```bash
reiniciar
```

---

**Última atualização:** 25/08/2025  
**Status:** ✅ Funcionando