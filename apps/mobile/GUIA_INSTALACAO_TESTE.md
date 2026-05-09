# REVISA Mobile - Guia de Instalação e Teste

**Versão:** 1.0  
**Data:** 14 de Abril de 2026  
**Status:** 🟢 Pronto para Teste do Cliente

---

## 📱 Sobre o REVISA Mobile

REVISA Mobile é uma **Progressive Web App (PWA)** que funciona como um aplicativo nativo em smartphones (iOS e Android) com suporte a **offline**, permitindo cadastramento de campo em áreas sem conexão.

### Características Principais

✅ **Instalação em 1 clique** (sem App Store/Play Store)  
✅ **Funciona offline** (sincroniza quando volta online)  
✅ **Sincronização automática** de dados  
✅ **Ícone na tela inicial** (como app nativo)  
✅ **Status bar customizado** (temática REVISA)  
✅ **Otimizado para câmera e localização** (futuro)  

---

## 🚀 Instalação em Android

### Via Chrome (Recomendado)

**Pré-requisitos:**
- Android 5.0 ou superior
- Google Chrome 47 ou superior

**Passos:**

1. **Abrir no Chrome**
   - Abra o navegador Chrome no celular
   - Acesse: `http://[SEU_IP]:5176/`
   - Aguarde a página carregar completamente

2. **Instalar como App**
   - Toque nos **3 pontos** (menu) no canto superior direito
   - Selecione **"Instalar app"** ou **"Adicionar à tela inicial"**
   - Confirme com **"Instalar"**
   - O app será adicionado à tela inicial automaticamente

3. **Abrir o App**
   - Localize o ícone **REVISA Mobile** na tela inicial
   - Toque para abrir
   - O app abrirá em **modo fullscreen** (sem barra de navegação do Chrome)

### Via Samsung Internet (Samsung devices)

Mesmo processo, mas usando o navegador Samsung Internet nativo.

---

## 🍎 Instalação em iOS

### Via Safari (Recomendado para iOS)

**Pré-requisitos:**
- iOS 11.3 ou superior
- Safari (padrão do iOS)

**Passos:**

1. **Abrir no Safari**
   - Abra o Safari no iPhone/iPad
   - Acesse: `http://[SEU_IP]:5176/`
   - Aguarde a página carregar completamente

2. **Adicionar à Tela Inicial**
   - Toque no ícone **Compartilhar** (caixa com seta) na barra inferior
   - Role para encontrar **"Adicionar à Tela Inicial"**
   - Toque em **"Adicionar à Tela Inicial"**
   - Modifique o nome se desejar (ex: "REVISA")
   - Toque em **"Adicionar"** no canto superior direito

3. **Abrir o App**
   - Volte à tela inicial
   - Localizar o ícone **REVISA**
   - Toque para abrir
   - Na primeira vez, mostrará a barra "Safari" por alguns segundos, depois desaparece

---

## 🌐 Acesso Web (Desktop/Tablet)

Se não quiser instalar como app, pode acessar diretamente no navegador:

**URLs de Acesso:**

| Serviço | URL | Descrição |
|---------|-----|-----------|
| REVISA Mobile | `http://127.0.0.1:5176/` | App mobile (PWA) |
| REVISA Web | `http://127.0.0.1:5175/` | Gestão central |
| API Docs | `http://127.0.0.1:8001/docs` | Documentação técnica |

---

## 🔐 Login e Credenciais

### Usuário de Teste

```
👤 Usuário: admin
🔐 Senha: Admin@123
```

### Primeira Vez

1. Na tela de login, o campo **API** vem preenchido com `http://127.0.0.1:8001`
2. Se acessando de outro celular na rede, altere para o IP da máquina:
   - **API:** `http://192.168.X.X:8001/` (IP da sua máquina)
3. Clique em **"Checar API"** para validar conexão
4. Clique em **"Entrar"** para fazer login
5. Clique em **"Carregar contexto"** para trazer dados de Polos e Gabinetes

---

## 📝 Teste da Aplicação

### Cenário 1: Cadastro Online (Com Internet)

1. **Login**: Efetue login com credenciais acima
2. **Contexto**: Carregue contexto (Polos, Gabinetes)
3. **Seleção de Modo**: Escolha **"Beneficiário do Polo"** ou **"Perfil Político"**
4. **Preenchimento**: Complete todos os campos
   - Nome completo
   - Telefone
   - CPF (opcional)
   - Data de nascimento
   - Gênero
   - Bairro
   - Prioridade
   - Email (opcional)
   - Observações
5. **Envio**: Clique em **"Registrar cadastro"**
6. **Validação**: Verifique se a resposta mostra sucesso (JSON com ID de pessoa)
7. **Timeline**: A jornada deve aparecer na seção "Histórico"
8. **Classificação**: (Opcional) Classifique a pessoa politicamente

### Cenário 2: Teste Offline

1. **Desativar Internet**
   - Ativar Modo Avião no celular OU
   - Permitir apenas Wi-Fi offline (desconectar da rede)

2. **Usar o App**
   - A interface continua funcionando normalmente
   - Mensagens de erro mostram "offline"
   - Os dados são armazenados localmente (IndexedDB/LocalStorage)

3. **Campo "Sincronização"**
   - Quando voltar online, o sistema deve sincronizar automaticamente
   - (Implementação futura de background sync)

### Cenário 3: Performance e UX

- **Navegação**: Todas as abas funcionam?
- **Campos obrigatórios**: Validação de CPF, email?
- **Responsividade**: O layout se adapta bem ao tamanho do celular?
- **Velocidade**: Carregam os dados rapidamente?
- **Erros**: Mensagens claras quando ocorrem?

---

## 🔧 Troubleshooting

### "API offline" na primeira tela

**Problema**: A API não responde ao clique em "Checar API"

**Solução**:
1. Verifique se o servidor backend está rodando: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8001`
2. Verifique se o celular está na mesma rede que o servidor
3. Altere o IP da API no campo (ex: `http://192.168.1.100:8001`)
4. Limpe o cache do navegador: Menu → Configurações → Limpar dados de navegação

### "Erro 422 - Validação"

**Problema**: Ao enviar cadastro, retorna erro de validação

**Solução**:
1. Certifique-se que todos os **campos obrigatórios** estão preenchidos:
   - Nome completo (obrigatório)
   - Telefone (obrigatório)
   - Bairro (obrigatório)
   - CPF: deve ser válido (11 dígitos) ou deixar em branco
   - Email: se preenchido, deve ser válido
2. Verifique os IDs de contexto (Organization, Vereador, Polo) se em branco

### "Salvo localmente" mas não sincroniza offline

**Problema**: Dados não sincronizam quando volta online

**Solução**:
- Esta é uma feature em desenvolvimento (background sync)
- Por enquanto, o usuário deve clicar em "Sincronizar" manualmente
- Refresh da página (`F5`) força sincronização

### App desaparece da tela inicial

**Problema**: O ícone do REVISA some depois de desinstalar

**Solução**: Se desinstalou, volte à URL e reinstale:
1. Acesse `http://127.0.0.1:5176/`
2. Menu (3 pontos) → "Instalar app"

---

## 📊 Relatório de Teste

Use este template para reportar achados:

```
REVISA Mobile - Relatório de Teste
Data: ___/___/2026
Testador: _______________________
Dispositivo: Android ___ / iOS ___
Navegador: Chrome / Safari / Samsung Internet

TESTES REALIZADOS:

☐ Instalação como app (sucesso?)
☐ Login (credenciais funcionam?)
☐ Carregamento de contexto (polos carregam?)
☐ Cadastro online (dados salvam?)
☐ Teste offline (app funciona sem internet?)
☐ Sincronização (dados sincronizam quando volta online?)
☐ Validação de campos (erros aparecem corretamente?)
☐ Performance (rápido/lento?)
☐ Usabilidade (interface clara?)

PROBLEMAS ENCONTRADOS:

1. Descrição: _________
   Passos para reproduzir: _________
   Severity: 🔴 Crítico / 🟠 Alto / 🟡 Médio / 🟢 Baixo

2. [...]

OBSERVAÇÕES GERAIS:

_________________________________________

Recomendações:
_________________________________________
```

---

## 🚀 Deploy em Produção

Quando estiver pronto para produção:

### 1. Obter Certificado SSL/TLS

PWA **requer HTTPS** em produção. Use Let's Encrypt gratuito:

```bash
certbot certonly --manual --preferred-challenges http -d seu-dominio.com.br
```

### 2. Atualizar API URL

No `index.html`, mudar:
```javascript
<input id="apiBase" value="http://127.0.0.1:8001" />
```

Para:
```javascript
<input id="apiBase" value="https://seu-dominio.com.br/api" />
```

Ou deixar sem domínio (servidor mesmo):
```javascript
<input id="apiBase" value="/api" />
```

### 3. Gerar Icons Corretamente

Substituir `assets/icon-*.png` com ícones reais:
- 192x192 px (normal)
- 512x512 px (splashscreen)
- 192x192 px maskable (Android adaptive icons)
- 512x512 px maskable (Android adaptive icons)

### 4. Screenshot para App Stores (Opcional)

Se quiser aparecer no Google Play:
- Screenshot 540x720 px (celular portrait)
- Nome: "screenshot-1.png", "screenshot-2.png"

### 5. Publicar Web App em Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📞 Suporte Técnico

Para dúvidas ou problemas:

**Equipe Técnica:**
- 📧 Email: support@revisa.com.br
- 📱 WhatsApp: +55 11 98765-4321
- 🕐 Horário: Seg-Sex, 9h-18h

**Para Reportar Bugs:**
1. Descreva o problema
2. Anexe screenshot
3. Especifique: dispositivo, SO, navegador, passos para reproduzir

---

## 📚 Recursos Adicionais

- [Documentação PWA - MDN](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/)
- [Manifest.json Spec](https://www.w3.org/TR/appmanifest/)
- [Service Workers - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Install - Google](https://developer.chrome.com/docs/web-platform/app-install-prompts/)

---

**Documento Preparado:** 14 de Abril de 2026  
**Versão:** 1.0 (Beta)  
**Status:** ✅ Pronto para Cliente Testar
