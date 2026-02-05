"""Endpoint for fetching, where a target keyword is used across all robot files."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.common import FileType
from roboview.schemas.dtos.keyword_usage import KeywordUsageRobotResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get keyword usage for target keyword across all robot files",
    response_model=KeywordUsageRobotResponse,
    responses={
        200: {"description": "Keyword usages in robot files fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_kw_usage_robot(request: Request, keyword_name: str):  # noqa: ANN201
    """Endpoint to fetch all keyword usages in robot files.

    Arguments:
        request (Request): FastAPI request object.
        keyword_name (str): Keyword name to get the corresponding robot file usages.

    Returns:
        KeywordUsageRobotResponse: List containing all robot file names and usage for the specified keyword.

    """
    try:
        kw_usages_robot = request.app.state.keyword_usage_service.get_keyword_usage_in_files_for_target_keyword(
            keyword_name, FileType.ROBOT
        )
    except Exception as e:
        logger.exception("Error robot files for keyword %s: ", keyword_name)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return KeywordUsageRobotResponse(keyword_usage_robot=kw_usages_robot)
