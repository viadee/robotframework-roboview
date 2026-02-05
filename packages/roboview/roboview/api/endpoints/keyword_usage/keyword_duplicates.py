"""Endpoint for fetching the potential duplicate keywords."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.keyword_similarity import DuplicateKeywordResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get all potential duplicate keywords",
    response_model=DuplicateKeywordResponse,  # noqa: FAST001
    responses={
        200: {"description": "Potential duplicate keywords fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_potential_duplicate_keywords(request: Request) -> DuplicateKeywordResponse:
    """Endpoint retrieving the top 5 most similar keywords.

    Arguments:
        request (Request): FastAPI request object.

    Returns:
        KeywordSimilarityResponse: top_n_similar_keywords (dict): Dictionary containing the n most similar keywords
        with similarity score.

    """
    try:
        potential_duplicate_keywords = request.app.state.keyword_usage_service.get_potential_duplicate_keywords(
            request.app.state.keyword_similarity_service
        )
    except Exception as e:
        logger.exception("Error retrieving potential duplicate keywords")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

    return DuplicateKeywordResponse(duplicate_keywords=potential_duplicate_keywords)
