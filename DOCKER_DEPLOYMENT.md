# 🐳 Docker Deployment Guide for Render

## Current Setup

Your Render services are configured to use **Docker**. This guide will help you deploy successfully.

---

## ✅ What I Fixed

1. **Created proper `backend/Dockerfile`**
   - Uses Python 3.11
   - Installs dependencies correctly
   - Runs migrations automatically
   - Uses Gunicorn for production
   - Binds to Render's `$PORT` variable

2. **Created `backend/.dockerignore`**
   - Excludes unnecessary files
   - Speeds up Docker build

3. **Simplified the build process**
   - No complex entrypoint scripts
   - Direct migration + gunicorn startup

---

## 🚀 Deploy Now

### Step 1: Commit and Push

```bash
# Add the Dockerfile
git add backend/Dockerfile backend/.dockerignore

# Commit
git commit -m "Add production-ready Dockerfile for Render"

# Push
git push
```

### Step 2: Configure Render Service

In your **Render Dashboard** for the backend service:

#### If Using Web Service (Docker):
- **Environment**: Docker
- **Dockerfile Path**: `./backend/Dockerfile`
- **Docker Context**: `./backend`
- **Docker Build Context Dir**: `backend`

#### Environment Variables:
```
SECRET_KEY = [Generate]
DJANGO_SETTINGS_MODULE = config.settings_prod
ALLOWED_HOSTS = *
PORT = 8000
```

Optional:
```
DEEPSEEK_API_KEY = your-key
WATCHMODE_API_KEY = your-key
```

### Step 3: Deploy

Render will automatically build and deploy after you push!

---

## 📋 Dockerfile Explanation

```dockerfile
FROM python:3.11-slim              # Base Python image
WORKDIR /app                        # Set working directory
COPY requirements.txt .             # Copy dependencies first (caching)
RUN pip install -r requirements.txt # Install dependencies
COPY . .                            # Copy all project files
RUN python manage.py collectstatic  # Collect static files
CMD python manage.py migrate &&     # Run migrations on startup
    gunicorn config.wsgi:application # Start Gunicorn
```

---

## 🔍 Render Service Configuration

### For Backend (Docker)

**Service Type**: Web Service
**Environment**: Docker

**Build Settings**:
- Dockerfile Path: `./backend/Dockerfile`
- Docker Context: `./backend`

**Health Check** (optional):
- Path: `/api/`
- Initial Delay: 30 seconds

### For Frontend (Native Node)

**Service Type**: Web Service
**Environment**: Node

**Build Settings**:
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Start Command: `npx http-server dist/frontend-app/browser -p $PORT`

---

## ✅ Expected Build Process

```
1. Cloning repository...
2. Building Docker image...
   - Installing system dependencies
   - Installing Python packages
   - Copying application files
   - Collecting static files
3. Starting container...
   - Running migrations
   - Starting Gunicorn
4. Service is live! ✅
```

Build time: ~5-8 minutes

---

## 🎯 After Deployment

### 1. Verify Backend

Visit: `https://your-backend-url.onrender.com/api/`

You should see the API root.

### 2. Check Admin

Visit: `https://your-backend-url.onrender.com/admin/`

### 3. Create Superuser

In Render Dashboard → Backend Service → Shell:

```bash
python manage.py createsuperuser
```

### 4. Update Frontend

Edit `frontend/src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiBaseUrl: 'https://your-actual-backend-url.onrender.com',
};
```

Commit and push:

```bash
git add frontend/src/environments/environment.prod.ts
git commit -m "Update production API URL"
git push
```

---

## 🐛 Troubleshooting

### Build Fails: "requirements.txt not found"

**Solution**: Check Dockerfile path in Render settings:
- Docker Context should be: `./backend`
- Dockerfile Path should be: `./backend/Dockerfile`

### Build Fails: "Module not found"

**Solution**: Ensure `requirements.txt` has all dependencies:

```bash
# Check locally
cd backend
pip install -r requirements.txt
```

### Container Starts but Crashes

**Check logs** in Render Dashboard → Logs tab

Common issues:
- Missing environment variables
- Database migration errors
- Port binding issues

### Static Files Not Loading

The Dockerfile runs `collectstatic` during build. If it fails:

1. Check `STATIC_ROOT` in settings
2. Ensure `whitenoise` is in `MIDDLEWARE`
3. Check build logs for errors

---

## 🔄 Alternative: Switch to Native Python

If Docker is causing issues, you can switch to native Python:

### In Render Dashboard:

1. **Service Settings** → **Environment**
2. Change from "Docker" to "Python"
3. **Build Command**: `cd backend && chmod +x build.sh && ./build.sh`
4. **Start Command**: `cd backend && gunicorn config.wsgi:application`
5. Save and redeploy

Then you won't need the Dockerfile!

---

## 📊 Docker vs Native Comparison

| Feature | Docker | Native Python |
|---------|--------|---------------|
| **Setup** | More complex | Simpler |
| **Build Time** | 5-8 min | 3-5 min |
| **Consistency** | Identical everywhere | Platform-dependent |
| **Debugging** | Harder | Easier |
| **Best For** | Production | Quick deploys |

**Recommendation**: Use Docker if you need exact environment control, otherwise native Python is faster and simpler.

---

## 🎉 Summary

1. ✅ Dockerfile is ready
2. ✅ `.dockerignore` optimizes build
3. ✅ Just commit and push
4. ✅ Render will build and deploy

**Deploy command**:

```bash
git add backend/Dockerfile backend/.dockerignore
git commit -m "Add production Dockerfile"
git push
```

Your deployment should work now! 🚀

---

## 📞 Need Help?

- **Check logs**: Render Dashboard → Your Service → Logs
- **Test locally**: `cd backend && docker build -t filmosphere .`
- **Verify settings**: Ensure Docker Context is `./backend`

Good luck! 🎊

