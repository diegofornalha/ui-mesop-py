"""Debug para encontrar o erro 'str' object has no attribute 'top'"""

import mesop as me
from styles.responsive import get_responsive_config
from components.mesop_responsive_utils import responsive_padding


@me.page(path="/debug")
def debug_page():
    """Página para debugar o erro"""
    
    # Teste 1: get_responsive_config
    config = get_responsive_config()
    with me.box(style=me.Style(padding=me.Padding.all(20))):
        me.text(f"Config padding value: {config.padding}")
        me.text(f"Config padding type: {type(config.padding)}")
    
    # Teste 2: responsive_padding
    paddings = responsive_padding()
    with me.box(style=me.Style(padding=me.Padding.all(20))):
        me.text(f"Responsive padding keys: {list(paddings.keys())}")
        me.text(f"Medium padding: {paddings['medium']}")
        me.text(f"Medium padding type: {type(paddings['medium'])}")
    
    # Teste 3: Usar o padding diretamente
    try:
        with me.box(
            style=me.Style(
                padding=me.Padding(
                    top=config.padding,
                    left=config.padding,
                    right=config.padding,
                    bottom=0,
                )
            )
        ):
            me.text("Teste com config.padding direto - OK")
    except Exception as e:
        me.text(f"ERRO no teste 3: {str(e)}")
    
    # Teste 4: Margin auto
    try:
        test_margin = me.Margin.symmetric(horizontal="auto", vertical=36)
        with me.box(style=me.Style(margin=test_margin)):
            me.text(f"Margin auto test - OK: {test_margin}")
    except Exception as e:
        me.text(f"ERRO no teste 4: {str(e)}")
    
    # Teste 5: Problemas potenciais
    me.text("\nVerificando possíveis problemas:")
    
    # Se config.padding for string
    if isinstance(config.padding, str):
        me.text(f"⚠️ config.padding é string: '{config.padding}'")
    else:
        me.text(f"✅ config.padding é número: {config.padding}")


if __name__ == "__main__":
    print("Execute: python debug_style_error.py")
    print("Ou adicione a rota ao main.py")