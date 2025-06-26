from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
import logging

# Add the parent directory to Python path to allow importing app modules
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class RecipeRequest(BaseModel):
    name: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: int
    difficulty: str = "medium"

class RecipeResponse(BaseModel):
    id: str
    name: str
    ingredients: List[str]
    instructions: List[str]
    cooking_time: int
    difficulty: str
    created_at: str

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

# In-memory storage for demo
recipes_db = {}
recipe_counter = 0

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ML backend is running"}

@app.get("/recipes", response_model=List[RecipeResponse])
async def get_recipes(
    limit: int = Query(10, description="Number of recipes to return"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level")
):
    """Get all recipes with optional filtering"""
    recipes = list(recipes_db.values())
    
    if difficulty:
        recipes = [r for r in recipes if r["difficulty"] == difficulty]
    
    return recipes[:limit]

@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(recipe_id: str):
    """Get a specific recipe by ID"""
    if recipe_id not in recipes_db:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipes_db[recipe_id]

@app.post("/recipes", response_model=RecipeResponse)
async def create_recipe(recipe: RecipeRequest):
    """Create a new recipe"""
    global recipe_counter
    recipe_counter += 1
    recipe_id = f"recipe_{recipe_counter}"
    
    new_recipe = {
        "id": recipe_id,
        "name": recipe.name,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "cooking_time": recipe.cooking_time,
        "difficulty": recipe.difficulty,
        "created_at": "2024-01-01T00:00:00Z"  # In real app, use datetime.now()
    }
    
    recipes_db[recipe_id] = new_recipe
    logger.info(f"Created recipe: {recipe.name}")
    return new_recipe

@app.put("/recipes/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(recipe_id: str, recipe: RecipeRequest):
    """Update an existing recipe"""
    if recipe_id not in recipes_db:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    updated_recipe = {
        "id": recipe_id,
        "name": recipe.name,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "cooking_time": recipe.cooking_time,
        "difficulty": recipe.difficulty,
        "created_at": recipes_db[recipe_id]["created_at"]
    }
    
    recipes_db[recipe_id] = updated_recipe
    logger.info(f"Updated recipe: {recipe.name}")
    return updated_recipe

@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: str):
    """Delete a recipe"""
    if recipe_id not in recipes_db:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    deleted_recipe = recipes_db.pop(recipe_id)
    logger.info(f"Deleted recipe: {deleted_recipe['name']}")
    return {"message": f"Recipe '{deleted_recipe['name']}' deleted successfully"}

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for food recognition"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # In a real application, you would process the image here
    # For now, just return file info
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file.size,
        "message": "Image uploaded successfully (processing would happen here)"
    }

@app.post("/analyze-nutrition")
async def analyze_nutrition(
    ingredients: List[str] = Form(...),
    serving_size: str = Form("1 serving")
):
    """Analyze nutrition for given ingredients"""
    # In a real application, you would use your nutrition analyzer model
    return {
        "ingredients": ingredients,
        "serving_size": serving_size,
        "nutrition": {
            "calories": 250,
            "protein": 12.5,
            "carbs": 30.2,
            "fat": 8.1,
            "fiber": 4.3
        },
        "message": "Nutrition analysis complete (using mock data)"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Use relative import since we're already in the app directory
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 