# Step-by-Step Deployment Guide: Vercel (Frontend) + Render (Backend)

## 🎯 Overview

- **Frontend**: Deploy to Vercel (Free, Easy, Fast)
- **Backend**: Deploy to Render (Free tier available, Easy setup)

---

## 📋 Prerequisites

1. **GitHub Account** (you already have this - code is at https://github.com/Tarunsai01/ARIA)
2. **Vercel Account** (free) - Sign up at https://vercel.com
3. **Render Account** (free tier) - Sign up at https://render.com
4. **API Keys Ready**:
   - OpenAI API key (if using OpenAI)
   - Google Gemini API key (if using Gemini)

---

## 🚀 Part 1: Deploy Backend to Render

### Step 1: Create Render Account

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (recommended - one click)
4. Authorize Render to access your GitHub repositories

### Step 2: Create New Web Service

1. In Render Dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Connect account"** if you haven't connected GitHub yet
4. Find and select your repository: **`Tarunsai01/ARIA`**
5. Click **"Connect"**

### Step 3: Configure Backend Service

Fill in the service configuration:

**Basic Settings:**
- **Name**: `aria-backend` (or any name you like)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: `backend` ⚠️ **IMPORTANT: Set this!**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Select **"Free"** plan (or paid if you prefer)

### Step 4: Set Environment Variables

Scroll down to **"Environment Variables"** section and click **"Add Environment Variable"**:

Add these variables one by one:

1. **SECRET_KEY**
   - Click **"Add Environment Variable"**
   - Key: `SECRET_KEY`
   - Value: (generate using command below)
   - Click **"Save"**

2. **ENCRYPTION_KEY**
   - Click **"Add Environment Variable"**
   - Key: `ENCRYPTION_KEY`
   - Value: (generate using command below)
   - Click **"Save"**

3. **CORS_ORIGINS**
   - Click **"Add Environment Variable"**
   - Key: `CORS_ORIGINS`
   - Value: `https://your-frontend-url.vercel.app` (you'll update this after Vercel deployment)
   - Click **"Save"**

**Generate Keys (Run in your local terminal):**
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Or use Python script:**
```bash
cd backend
python generate_keys.py
```

### Step 5: Advanced Settings (Optional)

1. **Auto-Deploy**: ✅ Enabled (deploys on every push to main)
2. **Health Check Path**: `/health` (optional, but recommended)
3. **Docker**: Leave unchecked (we're using Python runtime)

### Step 6: Deploy

1. Scroll to bottom and click **"Create Web Service"**
2. Render will start building and deploying (takes 3-5 minutes)
3. Watch the **"Logs"** tab to see build progress
4. Wait for: `Your service is live at https://...`

### Step 7: Get Backend URL

1. Once deployment completes, you'll see:
   - **Service URL**: `https://aria-backend.onrender.com` (or similar)
2. **Copy this URL** - you'll need it for frontend!
3. Test it: Open the URL in browser
   - Should see: `{"message":"ARIA API - Two-way Sign Language Interpreter","version":"2.0.0"}`
4. Test health: `https://your-backend-url.onrender.com/health`
   - Should return: `{"status":"healthy","version":"2.0.0"}`

### Step 8: Update CORS (After Frontend Deployment)

1. Go back to Render Dashboard → Your Service
2. Go to **"Environment"** tab
3. Find `CORS_ORIGINS` variable
4. Click **"Edit"**
5. Update value to include your Vercel URL:
   ```
   https://your-frontend-url.vercel.app,https://your-frontend-url-xyz.vercel.app
   ```
6. Click **"Save Changes"**
7. Render will automatically redeploy

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

1. **Framework Preset**: Vercel will auto-detect **Vite** ✅
2. **Root Directory**: 
   - Click **"Edit"** next to Root Directory
   - Change from `/` to `frontend`
   - Click **"Continue"**
3. **Build Command**: `npm run build` (auto-filled) ✅
4. **Output Directory**: `dist` (auto-filled) ✅
5. **Install Command**: `npm install` (auto-filled) ✅

### Step 4: Set Environment Variables

1. Scroll down to **"Environment Variables"** section
2. Click **"Add"** button
3. Add this variable:

**Variable:**
- **Key**: `VITE_API_URL`
- **Value**: `https://your-backend-url.onrender.com`
  - ⚠️ **Replace with your actual Render backend URL from Step 7 above!**
- **Environment**: Select all (Production, Preview, Development)
- Click **"Add"**

### Step 5: Deploy

1. Click **"Deploy"** button at the bottom
2. Wait for build to complete (1-2 minutes)
3. Vercel will show you the deployment URL
4. Example: `https://aria-frontend.vercel.app` or `https://aria-xyz123.vercel.app`

### Step 6: Get Frontend URL

1. After deployment, copy your frontend URL
2. It will be displayed on the deployment page
3. **Save this URL** - you'll need it to update CORS in Render

---

## 🔗 Part 3: Connect Frontend to Backend

### Step 1: Update Backend CORS in Render

1. Go to **Render Dashboard** → Your Backend Service
2. Click **"Environment"** tab
3. Find `CORS_ORIGINS` variable
4. Click **"Edit"** (pencil icon)
5. Update the value to include your Vercel URL:

```env
https://your-frontend-url.vercel.app,https://your-frontend-url-xyz.vercel.app
```

**Note**: 
- Add your main Vercel domain
- Add any preview domains (Vercel creates preview URLs for branches)
- Separate multiple URLs with commas (no spaces)

6. Click **"Save Changes"**
7. Render will automatically redeploy (takes 2-3 minutes)

### Step 2: Verify Connection

1. Open your Vercel frontend URL
2. Try to register/login
3. Check browser console (F12) for any CORS errors
4. If you see CORS errors, wait a few minutes for redeploy and try again

---

## ✅ Part 4: Verify Deployment

### Test Frontend

1. Open your Vercel URL: `https://your-app.vercel.app`
2. You should see the ARIA landing page
3. Try to:
   - Register a new account
   - Login
   - Use Speech to Sign feature
   - Use Sign to Speech feature

### Test Backend

1. Open: `https://your-backend-url.onrender.com/docs`
2. You should see Swagger API documentation
3. Test the `/health` endpoint
4. Test other endpoints if needed

### Common Issues

**CORS Errors:**
- ✅ Make sure `CORS_ORIGINS` in Render includes your exact Vercel URL
- ✅ Check for trailing slashes (don't include them)
- ✅ Wait 2-3 minutes after updating CORS (redeploy takes time)
- ✅ Clear browser cache and try again

**API Not Found:**
- ✅ Verify `VITE_API_URL` in Vercel matches your Render URL exactly
- ✅ Check Render logs for errors (Dashboard → Logs tab)
- ✅ Make sure backend is running (check Render dashboard status)

**Build Errors:**
- ✅ Check Vercel build logs (click on deployment → View Logs)
- ✅ Check Render build logs (Dashboard → Logs tab)
- ✅ Verify all environment variables are set correctly
- ✅ Check for missing dependencies

**Backend Won't Start:**
- ✅ Check Render logs for Python errors
- ✅ Verify all environment variables are set
- ✅ Check Python version (should be 3.12+)
- ✅ Verify `requirements.txt` is correct

---

## 🔄 Part 5: Automatic Deployments

### Both platforms support auto-deploy:

**Render:**
- ✅ Automatically deploys when you push to `main` branch
- ✅ You can disable auto-deploy in Settings if needed
- ✅ Manual deploy: Dashboard → Manual Deploy

**Vercel:**
- ✅ Automatically deploys when you push to `main` branch
- ✅ Creates preview deployments for other branches
- ✅ No configuration needed

### To update your app:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Both Render and Vercel will automatically redeploy!
4. Check deployment status in their dashboards

---

## 📊 Part 6: Monitoring & Logs

### Render Logs

1. Go to Render Dashboard → Your Service
2. Click **"Logs"** tab
3. See real-time logs, build logs, and runtime logs
4. Filter by: All, Build, Runtime

### Vercel Logs

1. Go to Vercel Dashboard → Your Project
2. Click on a deployment
3. See build logs and function logs
4. Check for errors or warnings

### Render Metrics

1. Render Dashboard → Your Service
2. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

---

## 💰 Part 7: Free Tier Limits

### Render Free Tier:
- ✅ 750 hours/month (enough for 24/7 operation)
- ✅ Auto-sleeps after 15 minutes of inactivity
- ✅ Wakes up automatically on first request (may take 30-60 seconds)
- ✅ 512 MB RAM
- ✅ 0.1 CPU

**Note**: Free tier services sleep after inactivity. First request after sleep takes 30-60 seconds to wake up.

### Vercel Free Tier:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Perfect for frontend hosting
- ✅ No sleep/wake delays

---

## 🎉 You're Done!

Your ARIA app is now live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`

### Next Steps:

1. **Test the app** - Register, login, use all features
2. **Share the URL** - Your app is publicly accessible
3. **Monitor usage** - Check Render and Vercel dashboards
4. **Set up custom domains** (optional):
   - Vercel: Settings → Domains
   - Render: Settings → Custom Domains

---

## 🆘 Troubleshooting

### Backend sleeps (Free tier):
- **Issue**: Backend takes 30-60 seconds to respond after inactivity
- **Solution**: This is normal for Render free tier. First request wakes it up.
- **Alternative**: Upgrade to paid plan for always-on service

### CORS errors persist:
1. Double-check `CORS_ORIGINS` in Render includes exact Vercel URL
2. Make sure no trailing slashes
3. Wait 3-5 minutes after updating (redeploy time)
4. Clear browser cache
5. Check browser console for exact error message

### Build fails on Render:
1. Check **Logs** tab for error messages
2. Verify Python version (Render auto-detects, but check)
3. Check `requirements.txt` is correct
4. Verify Root Directory is set to `backend`
5. Check Start Command is correct

### Environment variables not working:
1. Verify variables are set in Render Dashboard
2. Check variable names match exactly (case-sensitive)
3. Redeploy after adding/changing variables
4. Check logs for variable-related errors

---

## 📝 Quick Reference

**Render Backend URL Format:**
```
https://your-service-name.onrender.com
```

**Vercel Frontend URL Format:**
```
https://your-project-name.vercel.app
```

**Environment Variables Needed:**

**Render (Backend):**
- `SECRET_KEY` (required)
- `ENCRYPTION_KEY` (required)
- `CORS_ORIGINS` (required - update after Vercel deployment)

**Vercel (Frontend):**
- `VITE_API_URL` (required - your Render backend URL)

---

## 🔑 Generate Keys Script

Create a file `generate_keys.py` in `backend/`:

```python
import secrets
from cryptography.fernet import Fernet

print("SECRET_KEY=" + secrets.token_urlsafe(32))
print("ENCRYPTION_KEY=" + Fernet.generate_key().decode())
```

Run: `python generate_keys.py`

---

Good luck with your deployment! 🚀

