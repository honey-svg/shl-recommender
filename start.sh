#!/bin/bash
# Quick start script for local development

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
echo "Edit .env with your API key"

# Run the service
cd src
python -m uvicorn main:app --reload --port 8000
