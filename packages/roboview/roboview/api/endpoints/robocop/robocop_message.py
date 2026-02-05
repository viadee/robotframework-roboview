"""Endpoint for requesting a single Robocop message."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.robocop import RobocopMessageResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get a single Robocop message based on its uuid..",
    response_model=RobocopMessageResponse,
    responses={
        200: {"description": "Robocop message fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_robocop_message(request: Request, message_uuid: str):  # noqa: ANN201
    """Return a single RobocopMessage based on its uuid.

    Arguments:
        request (Request): FastAPI request object.
        message_uuid (str): RobocopMessage uuid.

    Returns:
        RobocopMessageResponse: Robocop Message object.

    """
    try:
        message = request.app.state.robocop_service.get_robocop_message_by_id(message_uuid)
    except Exception as e:
        logger.exception("Error retrieving keywords without usages.")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    return RobocopMessageResponse(message=message)
