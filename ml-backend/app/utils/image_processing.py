import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import logging
from typing import Tuple, Optional, List, Dict
from fastapi import UploadFile
import aiofiles

logger = logging.getLogger(__name__)

async def process_uploaded_image(file: UploadFile, 
                               target_size: Tuple[int, int] = (640, 640),
                               enhance_contrast: bool = True) -> np.ndarray:
    """
    Process uploaded image file for ML model inference
    
    Args:
        file: FastAPI UploadFile object
        target_size: Target size for resizing (width, height)
        enhance_contrast: Whether to enhance image contrast
        
    Returns:
        Processed image as numpy array
    """
    try:
        # Read image data
        image_data = await file.read()
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Enhance image quality if requested
        if enhance_contrast:
            pil_image = enhance_image_quality(pil_image)
        
        # Resize image
        pil_image = pil_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        image_array = np.array(pil_image)
        
        return image_array
        
    except Exception as e:
        logger.error(f"Error processing uploaded image: {e}")
        raise ValueError(f"Failed to process image: {str(e)}")

def enhance_image_quality(image: Image.Image) -> Image.Image:
    """
    Enhance image quality for better ML model performance
    
    Args:
        image: PIL Image object
        
    Returns:
        Enhanced PIL Image
    """
    try:
        # Enhance contrast
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(1.2)
        
        # Enhance sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(image)
        image = sharpness_enhancer.enhance(1.1)
        
        # Enhance color saturation slightly
        color_enhancer = ImageEnhance.Color(image)
        image = color_enhancer.enhance(1.1)
        
        return image
        
    except Exception as e:
        logger.warning(f"Error enhancing image quality: {e}")
        return image

def preprocess_for_yolo(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image specifically for YOLO model
    
    Args:
        image: Input image as numpy array (RGB)
        
    Returns:
        Preprocessed image array
    """
    try:
        # YOLO expects RGB format
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Already in correct format
            processed_image = image.copy()
        else:
            raise ValueError("Image must be in RGB format")
        
        # Normalize to 0-1 range if needed
        if processed_image.max() > 1.0:
            processed_image = processed_image.astype(np.float32) / 255.0
        
        return processed_image
        
    except Exception as e:
        logger.error(f"Error preprocessing image for YOLO: {e}")
        raise

def preprocess_for_clip(image: np.ndarray) -> Image.Image:
    """
    Preprocess image for CLIP model
    
    Args:
        image: Input image as numpy array
        
    Returns:
        PIL Image ready for CLIP processing
    """
    try:
        # Convert numpy array to PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image)
        
        # Ensure RGB format
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        return pil_image
        
    except Exception as e:
        logger.error(f"Error preprocessing image for CLIP: {e}")
        raise

def detect_food_regions(image: np.ndarray, 
                       confidence_threshold: float = 0.5) -> List[Tuple[int, int, int, int]]:
    """
    Detect potential food regions in the image using simple computer vision
    
    Args:
        image: Input image as numpy array
        confidence_threshold: Minimum confidence for detection
        
    Returns:
        List of bounding boxes (x1, y1, x2, y2)
    """
    try:
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use adaptive thresholding to find potential food regions
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and aspect ratio
        food_regions = []
        image_area = image.shape[0] * image.shape[1]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area (should be reasonable size)
            if area < image_area * 0.01 or area > image_area * 0.8:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio (food items shouldn't be too elongated)
            aspect_ratio = w / h
            if aspect_ratio < 0.2 or aspect_ratio > 5.0:
                continue
            
            food_regions.append((x, y, x + w, y + h))
        
        # Sort by area (largest first) and return top regions
        food_regions.sort(key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)
        return food_regions[:5]  # Return top 5 regions
        
    except Exception as e:
        logger.error(f"Error detecting food regions: {e}")
        return []

def extract_color_features(image: np.ndarray) -> Dict[str, float]:
    """
    Extract color features that might be useful for food classification
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Dictionary of color features
    """
    try:
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Calculate color statistics
        features = {}
        
        # RGB statistics
        features['red_mean'] = float(np.mean(image[:, :, 0]))
        features['green_mean'] = float(np.mean(image[:, :, 1]))
        features['blue_mean'] = float(np.mean(image[:, :, 2]))
        
        # HSV statistics
        features['hue_mean'] = float(np.mean(hsv[:, :, 0]))
        features['saturation_mean'] = float(np.mean(hsv[:, :, 1]))
        features['value_mean'] = float(np.mean(hsv[:, :, 2]))
        
        # Color dominance (most common colors)
        rgb_flat = image.reshape(-1, 3)
        unique_colors, counts = np.unique(rgb_flat, axis=0, return_counts=True)
        dominant_color_idx = np.argmax(counts)
        features['dominant_color_r'] = float(unique_colors[dominant_color_idx][0])
        features['dominant_color_g'] = float(unique_colors[dominant_color_idx][1])
        features['dominant_color_b'] = float(unique_colors[dominant_color_idx][2])
        
        # Color diversity (how many distinct colors)
        features['color_diversity'] = float(len(unique_colors) / len(rgb_flat))
        
        return features
        
    except Exception as e:
        logger.error(f"Error extracting color features: {e}")
        return {}

def detect_texture_features(image: np.ndarray) -> Dict[str, float]:
    """
    Extract texture features using simple computer vision techniques
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Dictionary of texture features
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        features = {}
        
        # Edge density (indicator of texture complexity)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        features['edge_density'] = float(edge_density)
        
        # Local binary pattern approximation
        # Calculate local variance as a simple texture measure
        kernel = np.ones((3, 3), np.float32) / 9
        local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        local_variance = cv2.filter2D((gray.astype(np.float32) - local_mean) ** 2, -1, kernel)
        features['texture_variance'] = float(np.mean(local_variance))
        
        # Contrast measure
        features['contrast'] = float(np.std(gray))
        
        return features
        
    except Exception as e:
        logger.error(f"Error extracting texture features: {e}")
        return {}

async def save_processed_image(image: np.ndarray, filename: str, 
                             output_dir: str = "temp_images") -> str:
    """
    Save processed image to temporary directory
    
    Args:
        image: Image array to save
        filename: Output filename
        output_dir: Output directory
        
    Returns:
        Path to saved file
    """
    try:
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert array to PIL Image and save
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image)
        filepath = os.path.join(output_dir, filename)
        pil_image.save(filepath)
        
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving processed image: {e}")
        raise

def validate_image_format(file: UploadFile) -> bool:
    """
    Validate if uploaded file is a supported image format
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        True if valid image format, False otherwise
    """
    try:
        supported_formats = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
            'image/bmp', 'image/tiff', 'image/webp'
        }
        
        return file.content_type in supported_formats
        
    except Exception as e:
        logger.error(f"Error validating image format: {e}")
        return False

def calculate_image_quality_score(image: np.ndarray) -> float:
    """
    Calculate a simple quality score for the image
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Quality score between 0 and 1
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate sharpness using Laplacian variance
        laplacian_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_variance / 1000.0)  # Normalize
        
        # Calculate brightness score (prefer well-lit images)
        brightness = np.mean(gray) / 255.0
        brightness_score = 1.0 - abs(0.5 - brightness) * 2  # Prefer ~50% brightness
        
        # Calculate contrast score
        contrast = np.std(gray) / 255.0
        contrast_score = min(1.0, contrast * 4)  # Normalize
        
        # Combined quality score
        quality_score = (sharpness_score * 0.5 + brightness_score * 0.3 + contrast_score * 0.2)
        
        return float(quality_score)
        
    except Exception as e:
        logger.error(f"Error calculating image quality score: {e}")
        return 0.5  # Default medium quality 