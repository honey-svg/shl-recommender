# Step-by-Step Render Deployment Guide

## Step 1: Prepare Your GitHub Repository

### 1a. Initialize Git (if not already done)
```bash
cd c:\Users\DELL\OneDrive\Desktop\shl
git init
git add .
git commit -m "SHL Assessment Recommender - Initial commit"
```

### 1b. Create GitHub Repository
1. Go to https://github.com/new
2. Create new repository named `shl-recommender`
3. Do NOT initialize with README (you already have files)
4. Click "Create repository"

### 1c. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/shl-recommender.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### 2a. Go to Render Dashboard
1. Visit https://dashboard.render.com
2. Sign up (free account) if you don't have one
3. Verify your email

### 2b. Create New Web Service
1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Search for `shl-recommender`
5. Click **"Connect"**

### 2c. Configure Service
Fill in these exact settings:

| Field | Value |
|-------|-------|
| **Name** | `shl-recommender` |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (or closest to you) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd src && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |

### 2d. Add Environment Variables
1. Scroll down to **"Environment"** section
2. Click **"Add Environment Variable"**
3. Add these:

| Key | Value |
|-----|-------|
| `PYTHONUNBUFFERED` | `1` |
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | `<your_key_here>` |

### 2e. Create Service
1. Scroll to bottom
2. Click **"Create Web Service"**
3. Wait 2-3 minutes for deployment

### 2f. Get Your URL
Once deployment completes:
1. You'll see your service dashboard
2. At the top, you'll see: `https://shl-recommender.onrender.com` (or similar)
3. **Copy this URL** - you'll need it for testing

## Step 3: Test Your Deployment

### 3a. Health Check
```bash
# Replace with YOUR actual URL
curl https://YOUR_URL/health
```

Expected response:
```json
{"status":"ok"}
```

### 3b. Test Basic Chat
```bash
curl -X POST https://YOUR_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need a Java developer assessment"}
    ]
  }'
```

Expected response:
```json
{
  "reply": "What's the job title or role you're hiring for?...",
  "recommendations": [],
  "end_of_conversation": false
}
```

### 3c. Test Multi-Turn Conversation
```bash
curl -X POST https://YOUR_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I am hiring a Java developer"},
      {"role": "assistant", "content": "Got it. What seniority level?"},
      {"role": "user", "content": "Mid-level, around 4 years experience, needs leadership skills"}
    ]
  }'
```

Expected response:
```json
{
  "reply": "Here are X assessments I'd recommend...",
  "recommendations": [
    {"name": "OPQ32r", "url": "https://www.shl.com/...", "test_type": "P"},
    ...
  ],
  "end_of_conversation": false
}
```

### 3d. Test Off-Topic Blocking
```bash
curl -X POST https://YOUR_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the market salary for Java developers?"}
    ]
  }'
```

Expected: Agent refuses with empty recommendations

## Step 4: Submit Your Work

### 4a. Gather Submission Materials
You need:
1. **Your Render URL** - from the dashboard (e.g., `https://shl-recommender.onrender.com`)
2. **APPROACH.md file** - Located in: `c:\Users\DELL\OneDrive\Desktop\shl\APPROACH.md`

### 4b. Submit via Form
1. Go to the submission form link provided
2. Fill in:
   - **API Endpoint URL**: Your Render URL
   - **Approach Document**: Upload APPROACH.md
3. Click Submit

### 4c. Verify Submission
After submitting, the evaluator will:
1. Call GET `/health` on your endpoint
2. Run automated multi-turn conversations
3. Test edge cases (vague queries, off-topic, refinement)
4. Grade on schema compliance and Recall@10

---

## Troubleshooting

### "Deployment Failed"
1. Check build logs in Render dashboard
2. Common issues:
   - Missing `requirements.txt` - ✓ You have it
   - Python syntax error - Run locally first to verify
   - Wrong start command - Use exact command above

### "Service returning 500 errors"
1. Check logs: Click service → Logs tab
2. Look for Python errors
3. Verify all files exist in `src/` directory

### "Cold start taking long (first request slow)"
- Normal on Render free tier (up to 2 minutes on first request)
- Subsequent requests are fast
- This is acceptable per assignment specs

### "URL not working"
1. Wait 5-10 minutes after deployment
2. Check service status: Click refresh button
3. Verify service is "Running" (green indicator)

---

## Quick Reference

| Item | Value |
|------|-------|
| **Dashboard** | https://dashboard.render.com |
| **Your Service Type** | Web Service (Python) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd src && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Health Check URL** | `YOUR_URL/health` |
| **Chat Endpoint** | `YOUR_URL/chat` (POST) |

---

## Summary

✅ **After following these steps you will have:**
- Live API deployed on Render
- Both /health and /chat endpoints working
- GROQ API configured
- Ready for automated evaluation

**Estimated time: 10-15 minutes**
