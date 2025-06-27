from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from dotenv import load_dotenv
from pathlib import Path
import logging
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

# Add the parent directory to Python path to allow importing app modules
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Import schemas from app.schemas
from app.schemas import ChatRequest, ChatResponse, ChatState
from app.models.recipe_analysis import analyze_food_image
from app.models.flyer_dinner import generate_flyer_dinner


class RecipeAnalysisRequest(BaseModel):
    image: str

class FlyerDinnerRequest(BaseModel):
    banner: str

# Initialize FastAPI app
app = FastAPI(
    title="Recipe AI ML Backend",
    description="Machine Learning backend for recipe analysis, ingredient recognition, and meal planning",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",  # Allow Vercel deployments
        "https://chef-gpt.vercel.app",  # Your specific Vercel domain
        "https://chef-gpt-git-main-jasodu.vercel.app",  # Alternative Vercel domain format
    ],  # Next.js dev server and deployed frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ML backend is running"}


@app.post("/recipe_analysis")
async def recipe_endpoint(request: RecipeAnalysisRequest):
    return await analyze_food_image(request.image)

@app.post("/flyer_dinner")
async def flyer_dinner_endpoint(request: FlyerDinnerRequest):
    return await generate_flyer_dinner(request.banner)


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint using LangGraph"""
    try:
        # Import here to avoid circular imports
        from app.services.chat_service import chat_stream

        return await chat_stream(request)
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Chat service not available. Please install required dependencies."
            },
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/chat/simple")
async def chat_simple_endpoint(request: ChatRequest):
    """Simple non-streaming chat endpoint"""
    try:
        # Import here to avoid circular imports
        from app.services.chat_service import chat_simple

        return await chat_simple(request)
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Chat service not available. Please install required dependencies."
            },
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Use relative import since we're already in the app directory
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
