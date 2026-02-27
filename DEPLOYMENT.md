# 🚀 Deployment Guide - Vercel + Railway

This guide covers **free deployment** for EnerScopeAI using Vercel (Frontend) + Railway (Backend).

---

## **Part 1: Deploy Frontend to Vercel**

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy Frontend
```bash
cd frontend
vercel
```

**Follow the prompts:**
- Link to GitHub account
- Select your NIRVANA repository
- Choose `frontend` as root directory
- Enable auto-deployment

**After deployment, you'll get:**
- Frontend URL: `https://yourapp.vercel.app`
- Automatic deployments on push to GitHub

### Step 3: Set Frontend Environment Variables
In Vercel Dashboard:
1. Go to your project settings
2. Add Environment Variable:
   ```
   VITE_API_URL = https://your-railway-backend-url
   ```

---

## **Part 2: Deploy Backend to Railway**

### Step 1: Create Railway Account
- Go to https://railway.app
- Sign up (free)
- Connect GitHub account

### Step 2: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 3: Login to Railway
```bash
railway login
```

### Step 4: Deploy Backend
```bash
cd backend
railway init
railway up
```

**During init:**
- Select "Python"
- Name your service "enerscopeai-backend"
- Choose environment "production"

**After deployment, you'll get:**
- Backend URL: `https://your-backend-railway.up.railway.app`
- Automatic health checks at `/api/health`

---

## **Step 3: Connect Frontend to Backend**

### Update Vercel Environment Variables
Go to Vercel Dashboard → Project Settings → Environment Variables

Update:
```
VITE_API_URL = https://your-backend-railway.up.railway.app
```

**Vercel will automatically redeploy.**

---

## **Environmental Variables Setup**

### Railway Backend `.env`
```env
# === AI (Gemini) ===
GEMINI_API_KEY=AIzaSyBKP2QYyQTXcF-ZFDQwmUaGkwpCIvcNiho

# === JWT Authentication ===
JWT_SECRET_KEY=your-super-secret-production-key-change-this

# === CORS ===
ALLOWED_ORIGINS=https://yourapp.vercel.app,https://your-backup-domain.com

# === NASA EARTHDATA (Optional) ===
NASA_EARTHDATA_USERNAME=shashank.31
NASA_EARTHDATA_PASSWORD=_Shashank@31
NASA_MERRA2_ENABLED=true

# === Database (Optional - Railway can provide free PostgreSQL) ===
DATABASE_URL=
```

**To add Railway environment variables:**
```bash
railway variables set GEMINI_API_KEY=your-key
railway variables set JWT_SECRET_KEY=your-secret
railway variables set ALLOWED_ORIGINS=https://yourapp.vercel.app
```

---

## **Monitoring & Logs**

### View Railway Logs
```bash
railway logs
```

### Monitor Vercel Deployment
- Dashboard: https://vercel.com/dashboard
- Logs: Click your project → Deployments → view logs

---

## **Troubleshooting**

### Backend Won't Start
```bash
railway logs  # Check for errors
railway status  # Check current status
```

### Frontend Can't Connect to Backend
1. Check CORS in Railway `.env`: Update `ALLOWED_ORIGINS`
2. Verify backend URL in Vercel env vars
3. Check Network tab in browser dev tools

### Out of Free Credits
- Railway: Free tier includes $5/month credit (usually enough)
- Upgrade plan starts at $5/month for more resources
- Vercel: Always free for hobby projects

---

## **Auto-Deployment on Code Push**

Both Vercel and Railway automatically redeploy when you push to GitHub:

```bash
git add .
git commit -m "update: production changes"
git push origin main
```

That's it! Both services will automatically rebuild and deploy.

---

## **Performance Tips**

1. **Frontend:** Vercel caches aggressive - always fast
2. **Backend:** Railway starts with 512MB RAM - enough for hobby use
3. **Database:** Use Railway PostgreSQL ($15/month, or stick with stateless)
4. **API Calls:** Solar + Wind data cached - only 2-3 external API calls per request

---

## **Cost Breakdown** (Monthly)

| Service | Free Tier | Pay-as-you-go |
|---------|-----------|---------------|
| Vercel | ✅ Unlimited | N/A (always free) |
| Railway | $5 credit | $0.50/hour after credit |
| Total | **$0** | **~$0-15/month** |

---

## **Next Steps**

1. Deploy frontend: `vercel` in `frontend/` folder
2. Deploy backend: `railway up` in `backend/` folder
3. Connect them via environment variables
4. Test at `https://yourapp.vercel.app`
5. Push updates to GitHub for auto-deployment

Questions? Check Railway/Vercel docs or GitHub Issues.

Good luck! 🚀
