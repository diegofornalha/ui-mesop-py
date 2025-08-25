"""Script de teste para demonstrar a responsividade do Chat UI"""

import mesop as me
from components.viewport_detector import (
    viewport_detector,
    responsive_container,
    responsive_text,
    responsive_grid,
    show_on_device,
    hide_on_device,
)
from styles.responsive import get_responsive_config

@me.page(
    path="/test",
    title="Teste de Responsividade",
    stylesheets=["/static/responsive.css"],
)
def test_responsive_page():
    """Página de teste para demonstrar componentes responsivos"""
    
    # Detector de viewport
    viewport_detector()
    
    with me.box(
        style=me.Style(
            padding=me.Padding.all(24),
            max_width=1200,
            margin=me.Margin.all(0),
        )
    ):
        # Título responsivo
        responsive_text(
            "Teste de Responsividade",
            mobile_size=24,
            tablet_size=28,
            desktop_size=32,
            font_weight="bold",
            margin_bottom=24,
        )
        
        # Informações do dispositivo
        render_device_info()
        
        # Demonstração de visibilidade condicional
        render_visibility_demo()
        
        # Grid responsivo
        render_grid_demo()
        
        # Container responsivo
        render_container_demo()


def render_device_info():
    """Mostra informações sobre o dispositivo atual"""
    config = get_responsive_config()
    
    with me.box(
        style=me.Style(
            background="#f5f5f5",
            padding=me.Padding.all(16),
            border_radius=8,
            margin_bottom=24,
        )
    ):
        me.text("Informações do Dispositivo", style=me.Style(font_weight="bold", margin=me.Margin(bottom=8)))
        
        # Mobile
        with show_on_device(["mobile"]):
            me.text("📱 Você está em um dispositivo MOBILE")
            me.text(f"Padding: {config.padding}px")
            me.text(f"Font size: {config.font_size}px")
        
        # Tablet
        with show_on_device(["tablet"]):
            me.text("📱 Você está em um TABLET")
            me.text(f"Padding: {config.padding}px")
            me.text(f"Font size: {config.font_size}px")
        
        # Desktop
        with show_on_device(["desktop"]):
            me.text("💻 Você está em um DESKTOP")
            me.text(f"Padding: {config.padding}px")
            me.text(f"Font size: {config.font_size}px")


def render_visibility_demo():
    """Demonstra componentes com visibilidade condicional"""
    with me.box(style=me.Style(margin=me.Margin(bottom=24))):
        me.text(
            "Visibilidade Condicional",
            style=me.Style(font_size=20, font_weight="bold", margin=me.Margin(bottom=16))
        )
        
        # Visível apenas em mobile
        with show_on_device(["mobile"]):
            with me.box(
                style=me.Style(
                    background="#d8407f",
                    color="white",
                    padding=me.Padding.all(12),
                    border_radius=8,
                    margin_bottom=8,
                )
            ):
                me.text("✅ Visível APENAS em Mobile")
        
        # Visível em tablet e desktop
        with show_on_device(["tablet", "desktop"]):
            with me.box(
                style=me.Style(
                    background="#4285f4",
                    color="white",
                    padding=me.Padding.all(12),
                    border_radius=8,
                    margin_bottom=8,
                )
            ):
                me.text("✅ Visível em Tablet e Desktop")
        
        # Escondido em mobile
        with hide_on_device(["mobile"]):
            with me.box(
                style=me.Style(
                    background="#34a853",
                    color="white",
                    padding=me.Padding.all(12),
                    border_radius=8,
                    margin_bottom=8,
                )
            ):
                me.text("❌ Escondido em Mobile")


def render_grid_demo():
    """Demonstra grid responsivo"""
    me.text(
        "Grid Responsivo",
        style=me.Style(font_size=20, font_weight="bold", margin=me.Margin(bottom=16))
    )
    
    with responsive_grid(
        mobile_columns=1,
        tablet_columns=2,
        desktop_columns=3,
        gap=16,
    ):
        # Criar 6 cards de exemplo
        for i in range(6):
            with me.box(
                style=me.Style(
                    background="#f0f0f0",
                    padding=me.Padding.all(16),
                    border_radius=8,
                    text_align="center",
                    min_height=100,
                    display="flex",
                    align_items="center",
                    justify_content="center",
                )
            ):
                me.text(f"Card {i + 1}")


def render_container_demo():
    """Demonstra container responsivo"""
    me.text(
        "Container Responsivo",
        style=me.Style(font_size=20, font_weight="bold", margin=me.Margin(bottom=16, top=24))
    )
    
    with responsive_container(
        mobile_style=me.Style(
            background="#ffe0ec",
            padding=me.Padding.all(12),
            border_radius=8,
        ),
        tablet_style=me.Style(
            background="#e3f2fd",
            padding=me.Padding.all(16),
            border_radius=12,
        ),
        desktop_style=me.Style(
            background="#f3e5f5",
            padding=me.Padding.all(24),
            border_radius=16,
        ),
    ):
        me.text(
            "Este container muda de cor e padding baseado no dispositivo!",
            style=me.Style(text_align="center")
        )
        
        with show_on_device(["mobile"]):
            me.text("Rosa claro + padding pequeno", style=me.Style(text_align="center", margin_top=8))
        
        with show_on_device(["tablet"]):
            me.text("Azul claro + padding médio", style=me.Style(text_align="center", margin_top=8))
        
        with show_on_device(["desktop"]):
            me.text("Roxo claro + padding grande", style=me.Style(text_align="center", margin_top=8))


if __name__ == "__main__":
    # Este arquivo pode ser importado pelo main_responsive.py
    # ou executado diretamente para testes
    print("Para testar, adicione a rota ao main_responsive.py ou acesse /test")