# Setup Guide for Frontend Team

Quick setup instructions for frontend developers to start working with the Filmosphere API.

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### 2. Start the Backend

```bash
# Navigate to backend directory
cd backend

# Start services
docker-compose up -d

# Check if services are running
docker-compose ps
```

You should see:
```
NAME                   STATUS
filmosphere_postgres   Up (healthy)
filmosphere_web        Up
```

### 3. Verify Backend is Working

```bash
# Test search endpoint
curl http://localhost:8000/api/search?q=inception

# Should return JSON with film results
```

### 4. Access Points

- **API Base URL**: `http://localhost:8000/api/`
- **API Documentation**: `http://localhost:8000/api/docs/` (Swagger UI)
- **Admin Panel**: `http://localhost:8000/admin/` (if needed)

### 5. Import Postman Collection

1. Open Postman
2. Click "Import"
3. Select `Filmosphere_Complete_API.postman_collection.json`
4. Set collection variable `base_url` to `http://localhost:8000`

---

## 📚 Documentation Files

1. **`FRONTEND_DEVELOPER_GUIDE.md`** - Complete guide with examples
2. **`API_ENDPOINTS_REFERENCE.md`** - Quick reference of all endpoints
3. **`Filmosphere_Complete_API.postman_collection.json`** - Postman collection for testing

---

## 🔑 Getting Your First Token

### Option 1: Using Postman
1. Open Postman collection
2. Go to "1. Authentication" folder
3. Run "Register User" or "Login"
4. Token is automatically saved to `access_token` variable

### Option 2: Using cURL

**Register**:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "display_name": "Test User"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Save the `access` token from the response.

---

## 🧪 Testing Your First API Call

### Search for Films
```bash
curl http://localhost:8000/api/search?q=shawshank
```

### Get Film Details (with authentication)
```bash
curl http://localhost:8000/api/films/tt0111161 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Rate a Film
```bash
curl -X POST http://localhost:8000/api/films/tt0111161/rate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overall_rating": 5,
    "plot_rating": 5,
    "acting_rating": 4
  }'
```

---

## 🎯 Key Features to Test

### 1. Authentication Flow
- Register → Login → Use token in requests

### 2. Film Interactions
- Search films
- View film details
- Rate films (overall + aspects)
- Create reviews
- Check spoiler detection

### 3. Social Features
- Follow users
- View followers/following
- View user profiles

### 4. Lists
- Create lists
- Add films to lists
- View lists

### 5. Badges
- View available badges
- Check progress
- Create custom badges

---

## 🔧 Troubleshooting

### Backend Not Starting
```bash
# Check logs
docker-compose logs web

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up -d --build
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Port Already in Use
If port 8000 is in use, update `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### CORS Issues
If you get CORS errors, check `filmosphere/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React default
    "http://localhost:5173",  # Vite default
    # Add your frontend URL here
]
```

---

## 📝 Environment Variables (Optional)

Create a `.env` file in the `backend` directory for custom configuration:

```env
# Database
DATABASE_URL=postgres://filmouser:filmopass@postgres:5432/filmosphere

# API Keys (optional - features work without them but with limited functionality)
DEEPSEEK_API_KEY=your_key_here
KINO_API_KEY=your_key_here
WATCHMODE_API_KEY=your_key_here

# Django
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
```

---

## 🎨 Frontend Integration Checklist

- [ ] Backend is running and accessible
- [ ] Postman collection imported and tested
- [ ] Authentication flow working
- [ ] Token stored securely in frontend
- [ ] CORS configured for your frontend URL
- [ ] Error handling implemented
- [ ] Loading states for API calls
- [ ] Token refresh logic implemented

---

## 📞 Need Help?

1. Check the logs: `docker-compose logs web`
2. Test endpoints in Postman first
3. Review `FRONTEND_DEVELOPER_GUIDE.md` for detailed examples
4. Check `API_ENDPOINTS_REFERENCE.md` for endpoint details

---

## 🎬 Next Steps

1. **Read the Documentation**:
   - Start with `FRONTEND_DEVELOPER_GUIDE.md`
   - Reference `API_ENDPOINTS_REFERENCE.md` as needed

2. **Test in Postman**:
   - Go through all folders in the collection
   - Understand request/response formats

3. **Build Your Frontend**:
   - Start with authentication
   - Then film search and details
   - Add user interactions (ratings, reviews)
   - Implement social features (following, badges)

4. **Integrate Features**:
   - Use the examples in the guide
   - Adapt to your framework (React, Vue, Angular, etc.)

Happy coding! 🚀

