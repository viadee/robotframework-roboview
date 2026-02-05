"""Endpoint for fetching keywords that have an empty [Documentation]."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.keyword_usage import KeywordsWithoutDocResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get keywords without a documentation",
    response_model=KeywordsWithoutDocResponse,
    responses={
        200: {"description": "Keywords without documentation fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_keywords_wo_doc(request: Request):  # noqa: ANN201
    """Returns a list of keywords that do not have any Robotframework documentation/description, with details.

    Arguments:
        request (Request): FastAPI request object.

    Returns:
        KeywordsWithoutDocResponse: List containing all keywords without documentation with usage.

    """
    try:
        keywords_wo_doc = request.app.state.keyword_usage_service.get_keywords_without_documentation()
    except Exception as e:
        logger.exception("Error retrieving keywords without documentation.")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    return KeywordsWithoutDocResponse(keywords_wo_documentation=keywords_wo_doc)
