"""Router that bundles all keyword usage related endpoints."""

from fastapi import APIRouter

from .keyword_duplicates import router as keyword_duplicate_router
from .keyword_similarity import router as keyword_similarity_router
from .keyword_usage_resource import router as keyword_usage_resource_router
from .keyword_usage_robot import router as keyword_usage_robot_router
from .keywords_called import router as keywords_called_router
from .keywords_initialized import router as keywords_initialized_router
from .keywords_wo_documentation import router as keywords_wo_documentation_router
from .keywords_wo_usages import router as keywords_wo_usages_router

# Create keyword usage API router
api_router = APIRouter()

# Include all keyword usage endpoint routers
api_router.include_router(keywords_called_router, prefix="/keywords-called", tags=["called_keywords"])
api_router.include_router(keyword_similarity_router, prefix="/keyword-similarity", tags=["keyword_similarity"])
api_router.include_router(keyword_usage_robot_router, prefix="/keyword-usage-robot", tags=["keyword_usage_robot"])
api_router.include_router(keywords_initialized_router, prefix="/keywords-initialized", tags=["initialized_keywords"])
api_router.include_router(
    keyword_usage_resource_router, prefix="/keyword-usage-resource", tags=["keyword_usage_resource"]
)
api_router.include_router(
    keywords_wo_documentation_router, prefix="/keywords-without-documentation", tags=["keyword_without_documentation"]
)

api_router.include_router(keywords_wo_usages_router, prefix="/keywords-without-usages", tags=["keyword_without_usages"])
api_router.include_router(keyword_duplicate_router, prefix="/keywords-duplicates", tags=["keyword_duplicates"])
