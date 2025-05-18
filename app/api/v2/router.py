from fastapi import APIRouter
from app.api.v2.endpoints import notifications, users

# Initialize v2 API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications-v2"])
api_router.include_router(users.router, prefix="/users", tags=["users-v2"])
