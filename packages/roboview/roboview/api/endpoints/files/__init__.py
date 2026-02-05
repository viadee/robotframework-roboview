"""Router that bundles all file related endpoints."""

from fastapi import APIRouter

from .all_files import router as all_files_router
from .resource_files import router as resource_router
from .robot_files import router as robot_router

# Create file API router
api_router = APIRouter()

# Include all file endpoint routers
api_router.include_router(robot_router, prefix="/robot", tags=["robot"])
api_router.include_router(all_files_router, prefix="/all-files", tags=["all"])
api_router.include_router(resource_router, prefix="/resource", tags=["resource"])
