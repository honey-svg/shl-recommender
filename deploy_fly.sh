#!/bin/bash
# Deployment script for Fly.io

# Install Fly CLI if not present
if ! command -v flyctl &> /dev/null; then
    curl -L https://fly.io/install.sh | sh
fi

# Login to Fly
flyctl auth login

# Launch app
flyctl launch

# Set environment variables
flyctl secrets set ANTHROPIC_API_KEY=your_key_here LLM_PROVIDER=anthropic

# Deploy
flyctl deploy

echo "Deployment complete! View at: $(flyctl info --json | jq '.Hostname')"
