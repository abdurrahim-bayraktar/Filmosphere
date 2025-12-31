# 🔧 Deployment Fix - Docker Detection Issue

## The Problem

If you're seeing this error during Render deployment:

```
error: failed to solve: failed to compute cache key: 
failed to calculate checksum of ref: "/requirements.txt": not found
```

**Cause**: Render is detecting the `Dockerfile` in the backend folder and trying to use Docker instead of the native Python environment we configured.

## ✅ The Solution (Already Fixed!)

I've renamed the Docker files so Render won't detect them and will use native Python/Node builds instead.

### What Changed

- `backend/Dockerfile` → `backend/Dockerfile.backup`
- `backend/docker-compose.yml` → `backend/docker-compose.yml.backup`
- Updated `render.yaml` to remove Docker references

### Apply the Fix

```bash
# 1. Commit the changes (Docker files are now renamed)
git add -A
git commit -m "Fix: Disable Docker detection for native Python builds"
git push

# 2. Render will automatically redeploy with native builds
# Wait 5-10 minutes and check the logs
```

That's it! The deployment should now work correctly with native Python/Node environments.

---

## 🔄 Alternative: Manual Service Deployment

If the Blueprint deployment still doesn't work, deploy each service manually:

### Backend Service

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. **Connect Repository**: Select your GitHub repo
4. **Configure**:
   - **Name**: `filmosphere-backend`
   - **Environment**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
   
5. **Environment Variables**:
   ```
   PYTHON_VERSION = 3.11.0
   SECRET_KEY = [Click Generate]
   DJANGO_SETTINGS_MODULE = config.settings_prod
   ALLOWED_HOSTS = *
   DEEPSEEK_API_KEY = [your-key or leave empty]
   WATCHMODE_API_KEY = [your-key or leave empty]
   ```

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment

### Frontend Service

1. **Go to Render Dashboard** again
2. Click **"New +"** → **"Web Service"**
3. **Connect Repository**: Same GitHub repo
4. **Configure**:
   - **Name**: `filmosphere-frontend`
   - **Environment**: `Node`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx http-server dist/frontend-app/browser -p $PORT`
   
5. **Environment Variables**:
   ```
   NODE_VERSION = 20.11.0
   ```

6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment

### After Both Services Deploy

1. Note your backend URL: `https://filmosphere-backend-xxxx.onrender.com`

2. Update `frontend/src/environments/environment.prod.ts`:
   ```typescript
   export const environment = {
     production: true,
     apiBaseUrl: 'https://filmosphere-backend-xxxx.onrender.com',  // Your actual URL
   };
   ```

3. Commit and push:
   ```bash
   git add frontend/src/environments/environment.prod.ts
   git commit -m "Update production API URL"
   git push
   ```

4. Frontend will auto-redeploy in 1-2 minutes

---

## 🎯 What Changed in the Fix

### Docker Files Renamed
To prevent Render from auto-detecting Docker:

- `backend/Dockerfile` → `backend/Dockerfile.backup`
- `backend/docker-compose.yml` → `backend/docker-compose.yml.backup`

These files are preserved with `.backup` extension in case you want to use Docker locally or on other platforms.

### `render.yaml`
Removed Docker-related configuration to ensure native builds:

```yaml
services:
  - type: web
    name: filmosphere-backend
    env: python  # ← Native Python environment
    buildCommand: "cd backend && chmod +x build.sh && ./build.sh"
    startCommand: "cd backend && gunicorn config.wsgi:application"
```

Now Render will use its native Python runtime instead of trying to build Docker images.

---

## ✅ Verification

After deployment, check:

- [ ] Backend service shows "Live" status
- [ ] Frontend service shows "Live" status
- [ ] Backend URL accessible: `https://your-backend-url.onrender.com/api/`
- [ ] Frontend URL accessible: `https://your-frontend-url.onrender.com`
- [ ] No errors in deployment logs

---

## 🚨 If Still Having Issues

### Check Build Logs

1. Go to Render Dashboard
2. Click on the failing service
3. Click **"Logs"** tab
4. Look for the specific error

### Common Issues & Solutions

| Error | Solution |
|-------|----------|
| Module not found | Check requirements.txt has all dependencies |
| Permission denied on build.sh | build.sh needs execute permission (should be in git) |
| gunicorn not found | Ensure requirements.txt includes gunicorn==21.2.0 |
| Port binding error | Ensure start command includes `$PORT` variable |

### Get Logs

```bash
# In Render Dashboard Shell
cd backend
python manage.py check
python manage.py migrate --check
```

---

## 💡 Using Docker (Advanced)

If you **want** to use Docker on Render:

1. **Update `render.yaml`**:
   ```yaml
   services:
     - type: web
       name: filmosphere-backend
       env: docker
       dockerfilePath: ./backend/Dockerfile
       dockerContext: ./backend
   ```

2. **Ensure Dockerfile is correct** (already fixed above)

3. **Push and deploy**

---

## 🆘 Still Need Help?

1. **Check** full deployment guide: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. **Review** Render's official docs: https://render.com/docs
3. **Verify** all files are committed and pushed to GitHub
4. **Check** that you're on the `main` branch

---

## 📝 Summary

**The Fix**: Updated `render.yaml` to prevent Docker detection
**Action Needed**: Commit and push the updated files
**Result**: Render will use native Python/Node builds (faster and simpler)

Your deployment should now work! 🚀

