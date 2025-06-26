#!/usr/bin/env python3
"""
Recipe AI ML Backend - Main Entry Point
"""

import asyncio
import uvicorn
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=getattr(logging, log_level),
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ml_backend.log') if os.getenv('LOG_FILE') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

async def startup_checks():
    """Perform startup checks and initialization"""
    try:
        logger.info("🚀 Starting Recipe AI ML Backend...")
        
        # Create necessary directories
        os.makedirs('models_cache', exist_ok=True)
        os.makedirs('temp_images', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        logger.info("✅ Directories created")
        
        # Test imports
        try:
            import torch
            logger.info(f"✅ PyTorch available: {torch.__version__}")
            logger.info(f"✅ CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            logger.warning("❌ PyTorch not available")
        
        try:
            import transformers
            logger.info(f"✅ Transformers available: {transformers.__version__}")
        except ImportError:
            logger.warning("❌ Transformers not available")
        
        try:
            import cv2
            logger.info(f"✅ OpenCV available: {cv2.__version__}")
        except ImportError:
            logger.warning("❌ OpenCV not available")
        
        # Import app modules
        from app.database import test_connection, init_database
        
        # Test database connection
        if await test_connection():
            logger.info("✅ Database connection successful")
            init_database()
        else:
            logger.warning("⚠️  Database connection failed - continuing without database")
        
        logger.info("🎉 ML Backend startup checks complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        return False

def main():
    """Main entry point"""
    print("🤖 Recipe AI ML Backend")
    print("=" * 50)
    
    # Run startup checks
    startup_success = asyncio.run(startup_checks())
    
    if not startup_success:
        logger.error("❌ Failed to start ML backend")
        sys.exit(1)
    
    # Get configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🌐 Starting server at http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("=" * 50)
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=log_level.lower(),
        workers=1,  # Use 1 worker for ML models to avoid memory issues
        access_log=True
    )

if __name__ == "__main__":
    main() 