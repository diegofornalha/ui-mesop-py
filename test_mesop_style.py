"""Teste simples para verificar me.Style"""

import mesop as me


@me.page(path="/test-style")
def test_style_page():
    """Página de teste para verificar estilos"""
    
    # Teste 1: Padding com números
    with me.box(
        style=me.Style(
            padding=me.Padding.all(16),
            background="#f0f0f0",
            margin=me.Margin.all(8),
        )
    ):
        me.text("Teste 1: Padding numérico OK")
    
    # Teste 2: Margin como string (válido)
    with me.box(
        style=me.Style(
            padding=me.Padding.all(16),
            background="#e0e0e0",
            margin="8px auto",  # String é válida
        )
    ):
        me.text("Teste 2: Margin string OK")
    
    # Teste 3: Padding symmetric
    with me.box(
        style=me.Style(
            padding=me.Padding.symmetric(horizontal=20, vertical=10),
            background="#d0d0d0",
            margin=me.Margin.symmetric(horizontal=0, vertical=8),
        )
    ):
        me.text("Teste 3: Padding symmetric OK")
    
    # Teste 4: Estilos responsivos
    with me.box(
        style=me.Style(
            width="min(600px, 90%)",
            padding=me.Padding.all(16),
            background="#c0c0c0",
            font_size="clamp(14px, 2vw, 20px)",
        )
    ):
        me.text("Teste 4: Estilos responsivos OK")


if __name__ == "__main__":
    print("Execute este arquivo com: python test_mesop_style.py")
    print("Ou importe no main_responsive_fixed.py")