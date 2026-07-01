# 🎯 NEXT STEPS - Deploy and Submit

## Three Simple Steps to Complete the Assignment

---

## STEP 1️⃣: Push Code to GitHub (5 minutes)

### Open Command Prompt and run:
```bash
cd c:\Users\DELL\OneDrive\Desktop\shl
git init
git add .
git commit -m "SHL Assessment Recommender"
```

### Create GitHub repo:
1. Go to https://github.com/new
2. Name it: `shl-recommender`
3. Click "Create repository"
4. Copy the URL (like: `https://github.com/YOUR_USERNAME/shl-recommender.git`)

### Continue in Command Prompt:
```bash
git remote add origin https://github.com/YOUR_USERNAME/shl-recommender.git
git branch -M main
git push -u origin main
```

✅ **Done!** Your code is on GitHub.

---

## STEP 2️⃣: Deploy to Render (5-10 minutes)

### Follow these exact steps:

1. Go to https://dashboard.render.com
2. Sign up (free account, no credit card needed)
3. Click **"New +"** button (top right)
4. Select **"Web Service"**
5. Click **"Connect a repository"**
6. Find and select `shl-recommender`

### Fill in these settings:

| Field | Enter This |
|-------|-----------|
| Name | `shl-recommender` |
| Environment | `Python 3` |
| Region | `Oregon` (default) |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `cd src && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Add Environment Variables:
Click "Add Environment Variable" and add:

| Key | Value |
|-----|-------|
| `PYTHONUNBUFFERED` | `1` |
| `LLM_PROVIDER` | `groq` |
| `GROQ_API_KEY` | `<your_key_here>` |

### Click "Create Web Service"

⏳ Wait 2-3 minutes for deployment...

✅ **Done!** Your API is live!

### Get Your URL:
Once it shows "Running", you'll see something like:
```
https://shl-recommender.onrender.com
```
**Copy this URL** - you'll need it for testing and submission.

---

## STEP 3️⃣: Test Your Deployment (5 minutes)

### Test Health Check:
```bash
curl https://YOUR_URL/health
```

Expected response:
```json
{"status":"ok"}
```

### Test Chat Endpoint:
```bash
curl -X POST https://YOUR_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "I am hiring a Java developer"}]}'
```

Expected response:
```json
{
  "reply": "...",
  "recommendations": [],
  "end_of_conversation": false
}
```

### Test Multi-Turn Conversation:
```bash
curl -X POST https://YOUR_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "I am hiring a Java developer"}, {"role": "assistant", "content": "Got it. What seniority?"}, {"role": "user", "content": "Senior level, needs leadership skills"}]}'
```

Expected: Should return recommendations with shl.com URLs.

✅ **Done!** API is working!

---

## STEP 4️⃣: Submit Your Work

### Gather These Items:
1. **Your Render URL**: `https://YOUR_URL` (e.g., `https://shl-recommender.onrender.com`)
2. **APPROACH.md file**: Located in `c:\Users\DELL\OneDrive\Desktop\shl\APPROACH.md`

### Find the Submission Form:
(You'll have been given a form link - it should be in your assignment email)

### Fill in the Form:
- **API Endpoint URL**: Paste your Render URL here
- **Approach Document**: Upload APPROACH.md file
- Click Submit

### After Submission:
✅ The evaluator will:
- Test your /health endpoint
- Run conversations against your /chat endpoint
- Grade on schema compliance and assessment recommendations
- Calculate your Recall@10 score

---

## 🎯 Success = Three Green Checkmarks

After following these steps, you should have:

✅ **Working Deployment**
- [ ] Service running on Render
- [ ] /health endpoint responds with 200
- [ ] /chat endpoint accepts POST requests

✅ **Correct Responses**
- [ ] Schema matches specification (reply, recommendations, end_of_conversation)
- [ ] All URLs contain "shl.com"
- [ ] Off-topic requests return empty recommendations
- [ ] Vague queries ask for clarification

✅ **Submitted**
- [ ] Form filled with URL and APPROACH.md
- [ ] Submission confirmed

---

## ⏱️ Total Time: ~20-30 Minutes

| Step | Time |
|------|------|
| GitHub setup | 5 min |
| Render deployment | 5 min |
| Waiting for startup | 3 min |
| Testing | 5 min |
| Submission | 2 min |
| **Total** | **~20 min** |

---

## 🆘 If Something Goes Wrong

### "GitHub push failed"
- Install Git: https://git-scm.com/download/win
- Make sure you're in the right directory: `cd c:\Users\DELL\OneDrive\Desktop\shl`

### "Render build failed"
- Check build logs in Render dashboard
- Make sure files uploaded correctly
- Try redeploying

### "Render service won't start"
- Wait 5 minutes - first startup takes time
- Check service status shows "Running"
- Refresh the page

### "API returning 500 errors"
- Check Render logs for errors
- Verify GROQ_API_KEY is set correctly
- Make sure all files are in place

### "Endpoints not responding"
- Wait 2-3 minutes for cold start
- Try hitting /health first
- Check Render status page

---

## 📚 Reference Documents

If you need more details:

- **RENDER_DEPLOYMENT_STEPS.md** - Detailed Render walkthrough
- **DEPLOYMENT_CHECKLIST.md** - Full checklist
- **APPROACH.md** - Your design document (required for submission)
- **README.md** - Project overview
- **pre_deployment_test.py** - Local testing script

---

## 💡 Remember

- **You've already tested locally** ✓ All tests pass
- **Code is production-ready** ✓ No changes needed
- **GROQ is configured** ✓ In .env file
- **Documentation is complete** ✓ APPROACH.md ready

**Just deploy it!** 🚀

---

## ✅ Final Checklist Before Submitting

- [ ] Code pushed to GitHub
- [ ] Service deployed on Render (status = Running)
- [ ] /health returns {"status":"ok"}
- [ ] /chat endpoint responds correctly
- [ ] Recommendations have shl.com URLs
- [ ] APPROACH.md file ready
- [ ] Form submission completed

---

**You're ready to submit!** 🎉

Good luck! The assignment is complete and production-ready.
