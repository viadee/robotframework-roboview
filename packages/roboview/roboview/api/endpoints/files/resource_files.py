"""Endpoint for retrieving all available resource files."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import ResourceFilesResponse
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Available resource files",
    response_model=ResourceFilesResponse,
    responses={
        200: {"description": "Available resource files retrieved successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def resource_files(project_root_dir: Path):  # noqa: ANN201
    """Endpoint to fetch all resource files.

    Arguments:
        project_root_dir (str): The project_root_directory path.

    Returns:
        ResourceFilesResponse: List containing all resource files.

    """
    try:
        resource_files_list = []
        directory_parser = DirectoryParser(project_root_dir)
        resource_files = directory_parser.get_resource_file_paths()

        resource_files_list.extend(SelectionFiles(file_name=file.name, path=file.as_posix()) for file in resource_files)

    except Exception as e:
        logger.exception("Error fetching resource file names: ")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return ResourceFilesResponse(resource_files=resource_files_list)
