# A2A Python Example UI

Interface de usuário para o framework de agentes Agent2Agent com Mesop.

## 🚀 Execução Rápida

### Opção 1: Script Automático (Recomendado)
```bash
./start_server_improved.sh
```

### Opção 2: Comando Manual
```bash
uv run main.py
```

### Opção 3: Script Original
```bash
./start_server.sh
```

### Parar o Servidor
```bash
./stop_server.sh
```

## ⚙️ Configuração

### Variáveis de Ambiente
O servidor usa as seguintes variáveis de ambiente:

- `A2A_UI_HOST`: Host do servidor (padrão: 0.0.0.0)
- `A2A_UI_PORT`: Porta preferida (padrão: 8888)
- `MESOP_DEFAULT_PORT`: Porta alternativa (padrão: 8888)
- `DEBUG_MODE`: Modo debug (padrão: false)

### Arquivo de Configuração
Copie `config.env.example` para `.env` e ajuste conforme necessário:

```bash
cp config.env.example .env
```

## 🔧 Funcionalidades

- **Seleção Inteligente de Porta**: Tenta usar a porta 8888, senão usa 8888
- **Patch Automático**: Aplica patch para `a2a.types.Message` automaticamente
- **Verificação de Ambiente**: Detecta e ativa ambiente virtual automaticamente
- **Liberação de Portas**: Tenta liberar portas em uso automaticamente

## 🌐 Acesso

A aplicação estará disponível em:
- **Porta Preferida**: http://localhost:8888
- **Porta Alternativa**: http://localhost:8888

## 📁 Estrutura do Projeto

```
ui-mesop-py/
├── main.py                 # Arquivo principal do servidor
├── start_server_improved.sh # Script de inicialização inteligente
├── start_server.sh         # Script de inicialização original
├── stop_server.sh          # Script para parar o servidor
├── config.env.example      # Exemplo de configuração
├── message_patch.py        # Patch para a2a.types.Message
├── components/             # Componentes da UI
├── pages/                  # Páginas da aplicação
├── service/                # Serviços backend
└── state/                  # Gerenciamento de estado
```

## 🐛 Solução de Problemas

### Porta em Uso
Se uma porta estiver em uso, o sistema tentará:
1. Liberar a porta automaticamente
2. Usar a porta alternativa
3. Exibir informações sobre o processo que está usando a porta

### Ambiente Virtual
O sistema detecta automaticamente se há um ambiente virtual e o ativa.

### Patch de Message
O patch para `a2a.types.Message` é aplicado automaticamente na inicialização.
