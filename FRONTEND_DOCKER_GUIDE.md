# Frontend Docker Rehberi

## 🤔 Frontend için Docker Gerekli mi?

**Kısa cevap**: **Hayır, zorunlu değil** ama **önerilir** (özellikle production için).

---

## 📊 Senaryolar ve Öneriler

### Senaryo 1: Development (Geliştirme) 🛠️

#### ❌ Docker Gerekmez
- Frontend developer'lar kendi bilgisayarlarında çalışabilir
- `npm install` veya `yarn install` yeterli
- Hot reload ile hızlı geliştirme

**Avantajları:**
- ✅ Daha hızlı development
- ✅ Daha az kaynak kullanımı
- ✅ Daha kolay debugging

**Dezavantajları:**
- ❌ Farklı Node.js versiyonları sorun çıkarabilir
- ❌ "Benim bilgisayarımda çalışıyor" problemi

#### ✅ Docker Kullanılırsa
- Tutarlı development ortamı
- Tüm ekip aynı Node.js versiyonunu kullanır
- `docker-compose up` ile tüm proje çalışır

---

### Senaryo 2: Production (Canlıya Alma) 🚀

#### ✅ Docker Önerilir
- Tutarlı deployment
- Kolay scaling
- Nginx ile static file serving

---

## 🎯 Projeniz İçin Öneri

### Mevcut Durum
- **Backend**: Django (Docker ile çalışıyor ✅)
- **Frontend**: HTML5, CSS3, JavaScript, HTMX, PrimeNG, Tailwind CSS
- **Frontend tipi**: Static site (SPA değil, server-side rendering yok)

### Öneri: **İki Seçenek**

---

## Seçenek 1: Docker Kullanmadan (Basit) ⚡

### Avantajlar
- ✅ Daha basit setup
- ✅ Frontend developer'lar için daha kolay
- ✅ Hızlı development

### Nasıl Çalışır?
```bash
# Backend (Docker ile)
cd backend
docker-compose up -d

# Frontend (Doğrudan)
cd frontend
npm install
npm run dev  # veya npm start
```

### CORS Ayarları
Backend'de CORS ayarları frontend'in çalıştığı portu içermeli:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Vite
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # Diğer portlar
]
```

---

## Seçenek 2: Docker ile (Önerilen) 🐳

### Avantajlar
- ✅ Tutarlı development ortamı
- ✅ Tek komutla tüm proje çalışır
- ✅ Production'a benzer ortam
- ✅ Kolay deployment

### Docker Compose Yapısı

#### Örnek: `docker-compose.yml` (Root seviyesinde)

```yaml
services:
  # Backend (Mevcut)
  postgres:
    image: postgres:16-alpine
    container_name: filmosphere_postgres
    environment:
      POSTGRES_USER: filmouser
      POSTGRES_PASSWORD: filmopass
      POSTGRES_DB: filmosphere
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U filmouser"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: ./backend
    container_name: filmosphere_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=postgres://filmouser:filmopass@postgres:5432/filmosphere
      - DJANGO_DEBUG=True
    depends_on:
      postgres:
        condition: service_healthy

  # Frontend (Yeni)
  frontend:
    build: ./frontend
    container_name: filmosphere_frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules  # node_modules'ü container içinde tut
    ports:
      - "3000:3000"  # veya 5173:5173 (Vite için)
    environment:
      - REACT_APP_API_URL=http://localhost:8000  # Backend URL
      - NODE_ENV=development
    depends_on:
      - web
    command: npm run dev  # Development için

volumes:
  postgres_data:
```

#### Frontend Dockerfile Örneği

**`frontend/Dockerfile`** (Development için):
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose port
EXPOSE 3000

# Development command (hot reload)
CMD ["npm", "run", "dev"]
```

**`frontend/Dockerfile.prod`** (Production için):
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production: Nginx ile serve et
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🎯 Benim Önerim

### Development için: **Docker Kullanmayın** ❌
- Frontend developer'lar için daha kolay
- Hot reload daha hızlı
- Daha az karmaşık

### Production için: **Docker Kullanın** ✅
- Tutarlı deployment
- Kolay scaling
- Nginx ile static file serving

---

## 📝 Pratik Çözüm: Hybrid Yaklaşım

### Development
```bash
# Backend Docker ile
cd backend
docker-compose up -d

# Frontend doğrudan
cd frontend
npm install
npm run dev
```

### Production
```bash
# Tüm proje Docker ile
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 Frontend Dockerfile Örneği (İhtiyaç Duyarsanız)

Eğer frontend için Docker kullanmak isterseniz, şu yapıyı kullanabilirsiniz:

### 1. `frontend/Dockerfile` (Development)
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose port (Vite default: 5173, React: 3000)
EXPOSE 5173

# Development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### 2. `frontend/.dockerignore`
```
node_modules
dist
build
.env.local
.git
```

### 3. Backend `docker-compose.yml`'e Ekleme
```yaml
  frontend:
    build: ./frontend
    container_name: filmosphere_frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - web
```

---

## ✅ Sonuç

**Sizin durumunuz için:**
1. **Development**: Docker gerekmez, doğrudan çalıştırın
2. **Production**: Docker kullanın (Nginx ile static serving)

**Basit başlangıç için:**
- Backend: Docker ✅ (Zaten var)
- Frontend: Docker yok ❌ (Gerekli değil)

**İleride production için:**
- Frontend için Docker ekleyebilirsiniz

---

## 🚀 Hızlı Başlangıç (Docker Olmadan)

```bash
# 1. Backend'i başlat
cd backend
docker-compose up -d

# 2. Frontend'i başlat (başka terminal)
cd frontend
npm install
npm run dev

# 3. Tarayıcıda aç
# http://localhost:3000 (veya 5173)
```

---

## 📚 Ek Kaynaklar

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Static File Serving](https://nginx.org/en/docs/http/ngx_http_core_module.html)
- [Vite Docker Guide](https://vitejs.dev/guide/static-deploy.html)



