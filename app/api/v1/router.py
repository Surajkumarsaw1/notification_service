from fastapi import APIRouter
from app.api.v1.endpoints import notifications, users

# Initialize v1 API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
