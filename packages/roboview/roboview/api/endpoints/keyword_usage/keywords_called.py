"""Endpoint for fetching called keywords in a Robot Framework file."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.common import KeywordType
from roboview.schemas.dtos.keyword_usage import CalledKeywordsResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get called keywords in a Robot Framework file",
    response_model=CalledKeywordsResponse,
    responses={
        200: {"description": "Called keywords fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_called_keywords(request: Request, file_path: Path):  # noqa: ANN201
    """Endpoint ro fetch all called keywords in a file.

    Arguments:
        request (Request): FastAPI request object.
        file_path (Path): File path to get called keywords from.

    Returns:
        CalledKeywordsResponse: List containing all called keyword names and usage.

    """
    try:
        called_keywords_with_usage = request.app.state.keyword_usage_service.get_keywords_with_global_usage_for_file(
            file_path, KeywordType.CALLED
        )
    except ValueError as v:
        logger.exception("Invalid file type. Must be .robot or .resource")
        raise HTTPException(status_code=400, detail="Bad Request") from v
    except Exception as e:
        logger.exception("Error fetching called keywords for file %s:", file_path)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return CalledKeywordsResponse(called_keywords=called_keywords_with_usage)
