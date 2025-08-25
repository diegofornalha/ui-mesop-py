#!/usr/bin/env python3
"""
Script para testar conexão direta com Gemini API
"""

import os
import google.generativeai as genai

# Configurar API Key
API_KEY = "AIzaSyDeyRoAZwxeA7_XcXwz4aTKurPBAWsnYY0"
genai.configure(api_key=API_KEY)

print("🔧 Testando conexão direta com Gemini API...")
print("-" * 50)

try:
    # Listar modelos disponíveis
    print("\n📋 Modelos disponíveis:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
    
    # Criar modelo
    print("\n🤖 Criando modelo Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Enviar mensagem de teste
    print("\n💬 Enviando mensagem de teste...")
    response = model.generate_content("Responda apenas: 'Sistema funcionando!'")
    
    print("\n✅ Resposta do Gemini:")
    print(f"   {response.text}")
    
    print("\n🎉 SUCESSO! Gemini API está funcionando!")
    
except Exception as e:
    print(f"\n❌ Erro ao conectar com Gemini: {str(e)}")
    print("\n💡 Possíveis causas:")
    print("   1. API Key inválida ou expirada")
    print("   2. Quota excedida")
    print("   3. Problema de conectividade")
    print("   4. Modelo não disponível")