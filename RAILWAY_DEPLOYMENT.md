# Railway Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository with your backend code
- PostgreSQL database already created on Railway

### 2. Environment Variables on Railway

Add these environment variables in your Railway project settings:

```bash
# Django Settings
SECRET_KEY=django-insecure-ufk^_$!wx3=#d6irhm7)xhufs(q)9ih)rzrb_xcuqp-oo^yg7g
DEBUG=False
ALLOWED_HOSTS=*.railway.app

# Database (Railway will provide this automatically if you link PostgreSQL service)
DATABASE_URL=postgresql://postgres:QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD@gondola.proxy.rlwy.net:46677/railway

# Or use internal URL (faster, recommended)
DATABASE_URL=postgresql://postgres:QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD@postgres.railway.internal:5432/railway

# CORS (update with your frontend URL after deployment)
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.railway.app
```

### 3. Deploy to Railway

#### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   cd backend
   git add .
   git commit -m "Configure for Railway deployment"
   git push origin main
   ```

2. **Create a new project on Railway:**
   - Go to https://railway.app/new
   - Click "Deploy from GitHub repo"
   - Select your repository: `adnandoh/Bna-hotjar`
   - Railway will automatically detect it's a Django app

3. **Link PostgreSQL Database:**
   - In your Railway project, click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable
   - Or use your existing PostgreSQL service

4. **Set Environment Variables:**
   - Go to your service → "Variables" tab
   - Add the variables listed above
   - Make sure `DATABASE_URL` points to your PostgreSQL instance

5. **Deploy:**
   - Railway will automatically build and deploy
   - Wait for the deployment to complete
   - Your app will be available at: `https://your-app.railway.app`

#### Option B: Deploy using Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize and Deploy:**
   ```bash
   cd backend
   railway init
   railway up
   ```

4. **Link PostgreSQL:**
   ```bash
   railway link
   railway add --database postgresql
   ```

### 4. Post-Deployment Steps

1. **Run Migrations:**
   Railway will automatically run migrations via the Procfile, but you can also run manually:
   ```bash
   railway run python manage.py migrate
   ```

2. **Create Superuser:**
   ```bash
   railway run python manage.py createsuperuser
   ```

3. **Collect Static Files:**
   ```bash
   railway run python manage.py collectstatic --noinput
   ```

### 5. Verify Deployment

1. Visit your Railway app URL: `https://your-app.railway.app`
2. Check the admin panel: `https://your-app.railway.app/admin`
3. Test API endpoints: `https://your-app.railway.app/api/`

### 6. Database Connection Details

Your PostgreSQL database is configured with:

- **Public URL:** `postgresql://postgres:QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD@gondola.proxy.rlwy.net:46677/railway`
- **Internal URL (faster):** `postgresql://postgres:QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD@postgres.railway.internal:5432/railway`
- **Host:** `gondola.proxy.rlwy.net` (public) or `postgres.railway.internal` (internal)
- **Port:** `46677` (public) or `5432` (internal)
- **Database:** `railway`
- **User:** `postgres`
- **Password:** `QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD`

**Note:** Use the internal URL for better performance when your app is deployed on Railway.

## 🔧 Troubleshooting

### Issue: Static files not loading
**Solution:** Run `railway run python manage.py collectstatic --noinput`

### Issue: Database connection error
**Solution:** 
- Check that `DATABASE_URL` is set correctly in Railway variables
- Verify PostgreSQL service is running
- Use internal URL for better connectivity

### Issue: Application crashes on startup
**Solution:**
- Check Railway logs: `railway logs`
- Verify all dependencies are in `requirements.txt`
- Ensure `Procfile` is present and correct

### Issue: CORS errors from frontend
**Solution:**
- Update `CORS_ALLOWED_ORIGINS` in Railway variables
- Add your frontend URL to the list

## 📝 Important Files for Deployment

- ✅ `Procfile` - Defines web server and release commands
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `railway.json` - Railway configuration
- ✅ `.env.example` - Environment variable template
- ✅ `config/settings.py` - Updated with PostgreSQL support

## 🎯 Next Steps

1. Update `ALLOWED_HOSTS` with your actual Railway domain
2. Generate a new `SECRET_KEY` for production
3. Set `DEBUG=False` in production
4. Configure CORS with your frontend URL
5. Set up monitoring and logging
6. Configure custom domain (optional)

## 📚 Resources

- Railway Documentation: https://docs.railway.app
- Django Deployment Checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
- Railway Discord: https://discord.gg/railway
