# 📋 Argumentos Válidos para me.Style() no Mesop

## ✅ Argumentos Suportados

### Layout
- `display` - flex, grid, block, inline, none
- `position` - relative, absolute, fixed, sticky
- `flex_direction` - row, column, row-reverse, column-reverse
- `flex_grow` - número
- `flex_shrink` - número
- `flex_wrap` - wrap, nowrap
- `align_items` - center, flex-start, flex-end, stretch
- `justify_content` - center, flex-start, flex-end, space-between, space-around
- `align_content` - similar a align_items
- `gap` - espaçamento entre items (número ou string)

### Dimensões
- `width` - largura (string com unidade: px, %, vw, min(), max())
- `height` - altura (string com unidade)
- `min_width` - largura mínima
- `max_width` - largura máxima
- `min_height` - altura mínima
- `max_height` - altura máxima

### Espaçamento
- `padding` - me.Padding object ou string
- `margin` - me.Margin object ou string

### Bordas
- `border` - string completa (ex: "1px solid #ccc")
- `border_radius` - número ou string
- `outline` - string completa

### Cores e Fundos
- `background` - cor ou gradiente
- `color` - cor do texto
- `opacity` - 0 a 1

### Texto
- `font_family` - família da fonte
- `font_size` - tamanho (número ou string)
- `font_weight` - normal, bold, ou número (100-900)
- `font_style` - normal, italic
- `text_align` - left, center, right, justify
- `text_decoration` - none, underline, line-through
- `text_transform` - none, uppercase, lowercase, capitalize
- `line_height` - altura da linha
- `letter_spacing` - espaçamento entre letras
- `white_space` - normal, nowrap, pre, pre-wrap

### Overflow
- `overflow` - visible, hidden, scroll, auto
- `overflow_x` - horizontal overflow
- `overflow_y` - vertical overflow
- `text_overflow` - clip, ellipsis

### Grid (quando display="grid")
- `grid_template_columns` - template de colunas
- `grid_template_rows` - template de linhas
- `grid_column` - posição da coluna
- `grid_row` - posição da linha
- `grid_gap` - espaçamento do grid

### Outros
- `cursor` - pointer, default, text, etc.
- `z_index` - número para empilhamento
- `transform` - transformações CSS
- `transition` - transições CSS
- `box_shadow` - sombra da caixa
- `filter` - filtros CSS
- `visibility` - visible, hidden
- `object_fit` - contain, cover, fill (para imagens)

## ❌ Argumentos NÃO Suportados

Estes argumentos causarão erro:
- `border_right`, `border_left`, `border_top`, `border_bottom` (use `border` completo)
- `hover_background`, `hover_color` (efeitos hover)
- `media_query` (media queries)
- `class_name` (classes CSS)
- `size` (use `font_size` ou `width`/`height`)
- `word_wrap`, `overflow_wrap` (quebra de palavras)

## 💡 Dicas

### Para bordas específicas:
```python
# Em vez de border_right
border="0 1px 0 0 solid #ccc"  # top right bottom left
```

### Para responsividade:
```python
# Use funções CSS
width="min(600px, 90%)"
font_size="clamp(16px, 2vw, 24px)"
padding="calc(1rem + 1vw)"
```

### Para espaçamento:
```python
# Use objetos Mesop
padding=me.Padding.all(16)
padding=me.Padding.symmetric(horizontal=20, vertical=10)
margin=me.Margin.all(8)
```

## 📚 Referência

Consulte a [documentação oficial do Mesop](https://google.github.io/mesop/api/style/) para mais detalhes.