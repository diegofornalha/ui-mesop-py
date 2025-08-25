#!/bin/bash
# Script para testar a responsividade do Chat UI

echo "🧪 Teste de Responsividade - Chat UI Mesop"
echo "=========================================="

# Verificar se o servidor está rodando
check_server() {
    if curl -s http://localhost:8888 > /dev/null 2>&1; then
        echo "✅ Servidor está rodando em http://localhost:8888"
        return 0
    else
        echo "❌ Servidor não está rodando!"
        echo "💡 Execute primeiro: ./start_server.sh"
        return 1
    fi
}

# Função para abrir navegador com diferentes tamanhos
open_browser_tests() {
    echo ""
    echo "🌐 Abrindo testes no navegador..."
    
    # Verificar se o navegador está disponível
    if command -v google-chrome > /dev/null 2>&1; then
        BROWSER="google-chrome"
    elif command -v firefox > /dev/null 2>&1; then
        BROWSER="firefox"
    else
        echo "⚠️  Navegador não encontrado. Abra manualmente:"
        echo "   http://localhost:8888"
        return
    fi
    
    echo "📱 Abrindo em modo mobile..."
    $BROWSER --window-size=375,667 http://localhost:8888 &
    sleep 2
    
    echo "📱 Abrindo em modo tablet..."
    $BROWSER --window-size=768,1024 http://localhost:8888 &
    sleep 2
    
    echo "💻 Abrindo em modo desktop..."
    $BROWSER --window-size=1200,800 http://localhost:8888 &
}

# Função para mostrar instruções de teste
show_test_instructions() {
    echo ""
    echo "📋 Instruções para Teste Manual:"
    echo "================================"
    echo ""
    echo "1. 📱 Teste Mobile (até 768px):"
    echo "   - Sidebar deve aparecer como drawer (menu hamburger)"
    echo "   - Chat bubbles devem ocupar 90% da largura"
    echo "   - Input deve ter altura adequada para touch"
    echo "   - Botões devem ter mínimo 44x44px"
    echo ""
    echo "2. 📱 Teste Tablet (769px - 1024px):"
    echo "   - Sidebar deve estar colapsada (60px)"
    echo "   - Chat bubbles devem ocupar 80% da largura"
    echo "   - Layout deve ser intermediário"
    echo ""
    echo "3. 💻 Teste Desktop (acima de 1024px):"
    echo "   - Sidebar deve estar expandida (200px)"
    echo "   - Chat bubbles devem ocupar 70% da largura"
    echo "   - Máxima largura de 600px para bubbles"
    echo ""
    echo "4. 🔄 Teste de Transições:"
    echo "   - Redimensione a janela gradualmente"
    echo "   - Observe as mudanças nos breakpoints"
    echo "   - Verifique se as transições são suaves"
    echo ""
    echo "5. 🎯 Teste de Funcionalidade:"
    echo "   - Envie mensagens em diferentes tamanhos"
    echo "   - Teste o menu mobile (se disponível)"
    echo "   - Verifique scroll e navegação"
    echo ""
}

# Função para mostrar ferramentas de desenvolvimento
show_dev_tools() {
    echo ""
    echo "🛠️  Ferramentas de Desenvolvimento:"
    echo "=================================="
    echo ""
    echo "Chrome DevTools (F12):"
    echo "  - Toggle device toolbar (Ctrl+Shift+M)"
    echo "  - Selecione dispositivos predefinidos"
    echo "  - Teste orientação landscape/portrait"
    echo ""
    echo "Firefox DevTools (F12):"
    echo "  - Responsive Design Mode"
    echo "  - Simular diferentes dispositivos"
    echo ""
    echo "Safari DevTools:"
    echo "  - Develop > Enter Responsive Design Mode"
    echo ""
}

# Função para verificar arquivos responsivos
check_responsive_files() {
    echo ""
    echo "📁 Verificando arquivos responsivos..."
    
    files=(
        "main_responsive.py"
        "styles/responsive.py"
        "components/responsive_chat_bubble.py"
        "components/responsive_conversation.py"
        "components/responsive_page_scaffold.py"
        "components/responsive_sidenav.py"
        "components/viewport_detector.py"
        "static/responsive.css"
        "pages/responsive_conversation.py"
    )
    
    missing_files=()
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "✅ $file"
        else
            echo "❌ $file (faltando)"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        echo ""
        echo "🎉 Todos os arquivos responsivos estão presentes!"
    else
        echo ""
        echo "⚠️  Alguns arquivos estão faltando. Execute a implementação completa."
    fi
}

# Execução principal
echo "🔍 Verificando ambiente..."

# Verificar arquivos responsivos
check_responsive_files

# Verificar servidor
if check_server; then
    echo ""
    echo "🎯 Escolha uma opção:"
    echo "1) Abrir testes automáticos no navegador"
    echo "2) Mostrar instruções de teste manual"
    echo "3) Mostrar ferramentas de desenvolvimento"
    echo "4) Sair"
    echo ""
    read -p "Digite sua escolha (1-4): " test_choice
    
    case $test_choice in
        1)
            open_browser_tests
            ;;
        2)
            show_test_instructions
            ;;
        3)
            show_dev_tools
            ;;
        4)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida!"
            ;;
    esac
else
    exit 1
fi

echo ""
echo "🎉 Teste concluído! Verifique os resultados no navegador."
