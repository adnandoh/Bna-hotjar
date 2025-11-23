# Railway Environment Variables - Quick Setup

Copy and paste these into your Railway project's environment variables:

## Required Variables

```
SECRET_KEY=django-insecure-ufk^_$!wx3=#d6irhm7)xhufs(q)9ih)rzrb_xcuqp-oo^yg7g
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

## Database Configuration

**Option 1: Use Internal URL (Recommended - Faster)**
```
DATABASE_URL=postgresql://postgres:QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD@postgres.railway.internal:5432/railway
```

**Option 2: Use Public URL**
```
DATABASE_URL=postgresql://postgres:QwrcSTcOAIyPlCUSxFEHjfIUiNUojdvD@gondola.proxy.rlwy.net:46677/railway
```

## CORS Configuration (Update after frontend deployment)

```
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.railway.app
```

---

## 🚀 Quick Deploy Steps

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **On Railway:**
   - New Project → Deploy from GitHub
   - Select: `adnandoh/Bna-hotjar`
   - Add environment variables above
   - Deploy!

3. **After Deployment:**
   - Create superuser: `railway run python manage.py createsuperuser`
   - Visit: `https://your-app.railway.app/admin`

---

## 📋 Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables added
- [ ] PostgreSQL linked
- [ ] Deployment successful
- [ ] Migrations run
- [ ] Superuser created
- [ ] Admin panel accessible
- [ ] API endpoints working
