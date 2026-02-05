"""File retrieving schemas for pydantic validation."""

from pydantic import BaseModel, Field
from roboview.schemas.domain.files import SelectionFiles


class ResourceFilesResponse(BaseModel):
    """Response model to validate and return when requesting resource files."""

    resource_files: list[SelectionFiles] = Field(description="List of all resource files.")


class RobotFilesResponse(BaseModel):
    """Response model to validate and return when requesting robot files."""

    robot_files: list[SelectionFiles] = Field(description="List of all robot files.")


class AllFilesResponse(BaseModel):
    """Response model to validate and return when requesting robot and resource files."""

    all_files: list[SelectionFiles] = Field(description="List of all robot and resource files.")
