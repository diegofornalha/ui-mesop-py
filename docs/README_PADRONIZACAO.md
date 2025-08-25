# 📋 Projeto de Padronização de Nomenclatura
## UI Mesop com Google ADK e A2A Protocol

---

## 🎯 **OBJETIVO**

Este projeto visa padronizar toda a nomenclatura de campos relacionados ao contexto no projeto UI Mesop para usar **`contextId` (camelCase)** como padrão único, eliminando inconsistências e garantindo compatibilidade total com A2A Protocol e Google ADK.

---

## 📚 **DOCUMENTAÇÃO DISPONÍVEL**

### **1. PRD - Product Requirements Document**
- **Arquivo:** `docs/PRD_PADRONIZACAO_NOMENCLATURA.md`
- **Conteúdo:** Requisitos funcionais, não funcionais, cronograma e critérios de sucesso
- **Uso:** Documento de referência para stakeholders e equipe

### **2. Plano de Implementação**
- **Arquivo:** `docs/PLANO_IMPLEMENTACAO_PADRONIZACAO.md`
- **Conteúdo:** Passos detalhados de implementação, exemplos de código e testes
- **Uso:** Guia prático para desenvolvedores implementarem as mudanças

### **3. Script de Validação**
- **Arquivo:** `scripts/validate_naming_patterns.py`
- **Conteúdo:** Script Python para validar padrões de nomenclatura no projeto
- **Uso:** Ferramenta para verificar conformidade e sugerir migrações

---

## 🚀 **COMO USAR**

### **Passo 1: Entender o Problema**
Leia o **PRD** para entender:
- Por que a padronização é necessária
- Quais são os objetivos do projeto
- Qual é o cronograma planejado

### **Passo 2: Planejar a Implementação**
Use o **Plano de Implementação** para:
- Entender as fases de desenvolvimento
- Ver exemplos de código antes/depois
- Planejar testes para cada fase

### **Passo 3: Validar o Estado Atual**
Execute o script de validação:
```bash
# Executar validação
python scripts/validate_naming_patterns.py

# Ou executar diretamente
./scripts/validate_naming_patterns.py
```

### **Passo 4: Implementar as Mudanças**
Siga o plano de implementação fase por fase:
1. **Fase 1:** Modelos Pydantic
2. **Fase 2:** Classes de Estado
3. **Fase 3:** ADK Host Manager
4. **Fase 4:** Limpeza e Otimização

---

## 🔍 **VALIDAÇÃO AUTOMÁTICA**

### **O que o Script Valida**
- ✅ **`contextId`** - Padrão correto (camelCase)
- ❌ **`context_id`** - snake_case (precisa migrar)
- ❌ **`contextid`** - lowercase (precisa migrar)
- ❌ **`context_Id`** - mixed (precisa migrar)
- ❌ **`ContextId`** - PascalCase (precisa migrar)
- ❌ **`contextID`** - mixed (precisa migrar)

### **Exemplo de Saída**
```
🔍 VALIDADOR DE PADRÕES DE NOMENCLATURA
============================================================
📁 Diretório raiz: /Users/2a/Desktop/ui-mesop-py

📂 Verificando diretório: service
📂 Verificando diretório: state
📂 Verificando diretório: components

📊 ESTATÍSTICAS
   Total de arquivos Python: 25
   Arquivos com violações: 8
   Arquivos sem violações: 17

📊 RELATÓRIO DE VIOLAÇÕES
==================================================

❌ CONTEXT_ID (5 arquivos):
   Total de ocorrências: 35
   📁 service/types.py: 12 ocorrências
   📁 state/state.py: 8 ocorrências
   📁 state/host_agent_service.py: 15 ocorrências

❌ CONTEXTID (3 arquivos):
   Total de ocorrências: 29
   📁 service/server/adk_host_manager.py: 20 ocorrências
   📁 components/async_poller.py: 9 ocorrências
```

---

## 🛠️ **FERRAMENTAS DE MIGRAÇÃO**

### **Comandos Sed Sugeridos**
O script sugere comandos para migração automática:
```bash
# Migrar service/types.py
sed -i 's/context_id/contextId/g' service/types.py
sed -i 's/contextid/contextId/g' service/types.py
sed -i 's/context_Id/contextId/g' service/types.py

# Migrar state/state.py
sed -i 's/context_id/contextId/g' state/state.py
sed -i 's/contextid/contextId/g' state/state.py
```

### **Verificação de Mudanças**
```bash
# Ver mudanças antes de aplicar
git diff

# Aplicar mudanças
git add .
git commit -m "feat: padronizar nomenclatura para contextId"
```

---

## 🧪 **TESTES RECOMENDADOS**

### **Testes por Fase**
1. **Fase 1:** Validação de modelos Pydantic
2. **Fase 2:** Testes de estado e conversão
3. **Fase 3:** Testes de integração ADK
4. **Fase 4:** Testes finais e performance

### **Comandos de Teste**
```bash
# Executar todos os testes
python -m pytest tests/

# Executar testes específicos
python -m pytest tests/test_adk_integration.py
python -m pytest tests/test_message_validation.py

# Verificar cobertura
python -m pytest --cov=service --cov=state tests/
```

---

## 📊 **MÉTRICAS DE SUCESSO**

### **Quantitativas**
- [ ] **0 variações** de nomenclatura em uso
- [ ] **100% testes** passando
- [ ] **0 erros** de validação Pydantic
- [ ] **< 1ms** overhead por validação

### **Qualitativas**
- [ ] Código mais limpo e legível
- [ ] Padrões consistentes em todo o projeto
- [ ] Facilidade de manutenção
- [ ] Conformidade com A2A Protocol

---

## 🚧 **GESTÃO DE RISCOS**

### **Riscos Identificados**
1. **Breaking Changes** - Mitigado com aliases Pydantic
2. **Perda de Funcionalidade** - Mitigado com testes extensivos
3. **Incompatibilidade A2A** - Mitigado com validação de protocolo

### **Plano de Rollback**
Cada fase tem plano de rollback específico:
```bash
# Rollback para versão anterior
git checkout HEAD~1 -- service/types.py
git checkout HEAD~1 -- state/
```

---

## 📞 **SUPORTE E AJUDA**

### **Durante Implementação**
- **Tech Lead:** Consultas técnicas
- **Dev Team:** Dúvidas de implementação
- **QA Team:** Validação de testes

### **Documentação Adicional**
- **A2A Protocol:** Especificação oficial
- **Google ADK:** Documentação da API
- **Pydantic:** Guia de aliases e validação

---

## 🔄 **WORKFLOW RECOMENDADO**

### **Para Desenvolvedores**
1. **Leia o PRD** para entender o contexto
2. **Execute o script** para ver o estado atual
3. **Siga o plano** de implementação fase por fase
4. **Teste cada fase** antes de prosseguir
5. **Valide o resultado** executando o script novamente

### **Para Tech Leads**
1. **Revise o PRD** e aprove o projeto
2. **Aloque recursos** para cada fase
3. **Monitore o progresso** usando o script de validação
4. **Valide cada fase** antes de aprovar a próxima

### **Para QA**
1. **Entenda os requisitos** através do PRD
2. **Planeje testes** baseado no plano de implementação
3. **Execute testes** em cada fase
4. **Valide conformidade** com padrões A2A

---

## 📝 **NOTAS IMPORTANTES**

### **Padrão de Nomenclatura**
- **Externo:** `contextId` (camelCase) para APIs e JSON
- **Interno:** `context_id` (snake_case) como propriedade Python
- **Validação:** Aliases Pydantic para conversão automática

### **Compatibilidade**
- **Retrocompatibilidade:** Código existente deve continuar funcionando
- **APIs Externas:** Manter formato esperado pelo A2A Protocol
- **Google ADK:** Garantir comunicação sem erros

---

## 🎉 **CONCLUSÃO**

Este projeto de padronização é essencial para:
- ✅ Garantir compatibilidade com A2A Protocol
- ✅ Otimizar integração com Google ADK
- ✅ Simplificar manutenção do código
- ✅ Eliminar bugs de nomenclatura

Use os documentos e ferramentas fornecidos para implementar as mudanças de forma segura e eficiente.

---

*Documento criado em: 25/08/2024*  
*Última atualização: 25/08/2024*  
*Versão: 1.0*
