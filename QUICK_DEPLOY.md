# Quick Deploy - 5 Minutes Setup

## Fastest Way: Render (Both Backend + Frontend FREE)

### Step 1: Push to GitHub (2 min)
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Ready for deployment"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy Backend on Render (2 min)
1. Go to https://render.com → Sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Select your repository
4. Fill in:
   - **Name**: `logistics-agent-api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Click **"Advanced"** → Add Environment Variable:
   - `OPENAI_API_KEY` = `your-key-here`
6. Click **"Create Web Service"**
7. **COPY THE URL** (e.g., `https://logistics-agent-api.onrender.com`)

### Step 3: Deploy Frontend on Render (1 min)
1. Click **"New +"** → **"Static Site"**
2. Select same repository
3. Fill in:
   - **Name**: `logistics-agent-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Click **"Advanced"** → Add Environment Variable:
   - `VITE_API_URL` = `https://logistics-agent-api.onrender.com` (URL from Step 2)
5. Click **"Create Static Site"**

### DONE! 🎉
Your app will be live at:
- Frontend: `https://logistics-agent-frontend.onrender.com`
- Backend API: `https://logistics-agent-api.onrender.com`

---

## Alternative: Vercel (Frontend) + Render (Backend)

### Backend: Same as above (Step 2)

### Frontend on Vercel:
1. Go to https://vercel.com → Import Project
2. Select your GitHub repo
3. Set:
   - **Root Directory**: `frontend`
   - **Framework**: Vite
4. Add Environment Variable:
   - `VITE_API_URL` = `https://your-backend-url.onrender.com`
5. Click **"Deploy"**

---

## Troubleshooting

### Backend not starting?
- Check Environment Variables in Render dashboard
- Check logs: Click on your service → "Logs" tab

### Frontend can't connect to backend?
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in `src/main.py`

### Database issues?
- SQLite data resets on redeploy on Render
- For persistent data, upgrade to PostgreSQL (still free on Render)

---

## Cost Breakdown
- **Render Free Tier**: Both backend + frontend = $0/month
- **OpenAI API**: Pay per use (typically $1-5/month for testing)
- **Total**: ~$1-5/month

---

## Next Steps After Deployment
- [ ] Test all features on live site
- [ ] Set up custom domain (optional)
- [ ] Enable monitoring/alerts
- [ ] Add GitHub Actions for auto-deploy on push
