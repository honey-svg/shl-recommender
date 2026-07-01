@echo off
REM Quick start script for local development on Windows

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Set up environment
copy .env.example .env
echo Edit .env with your API key

REM Run the service
cd src
python -m uvicorn main:app --reload --port 8000
