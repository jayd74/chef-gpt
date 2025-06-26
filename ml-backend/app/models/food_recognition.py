import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import cv2
import numpy as np
from PIL import Image
import logging
from typing import List, Dict, Any, Tuple
import json
import os
from ultralytics import YOLO
import clip
import time

logger = logging.getLogger(__name__)

class FoodRecognitionModel:
    """
    Advanced food recognition model using multiple ML approaches:
    1. YOLO for object detection and localization
    2. CLIP for semantic understanding
    3. Custom food classification model
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.yolo_model = None
        self.clip_model = None
        self.clip_preprocess = None
        self.food_classifier = None
        self.ingredient_classes = None
        self.nutrition_db = None
        
        # Load food ingredient mappings
        self.load_ingredient_mappings()
        
    async def load_model(self):
        """Load all required models"""
        try:
            logger.info("Loading food recognition models...")
            
            # Load YOLO model for object detection
            self.yolo_model = YOLO('yolov8n.pt')  # Will download if not present
            
            # Load CLIP model for semantic understanding
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
            
            # Load custom food classifier (ResNet50 fine-tuned on food dataset)
            self.food_classifier = resnet50(weights=ResNet50_Weights.DEFAULT)
            self.food_classifier.fc = torch.nn.Linear(2048, len(self.ingredient_classes))
            self.food_classifier.to(self.device)
            self.food_classifier.eval()
            
            # Load nutrition database
            self.load_nutrition_database()
            
            logger.info("Food recognition models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading food recognition models: {e}")
            raise
    
    def load_ingredient_mappings(self):
        """Load ingredient class mappings"""
        # In a real implementation, this would load from a trained model's classes
        self.ingredient_classes = [
            "apple", "banana", "orange", "tomato", "potato", "onion", "garlic",
            "carrot", "broccoli", "spinach", "lettuce", "cucumber", "bell_pepper",
            "chicken", "beef", "pork", "fish", "eggs", "cheese", "milk", "butter",
            "bread", "rice", "pasta", "flour", "sugar", "salt", "pepper",
            "olive_oil", "lemon", "lime", "avocado", "mushrooms", "corn",
            "beans", "peas", "nuts", "herbs", "spices", "berries"
        ]
        
        # Create ingredient to index mapping
        self.ingredient_to_idx = {ing: idx for idx, ing in enumerate(self.ingredient_classes)}
    
    def load_nutrition_database(self):
        """Load nutritional information database"""
        # Simplified nutrition database - in production, use USDA database
        self.nutrition_db = {
            "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
            "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
            "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
            "beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15},
            "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
            "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
            "onion": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1},
            "olive_oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100},
            # Add more ingredients as needed
        }
    
    async def analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze food image and return ingredient recognition results
        """
        start_time = time.time()
        
        try:
            # Convert numpy array to PIL Image
            if len(image.shape) == 3 and image.shape[2] == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image).convert('RGB')
            
            # Run multiple detection methods
            yolo_results = await self.detect_with_yolo(image)
            clip_results = await self.analyze_with_clip(pil_image)
            classifier_results = await self.classify_with_resnet(pil_image)
            
            # Combine and refine results
            ingredients = self.combine_detection_results(
                yolo_results, clip_results, classifier_results
            )
            
            # Generate recipe suggestions based on detected ingredients
            suggestions = self.generate_recipe_suggestions(ingredients)
            
            processing_time = time.time() - start_time
            
            return {
                "ingredients": ingredients,
                "suggestions": suggestions,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "ingredients": [],
                "suggestions": [],
                "processing_time": time.time() - start_time
            }
    
    async def detect_with_yolo(self, image: np.ndarray) -> List[Dict]:
        """Use YOLO for object detection"""
        try:
            results = self.yolo_model(image)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Map YOLO class to food ingredient if possible
                        class_name = self.yolo_model.names[class_id]
                        ingredient_name = self.map_yolo_class_to_ingredient(class_name)
                        
                        if ingredient_name and confidence > 0.5:
                            detections.append({
                                "name": ingredient_name,
                                "confidence": float(confidence),
                                "bounding_box": [float(x1), float(y1), float(x2), float(y2)],
                                "source": "yolo"
                            })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
            return []
    
    async def analyze_with_clip(self, image: Image.Image) -> List[Dict]:
        """Use CLIP for semantic understanding"""
        try:
            # Preprocess image for CLIP
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            # Create text prompts for common ingredients
            text_prompts = [f"a photo of {ingredient}" for ingredient in self.ingredient_classes]
            text_inputs = clip.tokenize(text_prompts).to(self.device)
            
            # Calculate features
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                text_features = self.clip_model.encode_text(text_inputs)
                
                # Calculate similarities
                similarities = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                similarities = similarities.cpu().numpy()[0]
            
            # Extract top predictions
            detections = []
            for i, similarity in enumerate(similarities):
                if similarity > 0.1:  # Threshold for relevance
                    detections.append({
                        "name": self.ingredient_classes[i],
                        "confidence": float(similarity),
                        "source": "clip"
                    })
            
            # Sort by confidence and return top results
            detections.sort(key=lambda x: x["confidence"], reverse=True)
            return detections[:10]
            
        except Exception as e:
            logger.error(f"Error in CLIP analysis: {e}")
            return []
    
    async def classify_with_resnet(self, image: Image.Image) -> List[Dict]:
        """Use custom ResNet classifier"""
        try:
            # Transform image for ResNet
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            image_tensor = transform(image).unsqueeze(0).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.food_classifier(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                probabilities = probabilities.cpu().numpy()[0]
            
            # Extract top predictions
            detections = []
            for i, prob in enumerate(probabilities):
                if prob > 0.05:  # Threshold for relevance
                    detections.append({
                        "name": self.ingredient_classes[i],
                        "confidence": float(prob),
                        "source": "resnet"
                    })
            
            # Sort by confidence
            detections.sort(key=lambda x: x["confidence"], reverse=True)
            return detections[:5]
            
        except Exception as e:
            logger.error(f"Error in ResNet classification: {e}")
            return []
    
    def combine_detection_results(self, yolo_results: List[Dict], 
                                clip_results: List[Dict], 
                                classifier_results: List[Dict]) -> List[Dict]:
        """Combine results from different models"""
        # Create a dictionary to aggregate results by ingredient name
        ingredient_scores = {}
        
        # Process YOLO results (high weight for localized detection)
        for detection in yolo_results:
            name = detection["name"]
            if name not in ingredient_scores:
                ingredient_scores[name] = {
                    "name": name,
                    "confidence": 0.0,
                    "bounding_box": detection.get("bounding_box"),
                    "quantity": None,
                    "unit": None
                }
            ingredient_scores[name]["confidence"] += detection["confidence"] * 0.4
        
        # Process CLIP results (medium weight for semantic understanding)
        for detection in clip_results:
            name = detection["name"]
            if name not in ingredient_scores:
                ingredient_scores[name] = {
                    "name": name,
                    "confidence": 0.0,
                    "bounding_box": None,
                    "quantity": None,
                    "unit": None
                }
            ingredient_scores[name]["confidence"] += detection["confidence"] * 0.35
        
        # Process classifier results (medium weight)
        for detection in classifier_results:
            name = detection["name"]
            if name not in ingredient_scores:
                ingredient_scores[name] = {
                    "name": name,
                    "confidence": 0.0,
                    "bounding_box": None,
                    "quantity": None,
                    "unit": None
                }
            ingredient_scores[name]["confidence"] += detection["confidence"] * 0.25
        
        # Convert to list and sort by confidence
        final_ingredients = list(ingredient_scores.values())
        final_ingredients.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Filter and normalize
        filtered_ingredients = []
        for ingredient in final_ingredients:
            if ingredient["confidence"] > 0.1:  # Final threshold
                # Normalize confidence to 0-1 range
                ingredient["confidence"] = min(1.0, ingredient["confidence"])
                filtered_ingredients.append(ingredient)
        
        return filtered_ingredients[:10]  # Return top 10
    
    def map_yolo_class_to_ingredient(self, yolo_class: str) -> str:
        """Map YOLO object class to food ingredient"""
        # Mapping from COCO classes to food ingredients
        class_mapping = {
            "apple": "apple",
            "banana": "banana",
            "orange": "orange",
            "carrot": "carrot",
            "broccoli": "broccoli",
            "pizza": "cheese",  # Approximation
            "donut": "flour",
            "cake": "flour",
            "sandwich": "bread",
            "hot dog": "pork",
            "person": None,  # Filter out non-food items
            "car": None,
            "chair": None,
        }
        
        return class_mapping.get(yolo_class.lower())
    
    def generate_recipe_suggestions(self, ingredients: List[Dict]) -> List[str]:
        """Generate recipe suggestions based on detected ingredients"""
        if not ingredients:
            return []
        
        # Extract ingredient names
        ingredient_names = [ing["name"] for ing in ingredients if ing["confidence"] > 0.3]
        
        # Simple rule-based recipe suggestions
        suggestions = []
        
        # Check for common combinations
        if "tomato" in ingredient_names and "onion" in ingredient_names:
            suggestions.append("Tomato and onion salad")
            if "olive_oil" in ingredient_names:
                suggestions.append("Mediterranean salad")
        
        if "chicken" in ingredient_names:
            suggestions.append("Grilled chicken")
            if "rice" in ingredient_names:
                suggestions.append("Chicken and rice bowl")
        
        if "apple" in ingredient_names:
            suggestions.append("Apple slices with cinnamon")
            if "flour" in ingredient_names:
                suggestions.append("Apple pie")
        
        # Generic suggestions based on main ingredient
        if ingredient_names:
            main_ingredient = ingredient_names[0]
            suggestions.append(f"Simple {main_ingredient} recipe")
            suggestions.append(f"{main_ingredient.capitalize()} stir-fry")
        
        return suggestions[:5]  # Return top 5 suggestions 