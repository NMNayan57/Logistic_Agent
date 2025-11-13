# Free Hosting Deployment Guide

## Your Tech Stack
- **Backend**: Python FastAPI + SQLite
- **Frontend**: React + Vite + TailwindCSS
- **APIs**: OpenAI (requires API key)

---

## **Option 1: Render (RECOMMENDED - Easiest)**

### Pros:
- 100% Free tier for both backend & frontend
- Auto-deploy from GitHub
- Free SSL/HTTPS
- PostgreSQL database (if needed)

### Deployment Steps:

#### 1. Push to GitHub (if not already)
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2. Deploy Backend on Render

1. Go to https://render.com and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name**: logistics-agent-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. Add Environment Variables:
   - `OPENAI_API_KEY` = your-openai-key
   - `PORT` = 10000 (auto-set by Render)
   - `DATABASE_URL` = sqlite:///./logistics.db

6. Click **"Create Web Service"**
7. Copy the backend URL (e.g., `https://logistics-agent-api.onrender.com`)

#### 3. Deploy Frontend on Render

1. Click **"New +"** → **"Static Site"**
2. Connect the same GitHub repo
3. Configure:
   - **Name**: logistics-agent-frontend
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

4. Add Environment Variable:
   - `VITE_API_URL` = `https://logistics-agent-api.onrender.com` (your backend URL from step 2)

5. Click **"Create Static Site"**

**Done!** Your app will be live at `https://logistics-agent-frontend.onrender.com`

---

## **Option 2: Vercel (Frontend) + Render (Backend)**

### Best for: Production-grade frontend performance

#### Deploy Backend on Render (same as Option 1)

#### Deploy Frontend on Vercel

1. Go to https://vercel.com and sign up
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repo
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variable:
   - `VITE_API_URL` = `https://your-backend-url.onrender.com`

6. Click **"Deploy"**

**Done!** Your frontend will be at `https://your-project.vercel.app`

---

## **Option 3: Railway (Full-Stack in One Place)**

### Pros:
- $5 free credit/month
- Deploy both frontend & backend together
- Built-in PostgreSQL (if needed)

### Deployment Steps:

1. Go to https://railway.app and sign up
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect both services

5. Configure Backend:
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add `OPENAI_API_KEY`

6. Configure Frontend:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Start Command**: `npx vite preview --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: `VITE_API_URL` = backend service URL

---

## **Option 4: Fly.io (Best Free Tier for APIs)**

### Pros:
- 3 small VMs free forever
- Good for Python apps
- Global deployment

### Deployment Steps:

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login and create app:
```bash
fly auth login
fly launch
```

3. Follow prompts, then deploy:
```bash
fly deploy
```

---

## **Important Notes**

### Before Deploying:

1. **Update CORS Settings** in `src/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://your-frontend-url.vercel.app",  # Production
        "https://your-frontend-url.onrender.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Database Consideration**:
   - SQLite works on Render but data will reset on redeployment
   - For persistent data, use Render's free PostgreSQL
   - Update `DATABASE_URL` to PostgreSQL connection string

3. **OpenAI API Key**:
   - NEVER commit `.env` file to GitHub
   - Add `.env` to `.gitignore`
   - Set API key in hosting platform's environment variables

4. **Frontend Environment Variable**:
   - Create `frontend/.env.example`:
     ```
     VITE_API_URL=http://localhost:8000
     ```

---

## **Comparison Table**

| Platform | Backend | Frontend | Database | Free Tier | Best For |
|----------|---------|----------|----------|-----------|----------|
| **Render** | ✅ | ✅ | PostgreSQL | Forever | Easiest setup |
| **Vercel** | ❌ | ✅ | - | Forever | Best frontend performance |
| **Railway** | ✅ | ✅ | PostgreSQL | $5/month credit | Full-stack simplicity |
| **Fly.io** | ✅ | ❌ | PostgreSQL | 3 VMs free | Best for APIs |
| **PythonAnywhere** | ✅ | ❌ | MySQL | Forever (limited) | Python-only projects |

---

## **Recommended Approach for Your Project**

**For the easiest deployment:**

1. **Use Render for both** (Option 1)
   - Deploy backend first
   - Deploy frontend second with backend URL
   - Total setup time: 10-15 minutes

**For best performance:**

2. **Use Vercel + Render** (Option 2)
   - Render for backend
   - Vercel for frontend
   - Faster frontend, more reliable

---

## **Post-Deployment Checklist**

- [ ] Test all API endpoints
- [ ] Verify OpenAI API key works
- [ ] Check CORS settings
- [ ] Test database connections
- [ ] Monitor free tier limits
- [ ] Set up custom domain (optional)

---

## **Need Help?**

- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs
- Railway docs: https://docs.railway.app
