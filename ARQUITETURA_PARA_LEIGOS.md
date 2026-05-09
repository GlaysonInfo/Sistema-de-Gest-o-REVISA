# 🏗️ REVISA: Explicação da Arquitetura para Leigos

> Para entender conceitos complexos de forma simples!

---

## 📖 O que é REVISA? (Em 30 segundos)

REVISA é um **sistema integrado de gestão** que permite:

```
🏛️ EXECUTIVOS
   ↓
📊 acompanham indicadores e relatórios
   ↓
👥 GESTORES DE CAMPO
   ↓
📱 coletam dados com celular offline
   ↓
💾 BANCO DE DADOS centralizado
   ↓
📈 gera insights e análises
```

Pense em um **aplicativo de delivery**, mas para gerenciar **pessoas, demandas e acompanhamento social**.

---

## 🎯 Analogia Com o Mundo Real

### Restaurante 🍕 vs Sistema REVISA 🏛️

| Componente | Restaurante | REVISA |
|-----------|-----------|---------|
| **👨‍💼 Gerente** | Vê vendas no painel | Executivo vê indicadores no **Gabinete** |
| **🚗 Entregador** | Coleta pedidos, entrega | Agente social coleta dados no **Mobile App** |
| **📦 Centro de distribuição** | Prepara pedidos | **API Backend** processa e armazena dados |
| **💾 Registro de vendas** | Caderno de controle | **PostgreSQL Database** (banco de dados) |
| **📞 Telefone** | Cliente liga para pedir | **Integração entre apps** (web, mobile, polos) |
| **👨‍🍳 Chef** | Prepara o prato | **Módulos especializados** (cada um faz sua função) |

---

## 🏗️ ARQUITETURA EM CAMADAS

```
┌─────────────────────────────────────────────────────────────┐
│ 🖥️ LAYER 1: INTERFACES (O USUÁRIO VÊ)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📱 MOBILE APP          🌐 WEB ADMIN         👔 GABINETE    │
│  (Campo, offline)      (Management)        (Executivos)    │
│  App no celular        Browser para        Dashboard       │
│  Funciona sem net      gestores            Indicadores    │
│                                                              │
└────────────────┬────────────────┬──────────────────┬────────┘
                 │                │                  │
┌────────────────▼────────────────▼──────────────────▼────────┐
│ 🌉 LAYER 2: GATEWAY / INTEGRAÇÃO (FastAPI)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ⚡ API REST CENTRALIZADA                                   │
│  • Recebe requisições de todos os apps                     │
│  • Valida dados                                            │
│  • Roteia para os módulos corretos                         │
│  • Devolve respostas em JSON                               │
│                                                              │
│  Exemplo:                                                  │
│  POST /api/v1/mobile/intake                                │
│  (Agente envia novo beneficiário)                          │
│                                                              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 📚 LAYER 3: MÓDULOS DE NEGÓCIO (Core do Sistema)           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Cada módulo = Um departamento especializado                │
│                                                              │
│  🔐 IAM (Autenticação)       🗺️ TERRITORY (Geografia)       │
│     Quem pode acessar?          Onde as coisas acontecem?   │
│     Login e Permissões         Zonas, regiões              │
│                                                              │
│  👥 CABINET (Gabinete)        📊 ANALYTICS (Análises)      │
│     Executivos do governo       Relatórios e gráficos      │
│     Principais decisores        Insights dos dados         │
│                                                              │
│  🏢 POLO (Unidades locais)    📋 WORKFLOW (Processos)      │
│     Postos de atendimento       Fluxos de trabalho         │
│     Agentes em campo            Etapas de um processo      │
│                                                              │
│  👤 PERSON (Pessoas)           🔗 RELATIONSHIP (Vínculos)  │
│     Beneficiários               Conexões entre pessoas     │
│     Dados pessoais              Família, relações         │
│                                                              │
│  📱 MOBILE (Campo)            📊 ADMINISTRATION (Gestão)   │
│     App offline de coleta       Relatórios gerenciais      │
│     Cadastros rápidos           Auditoria e controle       │
│                                                              │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 💾 LAYER 4: BANCO DE DADOS (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Cada módulo tem seu próprio "armário" (schema):           │
│                                                              │
│  ├─ iam/        (usuários, papéis, permissões)             │
│  ├─ cabinet/    (executivos, gabinete)                     │
│  ├─ polo/       (postos, agentes)                          │
│  ├─ person/     (beneficiários, dados demográficos)       │
│  ├─ territory/  (localização, zonas)                       │
│  ├─ analytics/  (métricas, relatórios)                     │
│  ├─ workflow/   (processsos, estados)                      │
│  ├─ mobile/     (registros de campo)                       │
│  ├─ relationship/ (vínculos entre pessoas)                 │
│  └─ administration/ (logs, auditoria)                      │
│                                                              │
│  Tudo sincronizado, com integridade garantida               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 OS 10 MÓDULOS EXPLICADOS

### 1️⃣ **IAM (Identity & Access Management)** 🔐
**O que é?** Sistema de controle de acesso  
**Responsabilidades:**
- Gerenciar quem pode entrar (login/senha)
- Definir papéis (admin, agente, gestor, executivo)
- Controlar permissões (quem pode ver/editar o quê)
- Rastrear último acesso de cada usuário

**Analogia:** Porteiro do edifício que verifica crachá e só deixa entrar quem tem permissão

**Dados que guarda:**
```
👤 Usuários (username, password, email)
📋 Papéis (Admin, Agente, Gestor, Executivo)
🔑 Permissões (ver relatórios, editar cadastros, etc)
```

---

### 2️⃣ **CABINET (Gabinete)** 👔
**O que é?** Módulo de executivos e tomadores de decisão  
**Responsabilidades:**
- Painel executivo com KPIs (indicadores chave)
- Visualizar indicadores de desempenho
- Acessar relatórios consolidados
- Tomar decisões baseadas em dados

**Analogia:** Sala de diretores com tela grande mostrando vendas do mês

**Dados que guarda:**
```
📊 Indicadores (pessoas atendidas, taxa de sucesso)
📈 Gráficos (tendências ao longo do tempo)
🎯 Metas (O que foi planejado vs realizado)
💼 Decisões (registros de deliberações)
```

---

### 3️⃣ **POLO (Pólos Regionais)** 🏢
**O que é?** Módulo que representa cada unidade de atendimento  
**Responsabilidades:**
- Gerenciar cada "posto de atendimento"
- Acompanhar agentes em campo
- Registrar atendimentos realizados
- Coordenar demandas locais
- Controlar agenda de agentes

**Analogia:** Filiais de um banco, cada uma operando localmente mas conectada ao sistema central

**Dados que guarda:**
```
🏪 Informações da unidade (endereço, horário, telefone)
👥 Agentes lotados (quem trabalha lá)
📅 Calendário de atividades
📊 Desempenho local
```

---

### 4️⃣ **TERRITORY (Território)** 🗺️
**O que é?** Módulo de organização geográfica  
**Responsabilidades:**
- Organizar o mapa em zonas/regiões
- Atribuir agentes a territórios
- Controlar cobertura geográfica
- Gerenciar deslocamentos

**Analogia:** Mapa dividido em zonas de entrega, cada entregador responsável por uma zona

**Dados que guarda:**
```
🗺️ Zonas/Regiões (poligonos no mapa)
📍 Localizações (ruas, bairros, cidades)
👤 Quem é responsável de cada área
📏 Distâncias e rotas
```

---

### 5️⃣ **PERSON (Pessoas)** 👤
**O que é?** Módulo de dados cadastrais de beneficiários  
**Responsabilidades:**
- Armazenar dados básicos (nome, CPF, telefone)
- Controlar dados de contato
- Gerenciar histórico de atualizações
- Integrar com outros módulos

**Analogia:** Agenda de contatos, mas com histórico e observações

**Dados que guarda:**
```
👤 Informações básicas (nome, CPF, RG)
📞 Contatos (telefone, email, endereço)
📋 Observações (notas sobre a pessoa)
📅 Histórico de atualizações
🏥 Dados de saúde/demandas específicas
```

---

### 6️⃣ **RELATIONSHIP (Relacionamentos)** 🔗
**O que é?** Módulo que mapeia vínculos entre pessoas  
**Responsabilidades:**
- Registrar relações (matriarca, filhos, dependentes)
- Rastrear estrutura familiar
- Gerenciar vínculos profissionais
- Conectar pessoas a processos/demandas

**Analogia:** Árvore genealógica que mostra quem está relacionado com quem

**Dados que guarda:**
```
👨‍👩‍👧‍👦 Relações familiares (pai, mãe, filho)
🤝 Relações profissionais (chefe, colega)
📋 Tipo de vínculo (responsável, dependente, etc)
📅 Quando começou a relação
```

---

### 7️⃣ **MOBILE (App de Campo)** 📱
**O what is?** Módulo que alimenta o app mobile  
**Responsabilidades:**
- Fornecer dados para o app offline
- Receber dados coletados em campo
- Sincronizar quando volta online
- Gerenciar integridade dos dados coletados

**Analogia:** Caixa de correspondência para o entregador deixar recados

**Dados que guarda:**
```
📝 Cadastros pendentes (personas novas)
📊 Observações (anotações do agente em campo)
🏆 Ações realizadas (visitas, ligações)
📱 Sincronização (o que já foi enviado)
```

---

### 8️⃣ **WORKFLOW (Processos)** 📋
**O what is?** Módulo que define fluxos de trabalho  
**Responsabilidades:**
- Definir etapas de um processo
- Controlar estado/progresso de cada item
- Enviar notificações de próxime etapa
- Rastrear tempo em cada estágio
- Gerenciar aprovações

**Analogia:** Receita de bolo que lista ingredientes, modo de fazer, tempo de forno

**Dados que guarda:**
```
🔄 Fluxos (sequência de passos)
📊 Estados (Em análise → Aprovado → Finalizado)
⏱️ Timings (quanto tempo em cada etapa)
📌 Responsáveis (quem aprova cada etapa)
```

---

### 9️⃣ **ANALYTICS (Análises)** 📊
**O what is?** Módulo de relatórios e inteligência de dados  
**Responsabilidades:**
- Calcular indicadores (KPIs)
- Gerar relatórios automáticos
- Criar dashboards com visualizações
- Identificar tendências
- Alertas quando algo anormal acontece

**Analogia:** Departamento de análise do banco que vê padrões nas movimentações financeiras

**Dados que guarda:**
```
📈 Métricas calculadas (média, total, percentual)
📊 Agregações (por região, por período)
🎯 Benchmark (esperado vs realizado)
🚨 Alertas (quando ultrapassa limite)
```

---

### 🔟 **ADMINISTRATION (Gestão)** 🛠️
**O what is?** Módulo administrativo e de governança  
**Responsabilidades:**
- Gerenciar usuários e papéis
- Auditoria de ações (quem fez o quê)
- Relatórios de conformidade
- Backups e recuperação
- Logs de sistema

**Analogia:** Departamento de RH + Controle Interno da empresa

**Dados que guarda:**
```
👥 Usuários (cadastro e papel)
📋 Logs de auditoria (histórico de ações)
📊 Relatórios de compliance
🔒 Registro de acessos
```

---

## 🔄 COMO OS MÓDULOS SE INTEGRAM?

### Fluxo 1: Agente Coleta Dados em Campo 📱
```
1. Agente abre app MOBILE no celular
   ↓
2. App envia dados para MOBILE module (via API)
   ↓
3. MOBILE module checa integridade com IAM (agente existe?)
   ↓
4. MOBILE module valida com TERRITORY (está na zona certa?)
   ↓
5. MOBILE module chama PERSON module (cadastra nova pessoa)
   ↓
6. MOBILE module chama RELATIONSHIP module (registra vínculos)
   ↓
7. MOBILE module chama WORKFLOW module (inicia processo)
   ↓
8. ANALYTICS module atualiza métricas
   ↓
9. Executivo vê no CABINET dashboard 📊
```

### Fluxo 2: Executivo Gera Relatório 📈
```
1. Executivo acessa CABINET
   ↓
2. Clica "Gerar Relatório"
   ↓
3. CABINET chama ANALYTICS module
   ↓
4. ANALYTICS consulta dados de:
   - PERSON (quantas pessoas)
   - POLO (por unidade)
   - TERRITORY (por região)
   - WORKFLOW (progresso)
   ↓
5. ANALYTICS calcula sobre o que foi coletado em MOBILE
   ↓
6. Resultado é mostrado em CABINET
```

### Fluxo 3: Validar Acesso de Usuário 🔐
```
1. Usuário tenta acessar web
   ↓
2. Digita username/password
   ↓
3. API chama IAM module
   ↓
4. IAM valida passwd e carrega PAPÉIS (roles)
   ↓
5. IAM carrega PERMISSÕES associadas
   ↓
6. Sistema libera acesso apenas ao que ele pode ver
   ↓
7. ADMINISTRATION module registra o login no audit log
```

---

## 👥 COMO CADA APP USA OS MÓDULOS?

### 📱 MOBILE APP (App de Campo)
**Quem usa?** Agentes em campo  
**Módulos principais:**
```
├─ MOBILE       (envia/recebe dados)
├─ PERSON       (cadastra beneficiários)
├─ RELATIONSHIP (registra famílias)
├─ TERRITORY    (sabe onde está)
├─ WORKFLOW     (segue processo)
├─ IAM          (autentica)
└─ ANALYTICS    (vê seu desempenho local)
```

**O que faz?**
```
✅ Cadastra nova pessoa com dados básicos
✅ Registra relacionamentos (marido, filha, etc)
✅ Abre demandas/processos
✅ Funciona SEM internet
✅ Sincroniza quando voltar online
```

---

### 🌐 WEB APP (Interface Principal)
**Quem usa?** Gestores, analistas, coordenadores  
**Módulos principais:**
```
├─ PERSON       (busca/edita pessoas)
├─ RELATIONSHIP (vê vínculos)
├─ POLO         (gerencia unidades)
├─ TERRITORY    (manipula zonas)
├─ WORKFLOW     (acompanha processos)
├─ MOBILE       (vê o que agentes coletaram)
├─ ANALYTICS    (vê relatórios)
├─ ADMINISTRATION (gerencia usuários)
└─ IAM          (autentica)
```

**O que faz?**
```
✅ Busca pessoas cadastradas
✅ Edita informações de beneficiários
✅ Acompanha processos em andamento
✅ Gera relatórios customizados
✅ Gerencia papéis e permissões
✅ Visualiza dashboard
```

---

### 👔 GABINETE APP (Dashboard Executivo)
**Quem usa?** Diretores, coordenadores gerais  
**Módulos principais:**
```
├─ CABINET      (sua interface)
├─ ANALYTICS    (relatórios e KPIs)
├─ POLO         (desempenho por unidade)
├─ TERRITORY    (cobertura geográfica)
├─ IAM          (autentica)
└─ ADMINISTRATION (auditoria)
```

**O que faz?**
```
✅ Vê indicadores gerenciais
✅ Compara desempenho entre unidades
✅ Acompanha metas
✅ Acessa relatórios prontos
✅ Toma decisões baseadas em dados
```

---

## 🚀 EXEMPLO PRÁTICO: Do Agente ao Executivo

### Dia do Agente (Segunda-feira 10:00 AM)

```
Agente Pedro está na Rua A, Bairro X
├─ Abre app MOBILE no celular
├─ Toca em "Novo Cadastro"
├─ Digita dados:
│  ├─ Nome: Maria Silva
│  ├─ CPF: 123.456.789-00
│  ├─ Endereço: Rua A, 123
│  ├─ Telefone: 99999-0000
│  └─ Demanda: Receber auxílio
├─ Toca em "Registrar Vínculo"
├─ Adiciona filha: "Ana Silva"
├─ Toca em "Enviar"
└─ (Se tiver internet) Envia logo
   (Se não tiver) Salva localmente, envia depois

❌ Pedro não tem internet agora
✅ Mas o app salva tudo no celular
```

### O Sistema Recebendo

```
Pedro/Android ───[SYNC EVENT]──→ API BACKEND
                                     ↓
                        MOBILE module processa
                                     ↓
                        PERSON module cria:
                        - Maria (id_12345)
                        - Ana (id_12346)
                                     ↓
                        RELATIONSHIP module cria:
                        - Vínculo mãe: Maria
                        - Filha: Ana
                                     ↓
                        WORKFLOW module inicia:
                        - Processo: "Análise de Elegibilidade"
                        - Status: "Pendente Análise"
                                     ↓
                        ANALYTICS atualiza:
                        - Total beneficiários: +2
                        - Taxa de cobertura: +0.5%
                                     ↓
                        ADMINISTRATION registra em audit log:
                        - Usuario: pedro.silva
                        - Ação: CREATE PERSON
                        - Timestamp: 10:30 AM
```

### Na Terça-Feira - Gestor no Computador

```
Gestor Ana acessa WEB APP
├─ Vê novo cadastro de Maria Silva
├─ Clica em "Análise de Elegibilidade"
├─ Carrega documentos
├─ Clica "Aprovar"
└─ Sistema atualiza WORKFLOW

STATUS AGORA:
├─ Pessoa: María Silva ✅
├─ Vínculo: filha Ana ✅
└─ Processo: APROVADO 🟢
```

### Na Quinta-Feira - Executivo no Dashboard

```
Diretor Marcelo acessa GABINETE
├─ Dashboard mostra:
│  ├─ Novos cadastrados esta semana: 47
│  ├─ Aprovados: 32
│  ├─ Taxa de aprovação: 68%
│  ├─ Por unidade: 
│  │  ├─ POLO Centro: 12 aprovados
│  │  ├─ POLO Zona Norte: 8 aprovados
│  │  └─ POLO Zona Sul: 12 aprovados
│  └─ Cobertura geográfica: 87%
├─ Clica em "Relatório Semanal"
├─ Vê gráficos e tendências
└─ Envia para reunião de diretoria
```

---

## 🔐 SEGURANÇA: Quem Vê O Quê?

### Permissões de Acesso

```
👤 AGENTE DE CAMPO
   ├─ ✅ Ver pessoas SUA ZONA
   ├─ ✅ Cadastrar beneficiários
   ├─ ✅ Ver seu próprio desempenho
   ├─ ✅ Enviar dados de campo
   ├─ ❌ Editar formações de outros agentes
   ├─ ❌ Acessar Dashboard executivo
   └─ ❌ Deletar dados

👥 GESTOR DE POLO
   ├─ ✅ Ver todos os beneficiários DESSE POLO
   ├─ ✅ Acompanhar agentes
   ├─ ✅ Gerar relatórios da unidade
   ├─ ✅ Aprovar/rejeitar processo
   ├─ ❌ Ver dados de outro POLO
   ├─ ❌ Deletar usuários
   └─ ❌ Mexer em papéis

👔 EXECUTIVO
   ├─ ✅ Ver TUDO consolidado
   ├─ ✅ Gerar qualquer relatório
   ├─ ✅ Acompanhar todas as unidades
   ├─ ✅ Acessar análises cruzadas
   ├─ ✅ Criar alertas e metas
   ├─ ✅ Gerenciar usuários
   ├─ ✅ Ver auditoria completa
   └─ ✅ Deletar dados (com confirmação)
```

---

## 📊 ESQUEMA VISUAL: Como Tudo Se Conecta

```
                      ┌─────────────────┐
                      │   📱 MOBILE APP │
                      │  (Campo, Offline)│
                      └────────┬────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │  ⚡ API BACKEND │
                      │    (FastAPI)     │
                      └────────┬────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
    ┌─────────┐        ┌────────────┐        ┌──────────┐
    │ 🌐 WEB  │        │ 👔 GABINETE │       │ 🏢 POLOS │
    │  APP    │        │   DASHBOARD │       │  MODULE  │
    └────┬────┘        └────┬───────┘        └──────────┘
         │                  │                      │
         └──────────────────┼──────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         ┌────▼──────┐            ┌──────▼────┐
         │ 10 MÓDULOS│ ◄────────► │   📊 BD   │
         │ DE LÓGICA │ (CRUD ops) │PostgreSQL │
         └───────────┘            └───────────┘
         
    ├─ IAM (Segurança)
    ├─ CABINET (Executivos)
    ├─ POLO (Unidades)
    ├─ PERSON (Pessoas)
    ├─ TERRITORY (Geography)
    ├─ RELATIONSHIP (Vínculos)
    ├─ MOBILE (Campo)
    ├─ WORKFLOW (Processos)
    ├─ ANALYTICS (Relatórios)
    └─ ADMINISTRATION (Gestão)
```

---

## 🚀 FLUXO DE DADOS: Um Vale para Uma Beneficiária

```
PASSO 1: AGENTE COLETA
┌──────────────────────────────┐
│ Agente abre app no celular   │
│ Cadastra: Maria (beneficiária)
│ Sem internet? Salva localmente│
└───────────┬──────────────────┘
            │
            ▼
PASSO 2: SINCRONIZAÇÃO
┌──────────────────────────────┐
│ Agente volta ao escritório   │
│ Conecta WiFi                 │
│ App sincroniza automaticamente│
│ Envia: {name, cpf, data}     │
└───────────┬──────────────────┘
            │
            ▼
PASSO 3: API VALIDA
┌──────────────────────────────┐
│ FastAPI recebe os dados      │
│ Verifica: CPF válido?        │
│ Verifica: Agente autorizado? │
│ Verifica: Dados completos?   │
└───────────┬──────────────────┘
            │
            ▼
PASSO 4: MÓDULOS PROCESSAM
┌──────────────────────────────┐
│ ✅ PERSON module:            │
│    Cria registro de Maria    │
│    ID gerado: uuid-12345     │
│                              │
│ ✅ TERRITORY module:         │
│    Registra localização      │
│                              │
│ ✅ MOBILE module:            │
│    Marca como sincronizado   │
│                              │
│ ✅ WORKFLOW module:          │
│    Inicia "Elegibilidade"    │
│                              │
│ ✅ ANALYTICS module:         │
│    Total beneficiários: +1   │
└───────────┬──────────────────┘
            │
            ▼
PASSO 5: BANCO ARMAZENA
┌──────────────────────────────┐
│ PostgreSQL salva:            │
│ ├─ person.beneficiary_maria  │
│ ├─ territory.location_xyz    │
│ ├─ workflow.case_123         │
│ └─ analytics.monthly_count   │
│ (Com backup automático)      │
└───────────┬──────────────────┘
            │
            ▼
PASSO 6: GESTOR VIRA
┌──────────────────────────────┐
│ Gestor acessa WEB APP        │
│ Busca: Maria                 │
│ Vê TODOS os dados coletados  │
│ Abre processo de análise     │
└───────────┬──────────────────┘
            │
            ▼
PASSO 7: EXECUTIVO ACOMPANHA
┌──────────────────────────────┐
│ Executivo no GABINETE        │
│ Dashboard mostra:            │
│ ├─ Novos cadastrados         │
│ ├─ Elegibilidade: 68%        │
│ ├─ Desempenho por unidade    │
│ └─ Tendências (seta ↗)       │
└──────────────────────────────┘
```

---

## ✨ Resumo da Modularização

| Módulo | Função Principal | Quem Usa | Dados Principais |
|--------|------------------|----------|-----------------|
| **IAM** | Controlar acesso | Todos | Usuários, papéis, permissões |
| **CABINET** | Dashboard executivo | Diretores | KPIs, indicadores |
| **POLO** | Gerenciar unidades | Gestores | Agentes, calendários |
| **PERSON** | Beneficiários | Todos | Nome, CPF, contato |
| **TERRITORY** | Organização geográfica | Agentes | Zonas, localização |
| **RELATIONSHIP** | Vínculos familiares | Gestores | Pai, mãe, filhos |
| **MOBILE** | Alimenta app | Agentes | Cadastros, sincronização |
| **WORKFLOW** | Processos | Gestores | Etapas, aprovações |
| **ANALYTICS** | Relatórios | Todos | Métricas, gráficos |
| **ADMINISTRATION** | Governança | Admin | Logs, auditoria |

---

## 🎓 Conclusão

REVISA é um **sistema integrado e modular** porque:

✅ **Cada módulo é independente** = fácil de manter e atualizar  
✅ **Mas todos se conectam** = dados fluem sem problemas  
✅ **Cada app vê o que precisa** = fácil de usar  
✅ **Os dados ficam sincronizados** = ninguém vê informação desatualizada  
✅ **Funciona offline + online** = agente em campo não fica preso  
✅ **Segurança em camadas** = cada um vê só o que pode  

É como um **hospital moderno**:

- 👨‍⚕️ **Médico** (agente) coleta sintomas (app mobile)
- 👼 **Enfermeiro** (gestor) organiza internações (web app)
- 🏥 **Diretor** (executivo) vê estatísticas de ocupação (gabinete)
- 💾 **Prontuário eletrônico** (PostgreSQL) centraliza tudo
- 📞 **Comunicação** (API) conecta todos

---

> Dúvidas? Cada módulo pode ser explicado em mais detalhes! 🎯
