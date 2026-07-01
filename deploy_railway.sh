#!/bin/bash
# Deployment script for Railway.app

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    npm install -g @railway/cli
fi

# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables
railway variable set LLM_PROVIDER=anthropic
echo "Set your API key:"
railway variable set ANTHROPIC_API_KEY

# Deploy
railway up

# Get the service URL
echo "Deployment complete!"
railway status
