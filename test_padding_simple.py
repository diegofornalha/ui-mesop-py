"""Teste simples para identificar o erro de padding"""

import mesop as me


@me.page(path="/test-padding")
def test_page():
    """Teste direto do problema"""
    
    # Teste 1: Padding com número direto
    try:
        with me.box(
            style=me.Style(
                padding=me.Padding(top=16, left=16, right=16, bottom=0)
            )
        ):
            me.text("✅ Teste 1: Padding com números - OK")
    except Exception as e:
        me.text(f"❌ Erro teste 1: {e}")
    
    # Teste 2: Padding.all()
    try:
        with me.box(style=me.Style(padding=me.Padding.all(16))):
            me.text("✅ Teste 2: Padding.all() - OK")
    except Exception as e:
        me.text(f"❌ Erro teste 2: {e}")
    
    # Teste 3: String como valor (deve dar erro)
    try:
        # Este deve dar erro
        with me.box(
            style=me.Style(
                padding=me.Padding(top="16px", left=16, right=16, bottom=0)
            )
        ):
            me.text("Teste 3: String no padding")
    except Exception as e:
        me.text(f"✅ Erro esperado no teste 3: {e}")
    
    # Teste 4: Importar e usar ResponsiveConfig
    try:
        from styles.responsive import get_responsive_config
        config = get_responsive_config()
        
        me.text(f"\nDados do config:")
        me.text(f"- padding: {config.padding} (tipo: {type(config.padding).__name__})")
        
        # Tentar usar o padding
        with me.box(
            style=me.Style(
                padding=me.Padding(
                    top=config.padding,
                    left=config.padding,
                    right=config.padding,
                    bottom=0
                )
            )
        ):
            me.text("✅ Teste 4: Config padding - OK")
    except Exception as e:
        me.text(f"❌ Erro teste 4: {e}")
        import traceback
        me.text(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    # Teste direto dos valores
    from styles.responsive import PADDING_DESKTOP, get_responsive_config
    
    print(f"PADDING_DESKTOP: {PADDING_DESKTOP} (tipo: {type(PADDING_DESKTOP)})")
    
    config = get_responsive_config()
    print(f"config.padding: {config.padding} (tipo: {type(config.padding)})")
    
    # Teste do Padding
    try:
        p = me.Padding(top=config.padding, left=16, right=16, bottom=0)
        print(f"Padding criado com sucesso: {p}")
    except Exception as e:
        print(f"ERRO ao criar Padding: {e}")
        import traceback
        traceback.print_exc()