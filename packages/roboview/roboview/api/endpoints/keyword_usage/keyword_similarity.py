"""Endpoint for fetching the keyword similarity for a specific keyword."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.keyword_similarity import KeywordSimilarityResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get keyword similarity for a specific keyword",
    response_model=KeywordSimilarityResponse,  # noqa: FAST001
    responses={
        200: {"description": "Keyword similarity fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_keyword_similarity(request: Request, keyword_name: str) -> KeywordSimilarityResponse:
    """Endpoint retrieving the top 5 most similar keywords.

    Arguments:
        request (Request): FastAPI request object.
        keyword_name (str): Target keyword name to get the corresponding n most similar keywords.

    Returns:
        KeywordSimilarityResponse: top_n_similar_keywords (dict): Dictionary containing the n most similar keywords
        with similarity score.

    """
    try:
        top_n = 5
        top_n_similar_keywords = request.app.state.keyword_similarity_service.get_n_most_similar_keywords(
            keyword_name, top_n
        )
    except Exception as e:
        logger.exception("Error retrieving similarity values for keyword %s: ", keyword_name)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

    return KeywordSimilarityResponse(top_n_similar_keywords=top_n_similar_keywords)
