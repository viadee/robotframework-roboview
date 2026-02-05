"""Endpoint for retrieving all available robot and resource files."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import AllFilesResponse
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="All available resource and robot files",
    response_model=AllFilesResponse,
    responses={
        200: {"description": "Available resource and robot files retrieved successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def all_files(project_root_dir: str):  # noqa: ANN201
    """Endpoint to fetch all resource and robot files.

    Arguments:
        project_root_dir (str): The project_root_directory path.

    Returns:
        AllFilesResponse: List containing all resource and robot file names.

    """
    try:
        selection_files = []
        directory_parser = DirectoryParser(Path(project_root_dir))
        robot_files = directory_parser.get_test_file_paths()
        resource_files = directory_parser.get_resource_file_paths()

        selection_files.extend(SelectionFiles(file_name=file.name, path=file.as_posix()) for file in robot_files)

        selection_files.extend(SelectionFiles(file_name=file.name, path=file.as_posix()) for file in resource_files)

    except Exception as e:
        logger.exception("Error fetching Robot Framework files: ")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return AllFilesResponse(all_files=selection_files)
