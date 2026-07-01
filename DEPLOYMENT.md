# Quick Deployment Guide - SHL Assessment Recommender

Choose one of the easiest options below to deploy your API in 5 minutes.

## 🚀 Option 1: Deploy to Render (Recommended - Easiest)

### Prerequisites
- GitHub account
- This repository pushed to GitHub

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "SHL Assessment Recommender"
   git remote add origin https://github.com/YOUR_USERNAME/shl-recommender.git
   git push -u origin main
   ```

2. **Create Render Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Select your GitHub repo
   - Fill in:
     - **Name**: `shl-recommender` (or any name)
     - **Region**: `Oregon` (or nearest to you)
     - **Branch**: `main`
     - **Runtime**: `Python 3.11`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `cd src && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - Click "Environment" tab
   - Add: `PYTHONUNBUFFERED=1`
   - Add: `LLM_PROVIDER=anthropic` (optional)
   - Add: `ANTHROPIC_API_KEY=sk-...` (optional, for future features)

4. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - You'll get a URL like: `https://shl-recommender.onrender.com`

5. **Test**
   ```bash
   curl https://shl-recommender.onrender.com/health
   # Should return: {"status":"ok"}
   ```

**That's it! Your API is live.** ✅

---

## 🚀 Option 2: Deploy to Railway.app

### Prerequisites
- GitHub account
- npm installed locally

### Steps

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login & Deploy**
   ```bash
   railway login
   railway init
   # Select "Python" as template
   # Name your project
   railway up
   ```

3. **Get Your URL**
   ```bash
   railway open
   # Or from dashboard, find your service URL
   ```

4. **Test**
   ```bash
   curl YOUR_RAILWAY_URL/health
   ```

---

## 🚀 Option 3: Deploy to Fly.io

### Prerequisites
- Fly.io account
- flyctl CLI installed

### Steps

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login & Launch**
   ```bash
   flyctl auth login
   flyctl launch
   # Answer prompts (Python, 8000 port)
   ```

3. **Deploy**
   ```bash
   flyctl deploy
   ```

4. **Get URL**
   ```bash
   flyctl status
   # URL will be shown
   ```

---

## 💻 Option 4: Run Locally (No Deployment)

Perfect for testing before deploying.

### Prerequisites
- Python 3.9+

### Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Service**
   ```bash
   # Windows
   start.bat
   
   # macOS/Linux
   bash start.sh
   
   # Or manually:
   cd src
   python -m uvicorn main:app --reload --port 8000
   ```

3. **Test**
   ```bash
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "Hiring Java developer"}]}'
   ```

---

## 🐳 Option 5: Deploy with Docker

Works on any platform that supports Docker.

### Steps

1. **Build Image**
   ```bash
   docker build -t shl-recommender .
   ```

2. **Run Container**
   ```bash
   docker run -p 8000:8000 \
     -e ANTHROPIC_API_KEY=sk-... \
     shl-recommender
   ```

3. **Test**
   ```bash
   curl http://localhost:8000/health
   ```

Or use Docker Compose:
```bash
docker-compose up
```

---

## ✅ Testing Your Deployment

Once deployed, test with these commands:

### Health Check
```bash
curl https://YOUR_API_URL/health
# Expected: {"status":"ok"}
```

### Basic Chat
```bash
curl -X POST https://YOUR_API_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need a Java developer assessment"}
    ]
  }'
```

### Conversation with Recommendations
```bash
curl -X POST https://YOUR_API_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hiring a Java developer"},
      {"role": "assistant", "content": "Got it. What seniority level?"},
      {"role": "user", "content": "Senior level with leadership needs"}
    ]
  }'
```

Expected response:
```json
{
  "reply": "Here are 8 assessments...",
  "recommendations": [
    {
      "name": "OPQ32r",
      "url": "https://www.shl.com/solutions/products/opq32r/",
      "test_type": "P"
    },
    ...
  ],
  "end_of_conversation": false
}
```

### Off-Topic Blocking
```bash
curl -X POST https://YOUR_API_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the market salary for Java developers?"}
    ]
  }'
```

Expected: Agent refuses, returns empty recommendations.

---

## 📊 Deployment Comparison

| Platform | Ease | Speed | Cost | Setup Time |
|----------|------|-------|------|-----------|
| **Render** | ⭐⭐⭐⭐⭐ | Fast | Free tier | 5 min |
| Railway | ⭐⭐⭐⭐ | Fast | Free tier | 5 min |
| Fly.io | ⭐⭐⭐⭐ | Fast | Free tier | 10 min |
| Local | ⭐⭐ | Instant | Free | 2 min |
| Docker | ⭐⭐⭐ | 1 min | Free | 3 min |

**Recommendation**: Use **Render** for simplicity. No CLI needed, just GitHub.

---

## 🔧 Troubleshooting

### "Service won't start"
Check logs on deployment platform:
- Render: Logs tab
- Railway: CLI or dashboard
- Fly: `flyctl logs`

### "Cold start taking too long"
This is normal for first deployment. Platform may take 1-2 minutes to start service. Subsequent requests are fast.

### "Port already in use (local)"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### "API returns 500 errors"
1. Check that `/health` endpoint works
2. Verify environment variables are set
3. Check platform logs for Python errors
4. Ensure requirements.txt is installed

### "Catalog not loading"
The service includes a fallback catalog (12 default assessments). If you see these, it's working fine.

---

## 📝 Submission

Once deployed:

1. **Copy your URL**
   - E.g., `https://shl-recommender.onrender.com`

2. **Test it one more time**
   ```bash
   curl YOUR_URL/health
   ```

3. **Submit via form**
   - Paste URL in submission form
   - Attach APPROACH.md
   - You're done! ✅

---

## 🆘 Need Help?

1. Check README.md for more details
2. Review APPROACH.md for design rationale
3. Check SUBMISSION.md for feature overview
4. Run local tests: `python tests/test_integration.py`

**You've got this!** 🚀
