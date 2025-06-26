from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import ARRAY
import os
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/recipe_ai_db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database Models for ML backend
class MLRecipe(Base):
    __tablename__ = "ml_recipes"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    ingredients = Column(JSON)  # Store as JSON array
    instructions = Column(JSON)  # Store as JSON array
    cuisine = Column(String, index=True)
    difficulty = Column(String)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    servings = Column(Integer)
    tags = Column(ARRAY(String))  # PostgreSQL array
    
    # ML-specific fields
    embeddings = Column(JSON)  # Store sentence embeddings
    nutrition_data = Column(JSON)  # Calculated nutrition
    ai_generated_tags = Column(ARRAY(String))
    pairing_suggestions = Column(ARRAY(String))
    
    # Metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_verified = Column(Boolean, default=False)

class MLIngredient(Base):
    __tablename__ = "ml_ingredients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    nutrition_per_100g = Column(JSON)
    aliases = Column(ARRAY(String))
    density = Column(Float)  # For unit conversions
    
    # ML features
    embeddings = Column(JSON)
    color_features = Column(JSON)
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class MLImageAnalysis(Base):
    __tablename__ = "ml_image_analyses"
    
    id = Column(String, primary_key=True, index=True)
    image_url = Column(String)
    detected_ingredients = Column(JSON)
    confidence_scores = Column(JSON)
    bounding_boxes = Column(JSON)
    analysis_metadata = Column(JSON)
    
    # Processing info
    model_version = Column(String)
    processing_time = Column(Float)
    created_at = Column(DateTime)

class MLUserPreference(Base):
    __tablename__ = "ml_user_preferences"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    dietary_restrictions = Column(ARRAY(String))
    cuisine_preferences = Column(ARRAY(String))
    ingredient_dislikes = Column(ARRAY(String))
    favorite_tags = Column(ARRAY(String))
    
    # ML-derived preferences
    preference_embeddings = Column(JSON)
    recommendation_weights = Column(JSON)
    
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize database tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

async def get_recipe_by_id(db: Session, recipe_id: str) -> MLRecipe:
    """
    Get recipe by ID
    """
    return db.query(MLRecipe).filter(MLRecipe.id == recipe_id).first()

async def get_recipes_by_tags(db: Session, tags: list, limit: int = 10) -> list[MLRecipe]:
    """
    Get recipes that match any of the provided tags
    """
    return db.query(MLRecipe).filter(
        MLRecipe.tags.overlap(tags)
    ).limit(limit).all()

async def get_recipes_by_cuisine(db: Session, cuisine: str, limit: int = 10) -> list[MLRecipe]:
    """
    Get recipes by cuisine type
    """
    return db.query(MLRecipe).filter(
        MLRecipe.cuisine.ilike(f"%{cuisine}%")
    ).limit(limit).all()

async def save_recipe_analysis(db: Session, recipe_data: dict) -> MLRecipe:
    """
    Save analyzed recipe data to database
    """
    try:
        recipe = MLRecipe(**recipe_data)
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return recipe
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving recipe analysis: {e}")
        raise

async def save_image_analysis(db: Session, analysis_data: dict) -> MLImageAnalysis:
    """
    Save image analysis results to database
    """
    try:
        analysis = MLImageAnalysis(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving image analysis: {e}")
        raise

async def get_ingredient_by_name(db: Session, name: str) -> MLIngredient:
    """
    Get ingredient by name or alias
    """
    # First try exact match
    ingredient = db.query(MLIngredient).filter(MLIngredient.name == name.lower()).first()
    
    if not ingredient:
        # Try alias match
        ingredient = db.query(MLIngredient).filter(
            MLIngredient.aliases.contains([name.lower()])
        ).first()
    
    return ingredient

async def save_user_preferences(db: Session, user_id: str, preferences: dict) -> MLUserPreference:
    """
    Save or update user preferences
    """
    try:
        # Check if preferences already exist
        existing = db.query(MLUserPreference).filter(
            MLUserPreference.user_id == user_id
        ).first()
        
        if existing:
            # Update existing preferences
            for key, value in preferences.items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new preferences
            preferences['user_id'] = user_id
            new_prefs = MLUserPreference(**preferences)
            db.add(new_prefs)
            db.commit()
            db.refresh(new_prefs)
            return new_prefs
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving user preferences: {e}")
        raise

async def search_recipes_by_embedding(db: Session, query_embedding: list, 
                                    limit: int = 10, similarity_threshold: float = 0.7) -> list[MLRecipe]:
    """
    Search recipes using embedding similarity
    Note: This would require a vector database like pgvector in production
    """
    # Simplified implementation - in production, use proper vector similarity search
    recipes = db.query(MLRecipe).filter(MLRecipe.embeddings.isnot(None)).limit(limit * 2).all()
    
    # Calculate similarities (simplified)
    similar_recipes = []
    for recipe in recipes:
        if recipe.embeddings:
            # In production, use proper cosine similarity with vector operations
            # This is a placeholder implementation
            similar_recipes.append(recipe)
    
    return similar_recipes[:limit]

# Connection testing
async def test_connection():
    """
    Test database connection
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False 