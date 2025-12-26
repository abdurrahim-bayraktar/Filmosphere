# 🚀 Quick Start - Deploy in 10 Minutes

## The Fastest Way to Deploy Filmosphere

### 1. Push to GitHub (2 minutes)

```bash
# If not already initialized
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/filmosphere.git
git push -u origin main
```

### 2. Deploy to Render (5 minutes)

1. **Sign up**: https://render.com (use GitHub login)

2. **Create Blueprint**:
   - Click **"New +"** → **"Blueprint"**
   - Select your GitHub repository
   - Render detects `render.yaml` automatically
   - Click **"Apply"**

3. **Set Environment Variables** (in the backend service):
   - `SECRET_KEY`: Click **"Generate"**
   - `DEEPSEEK_API_KEY`: (optional) Add if you have one
   - `WATCHMODE_API_KEY`: (optional) Add if you have one

4. **Wait**: Services deploy in ~5-8 minutes

### 3. Update Frontend URL (2 minutes)

After backend deploys, you'll get a URL like: `https://filmosphere-backend-xxxx.onrender.com`

Update `frontend/src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiBaseUrl: 'https://filmosphere-backend-xxxx.onrender.com',  // ← Your actual URL
};
```

Push the change:

```bash
git add frontend/src/environments/environment.prod.ts
git commit -m "Update API URL"
git push
```

Render auto-redeploys the frontend (1-2 minutes).

### 4. Done! ✅

- **Frontend**: `https://filmosphere-frontend-xxxx.onrender.com`
- **Backend**: `https://filmosphere-backend-xxxx.onrender.com`
- **Admin**: `https://filmosphere-backend-xxxx.onrender.com/admin`

---

## Create Admin User

In Render Dashboard → Backend Service → **Shell** tab:

```bash
python manage.py createsuperuser
```

---

## Important Notes

- **First load takes 30-60 seconds** (free tier "cold start")
- **Database resets** on service restart (use PostgreSQL for persistence)
- **750 free hours/month** - plenty for testing!

---

## Troubleshooting

### Error: "requirements.txt not found" during deployment

If you see a Docker-related error about requirements.txt:

**Solution**: Render is trying to use Docker instead of native build. This is now fixed in `render.yaml`.

1. **Commit the updated render.yaml:**
   ```bash
   git add render.yaml
   git commit -m "Fix Docker detection for Render"
   git push
   ```

2. **Redeploy**: Render will auto-deploy with the fix

**Alternative**: Deploy each service manually (see below)

### Manual Deployment (If Blueprint Doesn't Work)

**Backend:**
1. Dashboard → **New +** → **Web Service**
2. Connect GitHub repo
3. **Root Directory**: `backend`
4. **Build Command**: `chmod +x build.sh && ./build.sh`
5. **Start Command**: `gunicorn config.wsgi:application`
6. Add environment variables (SECRET_KEY, etc.)
7. Deploy

**Frontend:**
1. Dashboard → **New +** → **Web Service**
2. Connect GitHub repo
3. **Root Directory**: `frontend`
4. **Build Command**: `npm install && npm run build`
5. **Start Command**: `npx http-server dist/frontend-app/browser -p $PORT`
6. Deploy

---

## Need Help?

See full guide: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## Alternative: Railway (Even Faster!)

Railway is slightly faster and simpler:

1. **Sign up**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **Add services**: Railway auto-detects everything
4. **Deploy**: That's it! ($5 free credit/month)

---

## Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Blueprint deployed
- [ ] Environment variables set
- [ ] Backend deployed successfully
- [ ] Frontend API URL updated
- [ ] Frontend deployed successfully
- [ ] Admin user created
- [ ] Can access the app!

🎉 **You're live!**

