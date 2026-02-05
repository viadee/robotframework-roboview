"""Endpoint for fetching the most used keywords in the project."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.overview import MostUsedKeywordsResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get most used for the Robot Framework project",
    response_model=MostUsedKeywordsResponse,
    responses={
        200: {"description": "Most used keywords fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_most_used_keywords(request: Request):  # noqa: ANN201
    """Endpoint to fetch the most used keywords for the RoboView overview page.

    Arguments:
        request (Request): FastAPI request object.

    Returns:
        MostUsedKeywordsResponse: List containing most used user defined and external/builtin keywords.

    """
    try:
        most_used_user_keywords = request.app.state.keyword_usage_service.get_most_used_user_defined_keywords(5)
        most_used_external_or_builtin_keywords = (
            request.app.state.keyword_usage_service.get_most_used_external_or_builtin_keywords(5)
        )

    except Exception as e:
        logger.exception("Error fetchin most used keywords")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return MostUsedKeywordsResponse(
            most_used_user_keywords=most_used_user_keywords,
            most_used_external_keywords=most_used_external_or_builtin_keywords,
        )
