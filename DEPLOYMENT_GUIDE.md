# Filmosphere Deployment Guide

## Quick Deployment using Render.com (FREE)

This guide will help you deploy your Filmosphere app in the quickest way possible using Render.com's free tier.

---

## Prerequisites

1. A GitHub account
2. A Render.com account (sign up at https://render.com - it's free!)
3. Your code pushed to a GitHub repository

---

## Deployment Steps

### Step 1: Push Your Code to GitHub

If you haven't already:

```bash
git init
git add .
git commit -m "Prepare for deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy to Render (Automated Method)

Render can automatically detect and deploy both services from your `render.yaml` file.

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click "New +" → "Blueprint"

2. **Connect Your Repository**
   - Select your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables**
   - For the backend service, add these environment variables:
     - `SECRET_KEY`: Click "Generate" or use your own secure key
     - `DEEPSEEK_API_KEY`: Your DeepSeek API key (if you have one)
     - `WATCHMODE_API_KEY`: Your Watchmode API key (if you have one)
     - These are optional - the app will work without them but with limited features

4. **Deploy**
   - Click "Apply" to deploy both services
   - Wait 5-10 minutes for the deployment to complete

### Step 3: Update Frontend API URL

After the backend is deployed:

1. Note your backend URL (will be something like `https://filmosphere-backend.onrender.com`)
2. Update `frontend/src/environments/environment.prod.ts`:
   ```typescript
   export const environment = {
     production: true,
     apiBaseUrl: 'https://your-actual-backend-url.onrender.com',
   };
   ```
3. Commit and push the change:
   ```bash
   git add frontend/src/environments/environment.prod.ts
   git commit -m "Update production API URL"
   git push
   ```
4. Render will automatically redeploy the frontend

### Step 4: Access Your App

- **Frontend**: https://filmosphere-frontend.onrender.com
- **Backend API**: https://filmosphere-backend.onrender.com
- **Admin Panel**: https://filmosphere-backend.onrender.com/admin

---

## Manual Deployment (Alternative)

If you prefer to deploy services individually:

### Deploy Backend

1. **Create Web Service**
   - Dashboard → "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `backend` directory

2. **Configure**
   - Name: `filmosphere-backend`
   - Environment: `Python 3`
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `gunicorn config.wsgi:application`
   - Add environment variables as mentioned above

### Deploy Frontend

1. **Create Web Service**
   - Dashboard → "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `frontend` directory

2. **Configure**
   - Name: `filmosphere-frontend`
   - Environment: `Node`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx http-server dist/frontend-app/browser -p $PORT`

---

## Important Notes

### Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after inactivity may take 30-60 seconds (cold start)
- 750 hours/month of runtime (plenty for testing)

### Database Persistence

- Currently using SQLite (file-based database)
- On Render's free tier, the database resets when the service restarts
- **For production**: Upgrade to PostgreSQL (see below)

### Upgrading to PostgreSQL (Recommended for Production)

1. **Create PostgreSQL Database on Render**
   - Dashboard → "New +" → "PostgreSQL"
   - Note the internal database URL

2. **Update Backend Settings**
   - In `backend/config/settings_prod.py`, replace the SQLite database config with:
   ```python
   import dj_database_url
   
   DATABASES = {
       'default': dj_database_url.config(
           default=os.environ.get('DATABASE_URL'),
           conn_max_age=600
       )
   }
   ```

3. **Add to requirements.txt**
   ```
   dj-database-url==2.1.0
   ```

4. **Add Environment Variable**
   - In Render backend service settings, add:
   - `DATABASE_URL`: (Copy from your PostgreSQL instance)

---

## Alternative Quick Deployment Options

### Option 1: Railway.app (Similar to Render)

1. Visit https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Railway will auto-detect Django and Node.js
5. Add the same environment variables
6. Deploy!

**Pros**: Simpler interface, faster deploys
**Cons**: Free tier is $5 credit/month (usually enough for testing)

### Option 2: Vercel (Frontend) + Render (Backend)

**For Frontend:**
1. Visit https://vercel.com
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Deploy (automatic detection)

**For Backend:**
1. Use Render.com as described above

**Pros**: Vercel has excellent performance for static sites
**Cons**: Need to manage two platforms

### Option 3: Heroku (Paid but Robust)

Heroku no longer has a free tier but is very reliable:
- Frontend + Backend: ~$10-14/month
- Better for production workloads

---

## Troubleshooting

### Backend not starting?
- Check logs in Render dashboard
- Ensure all migrations ran successfully
- Verify environment variables are set

### Frontend can't connect to backend?
- Check CORS settings
- Verify API URL in `environment.prod.ts`
- Check browser console for errors

### Database issues?
- For free tier, database resets on restart (expected behavior)
- Upgrade to PostgreSQL for persistence

### Cold starts taking too long?
- This is normal on free tier
- Consider upgrading to paid tier ($7/month per service)
- Or use Railway which has faster cold starts

---

## Admin Panel Setup

After deployment, create a superuser:

```bash
# In Render dashboard, go to your backend service
# Click "Shell" tab
# Run:
python manage.py createsuperuser
```

Then access at: `https://your-backend-url.onrender.com/admin`

---

## Cost Breakdown

### Completely Free Option (Render Free Tier)
- Backend: Free
- Frontend: Free
- Database: Free (SQLite) or Free (PostgreSQL with limitations)
- **Total: $0/month**

### Recommended Production Setup
- Backend: $7/month (always-on)
- Frontend: Free (Vercel) or $7/month (Render)
- Database: $7/month (PostgreSQL)
- **Total: $14-21/month**

---

## Next Steps

1. ✅ Deploy using the steps above
2. ✅ Test your deployed app
3. ✅ Create admin user
4. ✅ Add your API keys for external services
5. 📈 Monitor usage and upgrade as needed
6. 🔒 Update CORS settings to restrict to your frontend URL only

---

## Support

If you encounter issues:
- Check Render logs: Dashboard → Service → Logs
- Review build logs for errors
- Ensure all environment variables are set correctly
- Database migrations completed successfully

---

## Summary of Changes Made for Deployment

1. ✅ Created `backend/config/settings_prod.py` - Production settings
2. ✅ Created `backend/build.sh` - Build script for Render
3. ✅ Created `render.yaml` - Automated deployment configuration
4. ✅ Added `gunicorn` and `whitenoise` to requirements.txt
5. ✅ Updated Django settings for static files
6. ✅ Added `http-server` to frontend package.json
7. ✅ Updated frontend production environment file
8. ✅ Updated frontend build command

Your app is now ready to deploy! 🚀

