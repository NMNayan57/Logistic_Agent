# Render Deployment Fix

## Issue
The `$PORT` environment variable wasn't being passed correctly to uvicorn.

## Solutions (Choose One)

### Option 1: Update Start Command in Render Dashboard (FASTEST)

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your `logistics-agent-api` service
3. Go to **Settings** tab
4. Scroll to **Start Command**
5. Replace the current command with:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 10000
   ```
   OR
   ```bash
   bash start.sh
   ```
6. Click **Save Changes**
7. Click **Manual Deploy** → **Deploy latest commit**

### Option 2: Wait for Auto-Deploy (Automatic)

The fix has been pushed to GitHub (commit `eb22b24`). Render will auto-detect and redeploy in ~1 minute.

---

## What Was Fixed

1. **Created `start.sh`**: A bash script that properly handles the PORT variable
2. **Updated `render.yaml`**: Changed start command to use the bash script
3. **Updated `Procfile`**: Added fallback port for other platforms

---

## Verification

Once deployed successfully, you should see:
```
✓ Build successful
✓ Starting service...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

---

## Alternative: Manual Port Configuration

If the issue persists, Render might not be setting the PORT variable. In that case:

1. In Render Dashboard → Your Service → Settings
2. Add Environment Variable:
   - **Key**: `PORT`
   - **Value**: `10000`
3. Save and redeploy

---

## Next Step: Frontend Deployment

Once backend is running successfully:
1. Copy your backend URL (e.g., `https://logistics-agent-api.onrender.com`)
2. Deploy frontend with that URL as `VITE_API_URL`
