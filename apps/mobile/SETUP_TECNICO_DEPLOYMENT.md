# REVISA Mobile - Setup Técnico e Deployment

---

## 📋 Checklist de Setup

### ✅ Backend Requirements

- [ ] Node.js 18+ ou Python 3.11+
- [ ] PostgreSQL 16
- [ ] Redis (opcional, para cache)
- [ ] HTTPS (self-signed OK para dev)

### ✅ Servidor Web

```bash
# Via Python SimpleHTTPServer (desenvolvimento)
cd apps/mobile
python -m http.server 5176 --bind 127.0.0.1

# Via Docker (recomendado)
docker-compose up
```

### ✅ Service Worker

- [x] `sw.js` registrado no `index.html`
- [x] Cache strategy: Cache-First (assets) + Network-First (API)
- [x] Offline fallback: JSON response com mensagem
- [x] Background sync hooks (pronto para implementação)

### ✅ PWA Features

- [x] `manifest.json` com icons, shortcuts, screenshots
- [x] Meta tags para iOS (apple-mobile-web-app-capable)
- [x] Meta tags para Android (mobile-web-app-capable)
- [x] Theme color (#2d7b8f)
- [x] Viewport settings (viewport-fit=cover para notch)

---

## 🔧 Configurações Importantes

### CORS (Se API em domínio diferente)

**API backend `app.py` ou `main.py`:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5176", "https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### HTTPS Redirect (Produção)

**Nginx (recomendado):**

```nginx
server {
    listen 80;
    server_name seu-dominio.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com.br;
    
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com.br/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5176;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Node/Express Alternative

```javascript
const express = require('express');
const https = require('https');
const fs = require('fs');

const app = express();
app.use(express.static('apps/mobile'));

https.createServer({
  key: fs.readFileSync('privkey.pem'),
  cert: fs.readFileSync('fullchain.pem')
}, app).listen(443);
```

---

## 🎨 Assets Necessários

Criar arquivos em `apps/mobile/assets/`:

```
assets/
├── logo-revisa.png          (já existe)
├── icon-192.png             (192x192, PNG color)
├── icon-512.png             (512x512, PNG color)
├── icon-maskable-192.png    (192x192, PNG maskable - Android adaptive)
├── icon-maskable-512.png    (512x512, PNG maskable)
├── icon-96.png              (96x96, para shortcuts)
├── screenshot-1.png         (540x720, tela login)
├── screenshot-2.png         (540x720, tela cadastro)
└── favicon.ico              (opcional)
```

### Gerar Icons Automaticamente

```bash
# Usar ImageMagick
convert logo-revisa.png -resize 192x192 icon-192.png
convert logo-revisa.png -resize 512x512 icon-512.png
convert logo-revisa.png -resize 96x96 icon-96.png

# Ou usar online: https://realfavicongenerator.net/
```

---

## 🧪 Testing Checklist

### Performance

- [ ] Lighthouse Score: 90+ (PWA)
- [ ] First Contentful Paint (FCP): < 2s
- [ ] Largest Contentful Paint (LCP): < 2.5s
- [ ] Cumulative Layout Shift (CLS): < 0.1
- [ ] Total Bundle Size: < 500KB

### Offline Testing

```javascript
// DevTools → Application → Service Workers
// Marcar "Offline" e testar:
- [ ] App carrega
- [ ] Login falha com mensagem clara
- [ ] Formulário abre mas mostra aviso "offline"
- [ ] SW cache está funcionando
```

### Device Testing

- [ ] Android 8+: Chrome, Firefox, Samsung Internet
- [ ] iOS 12+: Safari
- [ ] Tablet (iPad, Samsung Tab)
- [ ] Landscape orientation
- [ ] Notch handling (viewport-fit=cover)
- [ ] Dark mode support

### API Integration

- [ ] Login ✓
- [ ] Load context ✓
- [ ] Create person ✓
- [ ] Create capture ✓
- [ ] Create relationship ✓
- [ ] Offline queue (WIP)
- [ ] Sync pending (WIP)

---

## 📱 Install Verification

### Android Chrome

```
1. Open DevTools (F12)
2. Application → Manifest
   - Verify manifest.json valid
   - Check icons load
   - Check theme color
3. Application → Service Workers
   - Verify sw.js registered
   - Check "Update on reload"
4. Chrome Menu → "Install app"
   - Should appear if PWA valid
```

### iOS Safari

```
1. Safari → Gear icon → Settings
2. Scroll to "REVISA Mobile" if installed
3. Share → "Add to Home Screen"
   - Icon should appear on home screen
```

---

## 🚀 Docker Deployment

### Production docker-compose.yml

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: revisa_prod
      POSTGRES_USER: revisa_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U revisa_user"]
      interval: 10s
      timeout: 5s
      retries: 10

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://revisa_user:${DB_PASSWORD}@postgres:5432/revisa_prod
      ENVIRONMENT: production
    ports:
      - "8001:8000"
    depends_on:
      postgres:
        condition: service_healthy
    restart: always

  mobile:
    image: nginx:alpine
    volumes:
      - ./apps/mobile:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ${SSL_CERT}:/etc/nginx/certs/fullchain.pem:ro
      - ${SSL_KEY}:/etc/nginx/certs/privkey.pem:ro
    ports:
      - "443:443"
      - "80:80"
    depends_on:
      - api
    restart: always

volumes:
  postgres_data:
```

### Nginx Config (nginx.conf)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;
    gzip on;
    gzip_types text/plain text/css application/json;

    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;

        root /usr/share/nginx/html;
        index index.html;

        # PWA - Cache busting for index.html
        location = /index.html {
            add_header Cache-Control "max-age=0, no-cache, no-store, must-revalidate";
        }

        # Static assets - Long cache
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            add_header Cache-Control "max-age=31536000, immutable";
        }

        # Service worker - No cache
        location = /sw.js {
            add_header Cache-Control "max-age=0, no-cache, no-store, must-revalidate";
        }

        # Manifest - Short cache
        location = /manifest.json {
            add_header Cache-Control "max-age=3600";
        }

        # API proxy
        location /api/ {
            proxy_pass http://api:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # SPA routing - serve index.html for all non-existent routes
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 📊 Monitoring

### Metrics to Track

- [ ] PWA Install Rate
- [ ] API Response Time (avg < 200ms)
- [ ] Cache Hit Rate (target: > 80%)
- [ ] Offline Usage % (how often users go offline)
- [ ] Sync Success Rate (after online)
- [ ] Crash Rate (error logging)

### Error Tracking (Sentry example)

```javascript
// Add to app.js
import * as Sentry from "@sentry/browser";

Sentry.init({
  dsn: "https://xxx@xxx.ingest.sentry.io/xxx",
  environment: "production",
  tracesSampleRate: 0.1,
});
```

---

## 🔐 Security Checklist

- [ ] CSP (Content Security Policy) configured
- [ ] CORS properly restricted (not *)
- [ ] HTTPS enforced (no HTTP in prod)
- [ ] JWT tokens validated on API
- [ ] Sensitive data NOT in localStorage (use httpOnly if possible)
- [ ] API rate limiting enabled
- [ ] SQL injection tests passed
- [ ] XSS tests passed
- [ ] CSRF protection active (if forms)

---

## 📈 Performance Optimization

### Assets

```bash
# Minify JS and CSS
npm install -D esbuild minify
esbuild app.js --bundle --minify --outfile=app.min.js

# Optimize images
imagemin assets/ --out-dir=assets-optimized
```

### Caching Strategy

```javascript
// In sw.js: Already implemented
- Cache-First: Static assets (CSS, JS, images)
- Network-First: API calls with cache fallback
- Stale-While-Revalidate: (optional) serve cache, update in background
```

---

## 🎯 Ready for Production

**Checklist before launch:**

- [ ] All browser console errors resolved
- [ ] Service Worker properly caching
- [ ] Icons and manifest validated
- [ ] HTTPS certificate active
- [ ] API CORS configured
- [ ] Database backed up
- [ ] Error logging active (Sentry/etc)
- [ ] Lighthouse score > 90
- [ ] Cross-device testing complete
- [ ] Documentation updated
- [ ] Support team trained

---

**Última atualização:** 14 de Abril de 2026  
**Status:** ✅ Pronto para Deploy
