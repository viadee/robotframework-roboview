"""Health check endpoint for monitoring service availability."""

import logging

from fastapi import APIRouter
from roboview.schemas.dtos.common import HealthCheck

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Health Check",
    response_model=HealthCheck,
    responses={
        200: {"description": "Service is healthy and operational."},
        503: {"description": "Service is unavailable."},
    },
)
async def health_check():  # noqa: ANN201
    """Performs a basic health check on the FastAPI backend.

    This endpoint can primarily be used for Docker to ensure a robust container orchestration
    and management is in place.

    Returns:
        HealthCheck: Returns a JSON response with the health status

    """
    logger.info("Health check requested")
    return HealthCheck(status="ok")
