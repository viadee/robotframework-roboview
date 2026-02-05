"""Router that bundles all Robocop endpoints."""

from fastapi import APIRouter

from .robocop_message import router as robocop_message_router
from .robocop_messages import router as robocop_messages_router

# Create system API router
api_router = APIRouter()

# Include all robocop endpoint routers
api_router.include_router(robocop_message_router, prefix="/robocop-message", tags=["robocop_message"])
api_router.include_router(robocop_messages_router, prefix="/robocop-messages-all", tags=["robocop_messages_all"])
