"""Endpoint for fetching, where a target keyword is used across all resource files."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.common import FileType
from roboview.schemas.dtos.keyword_usage import KeywordUsageResourceResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get keyword usage for target keyword across all resource files",
    response_model=KeywordUsageResourceResponse,  # noqa: FAST001
    responses={
        200: {"description": "Keyword usages in resource files fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_kw_usage_resource(request: Request, keyword_name: str) -> KeywordUsageResourceResponse:
    """Endpoint to fetch all keyword usages in resource files.

    Arguments:
        request (Request): FastAPI request object.
        keyword_name (str): Keyword name to get the corresponding resource file usages.

    Returns:
        KeywordUsageResourceResponse: List containing all resource file names and usage for the specified keyword.

    """
    try:
        kw_usages_resource = request.app.state.keyword_usage_service.get_keyword_usage_in_files_for_target_keyword(
            keyword_name, FileType.RESOURCE
        )
    except Exception as e:
        logger.exception("Error fetching resource files for keyword %s: ", keyword_name)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return KeywordUsageResourceResponse(keyword_usage_resource=kw_usages_resource)
