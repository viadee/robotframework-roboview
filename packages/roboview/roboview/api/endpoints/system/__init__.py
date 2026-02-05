"""Router that bundles all system endpoints."""

from fastapi import APIRouter

from .health import router as health_router
from .initialize import router as initialize_router

# Create system API router
api_router = APIRouter()

# Include all system endpoint routers
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(initialize_router, prefix="/initialize", tags=["initialize"])
