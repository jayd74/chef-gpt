import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

logger = logging.getLogger(__name__)

class NutritionAnalyzer:
    """
    Advanced nutrition analyzer that uses ML and comprehensive nutritional databases
    to calculate accurate nutritional information for recipes
    """
    
    def __init__(self):
        self.nutrition_db = None
        self.ingredient_matcher = None
        self.portion_estimator = None
        self.density_database = None
        
    async def load_model(self):
        """Load nutrition databases and ML models"""
        try:
            logger.info("Loading nutrition analyzer...")
            
            # Load comprehensive nutrition database
            self.load_nutrition_database()
            
            # Initialize ingredient name matcher using TF-IDF
            self.initialize_ingredient_matcher()
            
            # Load portion size estimation model
            self.load_portion_estimator()
            
            # Load ingredient density database for unit conversions
            self.load_density_database()
            
            logger.info("Nutrition analyzer loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading nutrition analyzer: {e}")
            raise
    
    def load_nutrition_database(self):
        """Load comprehensive nutrition database (USDA FoodData Central style)"""
        # In production, this would load from USDA FoodData Central or similar
        # For now, using a comprehensive sample database
        
        nutrition_data = {
            # Fruits
            "apple": {
                "calories_per_100g": 52, "protein": 0.26, "carbs": 13.81, "fat": 0.17,
                "fiber": 2.4, "sugar": 10.39, "sodium": 1, "vitamin_c": 4.6,
                "calcium": 6, "iron": 0.12, "potassium": 107
            },
            "banana": {
                "calories_per_100g": 89, "protein": 1.09, "carbs": 22.84, "fat": 0.33,
                "fiber": 2.6, "sugar": 12.23, "sodium": 1, "vitamin_c": 8.7,
                "calcium": 5, "iron": 0.26, "potassium": 358
            },
            "orange": {
                "calories_per_100g": 47, "protein": 0.94, "carbs": 11.75, "fat": 0.12,
                "fiber": 2.4, "sugar": 9.35, "sodium": 0, "vitamin_c": 53.2,
                "calcium": 40, "iron": 0.1, "potassium": 181
            },
            
            # Vegetables
            "tomato": {
                "calories_per_100g": 18, "protein": 0.88, "carbs": 3.89, "fat": 0.2,
                "fiber": 1.2, "sugar": 2.63, "sodium": 5, "vitamin_c": 13.7,
                "calcium": 10, "iron": 0.27, "potassium": 237
            },
            "onion": {
                "calories_per_100g": 40, "protein": 1.1, "carbs": 9.34, "fat": 0.1,
                "fiber": 1.7, "sugar": 4.24, "sodium": 4, "vitamin_c": 7.4,
                "calcium": 23, "iron": 0.21, "potassium": 146
            },
            "carrot": {
                "calories_per_100g": 41, "protein": 0.93, "carbs": 9.58, "fat": 0.24,
                "fiber": 2.8, "sugar": 4.74, "sodium": 69, "vitamin_c": 5.9,
                "calcium": 33, "iron": 0.3, "potassium": 320
            },
            "broccoli": {
                "calories_per_100g": 34, "protein": 2.82, "carbs": 6.64, "fat": 0.37,
                "fiber": 2.6, "sugar": 1.55, "sodium": 33, "vitamin_c": 89.2,
                "calcium": 47, "iron": 0.73, "potassium": 316
            },
            "spinach": {
                "calories_per_100g": 23, "protein": 2.86, "carbs": 3.63, "fat": 0.39,
                "fiber": 2.2, "sugar": 0.42, "sodium": 79, "vitamin_c": 28.1,
                "calcium": 99, "iron": 2.71, "potassium": 558
            },
            
            # Proteins
            "chicken_breast": {
                "calories_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6,
                "fiber": 0, "sugar": 0, "sodium": 74, "vitamin_c": 0,
                "calcium": 15, "iron": 0.9, "potassium": 256
            },
            "beef_lean": {
                "calories_per_100g": 250, "protein": 26, "carbs": 0, "fat": 15,
                "fiber": 0, "sugar": 0, "sodium": 72, "vitamin_c": 0,
                "calcium": 18, "iron": 2.6, "potassium": 318
            },
            "salmon": {
                "calories_per_100g": 208, "protein": 22, "carbs": 0, "fat": 12,
                "fiber": 0, "sugar": 0, "sodium": 89, "vitamin_c": 0,
                "calcium": 9, "iron": 0.8, "potassium": 363
            },
            "eggs": {
                "calories_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11,
                "fiber": 0, "sugar": 1.1, "sodium": 124, "vitamin_c": 0,
                "calcium": 56, "iron": 1.75, "potassium": 138
            },
            
            # Grains and Starches
            "rice_white": {
                "calories_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3,
                "fiber": 0.4, "sugar": 0.1, "sodium": 1, "vitamin_c": 0,
                "calcium": 28, "iron": 0.8, "potassium": 35
            },
            "pasta": {
                "calories_per_100g": 131, "protein": 5, "carbs": 25, "fat": 1.1,
                "fiber": 1.8, "sugar": 0.8, "sodium": 1, "vitamin_c": 0,
                "calcium": 7, "iron": 0.9, "potassium": 44
            },
            "bread_white": {
                "calories_per_100g": 265, "protein": 9, "carbs": 49, "fat": 3.2,
                "fiber": 2.7, "sugar": 5, "sodium": 477, "vitamin_c": 0,
                "calcium": 77, "iron": 3.6, "potassium": 115
            },
            "flour": {
                "calories_per_100g": 364, "protein": 10, "carbs": 76, "fat": 1,
                "fiber": 2.7, "sugar": 0.3, "sodium": 2, "vitamin_c": 0,
                "calcium": 15, "iron": 1.2, "potassium": 107
            },
            
            # Dairy
            "milk_whole": {
                "calories_per_100g": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3,
                "fiber": 0, "sugar": 5.1, "sodium": 40, "vitamin_c": 0,
                "calcium": 113, "iron": 0.03, "potassium": 132
            },
            "cheese_cheddar": {
                "calories_per_100g": 403, "protein": 25, "carbs": 1.3, "fat": 33,
                "fiber": 0, "sugar": 0.5, "sodium": 621, "vitamin_c": 0,
                "calcium": 721, "iron": 0.68, "potassium": 76
            },
            "butter": {
                "calories_per_100g": 717, "protein": 0.85, "carbs": 0.06, "fat": 81,
                "fiber": 0, "sugar": 0.06, "sodium": 11, "vitamin_c": 0,
                "calcium": 24, "iron": 0.02, "potassium": 24
            },
            
            # Oils and Fats
            "olive_oil": {
                "calories_per_100g": 884, "protein": 0, "carbs": 0, "fat": 100,
                "fiber": 0, "sugar": 0, "sodium": 2, "vitamin_c": 0,
                "calcium": 1, "iron": 0.56, "potassium": 1
            },
            
            # Seasonings (minimal nutrition but important for recipes)
            "salt": {
                "calories_per_100g": 0, "protein": 0, "carbs": 0, "fat": 0,
                "fiber": 0, "sugar": 0, "sodium": 38758, "vitamin_c": 0,
                "calcium": 24, "iron": 0.33, "potassium": 8
            },
            "black_pepper": {
                "calories_per_100g": 251, "protein": 10.39, "carbs": 63.95, "fat": 3.26,
                "fiber": 25.3, "sugar": 0.64, "sodium": 20, "vitamin_c": 0,
                "calcium": 443, "iron": 9.71, "potassium": 1329
            }
        }
        
        self.nutrition_db = pd.DataFrame.from_dict(nutrition_data, orient='index')
        
        # Create aliases for common ingredient names
        self.ingredient_aliases = {
            "chicken": "chicken_breast",
            "beef": "beef_lean",
            "fish": "salmon",
            "egg": "eggs",
            "rice": "rice_white",
            "white_rice": "rice_white",
            "cheese": "cheese_cheddar",
            "bread": "bread_white",
            "milk": "milk_whole"
        }
    
    def initialize_ingredient_matcher(self):
        """Initialize TF-IDF vectorizer for ingredient name matching"""
        # Create a corpus of all ingredient names and aliases
        ingredient_names = list(self.nutrition_db.index) + list(self.ingredient_aliases.keys())
        
        # Add common variations and plurals
        extended_names = []
        for name in ingredient_names:
            extended_names.append(name)
            extended_names.append(name + "s")  # Plural
            extended_names.append(name.replace("_", " "))  # Space instead of underscore
        
        self.ingredient_matcher = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words=None,
            lowercase=True
        )
        self.ingredient_matcher.fit(extended_names)
        self.ingredient_corpus = extended_names
    
    def load_portion_estimator(self):
        """Load ML model for portion size estimation"""
        # Simplified portion size database
        # In production, this would be a trained ML model
        self.portion_sizes = {
            "apple": {"medium": 182, "large": 223, "small": 149},  # grams
            "banana": {"medium": 118, "large": 136, "small": 101},
            "orange": {"medium": 154, "large": 184, "small": 131},
            "tomato": {"medium": 123, "large": 182, "small": 91},
            "onion": {"medium": 110, "large": 150, "small": 70},
            "carrot": {"medium": 61, "large": 72, "small": 50},
            "egg": {"large": 50, "medium": 44, "small": 38},
            "chicken_breast": {"serving": 85},  # 3 oz serving
            "default": 100  # Default to 100g if no specific data
        }
    
    def load_density_database(self):
        """Load ingredient density data for unit conversions"""
        # Density in g/ml for volume to weight conversions
        self.densities = {
            "flour": 0.593,
            "sugar": 0.845,
            "milk": 1.03,
            "water": 1.0,
            "olive_oil": 0.92,
            "butter": 0.911,
            "honey": 1.4,
            "rice": 0.753,  # uncooked
            "oats": 0.41,
            "salt": 1.217
        }
    
    async def calculate_nutrition(self, ingredients: List[Dict], servings: int = 1) -> Dict[str, Any]:
        """
        Calculate comprehensive nutritional information for a recipe
        
        Args:
            ingredients: List of ingredient dictionaries with name, amount, unit
            servings: Number of servings the recipe makes
            
        Returns:
            Dictionary with nutritional information
        """
        try:
            total_nutrition = {
                "calories": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
                "fiber": 0.0,
                "sugar": 0.0,
                "sodium": 0.0,
                "vitamin_c": 0.0,
                "calcium": 0.0,
                "iron": 0.0,
                "potassium": 0.0
            }
            
            missing_ingredients = []
            total_confidence = 0.0
            processed_count = 0
            
            for ingredient in ingredients:
                ingredient_name = ingredient.get("name", "").lower().strip()
                amount = ingredient.get("amount", 100)  # Default 100g
                unit = ingredient.get("unit", "g").lower()
                
                # Find matching ingredient in database
                matched_ingredient, confidence = self.find_matching_ingredient(ingredient_name)
                
                if matched_ingredient:
                    # Convert amount to grams
                    amount_in_grams = self.convert_to_grams(amount, unit, matched_ingredient)
                    
                    # Get nutrition data for this ingredient
                    nutrition_data = self.nutrition_db.loc[matched_ingredient]
                    
                    # Calculate nutrition for the specified amount
                    scale_factor = amount_in_grams / 100  # Nutrition data is per 100g
                    
                    for nutrient in total_nutrition.keys():
                        if nutrient in nutrition_data:
                            total_nutrition[nutrient] += nutrition_data[nutrient] * scale_factor
                    
                    total_confidence += confidence
                    processed_count += 1
                else:
                    missing_ingredients.append(ingredient_name)
            
            # Calculate per-serving nutrition
            per_serving_nutrition = {}
            for nutrient, value in total_nutrition.items():
                per_serving_nutrition[nutrient] = round(value / servings, 2)
            
            # Calculate overall confidence
            overall_confidence = total_confidence / max(processed_count, 1) if processed_count > 0 else 0.0
            
            return {
                "nutrition": {
                    "calories": per_serving_nutrition["calories"],
                    "protein": per_serving_nutrition["protein"],
                    "carbs": per_serving_nutrition["carbs"],
                    "fat": per_serving_nutrition["fat"],
                    "fiber": per_serving_nutrition["fiber"],
                    "sugar": per_serving_nutrition["sugar"],
                    "sodium": per_serving_nutrition["sodium"],
                    "per_serving": True
                },
                "confidence": overall_confidence,
                "missing_ingredients": missing_ingredients
            }
            
        except Exception as e:
            logger.error(f"Error calculating nutrition: {e}")
            return {
                "nutrition": {
                    "calories": 0, "protein": 0, "carbs": 0, "fat": 0,
                    "fiber": 0, "sugar": 0, "sodium": 0, "per_serving": True
                },
                "confidence": 0.0,
                "missing_ingredients": []
            }
    
    def find_matching_ingredient(self, ingredient_name: str) -> tuple:
        """
        Find the best matching ingredient in the database using ML similarity
        
        Returns:
            tuple: (matched_ingredient_name, confidence_score)
        """
        try:
            # Clean the ingredient name
            cleaned_name = self.clean_ingredient_name(ingredient_name)
            
            # Check direct matches first
            if cleaned_name in self.nutrition_db.index:
                return cleaned_name, 1.0
            
            # Check aliases
            if cleaned_name in self.ingredient_aliases:
                return self.ingredient_aliases[cleaned_name], 0.95
            
            # Use TF-IDF similarity for fuzzy matching
            query_vector = self.ingredient_matcher.transform([cleaned_name])
            corpus_vectors = self.ingredient_matcher.transform(self.ingredient_corpus)
            
            similarities = cosine_similarity(query_vector, corpus_vectors)[0]
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            if best_similarity > 0.3:  # Threshold for acceptance
                matched_name = self.ingredient_corpus[best_match_idx]
                
                # Map back to database key
                if matched_name in self.nutrition_db.index:
                    return matched_name, best_similarity
                elif matched_name in self.ingredient_aliases:
                    return self.ingredient_aliases[matched_name], best_similarity * 0.9
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Error matching ingredient {ingredient_name}: {e}")
            return None, 0.0
    
    def clean_ingredient_name(self, name: str) -> str:
        """Clean and normalize ingredient name"""
        # Remove common recipe words
        remove_words = [
            "fresh", "dried", "chopped", "diced", "sliced", "minced", "grated",
            "cooked", "raw", "organic", "free-range", "extra", "virgin",
            "unsalted", "salted", "ground", "whole", "large", "medium", "small"
        ]
        
        cleaned = name.lower().strip()
        
        # Remove quantities and units that might be in the name
        cleaned = re.sub(r'\d+\s*(cup|cups|tbsp|tsp|oz|lb|g|kg|ml|l)\s*', '', cleaned)
        cleaned = re.sub(r'\d+', '', cleaned)
        
        # Remove common words
        for word in remove_words:
            cleaned = cleaned.replace(word, "")
        
        # Clean up spacing and punctuation
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        cleaned = re.sub(r'\s+', '_', cleaned.strip())
        
        return cleaned
    
    def convert_to_grams(self, amount: float, unit: str, ingredient_name: str) -> float:
        """Convert ingredient amount to grams"""
        unit = unit.lower().strip()
        
        # Direct weight units
        if unit in ['g', 'gram', 'grams']:
            return amount
        elif unit in ['kg', 'kilogram', 'kilograms']:
            return amount * 1000
        elif unit in ['oz', 'ounce', 'ounces']:
            return amount * 28.35
        elif unit in ['lb', 'pound', 'pounds']:
            return amount * 453.592
        
        # Volume units - need density conversion
        elif unit in ['ml', 'milliliter', 'milliliters']:
            density = self.densities.get(ingredient_name, 1.0)  # Default to water density
            return amount * density
        elif unit in ['l', 'liter', 'liters']:
            density = self.densities.get(ingredient_name, 1.0)
            return amount * 1000 * density
        elif unit in ['cup', 'cups']:
            density = self.densities.get(ingredient_name, 1.0)
            return amount * 236.588 * density  # 1 cup = 236.588 ml
        elif unit in ['tbsp', 'tablespoon', 'tablespoons']:
            density = self.densities.get(ingredient_name, 1.0)
            return amount * 14.787 * density  # 1 tbsp = 14.787 ml
        elif unit in ['tsp', 'teaspoon', 'teaspoons']:
            density = self.densities.get(ingredient_name, 1.0)
            return amount * 4.929 * density  # 1 tsp = 4.929 ml
        
        # Piece-based units
        elif unit in ['piece', 'pieces', 'whole', 'item', 'items']:
            portion_data = self.portion_sizes.get(ingredient_name, {"medium": self.portion_sizes["default"]})
            return amount * portion_data.get("medium", self.portion_sizes["default"])
        
        # Default fallback
        else:
            logger.warning(f"Unknown unit '{unit}' for ingredient '{ingredient_name}', defaulting to grams")
            return amount 