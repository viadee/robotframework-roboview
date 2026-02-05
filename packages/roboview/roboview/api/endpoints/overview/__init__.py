"""Router that bundles overview related endpoints."""

from fastapi import APIRouter

from .kpis import router as kpi_router
from .most_used_keywords import router as most_used_keyword_router
from .robocop_summary import router as issue_summary_router

# Create overview API router
api_router = APIRouter()

# Include all overview endpoint routers
api_router.include_router(kpi_router, prefix="/kpis", tags=["KPIs"])
api_router.include_router(most_used_keyword_router, prefix="/most-used-keywords", tags=["most_used_keywords"])
api_router.include_router(issue_summary_router, prefix="/robocop-issue-summary", tags=["robocop_issue_summary"])
