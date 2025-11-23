# Quick Deployment Checklist

## 🚀 Render (Backend) - 6 Steps

1. ✅ Go to https://render.com → Sign in with GitHub
2. ✅ New + → Web Service → Connect `Tarunsai01/ARIA` repo
3. ✅ Configure:
   - Name: `aria-backend`
   - **Language**: `Python 3` ⚠️ **NOT Docker!**
   - Root Directory: `backend` ⚠️ **IMPORTANT!**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. ✅ Environment → Add Variables:
   - `SECRET_KEY` = (generate below)
   - `ENCRYPTION_KEY` = (generate below)
   - `CORS_ORIGINS` = (add after Vercel deployment)
5. ✅ Create Web Service → Wait for deployment
6. ✅ Copy backend URL (e.g., `https://aria-backend.onrender.com`)

## 🎨 Vercel (Frontend) - 4 Steps

1. ✅ Go to https://vercel.com → Sign in with GitHub
2. ✅ Add New Project → Import `Tarunsai01/ARIA`
3. ✅ Root Directory: `frontend`
4. ✅ Environment Variables → Add:
   - `VITE_API_URL` = `https://your-railway-backend-url.railway.app`
5. ✅ Deploy → Copy frontend URL

## 🔗 Connect Them

1. ✅ Update Render `CORS_ORIGINS` with Vercel URL (Environment tab)
2. ✅ Wait 2-3 minutes for redeploy
3. ✅ Test both URLs work

## 🔑 Generate Keys (Run Locally)

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

**Full detailed guide**: See `DEPLOYMENT_STEPS_RENDER.md`

