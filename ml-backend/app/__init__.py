#!/usr/bin/env python3
"""
ML Backend Startup Script
"""

import asyncio
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def startup():
    """Startup routine for the ML backend"""
    try:
        logger.info("Starting Recipe AI ML Backend...")
        
        # Import and test database connection
        from app.database import test_connection, init_database
        
        # Test database connection
        if await test_connection():
            logger.info("Database connection successful")
            init_database()
        else:
            logger.error("Database connection failed")
            return False
        
        # Pre-load ML models (optional - they can be lazy loaded)
        logger.info("ML Backend startup complete")
        return True
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        return False

def main():
    """Main entry point"""
    # Run startup routine
    startup_success = asyncio.run(startup())
    
    if not startup_success:
        logger.error("Failed to start ML backend")
        exit(1)
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        workers=1  # Use 1 worker for ML models to avoid memory issues
    )

if __name__ == "__main__":
    main() 