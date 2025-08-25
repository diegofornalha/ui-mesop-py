#!/usr/bin/env python3
"""Teste simples para verificar se há erros com atributos"""

import mesop as me

@me.page(path="/simple", title="Teste Simples")
def simple_test():
    """Teste simples para verificar se há erros"""
    
    with me.box(
        style=me.Style(
            padding=me.Padding.all(24),
            margin=me.Margin.all(0),
        )
    ):
        me.text("Teste Simples - Sem Erros")
        
        # Teste com top
        with me.box(
            style=me.Style(
                background="#f0f0f0",
                padding=me.Padding(top=16, left=16, right=16, bottom=16),
                margin=me.Margin(top=8, bottom=8),
            )
        ):
            me.text("Teste com atributo 'top' - OK!")

if __name__ == "__main__":
    print("Teste simples criado. Execute com: uv run python test_simple.py")
