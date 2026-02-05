"""Endpoint for fetching KPIs for RoboView overview page."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.overview import KPIResponse
from roboview.utils.directory_parsing import DirectoryParser
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get KPIs for the Robot Framework project",
    response_model=KPIResponse,
    responses={
        200: {"description": "KPIs fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_kpis(request: Request, project_root_dir: Path):  # noqa: ANN201
    """Endpoint to fetch KPIs for the RoboView overview page.

    Arguments:
        request (Request): FastAPI request object.
        project_root_dir (Path): Path of the project root directory.

    Returns:
        KPIResponse: List containing all KPIs.

    """
    try:
        keyword_reusage_rate = request.app.state.keyword_usage_service.get_keyword_reusage_rate()
        documentation_coverage = request.app.state.keyword_usage_service.get_documentation_coverage()
        num_user_keywords = len(request.app.state.keyword_registry.get_user_defined_keywords())
        num_unused_keywords = len(request.app.state.keyword_usage_service.get_keywords_without_usages())
        num_robocop_issues = len(request.app.state.robocop_service.get_robocop_error_messages())

        directory_parser = DirectoryParser(Path(project_root_dir))
        robot_files_names = directory_parser.get_test_file_paths()
        resource_files_names = directory_parser.get_resource_file_paths()
        num_parsed_files = len(robot_files_names) + len(resource_files_names)

    except Exception as e:
        logger.exception("Error calculating KPIs")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return KPIResponse(
            num_user_keywords=num_user_keywords,
            num_unused_keywords=num_unused_keywords,
            keyword_reusage_rate=keyword_reusage_rate,
            num_robocop_issues=num_robocop_issues,
            documentation_coverage=documentation_coverage,
            num_rf_files=num_parsed_files,
        )
