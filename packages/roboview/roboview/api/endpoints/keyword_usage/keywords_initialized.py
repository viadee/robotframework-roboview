"""Endpoint for fetching initialized keywords in a Robot Framework file."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.common import KeywordType
from roboview.schemas.dtos.keyword_usage import InitializedKeywordsResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get initialized keywords in a Robot Framework file",
    response_model=InitializedKeywordsResponse,  # noqa: FAST001
    responses={
        200: {"description": "Initialized keywords fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_init_keywords(request: Request, file_path: Path) -> InitializedKeywordsResponse:
    """Endpoint ro fetch all initialized keywords in a file.

    Arguments:
        request (Request): FastAPI request object.
        file_path (Path): File path to get called keywords from.

    Returns:
        InitializedKeywordsResponse: List containing all initialized keyword names and usage.

    """
    try:
        init_keywords_with_usage = request.app.state.keyword_usage_service.get_keywords_with_global_usage_for_file(
            file_path, KeywordType.INITIALIZED
        )
    except Exception as e:
        logger.exception("Error fetching init keywords for resource %s:", file_path)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return InitializedKeywordsResponse(initialized_keywords=init_keywords_with_usage)
