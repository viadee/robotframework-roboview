"""Endpoint for fetching keywords that have not total usages across the whole project."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.keyword_usage import KeywordsWithoutUsagesResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get keywords that have not total usages across the whole project.",
    response_model=KeywordsWithoutUsagesResponse,
    responses={
        200: {"description": "Keywords without usages fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_keywords_wo_usages(request: Request):  # noqa: ANN201
    """Returns a list of keywords that have no total usages across the whole project.

    Arguments:
        request (Request): FastAPI request object.

    Returns:
        KeywordsWithoutUsagesResponse: List containing all keywords that have no total usages.

    """
    try:
        keywords_wo_usages = request.app.state.keyword_usage_service.get_keywords_without_usages()
    except Exception as e:
        logger.exception("Error retrieving keywords without usages.")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    return KeywordsWithoutUsagesResponse(keywords_wo_usages=keywords_wo_usages)
