# Quick Deployment Checklist

## 🚂 Railway (Backend) - 5 Steps

1. ✅ Go to https://railway.app → Sign in with GitHub
2. ✅ New Project → Deploy from GitHub → Select `Tarunsai01/ARIA`
3. ✅ Settings → Source → Root Directory: `backend`
4. ✅ Variables → Add:
   - `SECRET_KEY` = (generate below)
   - `ENCRYPTION_KEY` = (generate below)
   - `CORS_ORIGINS` = (add after Vercel deployment)
5. ✅ Settings → Deploy → Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. ✅ Copy backend URL from Settings → Networking

## 🎨 Vercel (Frontend) - 4 Steps

1. ✅ Go to https://vercel.com → Sign in with GitHub
2. ✅ Add New Project → Import `Tarunsai01/ARIA`
3. ✅ Root Directory: `frontend`
4. ✅ Environment Variables → Add:
   - `VITE_API_URL` = `https://your-railway-backend-url.railway.app`
5. ✅ Deploy → Copy frontend URL

## 🔗 Connect Them

1. ✅ Update Railway `CORS_ORIGINS` with Vercel URL
2. ✅ Test both URLs work

## 🔑 Generate Keys (Run Locally)

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

**Full detailed guide**: See `DEPLOYMENT_STEPS.md`

