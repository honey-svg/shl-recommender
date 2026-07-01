#!/bin/bash
# Deployment script for Render.com

# This script is for reference. To deploy to Render:
# 1. Push this repo to GitHub
# 2. Go to https://dashboard.render.com
# 3. Create a new Web Service
# 4. Connect your GitHub repository
# 5. Configure:
#    - Build Command: pip install -r requirements.txt
#    - Start Command: cd src && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
#    - Add environment variables (API keys)
# 6. Click Deploy

echo "Push code to GitHub and follow the steps above at https://dashboard.render.com"
