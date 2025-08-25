"""Componente para detectar e gerenciar o tamanho da viewport"""

import mesop as me
from typing import Callable


@me.stateclass
class ViewportState:
    """Estado da viewport"""
    width: int = 1200  # Desktop por padrão
    height: int = 800
    is_mobile: bool = False
    is_tablet: bool = False
    is_desktop: bool = True
    device_type: str = "desktop"


def update_viewport_size(width: int, height: int):
    """Atualiza o tamanho da viewport no estado"""
    from styles.responsive import MOBILE_BREAKPOINT, TABLET_BREAKPOINT
    
    state = me.state(ViewportState)
    state.width = width
    state.height = height
    
    # Determinar tipo de dispositivo
    if width <= MOBILE_BREAKPOINT:
        state.is_mobile = True
        state.is_tablet = False
        state.is_desktop = False
        state.device_type = "mobile"
    elif width <= TABLET_BREAKPOINT:
        state.is_mobile = False
        state.is_tablet = True
        state.is_desktop = False
        state.device_type = "tablet"
    else:
        state.is_mobile = False
        state.is_tablet = False
        state.is_desktop = True
        state.device_type = "desktop"


@me.component
def viewport_detector():
    """
    Componente que detecta o tamanho da viewport.
    
    Nota: Por enquanto, isso é um placeholder. 
    Em uma implementação real, precisaríamos de JavaScript para detectar
    o tamanho real da viewport e comunicar com o backend.
    """
    # Adicionar um script inline para detectar viewport
    # (Em produção, isso seria feito com JavaScript real)
    
    me.html(
        """
        <script>
        // Detectar tamanho da viewport
        function updateViewportSize() {
            const width = window.innerWidth;
            const height = window.innerHeight;
            
            // Enviar informações para o backend (placeholder)
            console.log('Viewport:', width, 'x', height);
            
            // Adicionar classes CSS baseadas no tamanho
            document.body.classList.remove('mobile', 'tablet', 'desktop');
            
            if (width <= 768) {
                document.body.classList.add('mobile');
            } else if (width <= 1024) {
                document.body.classList.add('tablet');
            } else {
                document.body.classList.add('desktop');
            }
        }
        
        // Atualizar no carregamento e redimensionamento
        window.addEventListener('load', updateViewportSize);
        window.addEventListener('resize', updateViewportSize);
        
        // Chamar imediatamente
        updateViewportSize();
        </script>
        """,
        mode="sandboxed",
    )


@me.component
def responsive_container(
    mobile_style: me.Style = None,
    tablet_style: me.Style = None,
    desktop_style: me.Style = None,
    default_style: me.Style = None,
):
    """
    Container que aplica estilos diferentes baseados no dispositivo.
    
    Args:
        mobile_style: Estilo para dispositivos móveis
        tablet_style: Estilo para tablets
        desktop_style: Estilo para desktop
        default_style: Estilo padrão aplicado sempre
    """
    viewport_state = me.state(ViewportState)
    
    # Determinar qual estilo usar
    if viewport_state.is_mobile and mobile_style:
        style = mobile_style
    elif viewport_state.is_tablet and tablet_style:
        style = tablet_style
    elif viewport_state.is_desktop and desktop_style:
        style = desktop_style
    else:
        style = default_style or me.Style()
    
    # Mesclar com estilo padrão se existir
    if default_style and style != default_style:
        # Aqui você mesclaria os estilos (simplificado)
        combined_style = style
    else:
        combined_style = style
    
    with me.box(style=combined_style):
        me.slot()


@me.component
def responsive_text(
    text: str,
    mobile_size: int = 14,
    tablet_size: int = 16,
    desktop_size: int = 18,
    **kwargs
):
    """
    Texto com tamanho responsivo.
    
    Args:
        text: Texto a exibir
        mobile_size: Tamanho da fonte em mobile
        tablet_size: Tamanho da fonte em tablet
        desktop_size: Tamanho da fonte em desktop
        **kwargs: Outros parâmetros de estilo
    """
    viewport_state = me.state(ViewportState)
    
    # Determinar tamanho da fonte
    if viewport_state.is_mobile:
        font_size = mobile_size
    elif viewport_state.is_tablet:
        font_size = tablet_size
    else:
        font_size = desktop_size
    
    # Criar estilo com tamanho responsivo
    style = me.Style(font_size=font_size, **kwargs)
    
    me.text(text, style=style)


@me.component
def responsive_grid(
    mobile_columns: int = 1,
    tablet_columns: int = 2,
    desktop_columns: int = 3,
    gap: int = 16,
):
    """
    Grid responsivo que ajusta número de colunas baseado no dispositivo.
    
    Args:
        mobile_columns: Número de colunas em mobile
        tablet_columns: Número de colunas em tablet
        desktop_columns: Número de colunas em desktop
        gap: Espaçamento entre elementos
    """
    viewport_state = me.state(ViewportState)
    
    # Determinar número de colunas
    if viewport_state.is_mobile:
        columns = mobile_columns
    elif viewport_state.is_tablet:
        columns = tablet_columns
    else:
        columns = desktop_columns
    
    # Criar grid style
    grid_style = me.Style(
        display="grid",
        grid_template_columns=f"repeat({columns}, 1fr)",
        gap=gap,
        width="100%",
    )
    
    with me.box(style=grid_style):
        me.slot()


@me.component
def show_on_device(device_types: list[str]):
    """
    Mostra conteúdo apenas em dispositivos específicos.
    
    Args:
        device_types: Lista de tipos de dispositivo ("mobile", "tablet", "desktop")
    """
    viewport_state = me.state(ViewportState)
    
    if viewport_state.device_type in device_types:
        me.slot()


@me.component
def hide_on_device(device_types: list[str]):
    """
    Esconde conteúdo em dispositivos específicos.
    
    Args:
        device_types: Lista de tipos de dispositivo ("mobile", "tablet", "desktop")
    """
    viewport_state = me.state(ViewportState)
    
    if viewport_state.device_type not in device_types:
        me.slot()