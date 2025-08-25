#!/bin/bash
# Script para iniciar o servidor A2A UI (Original ou Responsivo)

echo "🚀 Iniciando servidor A2A UI..."
echo "=================================="

# Função para mostrar menu de seleção
show_menu() {
    echo ""
    echo "📱 Escolha a versão do servidor:"
    echo "1) Versão Original (main.py)"
    echo "2) Versão Responsiva (main_responsive.py)"
    echo "3) Sair"
    echo ""
    read -p "Digite sua escolha (1-3): " choice
}

# Função para parar processos anteriores
stop_previous_processes() {
    echo "🔄 Parando processos anteriores..."
    pkill -f "python.*main.py" 2>/dev/null
    pkill -f "python.*main_responsive.py" 2>/dev/null
    sleep 2

    # Verificar se a porta está livre
    if lsof -i :8888 > /dev/null 2>&1; then
        echo "⚠️  Porta 8888 ainda em uso, forçando liberação..."
        lsof -ti:8888 | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Função para verificar ambiente virtual
check_venv() {
    if [ ! -d ".venv" ]; then
        echo "❌ Ambiente virtual não encontrado!"
        echo "💡 Execute: python -m venv .venv"
        exit 1
    fi
    echo "✅ Ambiente virtual encontrado"
}

# Função para iniciar servidor original
start_original_server() {
    echo "🖥️  Iniciando servidor ORIGINAL..."
    echo "📝 Características: Layout fixo, otimizado para desktop"
    
    GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
    A2A_UI_PORT=8888 \
    MESOP_DEFAULT_PORT=8888 \
    .venv/bin/python main.py
}

# Função para iniciar servidor responsivo
start_responsive_server() {
    echo "📱 Iniciando servidor RESPONSIVO..."
    echo "📝 Características: Layout adaptativo, mobile-first, drawer menu"
    
    # Verificar se os arquivos responsivos existem
    if [ ! -f "main_responsive.py" ]; then
        echo "❌ Arquivo main_responsive.py não encontrado!"
        echo "💡 Certifique-se de que todos os arquivos responsivos foram criados"
        exit 1
    fi
    
    GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
    A2A_UI_PORT=8888 \
    MESOP_DEFAULT_PORT=8888 \
    .venv/bin/python main_responsive.py
}

# Função para mostrar informações de conexão
show_connection_info() {
    # Obter o IP da máquina
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "🌐 Servidor iniciado na porta 8888"
    echo "🔗 URL Local: http://localhost:8888"
    echo "🔗 URL IP: http://${SERVER_IP}:8888"
    echo ""
    echo "💡 Dicas:"
    echo "   - Use F12 no navegador para testar responsividade"
    echo "   - Redimensione a janela para ver as adaptações"
    echo "   - Teste em dispositivos móveis reais"
    echo ""
}

# Execução principal
stop_previous_processes
check_venv

# Mostrar menu e processar escolha
while true; do
    show_menu
    
    case $choice in
        1)
            show_connection_info
            start_original_server
            break
            ;;
        2)
            show_connection_info
            start_responsive_server
            break
            ;;
        3)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida! Digite 1, 2 ou 3."
            ;;
    esac
done
