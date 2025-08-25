# 📱 Melhores Práticas de Responsividade no Mesop

## ✅ Abordagem Correta (Seguindo Mesop)

### 1. **Use Funções CSS Nativas**

```python
# ✅ CORRETO - Usando min(), max(), clamp()
me.Style(
    width="min(600px, 90%)",  # Largura responsiva
    font_size="clamp(16px, 2vw, 24px)",  # Fonte responsiva
    padding="calc(1rem + 1vw)",  # Padding dinâmico
)
```

### 2. **Evite JavaScript Customizado**

```python
# ❌ INCORRETO - JavaScript customizado
me.html("<script>window.innerWidth...</script>")

# ✅ CORRETO - Use CSS puro
me.Style(
    width="100vw",
    max_width="1200px",
)
```

### 3. **Use Estilos Inline**

```python
# ❌ INCORRETO - Classes CSS externas
style=me.Style(class_name="mobile-only")

# ✅ CORRETO - Estilos inline
style=me.Style(
    display="block",
    media_query="@media (max-width: 768px) { display: none; }"
)
```

## 📐 Técnicas Responsivas no Mesop

### 1. **Containers Fluidos**

```python
def responsive_container():
    return me.Style(
        width="min(1200px, 100%)",
        margin=me.Margin.symmetric(horizontal="auto"),
        padding=me.Padding.symmetric(
            horizontal="clamp(16px, 4vw, 32px)"
        ),
    )
```

### 2. **Grid Responsivo**

```python
@me.component
def responsive_grid():
    with me.box(
        style=me.Style(
            display="grid",
            grid_template_columns="repeat(auto-fit, minmax(300px, 1fr))",
            gap="clamp(16px, 2vw, 24px)",
        )
    ):
        me.slot()
```

### 3. **Tipografia Responsiva**

```python
# Tamanhos de fonte responsivos
FONT_SIZES = {
    "small": "clamp(14px, 1.5vw, 16px)",
    "medium": "clamp(16px, 2vw, 20px)",
    "large": "clamp(20px, 3vw, 28px)",
    "xlarge": "clamp(24px, 4vw, 36px)",
}
```

### 4. **Imagens Responsivas**

```python
me.image(
    src="image.png",
    style=me.Style(
        width="100%",
        max_width="min(600px, 100%)",
        height="auto",
        object_fit="contain",
    )
)
```

## 🎯 Padrões Recomendados

### 1. **Layout com Sidebar Responsiva**

```python
def responsive_layout_with_sidebar():
    # Desktop: sidebar fixa
    # Mobile: drawer ou oculta
    sidebar_width = "max(200px, 20vw)"  # Responsivo
    
    return me.Style(
        display="grid",
        grid_template_columns=f"{sidebar_width} 1fr",
        gap=0,
        media_query="@media (max-width: 768px) { grid-template-columns: 1fr; }"
    )
```

### 2. **Chat Bubbles Responsivos**

```python
def chat_bubble_style(is_user: bool):
    return me.Style(
        max_width="min(600px, 80%)",  # 80% em mobile, máx 600px
        margin_left="auto" if is_user else 0,
        margin_right=0 if is_user else "auto",
        padding="clamp(12px, 2vw, 20px)",
        font_size="clamp(14px, 1.5vw, 16px)",
    )
```

### 3. **Input Responsivo**

```python
def responsive_input_style():
    return me.Style(
        width="100%",
        max_width="min(800px, 100%)",
        padding="clamp(12px, 2vw, 16px)",
        font_size="max(16px, 1rem)",  # Previne zoom no iOS
        border_radius="clamp(20px, 3vw, 24px)",
    )
```

## ⚡ Performance

### 1. **Evite Re-renders Desnecessários**

```python
# Use state apenas quando necessário
# Prefira CSS para animações e transições
style=me.Style(
    transition="all 0.3s ease",
    transform="translateX(0)",
)
```

### 2. **Otimize Imagens**

```python
# Use lazy loading e tamanhos apropriados
me.image(
    src="image.png",
    loading="lazy",
    style=me.Style(
        width="100%",
        max_width="400px",
    )
)
```

## 🚫 O Que Evitar

1. **Media Queries Complexas em Python**
   - Use CSS functions (min, max, clamp) em vez disso

2. **Detecção de Viewport com JavaScript**
   - Use unidades CSS responsivas (vw, vh, %)

3. **Classes CSS Externas**
   - Use estilos inline do Mesop

4. **Breakpoints Rígidos**
   - Prefira design fluido com CSS functions

## 📱 Exemplo Completo

```python
import mesop as me

@me.page(path="/responsive-example")
def responsive_page():
    with me.box(
        style=me.Style(
            min_height="100vh",
            display="flex",
            flex_direction="column",
            font_family="system-ui, -apple-system, sans-serif",
        )
    ):
        # Header responsivo
        with me.box(
            style=me.Style(
                padding="clamp(16px, 3vw, 24px)",
                background="white",
                border_bottom="1px solid #e0e0e0",
            )
        ):
            me.text(
                "App Responsivo",
                style=me.Style(
                    font_size="clamp(20px, 4vw, 32px)",
                    font_weight="bold",
                )
            )
        
        # Conteúdo principal
        with me.box(
            style=me.Style(
                flex_grow=1,
                width="min(1200px, 100%)",
                margin=me.Margin.symmetric(horizontal="auto"),
                padding="clamp(16px, 4vw, 32px)",
            )
        ):
            # Grid responsivo
            with me.box(
                style=me.Style(
                    display="grid",
                    grid_template_columns="repeat(auto-fit, minmax(250px, 1fr))",
                    gap="clamp(16px, 2vw, 24px)",
                )
            ):
                for i in range(4):
                    card_component(f"Card {i + 1}")


def card_component(title: str):
    with me.box(
        style=me.Style(
            background="white",
            padding="clamp(16px, 3vw, 24px)",
            border_radius="8px",
            box_shadow="0 2px 8px rgba(0,0,0,0.1)",
        )
    ):
        me.text(
            title,
            style=me.Style(
                font_size="clamp(16px, 2vw, 20px)",
                font_weight="600",
            )
        )
```

## 🔗 Recursos

- [Mesop Style Documentation](https://google.github.io/mesop/api/style/)
- [CSS Functions MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Functions)
- [Fluid Typography](https://css-tricks.com/snippets/css/fluid-typography/)
- [CSS Grid Auto-Fit](https://css-tricks.com/auto-sizing-columns-css-grid-auto-fill-vs-auto-fit/)

## 📝 Resumo

Para responsividade no Mesop:
1. **Use CSS functions**: min(), max(), clamp(), calc()
2. **Evite JavaScript**: Prefira soluções CSS puras
3. **Design fluido**: Use unidades relativas e grids flexíveis
4. **Estilos inline**: Mantenha tudo no me.Style()
5. **Performance**: Minimize re-renders e use transições CSS