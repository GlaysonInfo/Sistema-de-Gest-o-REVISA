# REVISA Mobile - QA Testing Checklist

**Data:** ___/___/2026  
**Testador:** _______________________  
**Dispositivo:** ___________________  
**SO/Navegador:** ___________________

---

## 🔐 Login & Authentication

- [ ] **Campo API**
  - [ ] Aceita URL com protocolo (http://)
  - [ ] Aceita IP (192.168.1.100)
  - [ ] Remove trailing slash automaticamente
  - [ ] Restaura último IP ao recarregar página

- [ ] **Botão "Checar API"**
  - [ ] Verde/online se API responde
  - [ ] Vermelho/offline se API sem resposta
  - [ ] Mensagem clara ao usuário
  - [ ] Responde em < 5 segundos

- [ ] **Login**
  - [ ] Aceita admin / Admin@123
  - [ ] Rejeita credenciais inválidas com erro
  - [ ] Armazena token no LocalStorage
  - [ ] Token enviado em Authorization header

- [ ] **Recuperação de sessão**
  - [ ] Reload da página mantém token
  - [ ] Token expirado força novo login
  - [ ] Logout limpa token

---

## 📥 Carregamento de Contexto

- [ ] **Botão "Carregar Contexto"**
  - [ ] Faz requisição GET /api/v1/cabinets e /api/v1/polos
  - [ ] Mostra "Carregando..." enquanto processa
  - [ ] Preench campos: Polo, Gabinete, Destino
  - [ ] Funciona offline se dados foram carregados antes

- [ ] **Métricas exibidas**
  - [ ] "Destino": não modificável, informativo
  - [ ] "Polo": mostra nome do polo selecionado
  - [ ] "Gabinete": mostra nome do gabinete/vereador

---

## 📝 Formulário de Cadastro

### Seleção de Modo

- [ ] **Modo "Beneficiário do Polo"**
  - [ ] Radio button funciona
  - [ ] Mostra campo "Polo ID"
  - [ ] AutoFill com dados do contexto

- [ ] **Modo "Perfil Político"**
  - [ ] Radio button funciona
  - [ ] Esconde campo "Polo ID"
  - [ ] Mantém outros campos visíveis

### Campos Obrigatórios (Validação)

- [ ] **Nome Completo**
  - [ ] Obrigatório (erro se vazio)
  - [ ] Aceita até 255 caracteres
  - [ ] Caracteres especiais funcionam (acentos, etc)

- [ ] **Telefone**
  - [ ] Obrigatório (erro se vazio)
  - [ ] Aceita format (11970000001 ou +551197000001)
  - [ ] Máscara aplica automaticamente?

- [ ] **Bairro**
  - [ ] Obrigatório (erro se vazio)
  - [ ] Aceita até 100 caracteres
  - [ ] Autocomplete se houver dados históricos?

- [ ] **CPF** (Opcional)
  - [ ] Validação de CPF (11 dígitos)
  - [ ] Erro se menos de 11 digitos
  - [ ] Único na base? (conflito checa?)

- [ ] **Email** (Opcional)
  - [ ] Validação de email (formato correto)
  - [ ] Erro se formato inválido
  - [ ] Único na base?

- [ ] **Data de Nascimento**
  - [ ] Calendário picker funciona
  - [ ] Aceita datas válidas
  - [ ] Rejeita data futura
  - [ ] Calcula idade automaticamente?

- [ ] **Gênero**
  - [ ] Dropdown exibe opções (Não informado, Feminino, Masculino, Outro)
  - [ ] Seleção persiste ao navegar

- [ ] **Prioridade**
  - [ ] Dropdown: Baixa, Média, Alta
  - [ ] Default: Média
  - [ ] Afeta retorno/workflow?

### Campos Condicionais

- [ ] **Organization ID**
  - [ ] Se branco, obtém de contexto
  - [ ] Se preenchido, validação UUID?
  - [ ] Tooltip explicando formato?

- [ ] **Vereador ID**
  - [ ] Se branco, obtém de contexto (polo.vereador_id)
  - [ ] UUID válido

- [ ] **Polo ID** (Se Beneficiário do Polo)
  - [ ] Se branco, obtém de contexto
  - [ ] Obrigatório neste modo
  - [ ] UUID válido

- [ ] **Create Demand**
  - [ ] Checkbox funciona
  - [ ] Default: checked
  - [ ] Se checked, cria demand automaticamente

### Notas/Observações

- [ ] **Observação de Campo**
  - [ ] Textarea aceita múltiplas linhas
  - [ ] Preserva quebras de linha no envio
  - [ ] Character counter? (opcional)

---

## 📤 Envio de Cadastro

- [ ] **Validação Pré-envio**
  - [ ] Avisa se campos obrigatórios vazio
  - [ ] Avisa se CPF/Email inválido
  - [ ] Avisa se IDs não são UUIDs válidos

- [ ] **Envio (POST /api/v1/mobile/intake)**
  - [ ] Request contém todos os campos
  - [ ] Response retorna novo ID de pessoa
  - [ ] Mostra sucesso visual (verde)
  - [ ] Desabilita botão enquanto envia? (feedback)

- [ ] **Erro no Envio**
  - [ ] Retorna erro validação com campo específico
  - [ ] Mostra mensagem clara (não JSON puro)
  - [ ] Permite corrigir e tentar novamente

- [ ] **Timeline Atualiza**
  - [ ] Após sucesso, aparece entrada em "Timeline"
  - [ ] Mostra timestamp do cadastro
  - [ ] Mostra dados da pessoa criada
  - [ ] Link para ver detalhes?

---

## 🏷️ Classificação Política

- [ ] **Nível de Relacionamento**
  - [ ] Dropdown: Contato, Participante, Apoiador, Liderança, Voto Certo
  - [ ] Padrão: Contato?
  - [ ] Obrigatório?

- [ ] **Engajamento**
  - [ ] Dropdown: Frio, Médio, Forte
  - [ ] Padrão: Médio?
  - [ ] Obrigatório?

- [ ] **Observação Interna**
  - [ ] Textarea aceita múltiplas linhas
  - [ ] Optional field
  - [ ] Visível apenas em contexto privado?

- [ ] **Botão "Classificar Pessoa"**
  - [ ] Validação: require person ID (após cadastro)
  - [ ] Envio POST para criar relationship
  - [ ] Sucesso: mostra feedback verde
  - [ ] Erro: mensagem clara

- [ ] **Botão "Marcar Liderança"** (secundário)
  - [ ] Ativa relacionamento com nível=LIDERANÇA
  - [ ] Shortcut para classification comum
  - [ ] Feedback visual diferenciado

---

## 📊 Timeline & Histórico

- [ ] **Seção Timeline**
  - [ ] Apareçe após primeiro cadastro
  - [ ] Mostra lista de eventos
  - [ ] Organizados cronologicamente (mais recente no topo)?
  - [ ] Cada item mostra:
    - [ ] Tipo de evento (cadastro, demand, relationship)
    - [ ] Timestamp
    - [ ] Dados resumidos

- [ ] **Clicabilidade**
  - [ ] Timeline items são clicáveis? (expande detalhes)
  - [ ] Exibe JSON completo? (se dev mode)

---

## 🔌 Modo Offline

### Setup

1. **Verificar Initial Load**
   - [ ] Offline (Ctrl+Shift+K ou F12 → Network → Offline)
   - [ ] Página carrega normalmente (index.html do cache)

2. **Service Worker**
   - [ ] F12 → Application → Service Workers
   - [ ] Mostra "revisa-mobile-v1" ativado
   - [ ] Status: "running"

3. **Testes Offline**

- [ ] **Login é bloqueado**
  - [ ] "Checar API" retorna offline/vermelho
  - [ ] Tentativa de login mostra erro: "sem conexão"
  - [ ] Toast message clara

- [ ] **Se já logado, dados persistem**
  - [ ] Token mantido em localStorage
  - [ ] Contexto (polos/gabinetes) visível
  - [ ] Últimos dados carregados exibidos

- [ ] **Formulário funciona**
  - [ ] Pode preencher campos offline
  - [ ] Validação frontend funciona
  - [ ] Clique "Registrar" mostra aviso: "offline, dados salvos localmente"

- [ ] **Armazenamento Local**
  - [ ] Dados salvos em IndexedDB ou localStorage
  - [ ] F12 → Application → Storage
  - [ ] Ver dados armazenados
  - [ ] Confirmação visual que está offline

### Volta Online

4. **Reconexão**
   - [ ] Desabilitar modo offline
   - [ ] App detecta reconexão automaticamente
   - [ ] Toast message: "Sincronizando dados..."
   - [ ] Dados pendentes são enviados
   - [ ] Timeline atualiza com novos cadastros

5. **Falha de Sincronização**
   - [ ] Se API está offline mas cliente online: erro claro
   - [ ] Fila persiste até reconexão bem-sucedida
   - [ ] Retry automático? (ou manual)

---

## 🎨 Responsividade & UX

### Layout

- [ ] **Orientação Portrait**
  - [ ] Todos campos visíveis
  - [ ] Labels acima dos inputs
  - [ ] Espaçamento confortável
  - [ ] Botões acessíveis

- [ ] **Orientação Landscape**
  - [ ] Layout adapta (2 colunas?)
  - [ ] Sem overflow desnecessário
  - [ ] Teclado virtual não obstrui campos críticos

- [ ] **Teclado Virtual (Mobile)**
  - [ ] Campo "Telefone" abre teclado numérico
  - [ ] Campo "Email" abre teclado com @
  - [ ] "Data de Nascimento" usa date picker
  - [ ] Dropdowns não são obstruídos

### Notch/Safe Area (iOS)

- [ ] **iPhone com notch**
  - [ ] Conteúdo não fica sob notch
  - [ ] Status bar visível
  - [ ] Viewport-fit=cover não causa problemas

### Acessibilidade

- [ ] **Labels & ARIA**
  - [ ] Todos inputs têm labels
  - [ ] Screen reader encontra fields
  - [ ] ARIA roles correct (form, navigation, etc)

- [ ] **Cores**
  - [ ] Contraste suficiente (branco sobre azul OK?)
  - [ ] Mensagens de erro não só coloridas, mas com ícone/texto
  - [ ] Daltonismo: cores secundárias funcionam?

- [ ] **Tab Navigation**
  - [ ] Tab order faz sentido
  - [ ] Pode navegar form com teclado
  - [ ] Botão visível ao focar

---

## ⚡ Performance

- [ ] **Tempo de Carga**
  - [ ] Página inicial carrega em < 3 segundos
  - [ ] Primeira interação em < 2 segundos
  - [ ] Smooth 60fps ao descer formulário?

- [ ] **Tamanho de Assets**
  - [ ] app.js: esperado ~50KB
  - [ ] styles.css: esperado ~20KB
  - [ ] Total bundle: < 500KB

- [ ] **Requisições de Rede**
  - [ ] Contador mostra número de requests
  - [ ] Sem requests duplicadas ao carregar contexto
  - [ ] API response time < 1 segundo

---

## 🔒 Segurança

- [ ] **Token JWT**
  - [ ] Token armazenado no localStorage
  - [ ] Enviado em Authorization header (`Bearer xxx`)
  - [ ] Não exposto em URLs
  - [ ] Não logado em console em produção

- [ ] **Validação de Entrada**
  - [ ] CPF/Email validados frontend
  - [ ] UUID validados se requerido
  - [ ] Sem SQL injection attempts (backend validation)
  - [ ] XSS: HTML no nome não é executado (escapado)

- [ ] **HTTPS (Produção)**
  - [ ] Não aceita HTTP em produção
  - [ ] CSP headers presentes (F12 → Network → Headers)
  - [ ] Certificado SSL válido

---

## 🎯 Integração com API

- [ ] **Endpoints Testados**
  - [ ] POST /api/v1/auth/login ✓
  - [ ] GET /api/v1/cabinets ✓
  - [ ] GET /api/v1/polos ✓
  - [ ] GET /api/v1/persons ✓
  - [ ] POST /api/v1/mobile/intake ✓ (persons + captures + beneficiary)
  - [ ] POST /api/v1/relationships (classification) ✓
  - [ ] GET /api/v1/demands (se necessário)

- [ ] **Respostas de Erro**
  - [ ] 401 Unauthorized: força novo login
  - [ ] 422 Validation: mostra erro específico do campo
  - [ ] 500 Server: avisa "tente novamente mais tarde"
  - [ ] Network error: avisa desconexão

---

## 📱 PWA Features

- [ ] **Manifest Válido**
  - [ ] F12 → Application → Manifest
  - [ ] Todas propriedades presentes e válidas
  - [ ] Icons listados existem
  - [ ] Theme color correto

- [ ] **Instalação**
  - [ ] Android Chrome: botão "Instalar" aparece
  - [ ] iOS Safari: "Adicionar à Tela" funciona
  - [ ] Ícone aparece na tela inicial
  - [ ] Label correto (REVISA)

- [ ] **Launch**
  - [ ] App abre em modo fullscreen
  - [ ] Sem barra de navegação/endereço visível
  - [ ] Retorna corretamente ao home screen
  - [ ] Última página carregada (se implementado)

---

## 🐛 Edge Cases & Bugs

### Deixar em Branco

- [ ] [ ] Campo obrigatório vazio → erro
- [ ] [ ] CPF vazio (opcional) → sem erro
- [ ] [ ] Email vazio (opcional) → sem erro
- [ ] [ ] Observações vazias → allowed

### Caracteres Especiais

- [ ] [ ] Nome: "João da Silva" OK
- [ ] [ ] Nome: "María García" OK
- [ ] [ ] Nome: "Ñandú" OK (se suportado)
- [ ] [ ] Observação: quebra de linhas mantidas
- [ ] [ ] Observação: caracteres unicode OK

### Limites

- [ ] [ ] Nome > 255 caracteres: rejeitado/truncado?
- [ ] [ ] Telefone com formato: "(11) 97000-0001" é aceito/convertido?
- [ ] [ ] CPF com mascara: "123.456.789-00" é aceito/convertido?

### Duplicação

- [ ] [ ] Submeter 2x rápido: impede duplicação
- [ ] [ ] Botão desabilitado enquanto envia
- [ ] [ ] Mesma pessoa 2x: permite ou avisa?

### Reload & Back Button

- [ ] [ ] F5 durante preenchimento: mantém dados?
- [ ] [ ] Back button no navegador: perdadados OK?
- [ ] [ ] F5 após sucesso: permite novo cadastro

---

## 📋 Resultado Final

### Passar/Falhar por Categoria

| Categoria | Status | Notas |
|-----------|--------|-------|
| Login | ☐ PASS / ☐ FAIL | ___ |
| Contexto | ☐ PASS / ☐ FAIL | ___ |
| Formulário | ☐ PASS / ☐ FAIL | ___ |
| Classificação | ☐ PASS / ☐ FAIL | ___ |
| Offline | ☐ PASS / ☐ FAIL | ___ |
| Performance | ☐ PASS / ☐ FAIL | ___ |
| PWA/Install | ☐ PASS / ☐ FAIL | ___ |
| **GERAL** | ☐ **APROVADO** / ☐ **REJEITAR** | ___ |

### Bugs Encontrados

1. **[Severidade]** Descrição  
   Passos: ...  
   Expected: ...  
   Actual: ...

2. ...

### Recomendações

- [ ] ...

---

**Testador:** _________________ **Data:** ___/___/_____

**Assinatura:** _________________________________
