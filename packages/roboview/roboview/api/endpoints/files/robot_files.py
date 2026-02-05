"""Endpoint for retrieving all available robot files."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import RobotFilesResponse
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Available robot files",
    response_model=RobotFilesResponse,
    responses={
        200: {"description": "Available robot files retrieved successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def robot_files(project_root_dir: Path):  # noqa: ANN201
    """Endpoint to fetch all robot files.

    Arguments:
        project_root_dir (Path): The project_root_directory path.

    Returns:
        :return robot_files (list): List containing all robot file names.

    """
    try:
        robot_files_list = []
        directory_parser = DirectoryParser(project_root_dir)
        robot_files = directory_parser.get_test_file_paths()

        robot_files_list.extend(SelectionFiles(file_name=file.name, path=file.as_posix()) for file in robot_files)

    except Exception as e:
        logger.exception("Error fetching resource file names: ")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return RobotFilesResponse(robot_files=robot_files_list)
