import logging
from app.db.database import engine, Base
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

async def startup_event():
    """
    Function to handle application startup events
    """
    # Create database tables
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    
    # Initialize Gmail API service
    logger.info("Initializing Gmail API service")
    await email_service.initialize()
    
    logger.info("Application startup complete")

async def shutdown_event():
    """
    Function to handle application shutdown events
    """
    # Cleanup connections and resources
    logger.info("Shutting down application")
