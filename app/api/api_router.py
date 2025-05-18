from fastapi import APIRouter
from app.api.v1.router import api_router as api_v1_router
from app.api.v2.router import api_router as api_v2_router

# Main API router that includes all versioned routers
api_router = APIRouter()

# Include versioned routers
api_router.include_router(api_v1_router, prefix="/v1")
api_router.include_router(api_v2_router, prefix="/v2")
