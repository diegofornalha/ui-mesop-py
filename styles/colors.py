"""
Paleta de cores centralizada para toda a aplicação UI Mesop
Mantém consistência visual sem necessidade de dark mode
"""

# Cores principais
PRIMARY = '#1976d2'  # Azul corporativo profissional
SECONDARY = '#757575'  # Cinza médio para elementos secundários
ACCENT = '#ff4081'  # Rosa accent para destaque

# Backgrounds
BACKGROUND = '#ffffff'  # Fundo principal branco limpo
BACKGROUND_SECONDARY = '#f5f5f5'  # Fundo secundário cinza muito claro
SURFACE = '#fafafa'  # Superfícies elevadas
SIDEBAR = '#f8f9fa'  # Sidebar com leve destaque

# Texto
TEXT_PRIMARY = '#212121'  # Texto principal - cinza escuro
TEXT_SECONDARY = '#757575'  # Texto secundário - cinza médio
TEXT_ON_PRIMARY = '#ffffff'  # Texto sobre cor primária
TEXT_ON_SECONDARY = '#ffffff'  # Texto sobre cor secundária

# Estados e feedback
ERROR = '#d32f2f'  # Vermelho para erros
SUCCESS = '#388e3c'  # Verde para sucesso
WARNING = '#f57c00'  # Laranja para avisos
INFO = '#0288d1'  # Azul claro para informações

# Mensagens do chat (mantendo esquema rosa customizado)
MESSAGE_USER = '#d8407f'  # Rosa escuro para mensagens do usuário
MESSAGE_USER_TEXT = '#ffffff'  # Texto branco nas mensagens do usuário
MESSAGE_AI = '#ffe0ec'  # Rosa bem claro para mensagens da IA
MESSAGE_AI_TEXT = '#212121'  # Texto escuro nas mensagens da IA

# Containers e cards
CONTAINER_PRIMARY = '#e3f2fd'  # Container azul claro
CONTAINER_SECONDARY = '#f5f5f5'  # Container cinza claro

# Bordas e divisores
BORDER = '#e0e0e0'  # Borda padrão
DIVIDER = '#e0e0e0'  # Linha divisória

# Sombras (valores de box-shadow)
SHADOW_LIGHT = '0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15)'
SHADOW_MEDIUM = '0 2px 4px rgba(0,0,0,0.1)'
SHADOW_HEAVY = '0 4px 6px rgba(0,0,0,0.1)'

# Botões
BUTTON_PRIMARY = PRIMARY
BUTTON_PRIMARY_TEXT = TEXT_ON_PRIMARY
BUTTON_SECONDARY = SECONDARY
BUTTON_SECONDARY_TEXT = TEXT_ON_SECONDARY

# Input fields
INPUT_BACKGROUND = '#ffffff'
INPUT_BORDER = '#e0e0e0'
INPUT_FOCUS = PRIMARY