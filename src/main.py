"""
FastAPI service for SHL Assessment Recommender.
Provides /health and /chat endpoints.
"""
import os
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from catalog import get_catalog
from agent import ConversationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational agent for SHL assessment recommendations",
    version="1.0.0"
)

# Initialize catalog on startup
catalog = None
agents = {}  # Store agent state per conversation (for future use if needed)

@app.on_event("startup")
async def startup_event():
    """Initialize catalog on startup."""
    global catalog
    try:
        catalog = get_catalog()
        logger.info(f"Loaded catalog with {len(catalog.assessments)} assessments")
    except Exception as e:
        logger.error(f"Failed to load catalog: {e}")
        raise


# Pydantic models for request/response
class Message(BaseModel):
    """A single message in conversation history."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request payload for /chat endpoint."""
    messages: List[Message]


class Recommendation(BaseModel):
    """A recommended assessment."""
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    """Response payload from /chat endpoint."""
    reply: str
    recommendations: List[Recommendation] = []
    end_of_conversation: bool = False


# Endpoints

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Stateless - carries full conversation history.
    
    Request: {"messages": [{"role": "user", "content": "..."}, ...]}
    Response: {"reply": "...", "recommendations": [...], "end_of_conversation": false}
    """
    try:
        # Validate request
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages list cannot be empty")
        
        # Check turn limit (8 total turns including user and assistant)
        if len(request.messages) >= 8:
            return ChatResponse(
                reply="We've reached the conversation limit. Here are my final recommendations.",
                recommendations=[],
                end_of_conversation=True
            )
        
        # Get last user message
        last_user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                last_user_message = message.content
                break
        
        if not last_user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Create fresh agent for this stateless call
        agent = ConversationAgent()
        
        # Reconstruct context from conversation history
        for message in request.messages:
            if message.role == "user":
                agent._extract_context(message.content)
        
        # Process the user message
        reply, recommendations, end_conversation = agent.process_user_message(
            last_user_message, 
            catalog
        )
        
        # Convert recommendations to response format
        rec_objects = [
            Recommendation(
                name=rec["name"],
                url=rec["url"],
                test_type=rec["test_type"]
            )
            for rec in recommendations
        ]
        
        # Validate all URLs are from SHL catalog
        for rec in rec_objects:
            if "shl.com" not in rec.url:
                logger.warning(f"Invalid URL in recommendations: {rec.url}")
                # Remove non-catalog recommendations
                rec_objects = [r for r in rec_objects if "shl.com" in r.url]
        
        response = ChatResponse(
            reply=reply,
            recommendations=rec_objects,
            end_of_conversation=end_conversation or len(recommendations) > 0
        )
        
        logger.info(f"Chat response: {len(rec_objects)} recommendations, "
                   f"end_conversation={response.end_of_conversation}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "SHL Assessment Recommender",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat"
        }
    }


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
