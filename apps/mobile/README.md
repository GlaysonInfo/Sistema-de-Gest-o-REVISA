# REVISA Mobile App

**Progressive Web App (PWA)** para captação de dados em campo, com suporte **offline** e sincronização automática.

---

## 🚀 Iniciar Rápido

```bash
# Opção 1: Python SimpleHTTPServer (desenvolvimento)
python -m http.server 5176 --bind 127.0.0.1

# Opção 2: Node http-server
npx http-server . -p 5176

# Opção 3: Docker (com todo o stack)
docker-compose up
```

Acesse: **http://127.0.0.1:5176/**

---

## 📱 Instalar no Celular

### Android
1. Abra em **Chrome**
2. Menu (3 pontos) → **"Instalar app"**
3. Confirme

### iOS
1. Abra em **Safari**
2. Compartilhar (caixa com seta) → **"Adicionar à Tela Inicial"**
3. Confirme

👉 **Veja [GUIA_INSTALACAO_TESTE.md](GUIA_INSTALACAO_TESTE.md) para detalhes**

---

## 📂 Arquivos

```
apps/mobile/
├── index.html              # Interface HTML (com PWA meta tags)
├── app.js                  # Lógica da aplicação (150+ linhas)
├── styles.css              # Estilos responsivos
├── sw.js                   # Service Worker (cache + offline)
├── manifest.json           # Configuração PWA
├── assets/
│   └── logo-revisa.png     # Logo (adicionar icons: 192x512px)
├── GUIA_INSTALACAO_TESTE.md          # Como instalar e testar
└── SETUP_TECNICO_DEPLOYMENT.md       # Config técnica e deploy
```

---

## 🔐 Credenciais de Teste

```
Usuário: admin
Senha: Admin@123
API: http://127.0.0.1:8001
```

---

## ✨ Funcionalidades

✅ Login seguro (JWT)  
✅ Cadastro de beneficiário  
✅ Perfil político (liderança, engajamento)  
✅ Geração de demandas automáticas  
✅ Timeline da jornada do cadastro  
✅ Offline support (com Service Worker)  
✅ Sincronização automática  
✅ Interface responsiva (mobile-first)  

---

## 🧪 Testes

```bash
# Lighthouse (Chrome DevTools)
1. F12 → Lighthouse
2. Gerar relatório
3. Verificar PWA score > 90

# Offline Test
1. F12 → Network → Offline
2. Usar app normalmente
3. Dados devem ser salvos localmente

# Cross-device
1. Android + Chrome ✓
2. iOS + Safari ✓
3. Tablet portrait/landscape ✓
```

👉 **Veja [SETUP_TECNICO_DEPLOYMENT.md](SETUP_TECNICO_DEPLOYMENT.md) para checklist completo**

---

## 🚀 Deploy em Produção

```bash
# Com Docker
docker-compose -f docker-compose.prod.yml up -d

# Com Nginx + SSL
# (Ver SETUP_TECNICO_DEPLOYMENT.md)
```

---

## 📞 Suporte

- 📧 support@revisa.com.br
- 📱 +55 11 98765-4321
- 🕐 Seg-Sex 9h-18h

---

**Versão:** 1.0 | **Status:** 🟢 Pronto | **Data:** 14/04/2026
