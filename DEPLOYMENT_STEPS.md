# Step-by-Step Deployment Guide: Vercel (Frontend) + Railway (Backend)

## 🎯 Overview

- **Frontend**: Deploy to Vercel (Free, Easy, Fast)
- **Backend**: Deploy to Railway (Free tier available, Easy setup)

---

## 📋 Prerequisites

1. **GitHub Account** (you already have this - code is at https://github.com/Tarunsai01/ARIA)
2. **Vercel Account** (free) - Sign up at https://vercel.com
3. **Railway Account** (free tier) - Sign up at https://railway.app
4. **API Keys Ready**:
   - OpenAI API key (if using OpenAI)
   - Google Gemini API key (if using Gemini)

---

## 🚂 Part 1: Deploy Backend to Railway

### Step 1: Create Railway Account

1. Go to https://railway.app
2. Click **"Login"** → **"Start a New Project"**
3. Sign in with **GitHub** (recommended)
4. Authorize Railway to access your GitHub

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your repository: **`Tarunsai01/ARIA`**
4. Railway will detect it's a Python project

### Step 3: Configure Backend Service

1. Railway will create a service automatically
2. Click on the service to open settings
3. **Set Root Directory**: 
   - Go to **Settings** → **Source**
   - Set **Root Directory** to: `backend`
   - Click **Save**

### Step 4: Set Environment Variables

1. Go to **Variables** tab in Railway dashboard
2. Click **"New Variable"** and add each:

```env
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

**Generate Keys:**
```bash
# Run these in your local terminal:
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

**Note**: For `CORS_ORIGINS`, you'll update this after deploying frontend. For now, use:
```
CORS_ORIGINS=https://your-app-name.vercel.app
```

### Step 5: Configure Build & Start Commands

1. Go to **Settings** → **Deploy**
2. **Build Command**: Leave empty (or `pip install -r requirements.txt`)
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Railway auto-detects Python, but verify:
   - **Python Version**: 3.12 (or latest)

### Step 6: Deploy

1. Railway will automatically deploy when you push to GitHub
2. Or click **"Deploy"** button manually
3. Wait for deployment to complete (2-3 minutes)
4. Check **Logs** tab for any errors

### Step 7: Get Backend URL

1. Once deployed, go to **Settings** → **Networking**
2. Click **"Generate Domain"** (or use the default)
3. Copy the URL (e.g., `https://aria-backend-production.up.railway.app`)
4. **Save this URL** - you'll need it for frontend!

### Step 8: Test Backend

1. Open your backend URL in browser
2. You should see: `{"message":"ARIA API - Two-way Sign Language Interpreter","version":"2.0.0"}`
3. Test health endpoint: `https://your-backend-url.railway.app/health`
4. Should return: `{"status":"healthy","version":"2.0.0"}`

---

## 🎨 Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Sign in with **GitHub** (recommended)
4. Authorize Vercel to access your GitHub

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Find and select your repository: **`Tarunsai01/ARIA`**
3. Click **"Import"**

### Step 3: Configure Frontend Project

1. **Framework Preset**: Vercel will auto-detect **Vite**
2. **Root Directory**: Click **"Edit"** and set to: `frontend`
3. **Build Command**: `npm run build` (auto-filled)
4. **Output Directory**: `dist` (auto-filled)
5. **Install Command**: `npm install` (auto-filled)

### Step 4: Set Environment Variables

1. Scroll down to **"Environment Variables"**
2. Click **"Add"** and add:

```env
VITE_API_URL=https://your-backend-url.railway.app
```

**Important**: Replace `your-backend-url.railway.app` with your actual Railway backend URL from Step 7 above!

### Step 5: Deploy

1. Click **"Deploy"** button
2. Wait for build to complete (1-2 minutes)
3. Vercel will show you the deployment URL (e.g., `https://aria-frontend.vercel.app`)

### Step 6: Get Frontend URL

1. After deployment, copy your frontend URL
2. It will be something like: `https://aria-frontend.vercel.app` or `https://aria-xyz123.vercel.app`

---

## 🔗 Part 3: Connect Frontend to Backend

### Step 1: Update Backend CORS

1. Go back to **Railway Dashboard** → Your Backend Service
2. Go to **Variables** tab
3. Update `CORS_ORIGINS` to include your Vercel URL:

```env
CORS_ORIGINS=https://your-frontend-url.vercel.app,https://your-frontend-url-xyz.vercel.app
```

**Note**: Add both the main domain and any preview domains Vercel creates

4. Railway will automatically redeploy with new CORS settings

### Step 2: Update Frontend API URL (if needed)

1. Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. Verify `VITE_API_URL` is set correctly
3. If you need to change it, update and **redeploy**:
   - Go to **Deployments** tab
   - Click **"..."** on latest deployment → **"Redeploy"**

---

## ✅ Part 4: Verify Deployment

### Test Frontend

1. Open your Vercel frontend URL
2. You should see the ARIA landing page
3. Try to register/login
4. Check if API calls work

### Test Backend

1. Open: `https://your-backend-url.railway.app/docs`
2. You should see Swagger API documentation
3. Test endpoints if needed

### Common Issues

**CORS Errors:**
- Make sure `CORS_ORIGINS` in Railway includes your exact Vercel URL
- Check for trailing slashes
- Wait a few minutes after updating CORS (redeploy takes time)

**API Not Found:**
- Verify `VITE_API_URL` in Vercel matches your Railway URL
- Check Railway logs for errors
- Make sure backend is running (check Railway dashboard)

**Build Errors:**
- Check Vercel build logs
- Check Railway deployment logs
- Verify all environment variables are set

---

## 🔄 Part 5: Automatic Deployments

### Both platforms support auto-deploy:

**Railway:**
- Automatically deploys when you push to `main` branch
- No configuration needed (already set up)

**Vercel:**
- Automatically deploys when you push to `main` branch
- Creates preview deployments for other branches
- No configuration needed (already set up)

### To update your app:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Both Railway and Vercel will automatically redeploy!

---

## 📊 Part 6: Monitoring & Logs

### Railway Logs

1. Go to Railway Dashboard → Your Service
2. Click **"Logs"** tab
3. See real-time logs and errors

### Vercel Logs

1. Go to Vercel Dashboard → Your Project
2. Click on a deployment
3. See build logs and runtime logs

---

## 💰 Part 7: Free Tier Limits

### Railway Free Tier:
- $5 free credit per month
- Enough for small-medium traffic
- Auto-sleeps after inactivity (wakes on request)

### Vercel Free Tier:
- Unlimited deployments
- 100GB bandwidth
- Perfect for frontend hosting

---

## 🎉 You're Done!

Your ARIA app is now live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.railway.app`

### Next Steps:

1. **Test the app** - Register, login, use features
2. **Share the URL** - Your app is publicly accessible
3. **Monitor usage** - Check Railway and Vercel dashboards
4. **Set up custom domains** (optional):
   - Vercel: Settings → Domains
   - Railway: Settings → Networking → Custom Domain

---

## 🆘 Troubleshooting

### Backend won't start:
- Check Railway logs
- Verify all environment variables are set
- Check Python version (should be 3.12)

### Frontend can't connect to backend:
- Verify `VITE_API_URL` is correct
- Check CORS settings in Railway
- Test backend URL directly in browser

### Build fails:
- Check build logs in Vercel
- Verify `package.json` has correct scripts
- Check for missing dependencies

---

## 📝 Quick Reference

**Railway Backend URL Format:**
```
https://your-service-name.up.railway.app
```

**Vercel Frontend URL Format:**
```
https://your-project-name.vercel.app
```

**Environment Variables Needed:**

**Railway (Backend):**
- `SECRET_KEY`
- `ENCRYPTION_KEY`
- `CORS_ORIGINS`

**Vercel (Frontend):**
- `VITE_API_URL`

---

Good luck with your deployment! 🚀

