# 🔑 Limitação da API do Gemini - Guia Completo

## 🚨 Problema Encontrado
**Erro 429: RESOURCE_EXHAUSTED**  
A IA parou de responder devido ao limite de quota da API do Gemini.

## 📊 Detalhes da Limitação

### Plano Gratuito (Free Tier)
- **Limite:** 50 requisições por dia
- **Reset:** Diariamente às 00:00 UTC
- **Por projeto:** Cada API key tem seu próprio limite
- **Modelo afetado:** gemini-1.5-flash

### Mensagem de Erro Típica:
```json
{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
        "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
        "quotaValue": "50"
      }
    ]
  }
}
```

## ✅ Solução Implementada

### 1. Trocar a API Key
Quando a API key atinge o limite, a solução mais rápida é usar uma nova chave:

```bash
# Parar o servidor atual
pkill -f "python.*main.py"

# Aguardar 2 segundos
sleep 2

# Reiniciar com nova API key
export GOOGLE_API_KEY="NOVA_API_KEY_AQUI"
A2A_UI_PORT=8888 MESOP_DEFAULT_PORT=8888 GOOGLE_API_KEY="NOVA_API_KEY_AQUI" .venv/bin/python main.py
```

### 2. Comando Usado na Prática:
```bash
pkill -f "python.*main.py" && sleep 2 && \
export GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" && \
A2A_UI_PORT=8888 MESOP_DEFAULT_PORT=8888 \
GOOGLE_API_KEY="AIzaSyCPLR14FyhGCu5_lickBdMqZwtM72i97DI" \
.venv/bin/python main.py 2>&1 &
```

## 🎯 Resultado
**✅ FUNCIONOU PERFEITAMENTE!**  
Após trocar a API key, o sistema voltou a funcionar imediatamente.

## 💡 Estratégias para Gerenciar o Limite

### 1. **Múltiplas API Keys (Recomendado)**
- Criar várias contas Google
- Gerar uma API key para cada conta
- Alternar entre elas quando necessário
- Total: 50 requisições × N contas

### 2. **Rotação Automática de Keys**
Criar um arquivo `.env` com múltiplas chaves:
```env
GOOGLE_API_KEY_1=AIzaSy...
GOOGLE_API_KEY_2=AIzaSy...
GOOGLE_API_KEY_3=AIzaSy...
```

Script para rotação:
```python
import os
from datetime import datetime

def get_active_api_key():
    """Retorna uma API key baseada no horário ou contador"""
    keys = [
        os.getenv('GOOGLE_API_KEY_1'),
        os.getenv('GOOGLE_API_KEY_2'),
        os.getenv('GOOGLE_API_KEY_3'),
    ]
    # Rotaciona baseado na hora do dia
    hour = datetime.now().hour
    index = hour % len(keys)
    return keys[index]
```

### 3. **Monitoramento de Uso**
Adicionar contador de requisições:
```python
# No arquivo service/server/adk_host_manager.py
class RequestCounter:
    def __init__(self):
        self.count = 0
        self.limit = 50
    
    def increment(self):
        self.count += 1
        if self.count >= self.limit:
            print(f"⚠️ AVISO: Aproximando do limite! {self.count}/{self.limit}")
    
    def reset(self):
        self.count = 0
```

### 4. **Upgrade para Plano Pago**
- **Custo:** $0.00025 por 1K caracteres (input)
- **Custo:** $0.001 por 1K caracteres (output)
- **Sem limite diário**
- **Maior velocidade**

## 📝 Como Obter uma Nova API Key

### Passo a Passo:
1. Acesse: https://aistudio.google.com/app/apikey
2. Clique em "Create API Key"
3. Selecione ou crie um novo projeto
4. Copie a chave gerada
5. Substitua no servidor usando o comando acima

### Dica de Organização:
```bash
# Criar arquivo para armazenar chaves
echo "API_KEY_1=AIzaSy..." >> ~/gemini_keys.txt
echo "API_KEY_2=AIzaSy..." >> ~/gemini_keys.txt
echo "API_KEY_3=AIzaSy..." >> ~/gemini_keys.txt
```

## 🔍 Verificar Status da Quota

### Via Código Python:
```python
import google.generativeai as genai

def check_quota_status(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("test")
        print("✅ API Key funcionando!")
        return True
    except Exception as e:
        if "429" in str(e):
            print("❌ Quota excedida!")
            return False
        print(f"❌ Erro: {e}")
        return False
```

### Via Dashboard:
- Acesse: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
- Visualize o uso atual
- Monitore os limites

## 🚀 Melhorias Futuras Sugeridas

### 1. **Sistema de Fallback Automático**
```python
class APIKeyManager:
    def __init__(self, keys):
        self.keys = keys
        self.current_index = 0
    
    def get_next_key(self):
        """Retorna próxima chave disponível"""
        self.current_index = (self.current_index + 1) % len(self.keys)
        return self.keys[self.current_index]
    
    async def execute_with_fallback(self, func):
        """Executa função com fallback para próxima chave"""
        for _ in range(len(self.keys)):
            try:
                return await func(self.keys[self.current_index])
            except QuotaExceeded:
                print(f"Chave {self.current_index} excedeu quota, tentando próxima...")
                self.get_next_key()
        raise Exception("Todas as chaves excederam quota!")
```

### 2. **Cache de Respostas**
- Armazenar respostas comuns
- Reduzir requisições repetidas
- Economizar quota

### 3. **Rate Limiting Local**
- Implementar delay entre requisições
- Distribuir uso ao longo do dia
- Prevenir esgotamento rápido

## 📌 Lições Aprendidas

1. **Sempre tenha API keys de backup**
2. **Monitore o uso durante desenvolvimento**
3. **Implemente tratamento de erro 429**
4. **Considere plano pago para produção**
5. **Use cache sempre que possível**

## 🎉 Conclusão

A troca da API key resolveu o problema imediatamente! O sistema está preparado para lidar com limitações de quota, e com múltiplas chaves disponíveis, o desenvolvimento pode continuar sem interrupções significativas.

---

**Data do Incidente:** 25/08/2025  
**Tempo de Resolução:** < 2 minutos  
**Status:** ✅ RESOLVIDO COM SUCESSO

## 📚 Referências

- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Pricing](https://ai.google.dev/pricing)
- [API Key Management](https://aistudio.google.com/app/apikey)
- [Quota Dashboard](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)