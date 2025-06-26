import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import re
from collections import Counter
import json

logger = logging.getLogger(__name__)

class TagGenerator:
    """
    Advanced tag generator using NLP models to analyze recipes and generate relevant tags
    """
    
    def __init__(self):
        self.nlp = None
        self.classifier = None
        self.dietary_classifier = None
        self.cuisine_classifier = None
        self.cooking_method_classifier = None
        self.tag_rules = None
        self.ingredient_categories = None
        
    async def load_model(self):
        """Load NLP models and classification pipelines"""
        try:
            logger.info("Loading tag generation models...")
            
            # Download required NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('punkt')
                nltk.download('stopwords')
            
            # Load spaCy model for NER and linguistic analysis
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, using simplified processing")
                self.nlp = None
            
            # Initialize classification pipelines
            self.initialize_classifiers()
            
            # Load rule-based tag mappings
            self.load_tag_rules()
            
            # Load ingredient categorization
            self.load_ingredient_categories()
            
            logger.info("Tag generation models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading tag generation models: {e}")
            raise
    
    def initialize_classifiers(self):
        """Initialize various classification pipelines"""
        try:
            # General recipe classification pipeline
            self.classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased",
                return_all_scores=True
            )
            
            # Initialize other classifiers with fallback
            self.dietary_classifier = self.create_dietary_classifier()
            self.cuisine_classifier = self.create_cuisine_classifier()
            self.cooking_method_classifier = self.create_cooking_method_classifier()
            
        except Exception as e:
            logger.warning(f"Could not load transformer models: {e}")
            # Fallback to rule-based classification
            self.classifier = None
    
    def create_dietary_classifier(self):
        """Create classifier for dietary restrictions"""
        # Rule-based dietary classification
        return {
            "vegetarian": {
                "exclude": ["chicken", "beef", "pork", "fish", "meat", "bacon", "ham", "sausage", "lamb"],
                "include": ["vegetable", "fruit", "grain", "dairy", "egg"]
            },
            "vegan": {
                "exclude": ["chicken", "beef", "pork", "fish", "meat", "dairy", "cheese", "milk", "butter", "egg", "honey"],
                "include": ["vegetable", "fruit", "grain", "plant", "nuts", "seeds"]
            },
            "gluten-free": {
                "exclude": ["wheat", "flour", "bread", "pasta", "barley", "rye", "oats"],
                "include": ["rice", "quinoa", "corn", "potato"]
            },
            "dairy-free": {
                "exclude": ["milk", "cheese", "butter", "cream", "yogurt", "dairy"],
                "include": []
            },
            "low-carb": {
                "exclude": ["rice", "pasta", "bread", "potato", "sugar"],
                "include": ["meat", "vegetable", "protein"]
            },
            "keto": {
                "exclude": ["rice", "pasta", "bread", "potato", "sugar", "fruit"],
                "include": ["meat", "fat", "oil", "cheese", "nuts"]
            }
        }
    
    def create_cuisine_classifier(self):
        """Create classifier for cuisine types"""
        return {
            "italian": ["pasta", "tomato", "basil", "mozzarella", "parmesan", "olive oil", "garlic"],
            "mexican": ["pepper", "chili", "corn", "avocado", "lime", "cilantro", "cumin"],
            "chinese": ["soy sauce", "ginger", "garlic", "rice", "sesame", "green onion"],
            "indian": ["curry", "turmeric", "cumin", "coriander", "garam masala", "cardamom"],
            "thai": ["coconut", "lemongrass", "basil", "chili", "lime", "fish sauce"],
            "japanese": ["soy sauce", "miso", "rice", "nori", "wasabi", "ginger"],
            "french": ["butter", "cream", "wine", "herbs", "shallot", "thyme"],
            "mediterranean": ["olive oil", "tomato", "feta", "olives", "lemon", "oregano"],
            "american": ["bacon", "cheese", "burger", "bbq", "ranch", "corn"],
            "greek": ["feta", "olive oil", "lemon", "oregano", "olives", "cucumber"]
        }
    
    def create_cooking_method_classifier(self):
        """Create classifier for cooking methods"""
        return {
            "grilled": ["grill", "barbecue", "bbq", "char", "smoky"],
            "baked": ["bake", "oven", "roast", "crispy", "golden"],
            "fried": ["fry", "deep", "pan", "crispy", "oil"],
            "steamed": ["steam", "tender", "moist", "healthy"],
            "stir-fry": ["stir", "wok", "quick", "vegetables"],
            "slow-cooked": ["slow", "crock", "tender", "hours"],
            "raw": ["fresh", "salad", "uncooked", "raw"],
            "no-cook": ["no cook", "assembly", "mix", "combine"],
            "pressure-cooked": ["pressure", "instant", "quick"]
        }
    
    def load_tag_rules(self):
        """Load rule-based tag mappings"""
        self.tag_rules = {
            "meal_type": {
                "breakfast": ["breakfast", "morning", "cereal", "pancake", "waffle", "toast", "coffee"],
                "lunch": ["lunch", "sandwich", "salad", "soup", "wrap"],
                "dinner": ["dinner", "main", "entree", "roast", "steak"],
                "dessert": ["dessert", "sweet", "cake", "cookie", "pie", "chocolate", "sugar"],
                "snack": ["snack", "bite", "appetizer", "dip", "nuts"],
                "drink": ["drink", "beverage", "smoothie", "juice", "cocktail"]
            },
            "difficulty": {
                "easy": ["simple", "quick", "easy", "basic", "beginner"],
                "medium": ["medium", "intermediate", "moderate"],
                "hard": ["advanced", "complex", "difficult", "professional", "technique"]
            },
            "time": {
                "quick": ["5 min", "10 min", "15 min", "quick", "fast", "instant"],
                "30-minute": ["30 min", "half hour", "quick dinner"],
                "slow": ["hours", "overnight", "slow", "long", "patience"]
            },
            "season": {
                "summer": ["fresh", "cold", "salad", "fruit", "bbq", "grill"],
                "winter": ["warm", "hot", "soup", "stew", "comfort", "hearty"],
                "spring": ["fresh", "light", "green", "herbs"],
                "fall": ["pumpkin", "apple", "squash", "warm", "spice"]
            },
            "occasion": {
                "party": ["party", "crowd", "entertaining", "guests", "celebration"],
                "date-night": ["romantic", "elegant", "special", "intimate"],
                "family": ["family", "kids", "children", "crowd", "sharing"],
                "holiday": ["holiday", "thanksgiving", "christmas", "easter", "special"]
            }
        }
    
    def load_ingredient_categories(self):
        """Load ingredient categorization for better tag generation"""
        self.ingredient_categories = {
            "protein": ["chicken", "beef", "pork", "fish", "eggs", "tofu", "beans", "lentils"],
            "vegetables": ["tomato", "onion", "carrot", "broccoli", "spinach", "pepper", "cucumber"],
            "fruits": ["apple", "banana", "orange", "lemon", "lime", "berries", "grapes"],
            "grains": ["rice", "pasta", "bread", "quinoa", "oats", "barley"],
            "dairy": ["milk", "cheese", "butter", "cream", "yogurt"],
            "spices": ["salt", "pepper", "garlic", "ginger", "cumin", "paprika"],
            "herbs": ["basil", "oregano", "thyme", "rosemary", "cilantro", "parsley"],
            "fats": ["oil", "butter", "avocado", "nuts", "seeds"]
        }
    
    async def generate_tags(self, ingredients: List[Dict], instructions: List[str], 
                          cuisine: Optional[str] = None, category: Optional[str] = None) -> List[str]:
        """
        Generate comprehensive tags for a recipe
        
        Args:
            ingredients: List of ingredient dictionaries
            instructions: List of instruction steps
            cuisine: Optional cuisine type
            category: Optional recipe category
            
        Returns:
            List of relevant tags
        """
        try:
            tags = set()
            
            # Extract ingredient names
            ingredient_names = [ing.get("name", "").lower() for ing in ingredients]
            
            # Combine all text for analysis
            all_text = " ".join(ingredient_names + instructions)
            if cuisine:
                all_text += f" {cuisine}"
            if category:
                all_text += f" {category}"
            
            # Generate different types of tags
            dietary_tags = self.generate_dietary_tags(ingredient_names)
            cuisine_tags = self.generate_cuisine_tags(ingredient_names, cuisine)
            cooking_method_tags = self.generate_cooking_method_tags(instructions)
            meal_type_tags = self.generate_meal_type_tags(all_text, category)
            difficulty_tags = self.generate_difficulty_tags(instructions)
            time_tags = self.generate_time_tags(instructions)
            seasonal_tags = self.generate_seasonal_tags(ingredient_names)
            ingredient_category_tags = self.generate_ingredient_category_tags(ingredient_names)
            
            # Combine all tags
            tags.update(dietary_tags)
            tags.update(cuisine_tags)
            tags.update(cooking_method_tags)
            tags.update(meal_type_tags)
            tags.update(difficulty_tags)
            tags.update(time_tags)
            tags.update(seasonal_tags)
            tags.update(ingredient_category_tags)
            
            # Use NLP for additional tag extraction if available
            if self.nlp:
                nlp_tags = self.extract_nlp_tags(all_text)
                tags.update(nlp_tags)
            
            # Use transformer model for classification if available
            if self.classifier:
                ml_tags = await self.extract_ml_tags(all_text)
                tags.update(ml_tags)
            
            # Filter and rank tags
            final_tags = self.filter_and_rank_tags(list(tags), all_text)
            
            return final_tags[:15]  # Return top 15 tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ["recipe", "cooking"]  # Fallback tags
    
    def generate_dietary_tags(self, ingredients: List[str]) -> List[str]:
        """Generate dietary restriction tags"""
        tags = []
        
        for diet_type, rules in self.dietary_classifier.items():
            exclude_found = any(excl in " ".join(ingredients) for excl in rules["exclude"])
            include_found = any(incl in " ".join(ingredients) for incl in rules["include"]) if rules["include"] else True
            
            if not exclude_found and include_found:
                tags.append(diet_type)
        
        return tags
    
    def generate_cuisine_tags(self, ingredients: List[str], cuisine: Optional[str]) -> List[str]:
        """Generate cuisine-based tags"""
        tags = []
        ingredient_text = " ".join(ingredients)
        
        # Add provided cuisine
        if cuisine:
            tags.append(cuisine.lower())
        
        # Detect cuisine from ingredients
        for cuisine_type, keywords in self.cuisine_classifier.items():
            score = sum(1 for keyword in keywords if keyword in ingredient_text)
            if score >= 2:  # Require at least 2 matching ingredients
                tags.append(cuisine_type)
        
        return tags
    
    def generate_cooking_method_tags(self, instructions: List[str]) -> List[str]:
        """Generate cooking method tags"""
        tags = []
        instruction_text = " ".join(instructions).lower()
        
        for method, keywords in self.cooking_method_classifier.items():
            if any(keyword in instruction_text for keyword in keywords):
                tags.append(method)
        
        return tags
    
    def generate_meal_type_tags(self, text: str, category: Optional[str]) -> List[str]:
        """Generate meal type tags"""
        tags = []
        text_lower = text.lower()
        
        # Add provided category
        if category:
            tags.append(category.lower())
        
        # Detect meal type from text
        for meal_type, keywords in self.tag_rules["meal_type"].items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(meal_type)
        
        return tags
    
    def generate_difficulty_tags(self, instructions: List[str]) -> List[str]:
        """Generate difficulty tags based on instructions complexity"""
        tags = []
        instruction_text = " ".join(instructions).lower()
        num_steps = len(instructions)
        
        # Rule-based difficulty assessment
        if num_steps <= 3:
            tags.append("easy")
        elif num_steps <= 6:
            tags.append("medium")
        else:
            tags.append("hard")
        
        # Check for difficulty keywords
        for difficulty, keywords in self.tag_rules["difficulty"].items():
            if any(keyword in instruction_text for keyword in keywords):
                tags.append(difficulty)
                break
        
        return tags
    
    def generate_time_tags(self, instructions: List[str]) -> List[str]:
        """Generate time-based tags"""
        tags = []
        instruction_text = " ".join(instructions).lower()
        
        # Extract time mentions using regex
        time_pattern = r'(\d+)\s*(min|minute|minutes|hour|hours|hr|hrs)'
        times = re.findall(time_pattern, instruction_text)
        
        total_minutes = 0
        for time_val, unit in times:
            minutes = int(time_val)
            if unit in ['hour', 'hours', 'hr', 'hrs']:
                minutes *= 60
            total_minutes += minutes
        
        # Categorize by total time
        if total_minutes > 0:
            if total_minutes <= 15:
                tags.append("quick")
            elif total_minutes <= 30:
                tags.append("30-minute")
            elif total_minutes >= 120:
                tags.append("slow")
        
        # Check for time keywords
        for time_type, keywords in self.tag_rules["time"].items():
            if any(keyword in instruction_text for keyword in keywords):
                tags.append(time_type)
        
        return tags
    
    def generate_seasonal_tags(self, ingredients: List[str]) -> List[str]:
        """Generate seasonal tags based on ingredients"""
        tags = []
        ingredient_text = " ".join(ingredients)
        
        for season, keywords in self.tag_rules["season"].items():
            if any(keyword in ingredient_text for keyword in keywords):
                tags.append(season)
        
        return tags
    
    def generate_ingredient_category_tags(self, ingredients: List[str]) -> List[str]:
        """Generate tags based on ingredient categories"""
        tags = []
        ingredient_text = " ".join(ingredients)
        
        for category, items in self.ingredient_categories.items():
            if any(item in ingredient_text for item in items):
                tags.append(f"{category}-rich")
        
        return tags
    
    def extract_nlp_tags(self, text: str) -> List[str]:
        """Extract tags using spaCy NLP"""
        tags = []
        
        try:
            doc = self.nlp(text)
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['FOOD', 'PRODUCT', 'ORG'] and len(ent.text) > 2:
                    tags.append(ent.text.lower())
            
            # Extract adjectives that might be descriptive
            for token in doc:
                if token.pos_ == 'ADJ' and len(token.text) > 3:
                    tags.append(token.lemma_.lower())
            
        except Exception as e:
            logger.warning(f"Error in NLP tag extraction: {e}")
        
        return tags
    
    async def extract_ml_tags(self, text: str) -> List[str]:
        """Extract tags using transformer models"""
        tags = []
        
        try:
            # Use the classifier to get predictions
            results = self.classifier(text)
            
            # Extract high-confidence predictions
            for result in results:
                if result['score'] > 0.7:  # High confidence threshold
                    label = result['label'].lower()
                    if len(label) > 2:  # Filter out very short labels
                        tags.append(label)
            
        except Exception as e:
            logger.warning(f"Error in ML tag extraction: {e}")
        
        return tags
    
    def filter_and_rank_tags(self, tags: List[str], text: str) -> List[str]:
        """Filter and rank tags by relevance"""
        # Remove duplicates and very short tags
        unique_tags = list(set(tag for tag in tags if len(tag) > 2))
        
        # Score tags based on frequency in text and predefined importance
        tag_scores = {}
        text_lower = text.lower()
        
        for tag in unique_tags:
            score = 0
            
            # Base score from tag frequency in text
            score += text_lower.count(tag.replace("-", " "))
            
            # Bonus for important tag categories
            if tag in ["vegetarian", "vegan", "gluten-free", "dairy-free"]:
                score += 5
            elif tag in ["easy", "quick", "30-minute"]:
                score += 3
            elif tag in ["italian", "mexican", "chinese", "indian"]:
                score += 2
            
            tag_scores[tag] = score
        
        # Sort by score and return
        ranked_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, score in ranked_tags if score > 0] 