import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class RecipeRecommender:
    """
    Advanced recipe recommendation system using embeddings and ML techniques
    """
    
    def __init__(self):
        self.sentence_model = None
        self.tfidf_vectorizer = None
        self.recipe_embeddings = None
        self.recipe_database = None
        self.pairing_rules = None
        self.cuisine_embeddings = None
        
    async def load_model(self):
        """Load recommendation models and data"""
        try:
            logger.info("Loading recipe recommendation models...")
            
            # Load sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize TF-IDF vectorizer for keyword matching
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Load recipe database (in production, this would be from a real database)
            self.load_recipe_database()
            
            # Load pairing rules
            self.load_pairing_rules()
            
            # Pre-compute embeddings for faster recommendations
            await self.precompute_embeddings()
            
            logger.info("Recipe recommendation models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading recipe recommendation models: {e}")
            raise
    
    def load_recipe_database(self):
        """Load sample recipe database"""
        # In production, this would load from a real database
        sample_recipes = [
            {
                "id": "1",
                "title": "Classic Spaghetti Carbonara",
                "description": "Creamy Italian pasta with eggs, cheese, and pancetta",
                "ingredients": ["spaghetti", "eggs", "parmesan cheese", "pancetta", "black pepper", "olive oil"],
                "instructions": ["Cook pasta", "Fry pancetta", "Mix eggs and cheese", "Combine all"],
                "cuisine": "Italian",
                "difficulty": "Medium",
                "prep_time": 15,
                "cook_time": 20,
                "servings": 4,
                "tags": ["pasta", "italian", "comfort-food", "dinner"]
            },
            {
                "id": "2",
                "title": "Chicken Stir Fry",
                "description": "Quick and healthy chicken with vegetables",
                "ingredients": ["chicken breast", "broccoli", "bell pepper", "soy sauce", "ginger", "garlic", "rice"],
                "instructions": ["Cut chicken", "Stir fry vegetables", "Add sauce", "Serve with rice"],
                "cuisine": "Asian",
                "difficulty": "Easy",
                "prep_time": 10,
                "cook_time": 15,
                "servings": 2,
                "tags": ["chicken", "stir-fry", "healthy", "quick", "dinner"]
            },
            {
                "id": "3",
                "title": "Caesar Salad",
                "description": "Classic Roman salad with crispy croutons",
                "ingredients": ["romaine lettuce", "parmesan cheese", "croutons", "caesar dressing", "anchovies"],
                "instructions": ["Wash lettuce", "Make dressing", "Toss ingredients", "Serve immediately"],
                "cuisine": "Italian",
                "difficulty": "Easy",
                "prep_time": 15,
                "cook_time": 0,
                "servings": 4,
                "tags": ["salad", "vegetarian", "lunch", "fresh", "italian"]
            },
            {
                "id": "4",
                "title": "Beef Tacos",
                "description": "Spicy ground beef tacos with fresh toppings",
                "ingredients": ["ground beef", "taco shells", "onion", "tomato", "lettuce", "cheese", "cumin", "chili powder"],
                "instructions": ["Brown beef", "Season meat", "Warm shells", "Assemble tacos"],
                "cuisine": "Mexican",
                "difficulty": "Easy",
                "prep_time": 10,
                "cook_time": 15,
                "servings": 4,
                "tags": ["mexican", "beef", "tacos", "dinner", "spicy"]
            },
            {
                "id": "5",
                "title": "Vegetable Curry",
                "description": "Aromatic vegetable curry with coconut milk",
                "ingredients": ["mixed vegetables", "coconut milk", "curry powder", "ginger", "garlic", "onion", "rice"],
                "instructions": ["Sauté aromatics", "Add vegetables", "Pour coconut milk", "Simmer until tender"],
                "cuisine": "Indian",
                "difficulty": "Medium",
                "prep_time": 15,
                "cook_time": 25,
                "servings": 4,
                "tags": ["curry", "vegetarian", "indian", "coconut", "spicy", "dinner"]
            },
            {
                "id": "6",
                "title": "Greek Yogurt Parfait",
                "description": "Healthy breakfast with yogurt, berries, and granola",
                "ingredients": ["greek yogurt", "mixed berries", "granola", "honey", "almonds"],
                "instructions": ["Layer yogurt", "Add berries", "Top with granola", "Drizzle honey"],
                "cuisine": "Greek",
                "difficulty": "Easy",
                "prep_time": 5,
                "cook_time": 0,
                "servings": 1,
                "tags": ["breakfast", "healthy", "greek", "yogurt", "berries", "quick"]
            }
        ]
        
        self.recipe_database = pd.DataFrame(sample_recipes)
        
        # Create text representations for similarity matching
        self.recipe_database['text_representation'] = self.recipe_database.apply(
            lambda row: f"{row['title']} {row['description']} {' '.join(row['ingredients'])} {' '.join(row['tags'])}", 
            axis=1
        )
    
    def load_pairing_rules(self):
        """Load food pairing rules and suggestions"""
        self.pairing_rules = {
            "pasta": ["red wine", "garlic bread", "caesar salad", "parmesan cheese"],
            "chicken": ["white wine", "roasted vegetables", "rice pilaf", "lemon"],
            "beef": ["red wine", "mashed potatoes", "roasted root vegetables", "horseradish"],
            "fish": ["white wine", "lemon", "asparagus", "quinoa"],
            "salad": ["vinaigrette", "crusty bread", "white wine", "olive oil"],
            "curry": ["naan bread", "basmati rice", "mango chutney", "lassi"],
            "mexican": ["lime", "avocado", "cilantro", "mexican beer", "salsa"],
            "italian": ["olive oil", "basil", "tomatoes", "italian wine", "parmesan"],
            "asian": ["jasmine rice", "green tea", "sesame oil", "soy sauce"],
            "breakfast": ["coffee", "orange juice", "fresh fruit", "toast"],
            "dessert": ["coffee", "dessert wine", "vanilla ice cream", "whipped cream"]
        }
    
    async def precompute_embeddings(self):
        """Pre-compute embeddings for all recipes"""
        try:
            # Generate sentence embeddings
            texts = self.recipe_database['text_representation'].tolist()
            self.recipe_embeddings = self.sentence_model.encode(texts)
            
            # Fit TF-IDF vectorizer
            self.tfidf_vectorizer.fit(texts)
            
            logger.info(f"Pre-computed embeddings for {len(texts)} recipes")
            
        except Exception as e:
            logger.error(f"Error pre-computing embeddings: {e}")
            self.recipe_embeddings = None
    
    async def find_recipes(self, query: str, dietary_restrictions: List[str] = None, 
                          max_results: int = 10) -> List[Dict]:
        """
        Find recipes based on natural language query
        """
        try:
            if dietary_restrictions is None:
                dietary_restrictions = []
            
            # Parse query to extract search terms
            search_terms = self.parse_search_query(query)
            
            # Filter recipes based on dietary restrictions
            filtered_recipes = self.filter_by_dietary_restrictions(
                self.recipe_database, dietary_restrictions
            )
            
            if filtered_recipes.empty:
                return []
            
            # Calculate similarity scores
            scores = await self.calculate_similarity_scores(query, filtered_recipes)
            
            # Rank and return results
            filtered_recipes['similarity_score'] = scores
            top_recipes = filtered_recipes.nlargest(max_results, 'similarity_score')
            
            # Convert to response format
            recommendations = []
            for _, recipe in top_recipes.iterrows():
                rec = {
                    "title": recipe['title'],
                    "description": recipe['description'],
                    "ingredients": recipe['ingredients'],
                    "instructions": recipe['instructions'],
                    "tags": recipe['tags'],
                    "cuisine": recipe['cuisine'],
                    "difficulty": recipe['difficulty'],
                    "prep_time": recipe['prep_time'],
                    "cook_time": recipe['cook_time'],
                    "servings": recipe['servings'],
                    "confidence_score": float(recipe['similarity_score'])
                }
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error finding recipes: {e}")
            return []
    
    def parse_search_query(self, query: str) -> List[str]:
        """Parse natural language query to extract search terms"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        query_lower = query.lower()
        
        # Extract specific ingredients, cuisines, etc.
        terms = []
        
        # Common food keywords
        food_keywords = [
            "chicken", "beef", "pork", "fish", "vegetable", "pasta", "rice", "salad",
            "soup", "curry", "pizza", "burger", "sandwich", "stir-fry", "noodles"
        ]
        
        # Cuisine keywords
        cuisine_keywords = [
            "italian", "mexican", "chinese", "indian", "thai", "greek", "french",
            "japanese", "korean", "mediterranean", "american"
        ]
        
        # Dietary keywords
        dietary_keywords = [
            "vegetarian", "vegan", "gluten-free", "dairy-free", "low-carb", "keto",
            "paleo", "healthy", "light"
        ]
        
        # Extract keywords from query
        for keyword in food_keywords + cuisine_keywords + dietary_keywords:
            if keyword in query_lower:
                terms.append(keyword)
        
        # Add query words as potential terms
        words = query_lower.split()
        terms.extend([word for word in words if len(word) > 3])
        
        return list(set(terms))  # Remove duplicates
    
    def filter_by_dietary_restrictions(self, recipes_df: pd.DataFrame, 
                                     restrictions: List[str]) -> pd.DataFrame:
        """Filter recipes based on dietary restrictions"""
        if not restrictions:
            return recipes_df
        
        filtered_df = recipes_df.copy()
        
        for restriction in restrictions:
            restriction_lower = restriction.lower()
            
            if restriction_lower == "vegetarian":
                # Filter out recipes with meat
                meat_keywords = ["chicken", "beef", "pork", "fish", "meat", "bacon", "ham"]
                filtered_df = filtered_df[
                    ~filtered_df['text_representation'].str.lower().str.contains(
                        '|'.join(meat_keywords)
                    )
                ]
            
            elif restriction_lower == "vegan":
                # Filter out animal products
                animal_keywords = ["chicken", "beef", "pork", "fish", "meat", "dairy", 
                                 "cheese", "milk", "butter", "egg", "honey", "bacon"]
                filtered_df = filtered_df[
                    ~filtered_df['text_representation'].str.lower().str.contains(
                        '|'.join(animal_keywords)
                    )
                ]
            
            elif restriction_lower == "gluten-free":
                # Filter out gluten-containing ingredients
                gluten_keywords = ["wheat", "flour", "bread", "pasta", "barley", "rye"]
                filtered_df = filtered_df[
                    ~filtered_df['text_representation'].str.lower().str.contains(
                        '|'.join(gluten_keywords)
                    )
                ]
        
        return filtered_df
    
    async def calculate_similarity_scores(self, query: str, recipes_df: pd.DataFrame) -> np.ndarray:
        """Calculate similarity scores between query and recipes"""
        try:
            # Get embeddings for the query
            query_embedding = self.sentence_model.encode([query])
            
            # Get embeddings for filtered recipes
            if self.recipe_embeddings is not None:
                # Use pre-computed embeddings, filtering by recipe indices
                recipe_indices = recipes_df.index.tolist()
                recipe_embeddings = self.recipe_embeddings[recipe_indices]
            else:
                # Compute embeddings on the fly
                texts = recipes_df['text_representation'].tolist()
                recipe_embeddings = self.sentence_model.encode(texts)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_embedding, recipe_embeddings)[0]
            
            # Boost scores based on exact keyword matches
            boosted_scores = self.boost_keyword_matches(query, recipes_df, similarities)
            
            return boosted_scores
            
        except Exception as e:
            logger.error(f"Error calculating similarity scores: {e}")
            return np.zeros(len(recipes_df))
    
    def boost_keyword_matches(self, query: str, recipes_df: pd.DataFrame, 
                            base_scores: np.ndarray) -> np.ndarray:
        """Boost similarity scores for exact keyword matches"""
        query_words = set(query.lower().split())
        boosted_scores = base_scores.copy()
        
        for i, (_, recipe) in enumerate(recipes_df.iterrows()):
            recipe_text = recipe['text_representation'].lower()
            
            # Count exact matches
            matches = sum(1 for word in query_words if word in recipe_text)
            boost = matches * 0.1  # 10% boost per exact match
            
            boosted_scores[i] = min(1.0, boosted_scores[i] + boost)
        
        return boosted_scores
    
    async def generate_pairings(self, ingredients: List[str], cuisine: str = None, 
                              category: str = None) -> List[str]:
        """Generate food and drink pairing suggestions"""
        try:
            pairings = set()
            
            # Get pairings based on main ingredients
            for ingredient in ingredients:
                ingredient_name = ingredient.get("name", ingredient) if isinstance(ingredient, dict) else ingredient
                ingredient_lower = ingredient_name.lower()
                
                for food_type, pairing_list in self.pairing_rules.items():
                    if food_type in ingredient_lower:
                        pairings.update(pairing_list)
            
            # Add cuisine-specific pairings
            if cuisine:
                cuisine_lower = cuisine.lower()
                if cuisine_lower in self.pairing_rules:
                    pairings.update(self.pairing_rules[cuisine_lower])
            
            # Add category-specific pairings
            if category:
                category_lower = category.lower()
                if category_lower in self.pairing_rules:
                    pairings.update(self.pairing_rules[category_lower])
            
            # Remove ingredients that are already in the recipe
            ingredient_names = [
                (ing.get("name", ing) if isinstance(ing, dict) else ing).lower() 
                for ing in ingredients
            ]
            pairings = [p for p in pairings if p.lower() not in ingredient_names]
            
            return list(pairings)[:5]  # Return top 5 pairings
            
        except Exception as e:
            logger.error(f"Error generating pairings: {e}")
            return []
    
    async def estimate_difficulty(self, instructions: List[str]) -> str:
        """Estimate recipe difficulty based on instructions"""
        try:
            num_steps = len(instructions)
            instruction_text = " ".join(instructions).lower()
            
            # Count complex cooking techniques
            complex_techniques = [
                "fold", "whisk", "emulsify", "tempering", "julienne", "brunoise",
                "flambé", "sous vide", "confit", "braise", "reduce", "clarify"
            ]
            
            technique_count = sum(1 for technique in complex_techniques 
                                if technique in instruction_text)
            
            # Estimate based on steps and techniques
            if num_steps <= 3 and technique_count == 0:
                return "Easy"
            elif num_steps <= 6 and technique_count <= 1:
                return "Medium"
            else:
                return "Hard"
                
        except Exception as e:
            logger.error(f"Error estimating difficulty: {e}")
            return "Medium"
    
    async def generate_meal_plan(self, days: int, dietary_restrictions: List[str] = None,
                               cuisine_preferences: List[str] = None,
                               cooking_time_limit: int = None,
                               servings: int = 1) -> List[Dict]:
        """Generate a personalized meal plan"""
        try:
            if dietary_restrictions is None:
                dietary_restrictions = []
            if cuisine_preferences is None:
                cuisine_preferences = []
            
            meal_plan = []
            start_date = datetime.now().date()
            
            for day in range(days):
                current_date = start_date + timedelta(days=day)
                
                # Generate meals for each meal type
                breakfast = await self.find_meal_for_type(
                    "breakfast", dietary_restrictions, cuisine_preferences, 
                    cooking_time_limit, servings
                )
                
                lunch = await self.find_meal_for_type(
                    "lunch", dietary_restrictions, cuisine_preferences,
                    cooking_time_limit, servings
                )
                
                dinner = await self.find_meal_for_type(
                    "dinner", dietary_restrictions, cuisine_preferences,
                    cooking_time_limit, servings
                )
                
                day_plan = {
                    "date": current_date.isoformat(),
                    "breakfast": breakfast,
                    "lunch": lunch,
                    "dinner": dinner,
                    "snacks": []
                }
                
                meal_plan.append(day_plan)
            
            return meal_plan
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {e}")
            return []
    
    async def find_meal_for_type(self, meal_type: str, dietary_restrictions: List[str],
                               cuisine_preferences: List[str], time_limit: int = None,
                               servings: int = 1) -> Dict:
        """Find a suitable recipe for a specific meal type"""
        try:
            # Create query for meal type
            query = f"{meal_type} recipe"
            if cuisine_preferences:
                query += f" {random.choice(cuisine_preferences)}"
            
            # Find recipes
            recipes = await self.find_recipes(
                query=query,
                dietary_restrictions=dietary_restrictions,
                max_results=5
            )
            
            # Filter by time limit if specified
            if time_limit and recipes:
                recipes = [
                    r for r in recipes 
                    if (r.get('prep_time', 0) + r.get('cook_time', 0)) <= time_limit
                ]
            
            # Filter by meal type tags
            meal_recipes = [
                r for r in recipes 
                if meal_type in [tag.lower() for tag in r.get('tags', [])]
            ]
            
            # If no meal-specific recipes, use any suitable recipe
            if not meal_recipes and recipes:
                meal_recipes = recipes
            
            # Return random recipe or None
            if meal_recipes:
                return random.choice(meal_recipes)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error finding meal for type {meal_type}: {e}")
            return None 