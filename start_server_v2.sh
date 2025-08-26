#!/bin/bash
# Script para iniciar o servidor V2 com SDK real

echo "🚀 Iniciando servidor V2 com SDK real..."
echo "=================================="

# Parar processos anteriores
echo "🔄 Parando processos anteriores..."
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Adicionar SDK ao PYTHONPATH
export PYTHONPATH="/home/codable/terminal/claude-code-sdk-python/src:$PYTHONPATH"

echo "✅ SDK Path configurado"
echo "🌐 Iniciando servidor V2 na porta 8888..."
echo "🔗 URL: http://localhost:8888"
echo ""

# Executar com logging detalhado
GOOGLE_API_KEY="dummy" \
A2A_UI_PORT=8888 \
MESOP_DEFAULT_PORT=8888 \
PYTHONPATH="/home/codable/terminal/claude-code-sdk-python/src:$PYTHONPATH" \
python3 main.py