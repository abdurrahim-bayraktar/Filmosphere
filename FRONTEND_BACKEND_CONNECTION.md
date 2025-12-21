# Frontend-Backend Bağlantı Rehberi

## 🔗 Frontend Backend'e Nasıl Bağlanır?

**Önemli**: Frontend'in backend'e bağlanması için **Docker gerekmez**. Sadece backend'in çalışıyor olması yeterli!

---

## 📊 Nasıl Çalışır?

### Senaryo: Frontend Docker Olmadan, Backend Docker ile

```
┌─────────────────┐         HTTP Request          ┌─────────────────┐
│                 │  ───────────────────────────>  │                 │
│   Frontend      │                                 │    Backend      │
│  (localhost:3000)│  <───────────────────────────  │  (localhost:8000)│
│                 │         JSON Response          │                 │
│  (Docker YOK)   │                                 │   (Docker İÇİNDE)│
└─────────────────┘                                 └─────────────────┘
```

**Nasıl çalışır?**
1. Backend Docker container'ında `localhost:8000`'de çalışıyor
2. Frontend doğrudan bilgisayarınızda `localhost:3000`'de çalışıyor
3. Frontend, `fetch('http://localhost:8000/api/...')` ile backend'e istek atıyor
4. CORS ayarları bu isteklere izin veriyor ✅

---

## 🚀 Pratik Örnek

### 1. Backend'i Başlat (Docker ile)
```bash
cd backend
docker-compose up -d

# Backend şimdi http://localhost:8000'de çalışıyor ✅
```

### 2. Frontend'i Başlat (Docker OLMADAN)
```bash
cd frontend
npm install
npm run dev

# Frontend şimdi http://localhost:3000'de çalışıyor ✅
```

### 3. Frontend'den Backend'e İstek At

**JavaScript Örneği:**
```javascript
// Frontend kodunda (frontend/src/api.js)

const API_BASE_URL = 'http://localhost:8000/api';

// Film arama
async function searchFilms(query) {
  const response = await fetch(`${API_BASE_URL}/search?q=${query}`);
  const data = await response.json();
  return data.results;
}

// Film detayları
async function getFilmDetails(imdbId) {
  const response = await fetch(`${API_BASE_URL}/films/${imdbId}`);
  return await response.json();
}

// Kullanım
const films = await searchFilms('inception');
console.log(films);
```

**HTMX Örneği (Projenizde kullanılıyor):**
```html
<!-- Frontend HTML'de -->
<div hx-get="http://localhost:8000/api/search?q=inception" 
     hx-trigger="load"
     hx-swap="innerHTML">
  Loading...
</div>
```

---

## ⚙️ CORS Ayarları (Önemli!)

Backend'deki CORS ayarları frontend'in portunu içermeli:

```python
# backend/filmosphere/settings.py

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Vite default
    "http://localhost:5173",  # Vite default
    "http://localhost:8080",  # Diğer portlar için
    "http://127.0.0.1:3000",  # Alternatif localhost
]
```

**Eğer frontend farklı bir portta çalışıyorsa**, CORS ayarlarına ekleyin!

---

## 🔧 Frontend Yapılandırması

### Environment Variables (Önerilen)

**`frontend/.env`** dosyası oluşturun:
```env
VITE_API_URL=http://localhost:8000/api
# veya
REACT_APP_API_URL=http://localhost:8000/api
```

**Frontend kodunda kullanın:**
```javascript
// frontend/src/config.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// veya React için
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

---

## 📝 Tam Örnek: Film Arama

### Backend Endpoint
```
GET http://localhost:8000/api/search?q=inception
```

### Frontend Kodu (Vanilla JavaScript)
```javascript
// frontend/src/search.js

const API_BASE_URL = 'http://localhost:8000/api';

async function searchMovies(query) {
  try {
    const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.results; // [{imdb_id, title, year, image, type}, ...]
  } catch (error) {
    console.error('Search error:', error);
    return [];
  }
}

// Kullanım
document.getElementById('searchButton').addEventListener('click', async () => {
  const query = document.getElementById('searchInput').value;
  const films = await searchMovies(query);
  
  // Sonuçları göster
  films.forEach(film => {
    console.log(`${film.title} (${film.year})`);
  });
});
```

### Frontend Kodu (HTMX - Projenizde kullanılıyor)
```html
<!-- frontend/index.html -->
<input type="text" id="searchInput" placeholder="Film ara...">
<button hx-get="http://localhost:8000/api/search" 
        hx-include="#searchInput"
        hx-trigger="click"
        hx-target="#results">
  Ara
</button>

<div id="results"></div>
```

---

## 🔐 Authentication ile İstek

### Token Alma
```javascript
// Login
async function login(username, password) {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.tokens.access);
  localStorage.setItem('refresh_token', data.tokens.refresh);
}
```

### Token ile İstek
```javascript
// Authenticated request
async function getMyProfile() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/users/me/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return await response.json();
}
```

---

## ✅ Özet: Docker Gerekli mi?

### ❌ Frontend için Docker GEREKMEZ

**Neden?**
- Frontend sadece HTTP istekleri atıyor
- Backend'in URL'ini bilmesi yeterli
- CORS ayarları doğru olduğu sürece çalışır

### ✅ Backend için Docker VAR (Zaten mevcut)

**Neden?**
- Database (PostgreSQL) gerekiyor
- Python dependencies gerekiyor
- Tutarlı ortam sağlıyor

---

## 🎯 Çalışma Senaryosu

```bash
# Terminal 1: Backend (Docker ile)
cd backend
docker-compose up -d
# ✅ Backend http://localhost:8000'de çalışıyor

# Terminal 2: Frontend (Docker OLMADAN)
cd frontend
npm install
npm run dev
# ✅ Frontend http://localhost:3000'de çalışıyor

# Tarayıcı: http://localhost:3000
# Frontend otomatik olarak http://localhost:8000/api/... endpoint'lerine istek atıyor ✅
```

---

## 🐛 Sorun Giderme

### CORS Hatası
```
Access to fetch at 'http://localhost:8000/api/search' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Çözüm**: Backend'deki `CORS_ALLOWED_ORIGINS` listesine frontend portunu ekleyin.

### Connection Refused
```
Failed to fetch: net::ERR_CONNECTION_REFUSED
```

**Çözüm**: Backend'in çalıştığından emin olun:
```bash
curl http://localhost:8000/api/search?q=test
```

### 404 Not Found
```
GET http://localhost:8000/api/search 404 (Not Found)
```

**Çözüm**: URL'yi kontrol edin. Doğru format: `/api/search?q=...`

---

## 📚 Daha Fazla Bilgi

- Backend API dokümantasyonu: `backend/FRONTEND_DEVELOPER_GUIDE.md`
- API endpoint'leri: `backend/API_ENDPOINTS_REFERENCE.md`
- Postman collection: `backend/Filmosphere_Complete_API.postman_collection.json`



