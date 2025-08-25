#!/bin/bash
# Script para iniciar o servidor com o patch aplicado

echo "🚀 Iniciando servidor com patch para messageid..."
echo "=============================================="

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    echo "✅ Ativando ambiente virtual..."
    source .venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado, usando Python global"
fi

# Executar o servidor
echo "🔧 Patch será aplicado automaticamente..."
echo "📡 Iniciando servidor (porta será selecionada automaticamente)..."
echo "   - Porta preferida: 8888"
echo "   - Porta alternativa: 8888 (Mesop padrão)"
echo ""

# Verificar se há processos rodando na porta 8888
if lsof -ti:8888 > /dev/null 2>&1; then
    echo "⚠️  Porta 8888 está em uso por:"
    lsof -ti:8888 | xargs ps -p 2>/dev/null | grep -v PID || echo "   Processo não encontrado"
    echo ""
fi

echo "🐍 Usando uv run para executar com dependências corretas..."
uv run main.py