# SHL Assessment Recommender - Development Guide

## Quick Start

### Prerequisites
- Python 3.9+
- pip or conda

### Local Setup

```bash
# Windows
start.bat

# macOS/Linux
bash start.sh
```

Or manually:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API credentials

# Run service
cd src
python -m uvicorn main:app --reload --port 8000
```

### Testing Locally

```bash
cd tests
python evaluate.py
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I am hiring a Java developer"}
    ]
  }'
```

## Project Structure

```
shl/
├── src/
│   ├── main.py           # FastAPI application
│   ├── agent.py          # Conversation agent logic
│   ├── catalog.py        # SHL catalog management
│   └── __init__.py
├── data/
│   └── catalog_cache.json # Cached catalog (auto-generated)
├── tests/
│   └── evaluate.py       # Evaluation harness
├── requirements.txt      # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version
└── README.md
```

## Configuration

Edit `.env` to configure:
- LLM provider (anthropic, openai, groq)
- API keys
- Debug mode

## Deployment

### Render.com
1. Push to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Set environment variables
5. Deploy

### Railway.app
1. Install Railway CLI: `npm i -g @railway/cli`
2. Run: `railway up`
3. Set environment variables in dashboard

### Fly.io
1. Install Fly CLI
2. Run: `flyctl launch`
3. Deploy: `flyctl deploy`

## Key Components

### Catalog (`src/catalog.py`)
- Scrapes SHL product catalog
- Caches results for performance
- Provides search and filtering
- Falls back to curated defaults

### Agent (`src/agent.py`)
- Manages conversation state
- Extracts user context
- Generates clarification questions
- Scores and ranks assessments
- Handles comparisons

### API (`src/main.py`)
- Stateless chat endpoint
- Health check
- Request validation
- Error handling

## Testing Strategy

### Unit Tests
- Agent context extraction
- Assessment scoring
- Response formatting

### Integration Tests
- Full conversation flows
- Catalog loading
- API schema compliance

### Evaluation
- Run against provided traces
- Calculate Recall@10 metrics
- Test edge cases

See `tests/evaluate.py` for evaluation harness.

## Troubleshooting

### Catalog Loading Issues
- Check internet connection for web scraping
- Verify `data/` directory exists
- Check `catalog_cache.json` format

### API Port Issues
- Change port in `Procfile` or set `PORT` env variable
- Ensure port is not in use: `netstat -an | grep 8000`

### LLM Integration Issues
- Verify API keys in `.env`
- Check LLM provider status
- See logs for detailed errors

## Development Notes

- The agent is intentionally stateless per the requirements
- Context is extracted from full conversation history each turn
- Recommendations are limited to 1-10 items
- All URLs must come from SHL catalog
- Turn limit is 8 (user + assistant messages combined)
