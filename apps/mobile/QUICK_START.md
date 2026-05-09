# REVISA Mobile - Começar Hoje 🚀

Seu **aplicativo mobile para capturar dados em campo** está pronto!

---

## 🔧 Pré-requisito Único

Estar na **mesma rede que o servidor**. Se servidor está em:
- **`192.168.1.100`** → celular também deve estar nessa rede

---

## 📱 Em 3 Passos

### 1️⃣ Abrir no Navegador

Acesse no seu celular:

```
http://[IP_DO_SERVIDOR]:5176/
```

**Exemplo:**
- Se servidor é `192.168.1.100` → abra `http://192.168.1.100:5176/`
- Se servidor é local `127.0.0.1` → abra `http://127.0.0.1:5176/`

### 2️⃣ Fazer Login

```
👤 Usuário: admin
🔐 Senha: Admin@123
```

Clique em **"Checar API"** (deve ficar **verde**)

### 3️⃣ Instalar como App

**Android (Chrome):**
- Toque nos **3 pontos** (top-right)
- Selecione **"Instalar app"**
- Confirme

**iOS (Safari):**
- Toque no ícone **Compartilhar** (bottom)
- Selecione **"Adicionar à Tela Inicial"**
- Confirme

💡 **Pronto!** Agora tem um ícone na sua tela inicial.

---

## 📝 Usar o App

1. **Novo Cadastro**
   - Escolher modo (Beneficiário ou Político)
   - Preencher campos
   - Clique **"Registrar cadastro"**

2. **Classificação (Político)**
   - Após cadastro, classifique a pessoa
   - Nível: Contato, Participante, Apoiador, Liderança, Voto Certo
   - Engajamento: Frio, Médio, Forte

3. **Offline**
   - O app funciona sem internet!
   - Dados são salvos localmente
   - Sincronizados automaticamente quando volta online

---

## 🆘 Problemas?

### "API offline" (vermelho)

**Solução:**
1. Verifique o IP: `ipconfig` (Windows) ou `ifconfig` (Mac/Linux)
2. Digite o IP correto no campo API (ex: `http://192.168.1.100:8001`)
3. Enxote em **"Checar API"** novamente

### Login não funciona

**Solução:**
1. Confirme credenciais (admin / Admin@123)
2. Verifique se a API está rodando (deve estar)
3. Limpe cache do navegador

### App não instala

**Solução:**
1. Android: Usa **Chrome**, não Firefox/Safari
2. iOS: Usa **Safari**, não Chrome
3. Recarregue a página (F5)

---

## 📞 Suporte

Dúvidas? Contate:
- 📧 support@revisa.com.br
- 📱 +55 11 98765-4321

---

## 📚 Mais Informações

- **Instalação detalhada:** [GUIA_INSTALACAO_TESTE.md](GUIA_INSTALACAO_TESTE.md)
- **QA Checklist:** [QA_CHECKLIST.md](QA_CHECKLIST.md)
- **Config técnica:** [SETUP_TECNICO_DEPLOYMENT.md](SETUP_TECNICO_DEPLOYMENT.md)

---

**Versão:** 1.0 | **Data:** 14/04/2026 | **Status:** ✅ Pronto
