# 📊 RELATÓRIOS DO SISTEMA REVISA

> Lista completa de todos os relatórios que o SISTEMA REVISA como um todo pode gerar

---

## 📈 VISÃO GERAL

O sistema REVISA possui **múltiplos módulos de relatórios**, cada um servindo diferentes públicos e necessidades:

| App | Público | Foco | Tipos de Relatórios |
|-----|---------|------|-------------------|
| **🌐 WEB App** | Gestores/Analistas | Operação completa | 20+ tipos |
| **👔 GABINETE** | Executivos | Indicadores estratégicos | 8+ tipos |
| **🏢 POLO** | Gestores locais | Operação da unidade | 9+ tipos |
| **📱 MOBILE** | Agentes de campo | Sync operacional | 2 tipos |

---

## 🌐 RELATÓRIOS DA WEB APP

### 1. MÓDULO: Prestação de Contas (Accountability)
**Tipo:** Financeiro & Operacional  
**Público:** Gestores, Auditoria  
**Acesso:** Menu "Relatorios" → Modulo: "Prestacao de contas"

#### 📊 Sub-relatórios Integrados:

| Nome | O que mostra | Dados principais | Exportação |
|------|-------------|------------------|-----------|
| **Movimento Financeiro** | Entradas e saídas de recursos | Depósitos, transferências, pagamentos | CSV, PDF |
| **Folha de Pagamento** | Despesa mensal com pessoal | Salários, encargos, descontos | CSV, PDF |
| **Requisição de Materiais** | Requisições de compra e status | Aprovações, valores, fornecedores | CSV, PDF |
| **Documentos Fiscais** | Notas fiscais e comprovantes | NF, recibos, anexos | CSV, PDF |
| **Patrimônio (Bens Permanentes)** | Ativo fixo da unidade | Equipamentos, bem descrição, local | CSV, PDF |
| **Resumo Executivo** | Totalizações financeiras | Depositado, entradas, saídas, saldo | CSV, PDF |

**KPIs Mostrados:**
```
├─ Depositado (total de recursos)
├─ Entradas (inflows)
├─ Pagamentos (outflows)
├─ Folha mensal
└─ Saldo disponível
```

**Filtros disponíveis:**
```
├─ Período (data início - data fim)
├─ Unidade (Polo)
├─ Tipo de operação
└─ Status (aprovado, pendente, rejeitado)
```

---

### 2. MÓDULO: Financeiro
**Tipo:** Gestão de Recursos  
**Público:** Gestores, Coordenadores  
**Acesso:** Menu "Relatorios" → Modulo: "Financeiro"

#### 📊 Sub-relatórios:

| Nome | Descrição | Dados | Frequência |
|------|-----------|-------|-----------|
| **Captações por Fonte** | Recursos por origem | Fonte, valor, data | Mensal |
| **Execução vs Planejado** | Comparativo receita plano | % execução, desvios | Semanal |
| **Saldo por Unidade** | Recursos em caixa por Polo | Polo, saldo, data | Diário |
| **Alertas de Saque** | Saques que ultrapassam limite | Valor, limite, unidade | Real-time |
| **Reconciliação** | Batimento com banco | Saldo atual, saldo esperado | Diário |

---

### 3. MÓDULO: Plano de Trabalho × Execução
**Tipo:** Operacional & Planejamento  
**Público:** Gestores, Supervisores  
**Acesso:** Menu "Relatorios" → Modulo: "Workplan"

#### 📊 Sub-relatórios:

| Nome | Descrição | Dados principais | Status |
|------|-----------|------------------|--------|
| **Atividades Planejadas** | O que foi planejado fazer | Meta, período, responsável | Planejado |
| **Atividades Executadas** | O que foi realizado | Realizado, data, resultado | Executado |
| **Desvios** | Planejado vs Realizado | Diferença, %, motivo | Variância |
| **Cronograma** | Linha do tempo | Marcos, datas, status | Timeline |
| **Impacto de Atrasos** | Efeito de não cumprir prazos | Atividades dependentes afetadas | Análise |

---

### 4. MÓDULO: Gestão Financeira
**Tipo:** Contabilidade & Tesouraria  
**Público:** Gestores financeiros, Contadores  
**Acesso:** Menu "Relatorios" → Modulo: "Gestao Financeira"

#### 📊 Sub-relatórios:

| Nome | Descrição | Dados | Relatório |
|------|-----------|-------|----------|
| **Fluxo de Caixa** | Previsão de caixa | Entradas, saídas, saldo | 30/60/90 dias |
| **DRE (Demonstração de Resultado)** | P&L simplificado | Receita - Despesa = Resultado | Mensal |
| **Balanço Patrimonial** | Situação financeira | Ativo, Passivo, Patrimônio | Mensal |
| **Análise de Custos** | Quanto custa cada atividade | Custo unit., total, comparativo | Por programa |
| **Inadimplência** | Contas atrasadas | Devedor, valor, dias atraso | Mensal |

---

### 5. MÓDULO: Pessoas & Beneficiários
**Tipo:** Social & Demográfico  
**Público:** Gestores sociais, Supervisores  
**Acesso:** Menu "Relatorios" → Modulo: "Pessoas"

#### 📊 Sub-relatórios:

| Nome | O que documenta | Dados | Filtros |
|------|-----------------|-------|---------|
| **Cadastro Ativo** | Beneficiários ativos | Nome, CPF, contato, status | Por Polo, região |
| **Perfil Demográfico** | Características populacionais | Idade, gênero, renda, escolaridade | Por faixa |
| **Histórico de Contatos** | Toda interação registrada | Data, tipo, resultado, notas | Por período |
| **Relacionamentos** | Estrutura familiar | Matriarca, dependentes, vínculos | Por família |
| **Histórico de Desolidarização** | Pessoas que saíram | Motivo, data, acompanhamento | Por causa |

---

### 6. MÓDULO: Demandas & Processos
**Tipo:** Gestão de Casos  
**Público:** Gestores de caso, Agentes  
**Acesso:** Menu "Relatorios" → Modulo: "Demandas"

#### 📊 Sub-relatórios:

| Nome | Descrição | Status rastreados | Indicador |
|------|-----------|-------------------|-----------|
| **Demandas Abertas** | Casos em andamento | Aberta, em análise, em execução | Total ativo |
| **Taxa de Resolução** | Demandas solucionadas | Resolvida, arquivada | % mensal |
| **Tempo Médio de Resolução** | SLA de atendimento | Dias até fechamento | KPI |
| **Demandas por Tipo** | Classificação das solicitações | Saúde, educação, renda, etc | Distribuição |
| **Demandas com Risco** | Casos críticos não solucionados | Risco alto, prazo vencido | Alerta |

---

### 7. MÓDULO: Tarefas & Ações
**Tipo:** Gestão de Projetos  
**Público:** Coordenadores, Team leads  
**Acesso:** Menu "Relatorios" → Modulo: "Tarefas"

#### 📊 Sub-relatórios:

| Nome | Mostra | Dados | Período |
|------|--------|-------|---------|
| **Tarefas Pendentes** | O que falta fazer | Responsável, prazo, prioridade | Aberto |
| **Tarefas Atrasadas** | Prazos vencidos | Tarefa, dias atraso, impacto | Crítico |
| **Produtividade por Pessoa** | Desempenho individual | Tarefas completadas, taxa | Mensal |
| **Tarefas por Departamento** | Distribuição de trabalho | Depto, volume, carga | Snapshot |
| **Burndown** | Evolução do backlog | Tarefas restantes vs tempo | Sprint/Projeto |

---

### 8. MÓDULO: Auditoria & Logs
**Tipo:** Conformidade & Rastreabilidade  
**Público:** Administradores, Compliance  
**Acesso:** Menu "Relatorios" → Modulo: "Auditoria"

#### 📊 Sub-relatórios:

| Nome | O que registra | Dados rastreados | Retenção |
|------|-----------------|------------------|----------|
| **Log de Acessos** | Quem acessou quando | Usuário, data/hora, IP, ação | 1 ano |
| **Alterações de Dados** | Quem mudou o quê | Antes, depois, usuário, data | 2 anos |
| **Tentativas de Acesso Negado** | Segurança | Usuário, recurso, data, razão | 90 dias |
| **Exportações de Dados** | LGPD - Dados saíram do sistema | Arquivo, formato, usuário, data | 2 anos |
| **Operações Críticas** | Deleções, aprovações | Operação, entidade, usuário | 3 anos |

**Análises:**
```
├─ Atividade suspeita (múltiplas falhas)
├─ Usuários inativos
├─ Acessos em horário anormal
└─ Dados replicados/sincronizados
```

---

### 9. MÓDULO: Territory (Mapa Territorial)
**Tipo:** Geográfico & Espacial  
**Público:** Gestores de território, Supervisores  
**Acesso:** Menu "Relatorios" → Modulo: "Territorio"

#### 📊 Sub-relatórios:

| Nome | Mostra | Precisão | Atualização |
|------|--------|----------|------------|
| **Cobertura por Bairro** | % de população atendida | Bairro-nível | Diária |
| **Densidade de Beneficiários** | Concentração espacial | Heatmap | Semanal |
| **Localização de Agentes** | Onde estão os agentes | Zoom 100m | Real-time* |
| **Rotas Otimizadas** | Reduzir distância | Sequência de visitas | On-demand |
| **Gaps Territoriais** | Onde ainda não temos atendimento | Zonas vazias | Semanal |

*Requer módulo MOBILE com GPS ativo

---

### 10. MÓDULO: Integração Mobile
**Tipo:** Operacional  
**Público:** Gestores, Supervisores  
**Acesso:** Menu "Relatorios" → Modulo: "Mobile"

#### 📊 Sub-relatórios:

| Nome | Rastreia | Dados | Frequência |
|------|----------|-------|-----------|
| **Captura por Agente** | Quem cadastrou quanto | Contador, taxa/dia | Diária |
| **Captura por Bairro** | Distribuição geográfica | Beneficiários vs políticos | Diária |
| **Taxa de Sincronização** | Quantos já sincronizaram | Online/offline, %sync | Real-time |
| **Tempo de Campo** | Quanto cada agente trabalhou | Horas, produtividade | Semanal |
| **Entrada de Dados por Origem** | Mobile vs Web | Número, %, qualidade | Diária |

---

## 👔 RELATÓRIOS DO GABINETE

**Público:** Executivos, Tomadores de decisão  
**Frequência:** Atualização em tempo real  
**Acesso:** Dashboard principal + Menu "Relatorios"

### 1. Dashboard Executivo (Overview)
**Mostra:**
```
┌─────────────────────────────────────────┐
│ MÉTRICAS PRINCIPAIS (KPIs)              │
├─────────────────────────────────────────┤
│ 📊 Total de Cadastros                   │
│ 👥 Demandas Abertas                     │
│ ✅ Tarefas Pendentes                    │
│ 📈 Pessoas Vinculadas à Carteira        │
│ 🎯 Eventos Planejados                   │
│ 📋 Taxa de Progresso Mensal             │
└─────────────────────────────────────────┘
```

**Dados em tempo real:**
- Últimas captações
- Demandas em aberto
- Tarefas pendentes
- Próximos eventos

---

### 2. Relatório por Gabinete (Vereador)
**Tipo:** Executivo/Político  
**Filtros:**
```
├─ Gabinete (Vereador selecionado)
├─ Período (data início ~ fim)
├─ Status (todas as demandas/aberta/resolvida)
└─ Bairro/Região
```

**Dados gerados:**
```
├─ Carteira de beneficiários
├─ Captações realizadas neste período
├─ Demandas em andamento
├─ Tarefas do gabinete
├─ Evolução mês a mês
└─ Comparativo com período anterior
```

**Exportação:** CSV, PDF

---

### 3. Mapa Territorial do Gabinete
**Tipo:** Geográfico  
**Mostra:**
```
🗺️ Visualização:
├─ Bairros atendidos (cores)
├─ Concentração de beneficiários (heatmap)
├─ Agentes por zona
├─ Gaps de cobertura
└─ Linhas de ação por região
```

**Métrica:** % de cobertura por bairro

---

### 4. Timeline / Jornada de Atendimento
**Tipo:** Narrativo/Histórico  
**Mostra:**
```
📅 Para cada PESSOA selecionada:
├─ 1º contato (data, tipo)
├─ Captação (data, demandas)
├─ Acompanhamento (eventos)
├─ Resoluções (demandas fechadas)
├─ Status atual
└─ Próximas ações planejadas
```

---

### 5. Relatório Consolidado Multi-Gabinete
**Tipo:** Estratégico  
**Acesso:** Apenas admin/coordenador geral

**Compara:**
```
Gabinete A vs Gabinete B vs Gabinete C
├─ Total de beneficiários
├─ Taxa de resolução %
├─ Custo por beneficiário
├─ Tempo médio de resolução
├─ Ranking de desempenho
└─ Boas práticas de melhor performer
```

---

### 6. Alertas Críticos
**Tipo:** Real-time  
**Mostra:**
```
🚨 Dados que precisam atenção:
├─ Demandas vencidas
├─ Pessoas entrant/saindo
├─ Anomalias de gasto
├─ Falta de agentes em zona
└─ Sincronização mobile com atraso
```

---

### 7. Análise Comparativa Temporal
**Tipo:** Trending  
**Períodos:**
```
├─ Mês passado vs este mês
├─ Trimestre vs trimestre anterior
├─ Mesmo período do ano passado
└─ Acumulado do ano
```

**Indicadores:**
```
├─ Crescimento %
├─ Velocidade de mudança (seta)
├─ Projeção (onde vai chegar se continuar)
└─ Meta (está acima ou abaixo)
```

---

### 8. Relatório para Prestação de Contas Pública
**Tipo:** Político/Legal  
**Conteúdo:**
```
✅ O que foi realizado
├─ Total beneficiários atendidos
├─ Demandas resolvidas
├─ Valor gasto
└─ Fotodocumentação

📈 Indicadores de Desempenho
├─ Taxa de sucesso
├─ Tempo médio de resolução
├─ Satisfação (se houver)

🎯 Metas vs Realizado
├─ O que foi planejado
└─ O que foi entregue

📊 Despesas
├─ Recursos utilizados
└─ Orçamento restante
```

**Exportação:** PDF (para impressão/apresentação)

---

## 🏢 RELATÓRIOS DO POLO

**Público:** Gestores de unidade, Supervisores do Polo  
**Acesso:** Menu "Relatorios" → "Consulta do Polo"

### Menu de Seleção
```
Relatório [dropdown]:
├─ Todos
├─ Beneficiários
├─ Modalidades e Planos de Ação
├─ Equipe (Staff)
├─ Frequência de Agentes
├─ Ocorrências
├─ Requisições de Materiais
├─ Patrimônio (Bens Permanentes)
└─ Relatório Mensal

Status: [todos, ativo, inativo, bloqueado]
Período: [data início ~ data fim]
```

---

### 1. Relatório de Beneficiários
**Tipo:** Social  
**Dados:**
```
├─ Total de beneficiários cadastrados
├─ Beneficiários ativos (últimos 90 dias)
├─ Beneficiários inativos
├─ Novos beneficiários este período
├─ Beneficiários desincorporados
├─ Perfil demográfico:
│  ├─ Faixa etária
│  ├─ Gênero
│  ├─ Deficiências
│  └─ Renda aproximada
└─ Histórico de contatos por pessoa
```

**Tabela:** Listagem completa por beneficiário

---

### 2. Relatório de Modalidades e Planos de Ação
**Tipo:** Programático  
**Dados:**
```
Por cada Modalidade:
├─ Nome da modalidade
├─ Público-alvo
├─ Beneficiários inscritos
├─ Beneficiários ativos
├─ Plano de ação anual
└─ Taxa de presença
```

**Estatísticas:**
```
├─ Modalidades mais procuradas
├─ Taxa de retenção
├─ Custo por beneficiário
└─ Efetividade (resultado vs custo)
```

---

### 3. Relatório de Equipe (Staff)
**Tipo:** RH/Operacional  
**Dados por Agente:**
```
├─ Nome e CPF
├─ Cargo
├─ Contrato (tipo, período)
├─ Salário
├─ Status (ativo, licença, desligado)
├─ Últimas capacitações
├─ Horas trabalhadas
├─ Produtividade (cadastros/dia)
└─ Avaliação de desempenho
```

**Agregado:**
```
├─ Total de agentes ativos
├─ Folha de pagamento mensal
├─ Cobertura territorial (agentes por bairro)
├─ Absenteísmo %
└─ Rotatividade %
```

---

### 4. Relatório de Frequência
**Tipo:** Controle de presença  
**Dados:**
```
Por agente:
├─ Dias trabalhados
├─ Faltas
├─ Atrasos
├─ Licenças (repouso, médica, etc)
└─ Horas extras

Período: [customizável]
```

---

### 5. Relatório de Ocorrências
**Tipo:** Incidentes/Comportamento  
**Dados:**
```
├─ Tipo de ocorrência (falta, atraso, acidente, etc)
├─ Data e horário
├─ Agente envolvido
├─ Descrição
├─ Ação tomada
└─ Resultado
```

---

### 6. Relatório de Requisições de Materiais
**Tipo:** Suprimentos  
**Dados:**
```
├─ Descrição do material
├─ Quantidade solicitada
├─ Quantidade aprovada
├─ Data da solicitação
├─ Data da aprovação
├─ Fornecedor
├─ Custo
├─ Status (pendente, aprovado, recebido)
└─ Data de entrega
```

**Estatísticas:**
```
├─ Tempo médio de aprovação
├─ Taxa de aprovação %
├─ Custo mensal com materiais
└─ Itens em falta/urgentes
```

---

### 7. Relatório de Patrimônio (Bens Permanentes)
**Tipo:** Contabilidade/Controle  
**Dados por bem:**
```
├─ Número de identificação
├─ Descrição
├─ Categoria (móvel, imóvel, equipamento)
├─ Data de aquisição
├─ Valor de aquisição
├─ Localização (sala, setor)
├─ Responsável
├─ Status (ativo, danificado, baixado)
├─ Último inventário
└─ Condição (novo, bom, deteriorado)
```

**Controle:**
```
├─ Valores totais por categoria
├─ Depreciação
├─ Bens com manutenção necessária
├─ Responsabilidades por pessoa
└─ Conformidade com termo de responsabilidade
```

---

### 8. Relatório Mensal Integrado
**Tipo:** Executivo (resume tudo do Polo)  
**Conteúdo:**
```
RESUMO EXECUTIVO:
├─ Período: [mês/ano]
├─ Data de submissão
└─ Responsável

COMPETÊNCIA MENSAL:
├─ Modalidades ativas
├─ Beneficiários ativos
├─ Novas inscrições
├─ Altas (saíram)
└─ Taxa de presença

GESTÃO OPERACIONAL:
├─ Agentes em campo (dias)
├─ Cadastros realizados
├─ Demandas resolvidas
├─ Materiais requisitados
└─ Incidentes registrados

FINANCEIRO:
├─ Folha de pagamento
├─ Custeio (materiais, combustível)
├─ Investimento (patrimônio)
└─ Saldo de recursos

NARRATIVA:
├─ Principais avanços
├─ Desafios encontrados
├─ Acões corretivas tomadas
└─ Previsão para próximo mês

ANEXOS:
├─ Documentação de despesas
├─ Comprovantes de execução
└─ Fotos de atividades
```

**Exportação:** PDF, com anexos integrados

---

### 9. Análise de Performance do Polo
**Tipo:** Comparativo  
**Dados:**
```
Este mês vs:
├─ Mês anterior
├─ Trimestre anterior
├─ Mesmo mês do ano passado
└─ Meta anual

Indicadores:
├─ Crescimento %
├─ Eficiência (custo/beneficiário)
├─ Qualidade (taxa de resolução)
└─ Ranking entre polos
```

---

## 📱 RELATÓRIOS DO MOBILE APP

**Público:** Agentes de campo  
**Tipo:** Operacional/Local  
**Acesso:** Menu "Desempenho" (quando online)

### 1. Resumo de Captações
**Mostra:**
```
Hoje:
├─ Cadastros realizados
├─ Demandas registradas
└─ Tempo em campo

Esta semana:
├─ Total de captações
├─ Média por dia
└─ Histórico
```

**Atualização:** Semanal (quando conecta)

---

### 2. Status de Sincronização
**Mostra:**
```
📤 Sincronizando:
├─ ✅ Enviado: X cadastros
├─ ⏳ Pendente: Y cadastros
├─ 🔄 Última sincronização: data/hora
└─ 🔌 Status: Online/Offline

Alertas:
├─ ⚠️ Sem sincronizar há X dias
├─ 💾 Espaço restante no celular
└─ 🔋 Bateria (%)
```

---

## 📋 RESUMO: TIPOS DE RELATÓRIO POR CATEGORIA

### Por Público

**👔 EXECUTIVOS (Gabinete)**
```
├─ Dashboard KPIs
├─ Relatório consolidado multi-gabinete
├─ Timeline de atendimento
├─ Mapa territorial
└─ Relatório de prestação de contas pública
```

**🏢 GESTORES (Web + Polo)**
```
├─ Prestação de contas financeira
├─ Fluxo de caixa
├─ Gestão de tarefas
├─ Performance de equipe
├─ Relatório mensal integrado
└─ Análise comparativa temporal
```

**🎯 SUPERVISORES (Polo)**
```
├─ Frequência de agentes
├─ Ocorrências
├─ Resultados de campo
├─ Requisições aprovadas
└─ Patrimônio sob controle
```

**👥 AGENTES (Mobile)**
```
├─ Meu desempenho diário
├─ Status de sincronização
└─ Próximo turno
```

---

### Por Frequência

**⏰ REAL-TIME**
```
├─ Dashboard Gabinete (atualiza constantemente)
├─ Alertas críticos
└─ Status mobilidade (online/offline)
```

**📅 DIÁRIO**
```
├─ Saldo em caixa
├─ Captura por agente
├─ Cobertura por bairro
└─ Sincronização mobile
```

**📊 SEMANAL**
```
├─ Performance de equipe
├─ Tarefas pendentes
├─ Fluxo de caixa (previsão semanal)
└─ Resumo de agentes
```

**📈 MENSAL**
```
├─ Relatório integrado do Polo
├─ Prestação de contas
├─ Folha de pagamento
├─ DRE (P&L)
└─ Análise de desempenho
```

**📋 TRIMESTRAL**
```
├─ Análise de tendência
├─ Revisão de metas
└─ Benchmarking entre unidades
```

**🎯 ANUAL**
```
├─ Relatório de execução anual
├─ Planejamento para próximo ano
└─ Avaliação estratégica
```

---

### Por Formato

**📊 TABULAR (Excel/CSV)**
```
Relatórios em linhas × colunas:
├─ Prestação de contas
├─ Auditoria
├─ Lista de beneficiários
├─ Requisições
└─ Patrimônio
```

**📄 NARRATIVO (PDF)**
```
Relatórios com contexto:
├─ Relatório mensal do Polo
├─ Relatório de prestação pública
├─ Análise de tendências
└─ Relatório final de projeto
```

**📈 GRÁFICO/VISUAL (Dashboard)**
```
Representações visuais:
├─ Gráficos de linha (série temporal)
├─ Gráficos de barra (comparativo)
├─ Gráficos de pizza (proporção)
├─ Heatmap (geografico)
└─ Tabela interativa (filtres aplicados)
```

**🗺️ GEO-REFERENCIADO**
```
Mapas com dados:
├─ Heatmap de beneficiários
├─ Localização de agentes
├─ Cobertura territorial
└─ Gaps não atendidos
```

---

## 🔧 FUNCIONALIDADES COMUNS

### Filtros Disponíveis (Todos os Relatórios)
```
Padrão:
├─ Período (data início ~ fim)
├─ Gabinete/Polo (seleção)
├─ Status (todas/ativo/inativo/etc)
└─ Usuário responsável

Avançados:
├─ Bairro/Região
├─ Faixa etária
├─ Categoria
├─ Valor (mín ~ máx)
├─ Texto (busca livre)
└─ Ordem (crescente/decrescente)
```

### Exportação
```
Todos os relatórios podem ser exportados em:
├─ 📊 CSV (para Excel ou análise)
├─ 📄 PDF (para impressão)
├─ 📋 JSON (para integração)
└─ 📎 ZIP (com anexos)
```

### Agendamento
```
Alguns relatórios permitem:
├─ ⏰ Geração automática
├─ 📧 Envio por email
├─ 🔔 Notificação
└─ 💾 Armazenamento (últimas 10 gerações)
```

### Validações
```
Segurança aplicada:
├─ 🔐 Apenas dados que o usuário pode ver
├─ 🗺️ Apenas unidade do usuário (se gestor)
├─ 📋 Apenas período que tem permissão
└─ 🔒 Auditoria de quem gerou quando
```

---

## 📊 EXEMPLO: FLUXO COMPLETO DE UM RELATÓRIO

```
USUÁRIO FINAL:
1. Acessa app (Web/Gabinete/Polo)
2. Menu → Relatórios
3. Seleciona tipo e filtros
4. Clica "Aplicar Filtros"
   ↓
API BACKEND:
5. FastAPI recebe requisição
6. Valida: usuário pode ver isso?
7. Consulta BD:
   - Beneficiários (PERSON module)
   - Demandas (MOBILE module)
   - Financeiro (ADMINISTRATION module)
   - Logs (ANALYTICS module)
   ↓
BACKEND:
8. Processa dados
9. Calcula KPIs
10. Ordena e formata
   ↓
FRONTEND:
11. Recebe JSON da API
12. Renderiza tabela/gráfico
13. Mostra em tempo real
   ↓
USUÁRIO:
14. Vê resultado
15. Pode filtrar mais
16. Exporta (CSV ou PDF)
17. Compartilha ou imprime
```

---

## ✨ CONCLUSÃO

O REVISA oferece **50+ tipos de relatórios** através de seus módulos, servindo:

```
👔 Executivos        → Decisões estratégicas (dashboards, KPIs)
🏢 Gestores         → Operação (performance, financeiro, RH)
🎯 Supervisores     → Campo (equipe, qualidade, conformidade)
👥 Agentes          → Seu próprio desempenho (mobile local)
🔐 Auditorias       → Rastreabilidade e compliance
```

Cada relatório é:
- ✅ **Seguro** (respeita permissões)
- ✅ **Customizável** (filtros e períodos)
- ✅ **Exportável** (CSV, PDF, JSON)
- ✅ **Auditado** (quem gerou quand)
- ✅ **Integrado** (todos compartilham mesmos dados)

---

> **Dúvida?** Qual relatório você precisa que falte na lista? Podemos criar customizações!
