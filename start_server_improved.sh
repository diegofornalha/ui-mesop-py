#!/bin/bash
# Script melhorado para iniciar o servidor A2A UI

echo "🚀 Iniciando servidor A2A UI com configurações inteligentes..."
echo "=============================================================="

# Função para verificar se uma porta está disponível
check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "❌ Porta $port está em uso por:"
        lsof -ti:$port | xargs ps -p 2>/dev/null | grep -v PID || echo "   Processo não encontrado"
        return 1
    else
        echo "✅ Porta $port está disponível"
        return 0
    fi
}

# Função para matar processos em uma porta específica
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🔄 Matando processos na porta $port..."
        echo $pids | xargs kill -9 2>/dev/null
        sleep 1
        if check_port $port; then
            echo "✅ Porta $port liberada com sucesso"
        else
            echo "❌ Falha ao liberar porta $port"
            return 1
        fi
    fi
}

# Verificar ambiente virtual
if [ -d ".venv" ]; then
    echo "✅ Ativando ambiente virtual..."
    source .venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado, usando Python global"
fi

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "📝 Arquivo .env não encontrado, criando configurações padrão..."
    cat > .env << EOF
# Configurações do Servidor A2A UI
A2A_UI_HOST=0.0.0.0
A2A_UI_PORT=8888
MESOP_DEFAULT_PORT=8888
DEBUG_MODE=false
EOF
    echo "✅ Arquivo .env criado com configurações padrão"
fi

# Verificar portas
echo ""
echo "🔍 Verificando disponibilidade das portas..."
echo "--------------------------------------------"

# Verificar porta preferida (8888)
if check_port 8888; then
    echo "🎯 Usando porta preferida: 8888"
    PREFERRED_PORT=8888
else
    echo "⚠️  Porta 8888 em uso, tentando liberar..."
    if kill_port 8888; then
        PREFERRED_PORT=8888
    else
        echo "🔄 Tentando porta alternativa: 8888"
        if check_port 8888; then
            PREFERRED_PORT=8888
        else
            echo "⚠️  Porta 8888 também em uso, tentando liberar..."
            if kill_port 8888; then
                PREFERRED_PORT=8888
            else
                echo "❌ Não foi possível liberar nenhuma porta"
                echo "💡 Tente matar os processos manualmente ou reinicie o sistema"
                exit 1
            fi
        fi
    fi
fi

# Configurar variável de ambiente para a porta
export A2A_UI_PORT=$PREFERRED_PORT

echo ""
echo "🔧 Aplicando patch para messageid..."
echo "📡 Iniciando servidor na porta $PREFERRED_PORT..."
echo "🌐 URL: http://localhost:$PREFERRED_PORT"
echo ""

# Executar o servidor
echo "🐍 Usando uv run para executar com dependências corretas..."
uv run main.py
