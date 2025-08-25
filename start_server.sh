#!/bin/bash
# Script simplificado para iniciar o servidor A2A UI

echo "🚀 Iniciando servidor A2A UI..."
echo "=================================="

# Parar qualquer processo anterior
echo "🔄 Parando processos anteriores..."
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Verificar se a porta está livre
if lsof -i :8888 > /dev/null 2>&1; then
    echo "⚠️  Porta 8888 ainda em uso, forçando liberação..."
    lsof -ti:8888 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Verificar ambiente virtual
if [ ! -d ".venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "💡 Execute: python -m venv .venv"
    exit 1
fi

echo "✅ Ambiente virtual encontrado"
echo "🌐 Iniciando servidor na porta 8888..."
echo "🔗 URL: http://localhost:8888"
echo ""

# Executar o servidor com as configurações corretas
GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
A2A_UI_PORT=8888 \
MESOP_DEFAULT_PORT=8888 \
.venv/bin/python main.py
