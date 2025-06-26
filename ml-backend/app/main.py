from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
import logging
from app.services.chat_service import chat_stream

sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Recipe AI ML Backend",
    description="Machine Learning backend for recipe analysis, ingredient recognition, and meal planning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ML backend is running"}

@app.post("/chat")
async def chat_endpoint(request):
    """Chat endpoint"""
    return await chat_stream(request)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Use relative import since we're already in the app directory
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 