# 📋 PRD - Padronização de Nomenclatura de Campos
## Projeto: UI Mesop com Google ADK e A2A Protocol

---

## 📊 **INFORMAÇÕES DO PROJETO**

| Campo | Valor |
|-------|-------|
| **Nome do Projeto** | Padronização de Nomenclatura de Campos |
| **Versão** | 1.0 |
| **Data de Criação** | 25/08/2024 |
| **Responsável** | Equipe de Desenvolvimento |
| **Prioridade** | 🔴 ALTA |
| **Status** | 📋 PLANEJAMENTO |

---

## 🎯 **RESUMO EXECUTIVO**

### **Problema Identificado**
O projeto UI Mesop apresenta inconsistências críticas na nomenclatura de campos relacionados ao contexto de mensagens, causando:
- ❌ Erros de validação Pydantic
- ❌ Falhas na comunicação com Google ADK
- ❌ Incompatibilidades com A2A Protocol
- ❌ Dificuldade de manutenção e debugging

### **Solução Proposta**
Padronizar toda a nomenclatura de campos para usar **`contextId` (camelCase)** como padrão único, mantendo compatibilidade através de aliases Pydantic e propriedades Python.

### **Impacto Esperado**
- ✅ 100% compatibilidade com A2A Protocol
- ✅ Integração perfeita com Google ADK
- ✅ Código mais limpo e manutenível
- ✅ Eliminação de bugs de nomenclatura

---

## 🚨 **PROBLEMA ATUAL**

### **Sintomas Identificados**
1. **Múltiplas Variações em Uso:**
   - `context_id` (snake_case) - usado em 35 lugares
   - `contextid` (lowercase) - usado em 29 lugares  
   - `contextId` (camelCase) - usado em 161 lugares
   - `context_Id` (mixed) - usado em alguns lugares

2. **Consequências:**
   - Mensagens não processadas pelo Google Gemini
   - Interface mostra conversas com 0 mensagens
   - Erros de validação Pydantic frequentes
   - Código difícil de manter e debugar

### **Arquivos Afetados**
- `service/types.py` - Modelos Pydantic
- `state/state.py` - Classes de estado
- `service/server/adk_host_manager.py` - Gerenciador ADK
- `state/host_agent_service.py` - Serviço do agente
- `message_patch.py` - Patches de compatibilidade

---

## 🎯 **OBJETIVOS DO PROJETO**

### **Objetivo Principal**
Padronizar toda a nomenclatura de campos relacionados ao contexto para usar `contextId` (camelCase) como padrão único, eliminando inconsistências e garantindo compatibilidade total com A2A Protocol e Google ADK.

### **Objetivos Específicos**
1. **Padronização:** Unificar nomenclatura em todo o sistema
2. **Compatibilidade:** Manter retrocompatibilidade com código existente
3. **Conformidade:** Garantir conformidade com A2A Protocol
4. **Integração:** Otimizar integração com Google ADK
5. **Manutenibilidade:** Simplificar código e facilitar manutenção

---

## 📋 **REQUISITOS FUNCIONAIS**

### **RF-001: Padronização de Campos**
- **Descrição:** Todos os campos de contexto devem usar `contextId` (camelCase)
- **Critério de Aceitação:** 0 variações de nomenclatura em uso
- **Prioridade:** 🔴 ALTA

### **RF-002: Compatibilidade Retroativa**
- **Descrição:** Código existente deve continuar funcionando
- **Critério de Aceitação:** Todos os testes passam sem modificação
- **Prioridade:** 🔴 ALTA

### **RF-003: Conformidade A2A Protocol**
- **Descrição:** Campos devem seguir padrões A2A Protocol
- **Critério de Aceitação:** Validação A2A 100% bem-sucedida
- **Prioridade:** 🟡 MÉDIA

### **RF-004: Integração Google ADK**
- **Descrição:** Comunicação com Google ADK deve funcionar perfeitamente
- **Critério de Aceitação:** Mensagens processadas sem erros
- **Prioridade:** 🔴 ALTA

---

## 🔧 **REQUISITOS NÃO FUNCIONAIS**

### **RNF-001: Performance**
- **Descrição:** Normalização de campos não deve impactar performance
- **Critério de Aceitação:** < 1ms overhead por validação
- **Prioridade:** 🟡 MÉDIA

### **RNF-002: Manutenibilidade**
- **Descrição:** Código deve ser fácil de manter e entender
- **Critério de Aceitação:** Documentação clara e padrões consistentes
- **Prioridade:** 🟡 MÉDIA

### **RNF-003: Testabilidade**
- **Descrição:** Todas as mudanças devem ser testáveis
- **Critério de Aceitação:** Cobertura de testes > 90%
- **Prioridade:** 🟡 MÉDIA

---

## 🏗️ **ARQUITETURA DA SOLUÇÃO**

### **Padrão de Nomenclatura**
```python
# ✅ PADRÃO CORRETO
class Message(BaseModel):
    contextId: str = Field(alias="contextId")  # Campo principal camelCase
    
    @property
    def context_id(self) -> str:  # Alias Python snake_case
        return self.contextId
```

### **Estratégia de Migração**
1. **Fase 1:** Atualizar modelos Pydantic com aliases
2. **Fase 2:** Refatorar classes de estado
3. **Fase 3:** Simplificar patches de compatibilidade
4. **Fase 4:** Remover código de normalização desnecessário

### **Compatibilidade**
- **Externo:** `contextId` (camelCase) para APIs e JSON
- **Interno:** `context_id` (snake_case) como propriedade Python
- **Validação:** Aliases Pydantic para conversão automática

---

## 📅 **CRONOGRAMA DO PROJETO**

### **Fase 1: Modelos Pydantic (Semana 1)**
- [ ] Atualizar `service/types.py`
- [ ] Implementar aliases Pydantic
- [ ] Testes de validação
- [ ] Documentação

### **Fase 2: Classes de Estado (Semana 2)**
- [ ] Refatorar `state/state.py`
- [ ] Atualizar `state/host_agent_service.py`
- [ ] Testes de estado
- [ ] Validação de funcionalidades

### **Fase 3: ADK Host Manager (Semana 3)**
- [ ] Refatorar `service/server/adk_host_manager.py`
- [ ] Simplificar conversões
- [ ] Testes de integração ADK
- [ ] Validação com Google Gemini

### **Fase 4: Limpeza e Otimização (Semana 4)**
- [ ] Simplificar `message_patch.py`
- [ ] Remover código desnecessário
- [ ] Testes finais
- [ ] Documentação final

---

## 🧪 **PLANO DE TESTES**

### **Testes Unitários**
- [ ] Validação de modelos Pydantic
- [ ] Conversão de aliases
- [ ] Propriedades de compatibilidade
- [ ] Normalização de campos

### **Testes de Integração**
- [ ] Comunicação com Google ADK
- [ ] Processamento de mensagens
- [ ] Gerenciamento de estado
- [ ] Fluxo completo de conversas

### **Testes de Compatibilidade**
- [ ] Dados de APIs antigas
- [ ] Código existente
- [ ] Migração de dados
- [ ] Retrocompatibilidade

---

## 📊 **CRITÉRIOS DE SUCESSO**

### **Métricas Quantitativas**
- [ ] **0 variações** de nomenclatura em uso
- [ ] **100% testes** passando
- [ ] **0 erros** de validação Pydantic
- [ ] **100% mensagens** processadas pelo Google ADK

### **Métricas Qualitativas**
- [ ] Código mais limpo e legível
- [ ] Documentação clara e atualizada
- [ ] Padrões consistentes em todo o projeto
- [ ] Facilidade de manutenção

---

## 🚧 **RISCOS E MITIGAÇÕES**

### **Risco 1: Breaking Changes**
- **Probabilidade:** 🟡 MÉDIA
- **Impacto:** 🔴 ALTO
- **Mitigação:** Aliases Pydantic e propriedades de compatibilidade

### **Risco 2: Perda de Funcionalidade**
- **Probabilidade:** 🟡 MÉDIA
- **Impacto:** 🔴 ALTO
- **Mitigação:** Testes extensivos e migração gradual

### **Risco 3: Incompatibilidade com A2A Protocol**
- **Probabilidade:** 🟢 BAIXA
- **Impacto:** 🔴 ALTO
- **Mitigação:** Validação contra especificação A2A

---

## 📚 **DOCUMENTAÇÃO NECESSÁRIA**

### **Documentos Técnicos**
- [ ] Guia de Padrões de Nomenclatura
- [ ] Documentação de Migração
- [ ] Guia de Desenvolvimento
- [ ] API Reference

### **Documentos de Usuário**
- [ ] Guia de Instalação
- [ ] Manual de Configuração
- [ ] Troubleshooting Guide
- [ ] FAQ

---

## 🔄 **MANUTENÇÃO PÓS-IMPLANTAÇÃO**

### **Monitoramento Contínuo**
- [ ] Verificação de conformidade com padrões
- [ ] Análise de novos campos adicionados
- [ ] Validação de integrações externas
- [ ] Feedback da equipe de desenvolvimento

### **Atualizações**
- [ ] Revisão trimestral dos padrões
- [ ] Atualização de documentação
- [ ] Treinamento da equipe
- [ ] Melhorias baseadas em feedback

---

## 📝 **APROVAÇÕES**

| Papel | Nome | Data | Assinatura |
|-------|------|------|------------|
| **Product Owner** | | | |
| **Tech Lead** | | | |
| **Dev Team Lead** | | | |
| **QA Lead** | | | |

---

## 📞 **CONTATOS**

| Papel | Nome | Email | Telefone |
|-------|------|-------|----------|
| **Project Manager** | | | |
| **Tech Lead** | | | |
| **Dev Team** | | | |

---

## 📋 **CHECKLIST DE IMPLEMENTAÇÃO**

### **Pré-Implantação**
- [ ] PRD aprovado
- [ ] Recursos alocados
- [ ] Ambiente de desenvolvimento configurado
- [ ] Equipe treinada

### **Durante Implementação**
- [ ] Fases executadas conforme cronograma
- [ ] Testes realizados em cada fase
- [ ] Documentação atualizada
- [ ] Code review realizado

### **Pós-Implantação**
- [ ] Testes finais aprovados
- [ ] Documentação finalizada
- [ ] Treinamento da equipe
- [ ] Monitoramento ativo

---

*Documento criado em: 25/08/2024*  
*Última atualização: 25/08/2024*  
*Versão: 1.0*
