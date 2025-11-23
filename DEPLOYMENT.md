# ARIA Deployment Guide

## Overview

**Yes, you need to deploy backend and frontend separately** because:
- **Backend**: Python/FastAPI application (needs Python runtime)
- **Frontend**: React application (needs to be built to static files)

---

## 🚀 Deployment Options

### Option 1: Easy Cloud Platforms (Recommended for Quick Start)

#### Frontend: Vercel / Netlify
#### Backend: Railway / Render / Fly.io

### Option 2: Traditional VPS
- Deploy both on same server (Nginx for frontend, Gunicorn for backend)

### Option 3: Docker
- Containerize both and deploy anywhere

---

## 📦 Frontend Deployment

### Step 1: Build the Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with static files.

### Step 2: Configure API URL

Create `.env.production` in `frontend/`:
```env
VITE_API_URL=https://your-backend-url.com
```

Rebuild after setting:
```bash
npm run build
```

### Step 3: Deploy to Vercel (Easiest)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd frontend
   vercel
   ```

3. **Set Environment Variable:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend-url.com`
   - Redeploy

### Step 3 Alternative: Deploy to Netlify

1. **Install Netlify CLI:**
   ```bash
   npm i -g netlify-cli
   ```

2. **Deploy:**
   ```bash
   cd frontend
   netlify deploy --prod
   ```

3. **Set Environment Variable:**
   - Netlify Dashboard → Site Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend-url.com`

### Step 3 Alternative: Deploy to GitHub Pages

1. **Install gh-pages:**
   ```bash
   npm install --save-dev gh-pages
   ```

2. **Update `package.json`:**
   ```json
   {
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d dist"
     },
     "homepage": "https://yourusername.github.io/ARIA"
   }
   ```

3. **Deploy:**
   ```bash
   npm run deploy
   ```

---

## 🔧 Backend Deployment

### Step 1: Prepare Backend

1. **Create `backend/.env` file:**
   ```env
   SECRET_KEY=your-secret-key-here
   ENCRYPTION_KEY=your-encryption-key-here
   DATABASE_URL=sqlite:///./aria.db
   CORS_ORIGINS=https://your-frontend-url.com,https://your-frontend-url.vercel.app
   ```

2. **Generate Keys:**
   ```python
   from cryptography.fernet import Fernet
   import secrets
   
   print("SECRET_KEY:", secrets.token_urlsafe(32))
   print("ENCRYPTION_KEY:", Fernet.generate_key().decode())
   ```

### Step 2: Deploy to Railway (Easiest)

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize:**
   ```bash
   cd backend
   railway init
   ```

4. **Set Environment Variables:**
   ```bash
   railway variables set SECRET_KEY=your-secret-key
   railway variables set ENCRYPTION_KEY=your-encryption-key
   railway variables set CORS_ORIGINS=https://your-frontend-url.com
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

6. **Get Backend URL:**
   - Railway Dashboard → Your Service → Settings → Domains
   - Copy the URL (e.g., `https://aria-backend.railway.app`)

### Step 2 Alternative: Deploy to Render

1. **Create `render.yaml` in `backend/`:**
   ```yaml
   services:
     - type: web
       name: aria-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: SECRET_KEY
           sync: false
         - key: ENCRYPTION_KEY
           sync: false
         - key: CORS_ORIGINS
           value: https://your-frontend-url.com
   ```

2. **Deploy:**
   - Connect GitHub repo to Render
   - Select `backend/` as root directory
   - Add environment variables in dashboard
   - Deploy

### Step 2 Alternative: Deploy to Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `backend/fly.toml`:**
   ```toml
   app = "aria-backend"
   primary_region = "iad"

   [build]

   [env]
     PORT = "8080"

   [[services]]
     internal_port = 8080
     protocol = "tcp"

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

3. **Deploy:**
   ```bash
   cd backend
   fly launch
   fly secrets set SECRET_KEY=your-secret-key
   fly secrets set ENCRYPTION_KEY=your-encryption-key
   fly secrets set CORS_ORIGINS=https://your-frontend-url.com
   fly deploy
   ```

### Step 2 Alternative: Deploy to Traditional VPS (Ubuntu/Debian)

1. **SSH into server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx
   ```

3. **Clone and setup:**
   ```bash
   git clone your-repo-url
   cd ARIA/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Create systemd service `/etc/systemd/system/aria-backend.service`:**
   ```ini
   [Unit]
   Description=ARIA Backend API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/ARIA/backend
   Environment="PATH=/path/to/ARIA/backend/venv/bin"
   ExecStart=/path/to/ARIA/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start service:**
   ```bash
   sudo systemctl start aria-backend
   sudo systemctl enable aria-backend
   ```

6. **Configure Nginx `/etc/nginx/sites-available/aria-backend`:**
   ```nginx
   server {
       listen 80;
       server_name api.yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Enable and restart:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/aria-backend /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 🐳 Docker Deployment (Alternative)

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Deploy with Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - ./backend/user_files:/app/user_files
      - ./backend/aria.db:/app/aria.db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

Deploy:
```bash
docker-compose up -d
```

---

## ✅ Post-Deployment Checklist

### Backend:
- [ ] Environment variables set (SECRET_KEY, ENCRYPTION_KEY, CORS_ORIGINS)
- [ ] Database initialized
- [ ] Backend URL accessible (test: `https://your-backend.com/health`)
- [ ] CORS allows frontend domain

### Frontend:
- [ ] `VITE_API_URL` points to backend URL
- [ ] Frontend built and deployed
- [ ] Frontend URL accessible
- [ ] Can make API calls from frontend

### Testing:
- [ ] Register/Login works
- [ ] API calls succeed
- [ ] File uploads work
- [ ] Real-time features work

---

## 🔗 Update Frontend API URL

After backend is deployed, update frontend:

1. **Get backend URL** (e.g., `https://aria-backend.railway.app`)

2. **Update frontend environment:**
   - Vercel/Netlify: Add `VITE_API_URL` in dashboard
   - Rebuild frontend

3. **Or update `frontend/.env.production`:**
   ```env
   VITE_API_URL=https://aria-backend.railway.app
   ```

---

## 📝 Recommended Setup

**For Quick Start:**
- Frontend: **Vercel** (free, easy, automatic deployments)
- Backend: **Railway** (free tier, easy setup)

**For Production:**
- Frontend: **Vercel** or **Cloudflare Pages**
- Backend: **Railway**, **Render**, or **Fly.io**
- Database: **PostgreSQL** (instead of SQLite)

---

## 🆘 Troubleshooting

### CORS Errors
- Make sure `CORS_ORIGINS` includes your frontend URL
- Check for trailing slashes
- Include both `http://` and `https://` if needed

### API Not Found
- Verify `VITE_API_URL` is set correctly
- Check backend is running
- Test backend directly: `curl https://your-backend.com/health`

### Build Errors
- Clear `node_modules` and reinstall
- Check Node.js version (18+)
- Verify all environment variables are set

---

## 📚 Additional Resources

- [Vercel Deployment](https://vercel.com/docs)
- [Railway Deployment](https://docs.railway.app)
- [Render Deployment](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

