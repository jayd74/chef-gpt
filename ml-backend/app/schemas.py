from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class IngredientInput(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    preparation: Optional[str] = None

class RecipeAnalysisRequest(BaseModel):
    ingredients: List[IngredientInput]
    instructions: List[str]
    cuisine: Optional[str] = None
    category: Optional[str] = None
    servings: Optional[int] = 1

class IngredientRecognition(BaseModel):
    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    quantity: Optional[str] = None
    unit: Optional[str] = None
    bounding_box: Optional[List[float]] = None  # [x1, y1, x2, y2]

class IngredientRecognitionResponse(BaseModel):
    ingredients: List[IngredientRecognition]
    suggestions: List[str]
    processing_time: float

class NutritionInfo(BaseModel):
    calories: float
    protein: float  # grams
    carbs: float   # grams
    fat: float     # grams
    fiber: float   # grams
    sugar: float   # grams
    sodium: float  # milligrams
    per_serving: bool = True

class NutritionAnalysisResponse(BaseModel):
    nutrition: NutritionInfo
    confidence: float = Field(..., ge=0.0, le=1.0)
    missing_ingredients: List[str] = []

class RecipeAnalysisResponse(BaseModel):
    tags: List[str]
    nutrition: NutritionInfo
    pairings: List[str]
    difficulty: Optional[str] = None
    estimated_cost: Optional[float] = None
    processing_time: float

class RecipeRecommendationRequest(BaseModel):
    query: str
    dietary_restrictions: Optional[List[str]] = []
    cuisine_preferences: Optional[List[str]] = []
    max_cooking_time: Optional[int] = None
    max_results: Optional[int] = 10
    include_nutrition: bool = False

class RecipeRecommendation(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: List[str]
    instructions: List[str]
    tags: List[str]
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    servings: Optional[int] = None
    nutrition: Optional[NutritionInfo] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)

class RecipeRecommendationResponse(BaseModel):
    recommendations: List[RecipeRecommendation]
    total_found: int
    search_terms_used: List[str]

class MealPlanRequest(BaseModel):
    days: int = Field(..., ge=1, le=14)
    dietary_restrictions: Optional[List[str]] = []
    cuisine_preferences: Optional[List[str]] = []
    cooking_time_limit: Optional[int] = None
    servings: Optional[int] = 1
    exclude_ingredients: Optional[List[str]] = []
    calories_per_day: Optional[int] = None

class MealPlanDay(BaseModel):
    date: date
    breakfast: Optional[RecipeRecommendation] = None
    lunch: Optional[RecipeRecommendation] = None
    dinner: Optional[RecipeRecommendation] = None
    snacks: Optional[List[RecipeRecommendation]] = []
    total_calories: Optional[float] = None
    total_nutrition: Optional[NutritionInfo] = None

class MealPlanResponse(BaseModel):
    meal_plan: List[MealPlanDay]
    total_days: int
    avg_calories_per_day: Optional[float] = None
    shopping_list: Optional[List[str]] = []

class ImageAnalysisRequest(BaseModel):
    image_url: Optional[str] = None
    generate_recipe: bool = False
    include_nutrition: bool = False

class GeneratedRecipeStep(BaseModel):
    step_number: int
    instruction: str
    time_minutes: Optional[int] = None
    temperature: Optional[str] = None

class ImageToRecipeResponse(BaseModel):
    recognized_ingredients: List[IngredientRecognition]
    suggested_recipe: Optional[RecipeRecommendation] = None
    alternative_recipes: List[RecipeRecommendation] = []
    confidence: float = Field(..., ge=0.0, le=1.0)

class TagGenerationRequest(BaseModel):
    text: str
    recipe_type: Optional[str] = None
    max_tags: int = Field(default=10, ge=1, le=20)

class SimilarRecipeRequest(BaseModel):
    recipe_ingredients: List[str]
    recipe_tags: Optional[List[str]] = []
    max_results: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SimilarRecipeResponse(BaseModel):
    similar_recipes: List[RecipeRecommendation]
    similarity_scores: List[float]

# Error response schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None 

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    type: str
    content: str
    session_id: str

# Define the state structure
class ChatState(BaseModel):
    messages: List[Dict[str, Any]]
    session_id: str
    context: Dict[str, Any] = {}