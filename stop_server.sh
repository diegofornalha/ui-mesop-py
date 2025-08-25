#!/bin/bash
# Script para parar o servidor A2A UI

echo "🛑 Parando servidor A2A UI..."
echo "=============================="

# Função para parar processos em uma porta específica
stop_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🔄 Parando processos na porta $port..."
        echo $pids | xargs kill -TERM 2>/dev/null
        sleep 2
        
        # Verificar se ainda há processos
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$remaining_pids" ]; then
            echo "⚠️  Processos ainda ativos, forçando parada..."
            echo $remaining_pids | xargs kill -KILL 2>/dev/null
        fi
        
        if [ -z "$(lsof -ti:$port 2>/dev/null)" ]; then
            echo "✅ Porta $port liberada com sucesso"
        else
            echo "❌ Falha ao liberar porta $port"
            return 1
        fi
    else
        echo "✅ Porta $port já está livre"
    fi
}

# Parar processos nas portas principais
echo "🔍 Verificando portas em uso..."
echo "--------------------------------"

# Porta 8888 (preferida)
if lsof -ti:8888 > /dev/null 2>&1; then
    echo "📡 Servidor rodando na porta 8888"
    stop_port 8888
else
    echo "✅ Porta 8888 livre"
fi

# Porta 8888 (alternativa)
if lsof -ti:8888 > /dev/null 2>&1; then
    echo "📡 Servidor rodando na porta 8888"
    stop_port 8888
else
    echo "✅ Porta 8888 livre"
fi

echo ""
echo "🎯 Verificando se ainda há processos Python rodando..."
python_processes=$(ps aux | grep "main.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$python_processes" ]; then
    echo "🔄 Parando processos Python restantes..."
    echo $python_processes | xargs kill -TERM 2>/dev/null
    sleep 1
    echo "✅ Processos Python parados"
else
    echo "✅ Nenhum processo Python ativo"
fi

echo ""
echo "🎉 Servidor parado com sucesso!"
echo "💡 Use './start_server_improved.sh' para reiniciar"
