"""Utilitários de responsividade seguindo as práticas do Mesop"""

import mesop as me
from typing import Optional, Dict, Any


def create_responsive_style(
    base_style: Dict[str, Any],
    width_breakpoint: str = "min(680px, 100%)",
    max_width: Optional[int] = None,
) -> me.Style:
    """
    Cria um estilo responsivo seguindo o padrão do Mesop.
    
    Args:
        base_style: Dicionário com estilos base
        width_breakpoint: String com breakpoint (ex: "min(680px, 100%)")
        max_width: Largura máxima em pixels
    
    Returns:
        me.Style configurado de forma responsiva
    """
    style_dict = base_style.copy()
    
    # Aplicar largura responsiva
    if width_breakpoint:
        style_dict["width"] = width_breakpoint
    
    # Aplicar largura máxima se especificada
    if max_width:
        style_dict["max_width"] = f"{max_width}px"
    
    return me.Style(**style_dict)


def responsive_container(
    horizontal_margin: int = 0,
    vertical_margin: int = 36,
    max_width: str = "min(1200px, 100%)",
    padding: Optional[me.Padding] = None,
) -> me.Style:
    """
    Cria um container responsivo seguindo o padrão DuoChat.
    
    Args:
        horizontal_margin: Margem horizontal em pixels
        vertical_margin: Margem vertical em pixels
        max_width: Largura máxima responsiva
        padding: Padding opcional
    
    Returns:
        me.Style para container responsivo
    """
    style_dict = {
        "width": max_width,
        "margin": me.Margin.symmetric(
            horizontal=horizontal_margin,
            vertical=vertical_margin,
        ) if horizontal_margin != 0 else me.Margin(top=vertical_margin, bottom=vertical_margin, left=0, right=0),
        "display": "flex",
        "flex_direction": "column",
    }
    
    if padding:
        style_dict["padding"] = padding
    
    return me.Style(**style_dict)


def responsive_text_size(base_size: int = 16) -> Dict[str, int]:
    """
    Retorna tamanhos de texto responsivos usando calc() CSS.
    
    Args:
        base_size: Tamanho base da fonte
    
    Returns:
        Dicionário com tamanhos responsivos
    """
    return {
        "small": int(base_size * 0.875),  # 14px para base 16
        "medium": base_size,  # 16px
        "large": int(base_size * 1.125),  # 18px para base 16
        "xlarge": int(base_size * 1.25),  # 20px para base 16
        "xxlarge": int(base_size * 1.5),  # 24px para base 16
    }


def responsive_padding(base: int = 16) -> Dict[str, me.Padding]:
    """
    Retorna valores de padding responsivos.
    
    Args:
        base: Valor base de padding
    
    Returns:
        Dicionário com padding para diferentes tamanhos
    """
    return {
        "small": me.Padding.all(int(base * 0.5)),  # 8px
        "medium": me.Padding.all(base),  # 16px
        "large": me.Padding.all(int(base * 1.5)),  # 24px
    }


def responsive_gap(base: int = 16) -> Dict[str, int]:
    """
    Retorna valores de gap responsivos para flexbox/grid.
    
    Args:
        base: Valor base de gap
    
    Returns:
        Dicionário com gaps para diferentes tamanhos
    """
    return {
        "small": int(base * 0.5),  # 8px
        "medium": base,  # 16px
        "large": int(base * 1.5),  # 24px
    }


# Estilos base seguindo o padrão Mesop
RESPONSIVE_ROOT_STYLE = me.Style(
    background="#ffffff",
    min_height="100vh",
    font_family="Inter, system-ui, -apple-system, sans-serif",
    display="flex",
    flex_direction="column",
)

RESPONSIVE_HEADER_STYLE = me.Style(
    padding=me.Padding.all(16),
    background="white",
    border_bottom="1px solid #e0e0e0",
    position="sticky",
    top=0,
    z_index=100,
)

RESPONSIVE_MAIN_CONTENT_STYLE = me.Style(
    flex_grow=1,
    width="min(1200px, 100%)",
    margin="0 auto",
    padding=me.Padding.symmetric(horizontal=16, vertical=24),
)

RESPONSIVE_CHAT_INPUT_STYLE = me.Style(
    position="sticky",
    bottom=0,
    background="white",
    border_top="1px solid #e0e0e0",
    padding=me.Padding.all(16),
    width="100%",
)

RESPONSIVE_CHAT_BUBBLE_CONTAINER = me.Style(
    display="flex",
    width="100%",
    margin=me.Margin.symmetric(vertical=8),
)

RESPONSIVE_INPUT_WRAPPER_STYLE = me.Style(
    border_radius=16,
    padding=me.Padding.all(8),
    background="white",
    border="1px solid #e0e0e0",
    display="flex",
    width="min(800px, 100%)",
    margin="0 auto",
    align_items="center",
    gap=8,
)