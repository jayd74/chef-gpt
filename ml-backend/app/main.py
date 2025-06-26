from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import asyncio
import logging

from .models.food_recognition import FoodRecognitionModel
from .models.nutrition_analyzer import NutritionAnalyzer
from .models.recipe_recommender import RecipeRecommender
from .models.tag_generator import TagGenerator
from .schemas import (
    RecipeAnalysisRequest,
    RecipeAnalysisResponse,
    IngredientRecognitionResponse,
    NutritionAnalysisResponse,
    RecipeRecommendationRequest,
    RecipeRecommendationResponse,
    MealPlanRequest,
    MealPlanResponse
)
from .utils.image_processing import process_uploaded_image
from .database import get_db

# Load environment variables
load_dotenv()

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

# Initialize ML models (lazy loading)
food_model = None
nutrition_analyzer = None
recipe_recommender = None
tag_generator = None

async def get_food_model():
    global food_model
    if food_model is None:
        food_model = FoodRecognitionModel()
        await food_model.load_model()
    return food_model

async def get_nutrition_analyzer():
    global nutrition_analyzer
    if nutrition_analyzer is None:
        nutrition_analyzer = NutritionAnalyzer()
        await nutrition_analyzer.load_model()
    return nutrition_analyzer

async def get_recipe_recommender():
    global recipe_recommender
    if recipe_recommender is None:
        recipe_recommender = RecipeRecommender()
        await recipe_recommender.load_model()
    return recipe_recommender

async def get_tag_generator():
    global tag_generator
    if tag_generator is None:
        tag_generator = TagGenerator()
        await tag_generator.load_model()
    return tag_generator

@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup"""
    logger.info("Starting ML backend...")
    try:
        # Pre-load critical models
        await get_food_model()
        await get_nutrition_analyzer()
        logger.info("ML models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading ML models: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ML backend is running"}

@app.post("/analyze-food-image", response_model=IngredientRecognitionResponse)
async def analyze_food_image(
    file: UploadFile = File(...),
    food_model: FoodRecognitionModel = Depends(get_food_model)
):
    """
    Analyze a food image and identify ingredients with confidence scores
    """
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Process the uploaded image
        image = await process_uploaded_image(file)
        
        # Analyze with ML model
        result = await food_model.analyze_image(image)
        
        return IngredientRecognitionResponse(**result)
    
    except Exception as e:
        logger.error(f"Error analyzing food image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-recipe-tags", response_model=List[str])
async def generate_recipe_tags(
    request: RecipeAnalysisRequest,
    tag_generator: TagGenerator = Depends(get_tag_generator)
):
    """
    Generate AI tags for a recipe based on ingredients and instructions
    """
    try:
        tags = await tag_generator.generate_tags(
            ingredients=request.ingredients,
            instructions=request.instructions,
            cuisine=request.cuisine,
            category=request.category
        )
        return tags
    
    except Exception as e:
        logger.error(f"Error generating recipe tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-nutrition", response_model=NutritionAnalysisResponse)
async def analyze_nutrition(
    request: RecipeAnalysisRequest,
    nutrition_analyzer: NutritionAnalyzer = Depends(get_nutrition_analyzer)
):
    """
    Calculate nutritional information for a recipe
    """
    try:
        nutrition = await nutrition_analyzer.calculate_nutrition(
            ingredients=request.ingredients,
            servings=request.servings or 1
        )
        return NutritionAnalysisResponse(**nutrition)
    
    except Exception as e:
        logger.error(f"Error analyzing nutrition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-pairings", response_model=List[str])
async def generate_pairings(
    request: RecipeAnalysisRequest,
    recipe_recommender: RecipeRecommender = Depends(get_recipe_recommender)
):
    """
    Generate pairing suggestions for a recipe
    """
    try:
        pairings = await recipe_recommender.generate_pairings(
            ingredients=request.ingredients,
            cuisine=request.cuisine,
            category=request.category
        )
        return pairings
    
    except Exception as e:
        logger.error(f"Error generating pairings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend-recipes", response_model=RecipeRecommendationResponse)
async def recommend_recipes(
    request: RecipeRecommendationRequest,
    recipe_recommender: RecipeRecommender = Depends(get_recipe_recommender)
):
    """
    Find recipes based on natural language criteria
    """
    try:
        recommendations = await recipe_recommender.find_recipes(
            query=request.query,
            dietary_restrictions=request.dietary_restrictions,
            max_results=request.max_results or 10
        )
        return RecipeRecommendationResponse(recommendations=recommendations)
    
    except Exception as e:
        logger.error(f"Error recommending recipes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-meal-plan", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: MealPlanRequest,
    recipe_recommender: RecipeRecommender = Depends(get_recipe_recommender)
):
    """
    Generate a personalized meal plan
    """
    try:
        meal_plan = await recipe_recommender.generate_meal_plan(
            days=request.days,
            dietary_restrictions=request.dietary_restrictions,
            cuisine_preferences=request.cuisine_preferences,
            cooking_time_limit=request.cooking_time_limit,
            servings=request.servings
        )
        return MealPlanResponse(meal_plan=meal_plan)
    
    except Exception as e:
        logger.error(f"Error generating meal plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-recipe-complete", response_model=RecipeAnalysisResponse)
async def analyze_recipe_complete(
    request: RecipeAnalysisRequest,
    food_model: FoodRecognitionModel = Depends(get_food_model),
    nutrition_analyzer: NutritionAnalyzer = Depends(get_nutrition_analyzer),
    tag_generator: TagGenerator = Depends(get_tag_generator),
    recipe_recommender: RecipeRecommender = Depends(get_recipe_recommender)
):
    """
    Complete recipe analysis including tags, nutrition, and pairings
    """
    try:
        # Run all analyses in parallel for efficiency
        tasks = [
            tag_generator.generate_tags(
                ingredients=request.ingredients,
                instructions=request.instructions,
                cuisine=request.cuisine,
                category=request.category
            ),
            nutrition_analyzer.calculate_nutrition(
                ingredients=request.ingredients,
                servings=request.servings or 1
            ),
            recipe_recommender.generate_pairings(
                ingredients=request.ingredients,
                cuisine=request.cuisine,
                category=request.category
            )
        ]
        
        tags, nutrition, pairings = await asyncio.gather(*tasks)
        
        return RecipeAnalysisResponse(
            tags=tags,
            nutrition=nutrition,
            pairings=pairings,
            difficulty=await recipe_recommender.estimate_difficulty(request.instructions)
        )
    
    except Exception as e:
        logger.error(f"Error in complete recipe analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/status")
async def models_status():
    """
    Check the status of all ML models
    """
    return {
        "food_recognition": food_model is not None,
        "nutrition_analyzer": nutrition_analyzer is not None,
        "recipe_recommender": recipe_recommender is not None,
        "tag_generator": tag_generator is not None
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 