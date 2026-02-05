"""Endpoint for requesting a all registered Robocop messages."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.robocop import RobocopMessagesResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get all registered Robocop messages.",
    response_model=RobocopMessagesResponse,
    responses={
        200: {"description": "Robocop messages fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_robocop_messages(request: Request):  # noqa: ANN201
    """Return all registered RobocopMessages.

    Arguments:
        request (Request): FastAPI request object.

    Returns:
        RobocopMessagesResponse: A list of RobocopMessage objects.

    """
    try:
        messages = request.app.state.robocop_service.get_robocop_error_messages()
    except Exception as e:
        logger.exception("Error retrieving keywords without usages.")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    return RobocopMessagesResponse(messages=messages)
