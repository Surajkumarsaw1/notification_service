from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_router import api_router
from app.core.events import startup_event, shutdown_event
from app.core.config import settings

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="An API for sending and managing notifications across multiple channels",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Set up CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register event handlers
    application.add_event_handler("startup", startup_event)
    application.add_event_handler("shutdown", shutdown_event)

    # Register API router with versioned endpoints
    application.include_router(api_router, prefix=settings.API_PREFIX)

    @application.get("/", tags=["status"])
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION
        }

    return application

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
