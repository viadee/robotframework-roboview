"""Central router that bundles all API endpoints."""

from fastapi import APIRouter

from .files import api_router as files_router
from .keyword_usage import api_router as keyword_usage_router
from .overview import api_router as overview_router
from .robocop import api_router as robocop_router
from .system import api_router as system_router

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(system_router, prefix="/system", tags=["system"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(keyword_usage_router, prefix="/keyword-usage", tags=["keyword-usage"])
api_router.include_router(overview_router, prefix="/overview", tags=["overview"])
api_router.include_router(robocop_router, prefix="/robocop", tags=["robocop"])
